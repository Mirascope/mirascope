#!/usr/bin/env python3
"""Regenerate example files from Jinja2 templates."""

import re
import subprocess
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader


@dataclass
class ExampleTemplate:
    """Configuration for generating examples from a template."""

    path: Path
    basename: str
    options: list[str] | None  # e.g., ["async", "stream", "tools", "context"]


def parse_template_metadata(template_path: Path) -> ExampleTemplate:
    """Parse metadata from a Jinja2 template file."""
    content = template_path.read_text()

    # Look for metadata comment block
    pattern = r"\{\#\s*TEMPLATE_METADATA:(.*?)\#\}"
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        raise ValueError(f"No TEMPLATE_METADATA found in {template_path}")

    metadata_yaml = match.group(1).strip()
    metadata = yaml.safe_load(metadata_yaml)

    # Extract basename from filename (remove .j2 extension)
    basename = template_path.stem

    return ExampleTemplate(
        path=template_path.parent,
        basename=basename,
        options=metadata.get("options", []),
    )


def discover_templates(root_path: Path) -> list[ExampleTemplate]:
    """Discover all *.j2 template files and parse their metadata."""
    templates = []
    for template_file in root_path.rglob("*.j2"):
        # Skip macro/include files (starting with _)
        if template_file.name.startswith("_"):
            continue

        template_config = parse_template_metadata(template_file)
        templates.append(template_config)

    return templates


def get_all_combinations(options: list[str] | None) -> list[list[str]]:
    """Get all valid combinations of options."""
    if options is None:
        options = []

    all_combos = []

    # Base case (no options)
    all_combos.append([])

    # All possible combinations of options
    for r in range(1, len(options) + 1):
        for combo in combinations(options, r):
            all_combos.append(list(combo))

    return all_combos


def get_filename(basename: str, combo: list[str]) -> str:
    """Get filename for a given combination of options."""
    if not combo:
        return f"{basename}.py"

    parts = [basename] + sorted(combo)
    return f"{'_'.join(parts)}.py"


def get_template_vars(options: list[str] | None, combo: list[str]) -> dict:
    """Get template variables for a given combination of options."""
    if options is None:
        options = []
    return {f"use_{option}": option in combo for option in options}


def generate_examples(template_config: ExampleTemplate) -> None:
    """Generate all example files for a template configuration."""
    # Remove existing Python files that match the basename pattern
    pattern = f"{template_config.basename}*.py"
    for existing_file in template_config.path.glob(pattern):
        existing_file.unlink()

    # Generate all combinations of options
    combinations = get_all_combinations(template_config.options)
    examples_root = Path(__file__).parent.parent / "examples"
    rel_path = template_config.path.relative_to(examples_root)
    template_path = rel_path / f"{template_config.basename}.j2"

    for combo in combinations:
        filename = get_filename(template_config.basename, combo)
        template_vars = get_template_vars(template_config.options, combo)

        # Create fresh environment for each template with global variables
        env = Environment(loader=FileSystemLoader(examples_root))
        env.globals.update(template_vars)
        template = env.get_template(str(template_path))

        content = template.render(**template_vars)
        filepath = template_config.path / filename

        with open(filepath, "w") as f:
            f.write(content)

    # Format all generated files with ruff
    generated_files = list(template_config.path.glob(f"{template_config.basename}*.py"))
    if generated_files:
        python_dir = Path(__file__).parent.parent
        subprocess.run(
            ["uv", "run", "ruff", "check", "--fix"] + [str(f) for f in generated_files],
            check=True,
            cwd=python_dir,
        )
        subprocess.run(
            ["uv", "run", "ruff", "format"] + [str(f) for f in generated_files],
            check=True,
            cwd=python_dir,
        )


def main() -> None:
    """Main entry point for regenerating examples."""
    examples_root = Path(__file__).parent.parent / "examples"
    templates = discover_templates(examples_root)

    for template_config in templates:
        generate_examples(template_config)


if __name__ == "__main__":
    main()
