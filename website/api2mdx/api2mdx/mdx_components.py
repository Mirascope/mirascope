"""MDX component classes for consistent rendering.

This module provides Python classes that represent MDX components,
ensuring consistent rendering and type safety for component props.
"""

import json
from dataclasses import dataclass
from enum import Enum
from typing import Any

from api2mdx.models import ProcessedAttribute
from api2mdx.type_model import EnumEncoder, ParameterInfo, ReturnInfo, TypeInfo


class ApiTypeKind(Enum):
    """Types of API objects that can be documented."""

    MODULE = "Module"
    FUNCTION = "Function"
    CLASS = "Class"
    ATTRIBUTE = "Attribute"
    ALIAS = "Alias"


@dataclass
class ApiType:
    """Represents an <ApiType> MDX component."""

    type: ApiTypeKind
    slug: str  # Canonical slug
    symbol_name: str  # Name of the symbol

    def render(self) -> str:
        """Render the ApiType component as a string."""
        return f'<ApiType type="{self.type.value}" slug="{self.slug}" symbolName="{self.symbol_name}" />'


@dataclass
class TypeLink:
    """Represents a <TypeLink> MDX component."""

    type_info: TypeInfo

    def render(self) -> str:
        """Render the TypeLink component as a string."""
        type_json = json.dumps(self.type_info.to_dict(), cls=EnumEncoder)
        return f"<TypeLink type={{{type_json}}} />"


@dataclass
class ParametersTable:
    """Represents a <ParametersTable> MDX component."""

    parameters: list[ParameterInfo]

    def render(self) -> str:
        """Render the ParametersTable component as a string."""
        # Convert parameters to dictionaries inline
        param_dicts = []
        for param in self.parameters:
            param_dict: dict[str, Any] = {"name": param.name}
            if param.type_info:
                param_dict["type_info"] = param.type_info.to_dict()
            if param.default:
                param_dict["default"] = param.default
            if param.description:
                param_dict["description"] = param.description
            param_dicts.append(param_dict)

        # Convert to JSON format with proper indentation
        params_json = json.dumps(param_dicts, indent=2, cls=EnumEncoder)

        # Format the component with proper line breaks and proper JSX syntax
        return f"<ParametersTable\n  parameters={{{params_json}}}\n/>\n"


@dataclass
class ReturnTable:
    """Represents a <ReturnTable> MDX component."""

    return_info: ReturnInfo

    def render(self) -> str:
        """Render the ReturnTable component as a string."""
        # Create a return type dictionary with the full type_info object
        return_dict: dict[str, Any] = {
            "type_info": self.return_info.type_info.to_dict(),
        }

        if self.return_info.description:
            return_dict["description"] = self.return_info.description

        if self.return_info.name:
            return_dict["name"] = self.return_info.name

        # Convert to JSON format with proper indentation
        return_json = json.dumps(return_dict, indent=2, cls=EnumEncoder)

        # Format the component with proper line breaks and proper JSX syntax
        return f"<ReturnTable\n  returnType={{{return_json}}}\n/>\n"


@dataclass
class AttributesTable:
    """Represents an <AttributesTable> MDX component."""

    attributes: list[ProcessedAttribute]

    def render(self) -> str:
        """Render the AttributesTable component as a string."""
        # Convert attributes to dictionaries inline
        attr_dicts = []
        for attr in self.attributes:
            attr_dict: dict[str, Any] = {
                "name": attr.name,
                "type_info": attr.type_info.to_dict(),
            }
            if attr.description:
                attr_dict["description"] = attr.description
            attr_dicts.append(attr_dict)

        # Convert to JSON format with proper indentation
        attrs_json = json.dumps(attr_dicts, indent=2, cls=EnumEncoder)

        # Format the component with proper line breaks and proper JSX syntax
        return f"<AttributesTable\n  attributes={{{attrs_json}}}\n/>\n"
