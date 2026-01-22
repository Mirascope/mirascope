"""TypeScript meta.ts representation in Python.

This module provides Python classes that mirror the TypeScript interfaces used in the
`src/lib/content/spec.ts` file for structuring documentation metadata.
"""

import json
import re
from pathlib import Path
from typing import Any

from api2mdx.api_discovery import DirectivesPage

# Constants
SINGLE_NESTING_LEVEL = 2  # Path with format "parent/child" has 2 parts


class DocSpec:
    """Python representation of TypeScript DocSpec interface.

    Attributes:
        slug: URL slug component (no slashes)
        label: Display name in sidebar
        children: Child items (if this is a folder)
        has_extractable_snippets: Flag to indicate the doc has code snippets to extract
        weight: Search weight for this item (multiplicative with parent weights)
        has_content: If true, this item has its own content page (not just a folder).
                     Defaults to true if no children, false if has children.

    """

    def __init__(
        self,
        slug: str,
        label: str,
        children: list["DocSpec"] | None = None,
        has_extractable_snippets: bool | None = None,
        weight: float | None = None,
        has_content: bool | None = None,
    ) -> None:
        """Initialize a DocSpec.

        Args:
            slug: URL slug component (no slashes)
            label: Display name in sidebar
            children: Child items (if this is a folder)
            has_extractable_snippets: Whether the item has extractable code snippets
            weight: Search weight for this item (multiplicative with parent weights)
            has_content: If true, this item has its own content page (not just a folder).
                        Defaults to true if no children, false if has children.

        """
        self.slug = slug
        self.label = label
        self.children = children
        self.has_extractable_snippets = has_extractable_snippets
        self.weight = weight
        self.has_content = has_content

    def to_dict(self) -> dict[str, Any]:
        """Convert to a dictionary for serialization to TypeScript."""
        result: dict[str, Any] = {
            "slug": self.slug,
            "label": self.label,
        }

        if self.weight is not None:
            result["weight"] = self.weight

        if self.has_content is not None:
            result["hasContent"] = self.has_content

        if self.children is not None:
            result["children"] = [child.to_dict() for child in self.children]

        return result


class SectionSpec:
    """Python representation of TypeScript SectionSpec interface.

    Attributes:
        slug: Section slug for URL
        label: Display name
        children: Items in this section
        weight: Search weight for this section (multiplicative with product weight)

    """

    def __init__(
        self,
        slug: str,
        label: str,
        children: list[DocSpec],
        weight: float | None = None,
    ) -> None:
        """Initialize a SectionSpec.

        Args:
            slug: Section slug for URL
            label: Display name
            children: Items in this section
            weight: Search weight for this section (multiplicative with product weight)

        """
        self.slug = slug
        self.label = label
        self.children = children
        self.weight = weight

    def to_dict(self) -> dict[str, Any]:
        """Convert to a dictionary for serialization to TypeScript."""
        result: dict[str, Any] = {
            "slug": self.slug,
            "label": self.label,
        }

        if self.weight is not None:
            result["weight"] = self.weight

        result["children"] = [child.to_dict() for child in self.children]

        return result

    def to_typescript(self) -> str:
        """Convert the SectionSpec to TypeScript code."""
        # Convert to dict then to JSON with indentation for readability
        doc_dict = self.to_dict()
        json_str = json.dumps(doc_dict, indent=2)

        # Fix boolean values (true/false instead of True/False)
        json_str = json_str.replace("True", "true").replace("False", "false")

        # Convert JSON keys without quotes to TypeScript style
        json_str = re.sub(r'"(\w+)":', r"\1:", json_str)

        return json_str


def generate_meta_file_content(
    section: SectionSpec, export_name: str = "apiMeta"
) -> str:
    """Generate a complete TypeScript meta file content.

    Args:
        section: The SectionSpec object to convert to TypeScript
        export_name: The name to use for the exported variable (default: "apiMeta")

    Returns:
        A string containing the complete TypeScript file content

    """
    content = []
    # Add header
    content.append("/**")
    content.append(" * AUTO-GENERATED API DOCUMENTATION - DO NOT EDIT")
    content.append(" */")
    content.append("")
    # Add imports
    content.append('import type { SectionSpec } from "../../../cloud/app/lib/content/spec";')
    content.append("")
    # Add the export declaration
    content.append(
        f"export const {export_name}: SectionSpec = {section.to_typescript()};"
    )
    content.append("")
    # Add default export
    content.append(f"export default {export_name};")
    return "\n".join(content)


def generate_meta_from_directives(
    directives: list[DirectivesPage],
    weight: float | None,  # Default weight for API sections
) -> SectionSpec:
    """Generate a SectionSpec from API directives.

    Args:
        directives: List of ApiDirective objects
        weight: Search weight for this section (default: 0.25)

    Returns:
        A SectionSpec object representing the API structure

    """
    # Create a SectionSpec for the API
    section_slug = "api"
    section_label = "API Reference"
    children = []

    # Build a tree structure from the directives
    path_tree: dict[str, Any] = {}

    for api_directive in directives:
        # Convert file path to path parts
        path_parts = api_directive.file_path.replace(".mdx", "").split("/")

        # Navigate/create the tree structure
        current_level = path_tree
        for i, part in enumerate(path_parts):
            if part not in current_level:
                current_level[part] = {"_files": [], "_children": {}}

            if i == len(path_parts) - 1:
                # This is a file - store the ApiDirective
                current_level[part]["_files"].append(api_directive)
            else:
                # This is a directory
                current_level = current_level[part]["_children"]

    # Convert tree to DocSpec objects
    children = _tree_to_docspecs(path_tree, weight)

    return SectionSpec(
        slug=section_slug,
        label=section_label,
        children=children,
        weight=weight,
    )


