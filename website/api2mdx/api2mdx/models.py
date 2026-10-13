"""Data models for processed API documentation objects.

This module contains dataclasses representing API objects that have been
processed and prepared for rendering in various formats, along with functions
to create these models from Griffe objects.
"""

import logging
import re
from dataclasses import dataclass

# Forward declaration for type hints
from typing import TYPE_CHECKING

from griffe import (
    Alias,
    AliasResolutionError,
    Attribute,
    Class,
    DocstringSectionKind,
    Function,
    Module,
    Object,
)

from api2mdx.parser import parse_type_string
from api2mdx.type_extractor import extract_attribute_type_info, extract_type_info
from api2mdx.type_model import ParameterInfo, ReturnInfo, SimpleType, TypeInfo

if TYPE_CHECKING:
    from api2mdx.api_discovery import ApiDocumentation

from api2mdx.api_discovery import ObjectPath

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def extract_clean_docstring(obj: Object | Alias) -> str | None:
    """Extract clean descriptive text from a docstring.

    This function extracts only the descriptive text sections from a docstring,
    excluding parameter, returns, and other sections that would be redundant with
    our structured rendering of the API documentation.

    Args:
        obj: The Griffe object to extract the docstring from

    Returns:
        The clean docstring text, or None if no docstring is available

    """
    # Check if docstring is available
    if not (hasattr(obj, "docstring") and obj.docstring):
        return None

    # Extract text sections from the parsed docstring
    text_sections = []

    for section in obj.docstring.parsed:
        if (
            section.kind == DocstringSectionKind.text
            and hasattr(section, "value")
            and section.value
        ):
            text_sections.append(str(section.value).strip())

    # Join text sections with newlines
    if text_sections:
        docstring = "\n\n".join(text_sections)
    else:
        # Fallback to raw value if no text sections were found
        docstring = obj.docstring.value.strip() if obj.docstring.value else None

    if docstring:
        # Only escape curly braces that might cause issues with JSX
        # This approach handles common Python f-string and formatting cases
        # For more complex cases, we might need a more sophisticated parser

        # Define patterns to identify string literals and code blocks
        code_block_pattern = r"```([\s\S]*?)```"
        backtick_pattern = r"`([^`]*?)`"
        quote_patterns = [
            r'"([^"\\]*(?:\\.[^"\\]*)*)"',  # Double quoted strings
            r"'([^'\\]*(?:\\.[^'\\]*)*)'",  # Single quoted strings
        ]

        # Find and store all code blocks and string literals
        placeholders = {}
        placeholder_counter = 0

        # Replace code blocks with placeholders
        for pattern in [code_block_pattern, backtick_pattern, *quote_patterns]:

            def replace_with_placeholder(match: re.Match[str]) -> str:
                nonlocal placeholder_counter
                placeholder = f"__PLACEHOLDER_{placeholder_counter}__"
                placeholders[placeholder] = match.group(0)
                placeholder_counter += 1
                return placeholder

            docstring = re.sub(
                pattern, replace_with_placeholder, docstring, flags=re.DOTALL
            )

        # Now escape the curly braces in the remaining text
        docstring = docstring.replace("{", "\\{").replace("}", "\\}")

        # Put back the original code blocks and string literals
        for placeholder, original in placeholders.items():
            docstring = docstring.replace(placeholder, original)

    return docstring


@dataclass
class ProcessedAttribute:
    """Represents a fully processed class attribute ready for rendering."""

    name: str
    type_info: TypeInfo
    description: str | None
    object_path: ObjectPath


@dataclass
class ProcessedFunction:
    """Represents a fully processed function ready for rendering.

    This dataclass contains all the information needed to render
    documentation for a function, extracted from Griffe objects.
    """

    name: str
    docstring: str | None
    parameters: list[ParameterInfo]
    return_info: ReturnInfo | None
    module_path: str
    object_path: ObjectPath


