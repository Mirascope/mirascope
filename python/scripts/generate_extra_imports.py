"""Generate EXTRA_IMPORTS mapping from pyproject.toml by inspecting packages.

This script installs each package from optional-dependencies in isolation
and inspects its installed files to determine the actual Python import paths.

Usage:
    # Output JSON for CI validation
    uv run python scripts/generate_extra_imports.py

    # Update _stubs.py with generated mapping
    uv run python scripts/generate_extra_imports.py --overwrite
"""

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import tomli


def normalize_package_name(package_spec: str) -> str:
    """Extract package name from version spec like 'package>=1.0.0'."""
    for op in [">=", "==", "<=", ">", "<", "~="]:
        if op in package_spec:
            package_spec = package_spec.split(op)[0]
    return package_spec.strip()


def get_import_paths(package_spec: str) -> list[str]:
    """Get the import path(s) to check for a package.

    For example:
    - opentelemetry-exporter-otlp → ['opentelemetry.exporter.otlp']
    - anthropic → ['anthropic']
    - google-genai → ['google.genai']

    Args:
        package_spec: Package spec like 'opentelemetry-exporter-otlp>=1.38.0'

    Returns:
        List of import paths to check
    """
    pkg_name = normalize_package_name(package_spec)

    with tempfile.TemporaryDirectory() as tmpdir:
        # Install package to temp location
        install_result = subprocess.run(
            ["uv", "pip", "install", "--target", tmpdir, package_spec],
            capture_output=True,
            text=True,
        )

        if install_result.returncode != 0:
            # Fallback: use package name convention
            return [pkg_name.replace("-", "_")]

        tmpdir_path = Path(tmpdir)
        normalized_pkg = pkg_name.replace("-", "_").lower()

        # Find matching dist-info
        matching_dist_infos = [
            d
            for d in tmpdir_path.glob("*.dist-info")
            if d.name.lower().startswith(normalized_pkg + "-")
        ]

        if not matching_dist_infos:
            return [pkg_name.replace("-", "_")]

        dist_info = matching_dist_infos[0]
        record_file = dist_info / "RECORD"

        if not record_file.exists():
            return [pkg_name.replace("-", "_")]

        # Find all Python module paths this distribution provides
        all_paths: set[tuple[str, ...]] = set()
        for line in record_file.read_text().split("\n"):
            if not line or "/" not in line:
                continue
            file_path = line.split(",")[0]
            if file_path.startswith(dist_info.name) or file_path.startswith("bin/"):
                continue

            # Only consider Python files, skip binary libraries and pycache
            if not file_path.endswith(".py") and "/__pycache__/" in file_path:
                continue

            parts = file_path.split("/")
            if not parts[0] or parts[0].startswith("_"):
                continue

            # Skip binary library directories (e.g., pillow.libs, numpy.libs)
            if any(part.endswith(".libs") for part in parts):
                continue

            # Build the module path (excluding the filename)
            module_parts: list[str] = []
            for part in parts[:-1]:
                if part == "__pycache__" or part.startswith("_"):
                    break
                module_parts.append(part)

            if module_parts:
                all_paths.add(tuple(module_parts))

        if not all_paths:
            return [pkg_name.replace("-", "_")]

        # Find the shortest common prefix for each top-level namespace
        by_namespace: dict[str, list[tuple[str, ...]]] = {}
        for path in all_paths:
            namespace = path[0]
            by_namespace.setdefault(namespace, []).append(path)

        result: list[str] = []
        for namespace, paths in sorted(by_namespace.items()):
            if len(paths) == 1:
                result.append(".".join(paths[0]))
            else:
                # Find common prefix among all paths, but prefer shorter paths
                # For namespace packages, the shortest unique path is usually correct
                sorted_paths = sorted(paths, key=len)
                common: tuple[str, ...] = sorted_paths[0]

                for path in sorted_paths[1:]:
                    if path[: len(common)] != common:
                        # Find common prefix
                        common = tuple(
                            a for a, b in zip(common, path, strict=False) if a == b
                        )
                    if not common:
                        common = (namespace,)
                        break

                result.append(".".join(common))

        return result


def generate_mapping() -> dict[str, list[str]]:
    """Generate EXTRA_IMPORTS from pyproject.toml."""
    pyproject = Path(__file__).parent.parent / "pyproject.toml"

    if not pyproject.exists():
        print(f"Error: {pyproject} not found", file=sys.stderr)
        sys.exit(1)

    with open(pyproject, "rb") as f:
        config = tomli.load(f)

    extras: dict[str, list[str]] = config["project"]["optional-dependencies"]
    mapping: dict[str, list[str]] = {}

    for extra_name, packages in extras.items():
        if extra_name == "all":
            continue

        imports: list[str] = []
        seen: set[str] = set()

        for package_spec in packages:
            for import_name in get_import_paths(package_spec):
                if import_name not in seen:
                    imports.append(import_name)
                    seen.add(import_name)

        mapping[extra_name] = imports

    return mapping


def format_as_python(mapping: dict[str, list[str]]) -> str:
    """Format the mapping as Python code for _stubs.py."""
    lines = ["EXTRA_IMPORTS: dict[str, list[str]] = {"]

    for extra_name, imports in mapping.items():
        if len(imports) == 1:
            lines.append(f'    "{extra_name}": ["{imports[0]}"],')
        else:
            lines.append(f'    "{extra_name}": [')
            for imp in imports:
                lines.append(f'        "{imp}",')
            lines.append("    ],")

    lines.append("}")
    return "\n".join(lines)


def update_stubs_file(mapping: dict[str, list[str]]) -> None:
    """Update _stubs.py with the generated mapping."""
    stubs_file = Path(__file__).parent.parent / "mirascope" / "_stubs.py"

    if not stubs_file.exists():
        print(f"Error: {stubs_file} not found", file=sys.stderr)
        sys.exit(1)

    content = stubs_file.read_text()

    # Find the EXTRA_IMPORTS section using markers
    start_marker = "# BEGIN GENERATED - DO NOT EDIT MANUALLY"
    end_marker = "# END GENERATED"

    if start_marker not in content or end_marker not in content:
        print(
            f"Error: Could not find markers in {stubs_file}",
            file=sys.stderr,
        )
        print("Expected markers:", file=sys.stderr)
        print(f"  {start_marker}", file=sys.stderr)
        print(f"  {end_marker}", file=sys.stderr)
        sys.exit(1)

    # Replace content between markers
    pattern = f"({re.escape(start_marker)})(.*?)({re.escape(end_marker)})"
    generated_code = format_as_python(mapping)

    new_content = re.sub(
        pattern,
        rf"\1\n{generated_code}\n\3",
        content,
        flags=re.DOTALL,
    )

    stubs_file.write_text(new_content)
    print(f"✓ Updated {stubs_file}", file=sys.stderr)


if __name__ == "__main__":
    mapping = generate_mapping()

    # Check for --overwrite flag
    if "--overwrite" in sys.argv:
        update_stubs_file(mapping)
    else:
        # Default: output JSON for CI validation
        print(json.dumps(mapping, indent=2))
