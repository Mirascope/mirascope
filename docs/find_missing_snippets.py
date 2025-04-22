"""Scope:
Finds every code import in docs/learn/**/*.md, and checks that the target file exists.

Usage: python -m docs.find_missing_snippets

Note: The script depends on hand-maintained substitutions
in FILE_SPECIFIC_SUBSTITUTUTIONS, which may require updates as documents
are changed or updated. There is automated testing to ensure that all new
imports exist, which will fail if FILE_SPECIFIC_SUBSTITUTUTIONS is not updated.
"""

import re
from collections.abc import Iterable
from itertools import product
from pathlib import Path

# Define the namedtuple
from typing import Dict, List, NamedTuple

import yaml
from docs.generate_provider_examples import (
    generate_provider_examples,
)

Substitutions = Dict[str, List[str]]


# Hardcoded list of which docs files have non-standard substitutions,
# which we maintain by hand because this changes infrequently and implementing a general
# solution via parsing the jinja2 templates and environment is overkill.
FILE_SPECIFIC_SUBSTITUTIONS: dict[str, Substitutions] = {
    "docs/learn/tools.md": {
        "{{ tool_method }}": ["base_tool", "function"],
        "{{ pre_made_tool_method }}": ["basic_usage", "custom_config"],
    },
    "docs/learn/local_models.md": {
        "{{ provider.lower() }}": ["ollama", "vllm"],
    },
    "docs/learn/prompts.md": {
        "{{ audio_pkg }}": ["pydub", "wave"],
        "{{ filename }}": ["lists", "texts", "parts"],
    },
}


def extact_yaml_section(file_path, section_name):
    # Manually get some info from yaml files, as mkdocs.yml is not easy to parse
    section_lines = []
    in_section = False
    section_indent = None

    with open(file_path, "r") as file:
        section_indent = 0
        for line in file:
            if line.lstrip().startswith(section_name + ":"):
                in_section = True
                section_indent = len(line) - len(line.lstrip())
                continue

            if in_section:
                current_indent = len(line) - len(line.lstrip())
                if current_indent > section_indent:
                    section_lines.append(line)
                else:
                    break

    section_content = "\n".join(section_lines)
    return yaml.safe_load(section_content) if section_lines else []


CONFIG_FILE = Path("mkdocs.yml")
PROVIDERS = [
    p.split()[0].lower()
    for p in extact_yaml_section(CONFIG_FILE, "supported_llm_providers")
]
BASE_SUBSTITUTIONS = {
    "{{ provider | provider_dir }}": PROVIDERS,
    "{{ method }}": extact_yaml_section(CONFIG_FILE, "prompt_writing_methods"),
}


class Snippet(NamedTuple):
    path: Path
    source_file: Path


def substituted_snippet_paths(
    markdown_content: str, substitutions: dict[str, list[str]]
) -> Iterable[Path]:
    pattern = r'--8<--\s*"([^"]+\.py(?::\d+(?::\d+)?)?)"'
    # Extract paths and strip line numbers
    paths = {
        match.group(1).split(":")[0] for match in re.finditer(pattern, markdown_content)
    }

    for path in paths:
        # Find all keys in the import path that need substitution
        keys_to_substitute = [key for key in substitutions if key in path]

        # Generate all combinations of substitutions for the keys
        substitution_combinations = product(
            *(substitutions[key] for key in keys_to_substitute)
        )

        for combination in substitution_combinations:
            # Create a new path with all substitutions applied
            new_path = path
            for key, value in zip(keys_to_substitute, combination):
                new_path = new_path.replace(key, value)

            yield Path(new_path)


def missing_snippets_for_file(
    markdown_path: Path, substitutions: dict[str, list[str]]
) -> Iterable[Snippet]:
    markdown_content = markdown_path.read_text()
    for path in substituted_snippet_paths(markdown_content, substitutions):
        if not path.exists():
            yield Snippet(path, markdown_path)  # pragma: no cover


def all_missing_snippets(root_dir: Path) -> Iterable[Snippet]:
    provider_example_dirs = extact_yaml_section(CONFIG_FILE, "provider_example_dirs")
    generate_provider_examples(
        example_dirs=provider_example_dirs,
        examples_root=root_dir / "examples",
        snippets_dir=root_dir / "build/snippets",
    )
    for md_path in root_dir.glob("docs/**/*.md"):
        relative_path = md_path.relative_to(root_dir)
        substitutions = {
            **BASE_SUBSTITUTIONS,
            **FILE_SPECIFIC_SUBSTITUTIONS.get(str(relative_path), {}),
        }
        yield from missing_snippets_for_file(md_path, substitutions)


if __name__ == "__main__":  # pragma: no cover
    for imp in all_missing_snippets(Path(".")):
        print(f"Missing import: {imp.path} (from {imp.source_file})")