@dataclass
class ProcessedAlias:
    """Represents a fully processed alias ready for rendering.

    This dataclass contains all the information needed to render
    documentation for an alias, extracted from Griffe objects.
    """

    name: str
    docstring: str | None
    parameters: list[ParameterInfo]
    return_info: ReturnInfo | None
    target_path: str
    module_path: str
    object_path: ObjectPath


@dataclass
class ProcessedClass:
    """Represents a fully processed class ready for rendering.

    This dataclass contains all the information needed to render
    documentation for a class, extracted from Griffe objects.
    """

    name: str
    docstring: str | None
    bases: list[TypeInfo]
    members: list["ProcessedObject"]
    module_path: str
    object_path: ObjectPath


@dataclass
class ProcessedModule:
    """Represents a fully processed module ready for rendering.

    This dataclass contains all the information needed to render
    documentation for a module, extracted from Griffe objects.
    """

    name: str
    docstring: str | None
    members: list["ProcessedObject"]
    module_path: str
    object_path: ObjectPath


ProcessedObject = (
    ProcessedModule
    | ProcessedAlias
    | ProcessedAttribute
    | ProcessedClass
    | ProcessedFunction
)


def process_function(
    func_obj: Function, api_docs: "ApiDocumentation"
) -> ProcessedFunction:
    """Process a Function object into a ProcessedFunction model.

    Args:
        func_obj: The Griffe Function object to process

    Returns:
        A ProcessedFunction object containing all necessary information

    """
    # Get basic function information
    name = getattr(func_obj, "name", "")

    # Extract module path
    module = getattr(func_obj, "module", None)
    module_path = getattr(module, "path", "")

    # Extract clean docstring
    docstring = extract_clean_docstring(func_obj)

    # Extract parameters and return type
    params, return_info = extract_type_info(func_obj, api_docs)

    # Create and return the processed function
    return ProcessedFunction(
        name=name,
        docstring=docstring,
        parameters=params or [],
        return_info=return_info,
        module_path=module_path,
        object_path=ObjectPath(func_obj.canonical_path),
    )


def process_class(class_obj: Class, api_docs: "ApiDocumentation") -> ProcessedClass:
    """Process a Class object into a ProcessedClass model.

    Args:
        class_obj: The Griffe Class object to process

    Returns:
        A ProcessedClass object containing all necessary information

    """
    # Get basic class information
    name = getattr(class_obj, "name", "")

    # Extract module path
    module = getattr(class_obj, "module", None)
    module_path = getattr(module, "path", "")

    # Extract clean docstring
    docstring = extract_clean_docstring(class_obj)

    # Extract base classes
    bases = []
    if hasattr(class_obj, "bases") and class_obj.bases:
        for base in class_obj.bases:
            base_str = str(base)
            try:
                base_type_info = parse_type_string(base_str)
                # Resolve URL for the base type
                from api2mdx.type_extractor import _resolve_url_for_type_info

                _resolve_url_for_type_info(base_type_info, api_docs)
                bases.append(base_type_info)
            except Exception as e:
                logger.warning(
                    f"Failed to parse base class type: {base_str}. Error: {e}"
                )
                # Fallback to simple type
                bases.append(SimpleType(type_str=base_str))

    # Process all members
    processed_members = []
    if hasattr(class_obj, "members"):
        for member_name, member in class_obj.members.items():
            # Skip private members (starting with underscore)
            if member_name.startswith("_"):
                continue

            processed_obj = process_object(member, api_docs)
            if isinstance(processed_obj, ProcessedAlias):
                continue  # Don't document aliases on classes
            if processed_obj is not None:
                processed_members.append(processed_obj)

    # Create and return the processed class
    return ProcessedClass(
        name=name,
        docstring=docstring,
        bases=bases,
        members=processed_members,
        module_path=module_path,
        object_path=ObjectPath(class_obj.canonical_path),
    )


def process_attribute(
    obj: Attribute, api_docs: "ApiDocumentation"
) -> ProcessedAttribute:
    name = getattr(obj, "name", "")
    type_info = extract_attribute_type_info(obj)
    descr = extract_clean_docstring(obj)
    return ProcessedAttribute(
        name=name,
        type_info=type_info,
        description=descr,
        object_path=ObjectPath(obj.canonical_path),
    )


