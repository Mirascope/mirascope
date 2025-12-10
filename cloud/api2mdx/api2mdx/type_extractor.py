"""Type extraction logic for API documentation generation.

This module provides utilities for extracting type information from Python
functions, methods, and parameters within the API documentation system.
"""

import logging
from typing import TypeVar, cast

from griffe import (
    Alias,
    Attribute,
    DocstringParameter,
    DocstringReturn,
    DocstringSection,
    DocstringSectionParameters,
    DocstringSectionReturns,
    Function,
    Object,
)

from .api_discovery import ApiDocumentation
from .parser import parse_type_string
from .type_model import GenericType, ParameterInfo, ReturnInfo, SimpleType, TypeInfo

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Generic helper for type safety
T = TypeVar("T", bound=DocstringSection)


def resolve_symbol_url(symbol_name: str, api_docs: ApiDocumentation) -> str | None:
    """Resolve a symbol name to its canonical documentation URL.

    Args:
        symbol_name: The symbol name to resolve (e.g., "Response", "AsyncCall")
        api_docs: The ApiDocumentation registry containing symbol mappings

    Returns:
        Canonical URL if symbol is found in registry, None otherwise

    """
    # Skip ellipsis - it's a literal syntax, not a type to resolve
    if symbol_name == "...":
        return None

    if symbol_name in api_docs._symbol_registry:
        api_object = api_docs._symbol_registry[symbol_name]

        # If canonical_docs_path is already a full URL (e.g., Python docs), return it as-is
        if api_object.canonical_docs_path.startswith(("http://", "https://")):
            return api_object.canonical_docs_path

        # Strip "index" from the path as it represents the root/default page
        docs_path = api_object.canonical_docs_path
        if docs_path == "index":
            docs_path = ""
        elif docs_path.endswith("/index"):
            docs_path = docs_path[:-6]  # Remove "/index"
        
        if docs_path:
            # Only add the leading slash if docs path is nonempty
            # Sicne /api#context is preferred to /api/#context
            docs_path = "/" + docs_path

        # Otherwise, construct relative URL with api_root
        return f"{api_docs.api_root}{docs_path}#{api_object.canonical_slug}"

    # Track unresolved symbols (but not ellipsis)
    api_docs._unresolved_symbols.add(symbol_name)
    return None


def _resolve_url_for_type_info(type_info: TypeInfo, api_docs: ApiDocumentation) -> None:
    """Recursively resolve URLs for a TypeInfo object and all its nested types.

    This modifies the TypeInfo objects in-place by setting their url field.

    Args:
        type_info: The TypeInfo object to resolve URLs for
        api_docs: The ApiDocumentation registry containing symbol mappings

    """
    if isinstance(type_info, SimpleType):
        if type_info.symbol_name:
            type_info.doc_url = resolve_symbol_url(type_info.symbol_name, api_docs)
    elif isinstance(type_info, GenericType):
        # Resolve URL for the base type
        if type_info.base_type.symbol_name:
            type_info.base_type.doc_url = resolve_symbol_url(
                type_info.base_type.symbol_name, api_docs
            )

        # Recursively resolve URLs for all parameters
        for param in type_info.parameters:
            _resolve_url_for_type_info(param, api_docs)


def find_docstring_section(
    obj: Object | Alias, section_kind: str, section_type: type[T]
) -> T | None:
    """Safely extract a specific docstring section from an object.

    Args:
        obj: The object to extract docstring section from
        section_kind: The kind of section to extract (e.g., "parameters", "returns")
        section_type: The expected type of the section

    Returns:
        The section of the specified type, or None if not found

    """
    # Check if docstring is available and properly parsed
    if not (
        hasattr(obj, "docstring") and obj.docstring and hasattr(obj.docstring, "parsed")
    ):
        return None

    # Look for the specified section kind
    for section in obj.docstring.parsed:
        if section.kind == section_kind:
            return cast(T, section)

    return None


