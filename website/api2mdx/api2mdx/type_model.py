"""Type modeling and parsing for API documentation generation.

This module provides a structured type model for Python type annotations,
offering a more comprehensive representation than simple strings.
"""

import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class EnumEncoder(json.JSONEncoder):
    """JSON encoder that handles Enum types by converting them to their values."""

    def default(self, o: Any) -> Any:  # noqa: ANN401
        """Convert Enum instances to their string values for JSON serialization.

        Args:
            o: The object to convert

        Returns:
            The enum value if o is an Enum, otherwise delegates to parent class

        """
        if isinstance(o, Enum):
            return o.value
        return super().default(o)


class TypeKind(Enum):
    """Kinds of type representations."""

    SIMPLE = "simple"
    GENERIC = "generic"
    UNION = "union"
    OPTIONAL = "optional"
    CALLABLE = "callable"
    TUPLE = "tuple"

    def __str__(self) -> str:
        """Return the string value of the enum."""
        return self.value


@dataclass
class BaseTypeInfo:
    """Base class for all type info representations."""

    type_str: str  # Original string representation
    description: str | None = None  # Optional description
    # Making kind a required argument but with a default that gets overridden in subclasses
    kind: TypeKind = field(default=TypeKind.SIMPLE)

    def to_dict(self) -> dict:
        """Convert this object to a dictionary suitable for JSON serialization."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert this object to a JSON string."""
        return json.dumps(self.to_dict(), cls=EnumEncoder)


@dataclass
class SimpleType(BaseTypeInfo):
    """Represents a simple type like 'str', 'int', or custom class."""

    # Use field with default to ensure kind is always SIMPLE
    kind: TypeKind = field(default=TypeKind.SIMPLE)
    # Symbol name for this type (e.g., "Response", "AsyncCall")
    symbol_name: str | None = None
    # Canonical URL for this type, resolved from ApiDocumentation registry
    doc_url: str | None = None


@dataclass
class GenericType(BaseTypeInfo):
    """Represents a generic type like List[str] or Dict[str, int]."""

    # Use field with default to ensure kind is GENERIC by default
    kind: TypeKind = field(default=TypeKind.GENERIC)
    # The base type (e.g., "List" in List[str]) as a SimpleType
    base_type: SimpleType = field(default_factory=lambda: SimpleType(type_str=""))
    # Type parameters (can be any TypeInfo)
    parameters: list["TypeInfo"] = field(default_factory=list)
    # Canonical URL for this type, resolved from ApiDocumentation registry
    doc_url: str | None = None


# Define the TypeInfo union type
TypeInfo = SimpleType | GenericType


@dataclass
class ParameterInfo:
    """Represents a function parameter."""

    name: str
    type_info: TypeInfo
    description: str | None = None
    default: str | None = None  # String representation of default value
    is_optional: bool = False  # Whether this parameter can be omitted

    def to_dict(self) -> dict:
        """Convert this object to a dictionary suitable for JSON serialization."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert this object to a JSON string."""
        return json.dumps(self.to_dict(), cls=EnumEncoder)


@dataclass
class ReturnInfo:
    """Represents a function return value."""

    type_info: TypeInfo
    description: str | None = None
    name: str | None = None  # Some APIs name their return values

    def to_dict(self) -> dict:
        """Convert this object to a dictionary suitable for JSON serialization."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert this object to a JSON string."""
        return json.dumps(self.to_dict(), cls=EnumEncoder)


# Note: Type string parsing is now handled by the parser module