def process_object(
    obj: Object | Alias, api_docs: "ApiDocumentation"
) -> ProcessedObject | None:
    """Process a Griffe object into the appropriate processed model.

    Args:
        obj: The Griffe object to process
        name: Optional name override for the object

    Returns:
        A processed object appropriate for the input type, or None for unsupported types

    """
    if isinstance(obj, Class):
        return process_class(obj, api_docs)
    elif isinstance(obj, Function):
        return process_function(obj, api_docs)
    elif isinstance(obj, Attribute):
        return process_attribute(obj, api_docs)
    elif isinstance(obj, Alias):
        try:
            return process_alias(obj, api_docs)
        except AliasResolutionError as e:
            logger.warning(e)
            return None
    elif isinstance(obj, Module):
        return process_module(obj, api_docs)
    else:
        raise ValueError("Unexpected object", obj)


def process_module(module_obj: Module, api_docs: "ApiDocumentation") -> ProcessedModule:
    """Process a Module object into a ProcessedModule model.

    Args:
        module_obj: The Griffe Module object to process

    Returns:
        A ProcessedModule object containing all necessary information

    """
    # Get basic module information
    name = getattr(module_obj, "name", "")
    module_path = getattr(module_obj, "path", "")

    # Extract clean docstring
    docstring = extract_clean_docstring(module_obj)

    # Process all members
    processed_members = []

    # Check if the module has an __all__ attribute
    module_all = None
    if hasattr(module_obj, "members") and "__all__" in module_obj.members:
        all_member = module_obj.members["__all__"]
        value = getattr(all_member, "value", None)
        if value:
            try:
                # Try to evaluate the __all__ list
                module_all = eval(str(value))
                logger.info(f"Found __all__ in module {module_path}: {module_all}")
            except Exception as e:
                logger.warning(
                    f"Failed to evaluate __all__ in module {module_path}: {e}"
                )

    if hasattr(module_obj, "members"):
        # If we have __all__, only process those members
        if module_all:
            for member_name in module_all:
                if member_name in module_obj.members:
                    member = module_obj.members[member_name]
                    processed_obj = process_object(member, api_docs)
                    if processed_obj is not None:
                        processed_members.append(processed_obj)
                else:
                    logger.warning(
                        f"Member {member_name} in __all__ not found in module {module_path}"
                    )
        else:
            # Otherwise, process all members (except private ones or aliases)
            for member_name, member in module_obj.members.items():
                # Skip private members (starting with underscore)
                if member_name.startswith("_"):
                    continue

                processed_obj = process_object(member, api_docs)
                if isinstance(processed_obj, ProcessedAlias):
                    continue
                if processed_obj is not None:
                    processed_members.append(processed_obj)

    # Create and return the processed module
    return ProcessedModule(
        name=name,
        docstring=docstring,
        members=processed_members,
        module_path=module_path,
        object_path=ObjectPath(module_obj.canonical_path),
    )


def process_alias(alias_obj: Alias, api_docs: "ApiDocumentation") -> ProcessedAlias:
    """Process an Alias object into a ProcessedAlias model.

    Args:
        alias_obj: The Griffe Alias object to process

    Returns:
        A ProcessedAlias object containing all necessary information

    """
    # Get basic alias information
    name = getattr(alias_obj, "name", "")

    # Extract module path
    module = getattr(alias_obj, "module", None)
    module_path = getattr(module, "path", "")

    # Extract clean docstring
    docstring = extract_clean_docstring(alias_obj)

    # Extract parameters and return type
    params, return_info = extract_type_info(alias_obj, api_docs)

    # Extract target path
    target_path = ""
    if hasattr(alias_obj, "target") and alias_obj.target:
        target_path = getattr(alias_obj.target, "path", str(alias_obj.target))

    # Create and return the processed alias
    return ProcessedAlias(
        name=name,
        docstring=docstring,
        parameters=params or [],
        return_info=return_info,
        target_path=target_path,
        module_path=module_path,
        object_path=ObjectPath(alias_obj.canonical_path),
    )
