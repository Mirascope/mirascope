"""Integration with Griffe for API documentation generation.

This module provides functionality to process API directives and generate
documentation using Griffe. The implementation follows a clear model-view
pattern where:
1. Data is extracted and processed into structured models (via process_* functions)
2. Models are rendered into MDX format (via render_* functions)
3. Error handling ensures graceful fallbacks for missing dependencies

The code is organized in the following sections:
- Configuration: Loader setup for parsing docstrings
- Documentation Generation: Core object processing and rendering
- Directive Processing: Handling API directives and error cases
"""

# Forward declaration for type hints
from typing import TYPE_CHECKING

from griffe import (
    Alias,
    GriffeLoader,
    Module,
    Object,
    Parser,
)

from api2mdx.api_discovery import RawDirective
from api2mdx.mdx_renderer import (
    render_object,
)

if TYPE_CHECKING:
    from api2mdx.api_discovery import ApiDocumentation

from api2mdx.models import (
    process_object,
)

# Default content subpath for documentation
MODULE_CONTENT_SUBPATH = "docs/mirascope"


def get_loader() -> GriffeLoader:
    """Create a configured Griffe loader."""
    # Set up the parser for Google-style docstrings
    parser = Parser("google")

    # Create loader with specified docstring parser
    loader = GriffeLoader(docstring_parser=parser)

    return loader


def document_object(
    obj: Object | Alias, doc_path: str, api_docs: "ApiDocumentation"
) -> str:
    """Generate documentation for any supported Griffe object type.

    Args:
        obj: The Griffe object to document
        doc_path: Optional path to the document, used for API component links

    Returns:
        MDX documentation with enhanced component usage

    """
    # Process all objects the same way - modules get their own dedicated pages
    processed_obj = process_object(obj, api_docs)
    if processed_obj is None:
        raise ValueError(f"Failed to process object: {obj}")

    return render_object(processed_obj, doc_path, api_docs)


def render_directive(
    directive: RawDirective, module: Module, doc_path: str, api_docs: "ApiDocumentation"
) -> str:
    """Process an API directive and generate documentation.

    Args:
        directive: The Directive object containing object path and type
        module: The pre-loaded Griffe module
        doc_path: Optional path to the document, used for API component links

    Returns:
        The generated documentation content

    """
    object_path = directive.object_path

    # Split the path to navigate to the object
    path_parts = object_path.split(".")

    # Start with the loaded module
    current_obj: Object | Alias = module

    # If the directive path exactly matches the loaded module path, return the module itself
    if object_path == module.canonical_path:
        pass  # current_obj is already the target module
    else:
        # Navigate through the object path, skipping parts that match the module path
        module_parts = module.canonical_path.split(".")

        # Find the starting index - skip parts that match the loaded module path
        start_index = 0
        if path_parts[: len(module_parts)] == module_parts:
            start_index = len(module_parts)

        # Navigate from the starting index
        for i, part in enumerate(path_parts[start_index:], start_index):
            if hasattr(current_obj, "members") and part in current_obj.members:
                current_obj = current_obj.members[part]
            else:
                raise ValueError(
                    f"Could not find {'.'.join(path_parts[: i + 1])} in the module."
                )

    # Use the document_object dispatcher function
    return document_object(current_obj, doc_path, api_docs)
