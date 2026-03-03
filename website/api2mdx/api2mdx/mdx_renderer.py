"""MDX renderer for processed API documentation objects.

This module provides functions to render processed API objects into MDX format
for documentation websites. It focuses purely on the rendering aspect, working
with pre-processed data models rather than directly with Griffe objects.
"""

# Forward declaration for type hints
from typing import TYPE_CHECKING

from api2mdx.mdx_components import (
    ApiType,
    ApiTypeKind,
    AttributesTable,
    ParametersTable,
    ReturnTable,
    TypeLink,
)
from api2mdx.models import (
    ProcessedAlias,
    ProcessedAttribute,
    ProcessedClass,
    ProcessedFunction,
    ProcessedModule,
    ProcessedObject,
)

if TYPE_CHECKING:
    from api2mdx.api_discovery import ApiDocumentation


def render_object(
    processed_obj: ProcessedObject, doc_path: str, api_docs: "ApiDocumentation"
) -> str:
    """Render any processed object into MDX documentation.

    Args:
        processed_obj: The processed object to render
        doc_path: Path to the document, used for API component links
        api_docs: The API documentation registry

    Returns:
        MDX documentation string

    """
    if isinstance(processed_obj, ProcessedModule):
        return render_module(processed_obj, doc_path, api_docs)
    elif isinstance(processed_obj, ProcessedClass):
        return render_class(processed_obj, doc_path, api_docs)
    elif isinstance(processed_obj, ProcessedFunction):
        return render_function(processed_obj, doc_path, api_docs)
    elif isinstance(processed_obj, ProcessedAttribute):
        return render_attribute(processed_obj, doc_path, api_docs)
    elif isinstance(processed_obj, ProcessedAlias):
        return render_alias(processed_obj, doc_path, api_docs)
    else:
        raise ValueError(f"Unsupported object type: {type(processed_obj)}")


def render_module(
    processed_module: ProcessedModule, doc_path: str, api_docs: "ApiDocumentation"
) -> str:
    """Render a processed module into MDX documentation.

    Args:
        processed_module: The processed module object to render
        doc_path: Path to the document, used for API component links
        api_docs: The API documentation registry

    Returns:
        MDX documentation string

    """
    # Check if there's exactly one member (special compact rendering case)
    if len(processed_module.members) == 1:
        content = []

        # Add docstring if available (keeping important usage links)
        if processed_module.docstring:
            content.append(processed_module.docstring.strip())
            content.append("")

        # Add the single member item
        content.append(render_object(processed_module.members[0], doc_path, api_docs))

        return "\n".join(content)

    # Otherwise, use the standard module rendering approach
    content: list[str] = []

    # Get the module name for the heading
    module_name = processed_module.module_path.split(".")[-1]

    # Add heading with embedded ApiType component
    slug = api_docs.get_slug(processed_module.object_path)
    api_type = ApiType(ApiTypeKind.MODULE, slug, module_name)
    content.append(f"## {api_type.render()} {module_name}\n")

    # Add docstring if available
    if processed_module.docstring:
        content.append(processed_module.docstring.strip())
        content.append("")

    # # Render all members in order
    # for member in processed_module.members:
    #     content.append(render_object(member, doc_path, api_docs))
    #     content.append("")

    return "\n".join(content)


def render_function(
    processed_func: ProcessedFunction, doc_path: str, api_docs: "ApiDocumentation"
) -> str:
    """Render a processed function into MDX documentation.

    Args:
        processed_func: The processed function object to render
        doc_path: Path to the document, used for API component links
        api_docs: The API documentation registry

    Returns:
        MDX documentation string

    """
    content: list[str] = []

    # Add heading with embedded ApiType component
    slug = api_docs.get_slug(processed_func.object_path)
    api_type = ApiType(ApiTypeKind.FUNCTION, slug, processed_func.name)
    content.append(f"## {api_type.render()} {processed_func.name}\n")

    # Add docstring if available
    if processed_func.docstring:
        content.append(processed_func.docstring.strip())
        content.append("")

    # Add parameters table if available
    if processed_func.parameters:
        params_table = ParametersTable(processed_func.parameters)
        content.append(params_table.render())

    # Add return type if available
    if processed_func.return_info:
        return_table = ReturnTable(processed_func.return_info)
        content.append(return_table.render())

    return "\n".join(content)