def _tree_to_docspecs(tree: dict[str, Any], weight: float | None) -> list[DocSpec]:
    """Convert a path tree to DocSpec objects.

    Args:
        tree: Tree structure from generate_meta_from_directives
        weight: Weight to apply to items (optional)

    Returns:
        List of DocSpec objects

    """
    specs = []

    for name, node in tree.items():
        files = node.get("_files", [])
        children_tree = node.get("_children", {})

        # Determine label: use API directive name if we have a file, else titleify the name
        if files:
            assert len(files) == 1, (
                f"Expected exactly one file for {name}, got {len(files)}"
            )
            label = files[0].name
        else:
            label = titleify(name)

        # Process children if any
        children = _tree_to_docspecs(children_tree, weight) if children_tree else None

        # Determine has_content: explicit True for hybrid items (has both file and children)
        has_content = True if (files and children) else None

        specs.append(
            DocSpec(
                slug=name,
                label=label,
                children=children,
                weight=weight,
                has_content=has_content,
            )
        )

    return specs


def generate_meta_from_organized_files(
    organized_files: dict[str, list[Path]],
    weight: float = 0.25,  # Default weight for API sections
) -> SectionSpec:
    """Generate a SectionSpec from organized files.

    Args:
        organized_files: A dictionary of files organized by directory
        weight: Search weight for this section (default: 0.25)

    Returns:
        A SectionSpec object representing the API structure

    """
    # Create a SectionSpec for the API
    section_slug = "api"
    section_label = "API Reference"
    children = []

    # Process files in the root directory
    root_files = organized_files.get("", [])
    root_items = create_doc_specs(root_files)

    # Add an index item if it doesn't exist
    if not any(item.slug == "index" for item in root_items):
        # Create a synthetic index item and put it first
        children.append(DocSpec(slug="index", label="Overview"))

    # Add the remaining root items
    children.extend(root_items)

    # Process all subdirectories as child DocSpecs
    for dir_name, files in sorted(organized_files.items()):
        if dir_name == "":
            continue

        # Skip items already processed at root level
        if "/" not in dir_name:
            child_specs = create_doc_specs(files)
            if child_specs:
                # Check if there's also a root file with this name (hybrid case)
                has_root_file = any(item.slug == dir_name for item in root_items)
                child = DocSpec(
                    slug=dir_name,
                    label=titleify(dir_name),
                    children=child_specs,
                    has_content=True if has_root_file else None,
                )
                children.append(child)
            continue

        # Handle nested directories
        parts = dir_name.split("/")
        parent_slug = parts[0]

        # Find the parent item in the children list
        parent_item = next(
            (item for item in children if item.slug == parent_slug), None
        )
        if parent_item is None:
            # Create a new parent item if it doesn't exist
            parent_item = DocSpec(
                slug=parent_slug, label=titleify(parent_slug), children=[]
            )
            children.append(parent_item)
        else:
            # Parent already exists (from root files) - mark it as having content
            parent_item.has_content = True

        # Ensure parent has children list
        if parent_item.children is None:
            parent_item.children = []

        # For simplicity, just handling one level of nesting
        # For deeper nesting, a recursive approach would be needed
        if len(parts) == SINGLE_NESTING_LEVEL:
            child_slug = parts[1]
            # Check if this child already exists
            if not any(child.slug == child_slug for child in parent_item.children):
                child_specs = create_doc_specs(files)
                child = DocSpec(
                    slug=child_slug,
                    label=titleify(child_slug),
                    children=child_specs if child_specs else None,
                )
                parent_item.children.append(child)

    # Sort children alphabetically to ensure consistent output
    for item in children:
        if item.children:
            item.children.sort(key=lambda x: x.slug)
    children.sort(key=lambda x: x.slug)

    # Make sure "index" is first
    children.sort(key=lambda x: "0" if x.slug == "index" else x.slug)

    # Create the section with all content
    return SectionSpec(
        slug=section_slug,
        label=section_label,
        children=children,
        weight=weight,
    )


def titleify(stem: str) -> str:
    """Convert a string to a title format.

    Args:
        stem: The string to convert

    Returns:
        A title-formatted string

    """
    return stem.replace("_", " ").title()


def create_doc_specs(files: list[Path]) -> list[DocSpec]:
    """Create a list of DocSpec from a list of file paths.

    Args:
        files: A list of file paths

    Returns:
        A list of DocSpec objects

    """
    result = []
    stems = sorted({item.stem for item in files})

    # Handle index files first
    if "index" in stems:
        result.append(DocSpec(slug="index", label="Overview"))
        stems.remove("index")

    # Add the rest of the files
    for stem in stems:
        result.append(DocSpec(slug=stem, label=titleify(stem)))

    return result