def extract_function_parameters(
    obj: Function, api_docs: ApiDocumentation
) -> list[ParameterInfo]:
    """Extract parameter information directly from a Function object's parameters.

    Args:
        obj: The Function object to extract parameters from

    Returns:
        A list of ParameterInfo objects

    """
    params: list[ParameterInfo] = []

    # Process direct parameters (most reliable source)
    if not obj.parameters:
        return params

    # Process each parameter
    for param in obj.parameters:
        # Extract parameter info
        name = param.name

        # Get type if available
        type_info: TypeInfo
        if hasattr(param, "annotation") and param.annotation:
            type_str = str(param.annotation)
            type_info = parse_type_string(type_str)
            # Resolve URL for the type
            _resolve_url_for_type_info(type_info, api_docs)
        else:
            type_info = SimpleType(type_str="Any")

        # Get default value if available
        default: str | None = None
        is_optional: bool = False
        if hasattr(param, "default") and param.default:
            default = str(param.default)
            is_optional = True

        # Create parameter info
        param_info = ParameterInfo(
            name=name,
            type_info=type_info,
            description=None,  # No description from direct parameters
            default=default,
            is_optional=is_optional,
        )
        params.append(param_info)

    return params


def extract_parameters_from_docstring(
    obj: Object | Alias, api_docs: ApiDocumentation
) -> list[ParameterInfo]:
    """Extract parameter information from a Griffe object's docstring.

    Args:
        obj: The Griffe object to extract parameters from

    Returns:
        A list of ParameterInfo objects

    """
    params: list[ParameterInfo] = []

    # Get parameters section
    params_section = find_docstring_section(
        obj, "parameters", DocstringSectionParameters
    )

    if not params_section or not hasattr(params_section, "value"):
        return params

    # Process each parameter in the section
    for param_item in params_section.value:
        if not isinstance(param_item, DocstringParameter):
            continue

        # Extract parameter info
        name = param_item.name

        # Get type if available
        type_info: TypeInfo
        if hasattr(param_item, "annotation") and param_item.annotation:
            type_str = str(param_item.annotation)
            type_info = parse_type_string(type_str)
            # Resolve URL for the type
            _resolve_url_for_type_info(type_info, api_docs)
        else:
            type_info = SimpleType(type_str="Any")

        # Get description if available
        description: str | None = None
        if param_item.description:
            description = str(param_item.description)

        # Get default value if available
        default: str | None = None
        is_optional: bool = False
        if param_item.default:
            default = str(param_item.default)
            is_optional = True

        # Create and add parameter info
        param_info = ParameterInfo(
            name=name,
            type_info=type_info,
            description=description,
            default=default,
            is_optional=is_optional,
        )
        params.append(param_info)

    return params


def extract_return_info_from_docstring(
    obj: Object | Alias, api_docs: ApiDocumentation
) -> ReturnInfo | None:
    """Extract return type information from a Griffe object's docstring.

    Args:
        obj: The Griffe object to extract return info from

    Returns:
        ReturnInfo object if available, None otherwise

    """
    # Get returns section
    returns_section = find_docstring_section(obj, "returns", DocstringSectionReturns)

    if not returns_section:
        return None

    return process_returns_section(returns_section, api_docs)


def process_returns_section(
    section: DocstringSectionReturns, api_docs: ApiDocumentation
) -> ReturnInfo | None:
    """Process a returns section to extract type information.

    Args:
        section: The returns section to process

    Returns:
        ReturnInfo object if valid information was found, None otherwise

    """
    type_str: str | None = None
    description: str | None = None

    # DocstringSectionReturns doesn't have an annotation attribute directly.
    # We need to extract type information only from the section's value.

    # Try to extract information from section value
    if hasattr(section, "value") and section.value:
        section_value = section.value

        # Handle string value (usually description)
        if isinstance(section_value, str):
            description = str(section_value)

        # Handle list of return objects
        elif isinstance(section_value, list) and section_value:
            # Assume first item is a DocstringReturns
            item = section_value[0]

            if isinstance(item, DocstringReturn):
                # Get type from annotation if available
                if not type_str and item.annotation:
                    type_str = str(item.annotation)

                # Get description if available
                if item.description:
                    description = str(item.description)

        # Handle DocstringReturn object
        elif isinstance(section_value, DocstringReturn):
            # Get type from annotation if available
            if not type_str and section_value.annotation:
                type_str = str(section_value.annotation)

            # Get description if available
            if section_value.description:
                description = str(section_value.description)

    # Return None if no type information was found
    if not type_str:
        return None

    # Parse the type string
    type_info = parse_type_string(type_str)

    # Resolve URL for the type
    _resolve_url_for_type_info(type_info, api_docs)

    # Create and return the return info
    return ReturnInfo(type_info=type_info, description=description)