def render_class(
    processed_class: ProcessedClass, doc_path: str, api_docs: "ApiDocumentation"
) -> str:
    """Render a processed class into MDX documentation.

    Args:
        processed_class: The processed class object to render
        doc_path: Path to the document, used for API component links
        api_docs: The API documentation registry

    Returns:
        MDX documentation string

    """
    content: list[str] = []

    # Add heading with embedded ApiType component
    slug = api_docs.get_slug(processed_class.object_path)
    api_type = ApiType(ApiTypeKind.CLASS, slug, processed_class.name)
    content.append(f"## {api_type.render()} {processed_class.name}\n")

    # Add docstring if available
    if processed_class.docstring:
        content.append(processed_class.docstring.strip())
        content.append("")

    # Add information about base classes with TypeLink
    if processed_class.bases:
        content.append("**Bases:** ")
        base_links = []
        for base_type in processed_class.bases:
            type_link = TypeLink(base_type)
            base_links.append(type_link.render())
        content.append(", ".join(base_links) + "\n")

    # Collect all attributes for the attributes table
    attributes = []
    for member in processed_class.members:
        if isinstance(member, ProcessedAttribute):
            attributes.append(member)

    # Document attributes using AttributesTable component if there are any
    if attributes:
        attrs_table = AttributesTable(attributes)
        content.append(attrs_table.render())

    # Render other members in order (except attributes which are in the table)
    for member in processed_class.members:
        if not isinstance(member, ProcessedAttribute):
            content.append(render_object(member, doc_path, api_docs))
            content.append("")

    return "\n".join(content)


def render_attribute(
    processed_attr: ProcessedAttribute, doc_path: str, api_docs: "ApiDocumentation"
) -> str:
    """Render a processed attribute into MDX documentation.

    Args:
        processed_attr: The processed attribute object to render
        doc_path: Path to the document, used for API component links
        api_docs: The API documentation registry

    Returns:
        MDX documentation string

    """
    content: list[str] = []

    # Add heading with embedded ApiType component
    slug = api_docs.get_slug(processed_attr.object_path)
    api_type = ApiType(ApiTypeKind.ATTRIBUTE, slug, processed_attr.name)
    content.append(f"## {api_type.render()} {processed_attr.name}\n")

    # Add type information
    type_link = TypeLink(processed_attr.type_info)
    content.append(f"**Type:** {type_link.render()}\n")

    # Add description if available
    if processed_attr.description:
        content.append(processed_attr.description.strip())
        content.append("")

    return "\n".join(content)


def render_alias(
    processed_alias: ProcessedAlias, doc_path: str, api_docs: "ApiDocumentation"
) -> str:
    """Render a processed alias into MDX documentation.

    Args:
        processed_alias: The processed alias object to render
        doc_path: Path to the document, used for API component links
        api_docs: The API documentation registry

    Returns:
        MDX documentation string

    """
    content: list[str] = []

    # Add heading with embedded ApiType component
    slug = api_docs.get_slug(processed_alias.object_path)
    api_type = ApiType(ApiTypeKind.ALIAS, slug, processed_alias.name)
    content.append(f"## {api_type.render()} {processed_alias.name}\n")
    # Add docstring if available
    if processed_alias.docstring:
        content.append(processed_alias.docstring.strip())
        content.append("")

    # Add parameters table if available
    if processed_alias.parameters:
        params_table = ParametersTable(processed_alias.parameters)
        content.append(params_table.render())

    # Add return type if available
    if processed_alias.return_info:
        return_table = ReturnTable(processed_alias.return_info)
        content.append(return_table.render())

    # Add what this is an alias to, if target path is available
    if processed_alias.target_path:
        content.append(f"\n**Alias to:** `{processed_alias.target_path}`")

    return "\n".join(content)
