#!/usr/bin/env python3
"""
Script to automatically generate docs/content/examples.mdx from all Python examples
in python/examples directory.
"""

import os
from pathlib import Path
from typing import Dict, List


def get_section_order() -> List[str]:
    """Define the order of sections in the output."""
    return [
        "calls",
        "streams", 
        "tools",
        "agents",
        "structured_outputs",
        "messages",
        "prompt_templates"
    ]


def get_section_title(section: str) -> str:
    """Convert section directory name to display title."""
    titles = {
        "calls": "Calls",
        "streams": "Streams", 
        "tools": "Tools",
        "agents": "Agents",
        "structured_outputs": "Response Formats",
        "messages": "Messages",
        "prompt_templates": "Prompt Templates"
    }
    return titles.get(section, section.replace("_", " ").title())


def collect_examples(examples_dir: Path) -> Dict[str, List[Path]]:
    """Collect all Python example files organized by section."""
    sections = {}
    
    for section_dir in examples_dir.iterdir():
        if not section_dir.is_dir() or section_dir.name.startswith('.'):
            continue
            
        section_name = section_dir.name
        sections[section_name] = []
        
        # Recursively find all .py files
        for py_file in section_dir.rglob("*.py"):
            # Skip template files and other non-example files
            if py_file.name.endswith('.j2') or py_file.name.startswith('_'):
                continue
            sections[section_name].append(py_file)
    
    # Sort files within each section
    for section in sections:
        sections[section].sort()
    
    return sections


def generate_examples_mdx(examples_dir: Path, output_path: Path):
    """Generate the examples.mdx file."""
    sections = collect_examples(examples_dir)
    section_order = get_section_order()
    
    content = []
    content.append("---")
    content.append("title: Examples")
    content.append("description: Unified doc with diverse examples, intended as a primer for LLMs on common Mirascope patterns.")
    content.append("---")
    content.append("")
    content.append("# Unified Examples")
    content.append("")
    content.append("This document contains a wide variety of Mirascope code examples, intended for feeding as context to LLMs to get a comprehensive primer of Mirascope v2 usage patterns.")
    content.append("")
    
    # Process sections in order
    for section in section_order:
        if section not in sections or not sections[section]:
            continue
            
        content.append(f"## {get_section_title(section)}")
        content.append("")
        
        for py_file in sections[section]:
            # Get relative path from examples directory
            rel_path = py_file.relative_to(examples_dir)
            
            # Create section header using relative path
            content.append(f"### `{rel_path}`")
            content.append("")
            content.append(f'<CodeExample file="examples/{rel_path}" />')
            content.append("")
    
    # Add any remaining sections not in the ordered list
    for section, files in sections.items():
        if section in section_order or not files:
            continue
            
        content.append(f"## {get_section_title(section)}")
        content.append("")
        
        for py_file in files:
            rel_path = py_file.relative_to(examples_dir)
            content.append(f"### `{rel_path}`")
            content.append("")
            content.append(f'<CodeExample file="examples/{rel_path}" />')
            content.append("")
    
    # Write the file
    with open(output_path, 'w') as f:
        f.write('\n'.join(content))


def main():
    """Main function."""
    # Get paths relative to script location
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent
    examples_dir = repo_root / "python" / "examples"
    output_path = repo_root / "docs" / "content" / "examples.mdx"
    
    if not examples_dir.exists():
        print(f"Examples directory not found: {examples_dir}")
        return 1
    
    print(f"Scanning examples in: {examples_dir}")
    print(f"Generating: {output_path}")
    
    generate_examples_mdx(examples_dir, output_path)
    print("Generated examples.mdx successfully!")
    
    return 0


if __name__ == "__main__":
    exit(main())