def extract_function_return_info(
    obj: Function, api_docs: ApiDocumentation
) -> ReturnInfo | None:
    """Extract return type information directly from a Function object.

    Args:
        obj: The Function object to extract return info from

    Returns:
        ReturnInfo object if available, None otherwise

    """
    # Check if the function has a return type annotation
    if obj.returns:
        # Extract return type
        type_str = str(obj.returns)
        type_info = parse_type_string(type_str)

        # Resolve URL for the type
        _resolve_url_for_type_info(type_info, api_docs)

        # Create and return ReturnInfo (no description available from direct extraction)
        return ReturnInfo(type_info=type_info, description=None)

    return None


def extract_alias_return_info(
    obj: Alias, api_docs: ApiDocumentation
) -> ReturnInfo | None:
    """Extract return type information from an Alias object.

    Args:
        obj: The Alias object to extract return info from

    Returns:
        ReturnInfo object if available, None otherwise

    """
    # Check if alias's target exists
    if hasattr(obj, "target") and obj.target:
        target = obj.target
        # The target could be a Function or another object with an annotation
        # Check if it has an annotation attribute carefully
        annotation = getattr(target, "annotation", None)
        if annotation:
            # Get type from target's annotation
            type_str = str(annotation)
            type_info = parse_type_string(type_str)

            # Resolve URL for the type
            _resolve_url_for_type_info(type_info, api_docs)

            # Create and return ReturnInfo
            return ReturnInfo(type_info=type_info, description=None)

    return None


def extract_attribute_type_info(attr: Attribute) -> TypeInfo:
    """Extract type information from a Griffe Attribute object.

    Args:
        attr: The Griffe Attribute object to extract type info from

    Returns:
        A TypeInfo object representing the attribute's type

    """
    # Get the annotation (can be string or Expr)
    annotation = getattr(attr, "annotation", None)
    value = getattr(attr, "value", None)
    type = None
    if annotation is not None:
        type = str(annotation)
    if type is None and value is not None:
        type = str(value)

    # Handle different annotation types
    if type is not None:
        try:
            attr_type_info = parse_type_string(type)
        except Exception as e:
            # Log a warning with the failed type string
            logger.warning(f"Failed to parse type annotation: '{type}'. Error: {e}")
            # Fallback to simple type with the original string
            attr_type_info = SimpleType(type_str=type)
    else:
        # Create a simple "Any" type for empty annotations
        attr_type_info = SimpleType(type_str="Any")

    return attr_type_info


def extract_type_info(
    obj: Object | Alias,
    api_docs: ApiDocumentation,
) -> tuple[list[ParameterInfo], ReturnInfo | None]:
    """Extract both parameter and return type information from a Griffe object.

    Args:
        obj: The Griffe object to extract type info from

    Returns:
        A tuple of (parameters, return_info)

    """
    # Extract parameters, preferring direct function parameters if available
    docstring_params = extract_parameters_from_docstring(obj, api_docs)
    parameters = docstring_params

    # If the object is a Function, try to get parameters directly
    if isinstance(obj, Function):
        function_params = extract_function_parameters(obj, api_docs)

        # Use direct function parameters if available
        if function_params:
            # Create a map of docstring parameters by name for quick lookup
            docstring_param_map = {param.name: param for param in docstring_params}

            # Enhance function parameters with descriptions from docstring
            for i, param in enumerate(function_params):
                if param.name in docstring_param_map:
                    # Add description from docstring if available
                    docstring_param = docstring_param_map[param.name]
                    if docstring_param.description:
                        function_params[i].description = docstring_param.description

            # Use the enhanced function parameters
            parameters = function_params

    # Extract return info, preferring direct return info if available
    return_info = extract_return_info_from_docstring(obj, api_docs)

    # If return info not found in docstring, try from object directly
    if not return_info:
        if isinstance(obj, Function):
            # Try to get return info from Function
            function_return = extract_function_return_info(obj, api_docs)
            if function_return:
                return_info = function_return
        elif isinstance(obj, Alias):
            # Try to get return info from Alias
            alias_return = extract_alias_return_info(obj, api_docs)
            if alias_return:
                return_info = alias_return

    return parameters, return_info
