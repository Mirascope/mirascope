"""Exceptions for serialization/deserialization."""

from ..exceptions import MirascopeLLMError


class SerializationError(MirascopeLLMError):
    """Base exception for serialization errors."""


class IncompatibleVersionError(SerializationError):
    """Raised when attempting to decode an incompatible serialization format version."""

    def __init__(
        self, message: str, *, found_version: str, expected_version: str
    ) -> None:
        super().__init__(message)
        self.found_version = found_version
        self.expected_version = expected_version


class InvalidSerializedDataError(SerializationError):
    """Raised when serialized data is malformed or missing required fields."""


class UnknownContentTypeError(SerializationError):
    """Raised when an unknown content type is encountered during decoding."""

    def __init__(self, content_type: str) -> None:
        super().__init__(f"Unknown content type: {content_type}")
        self.content_type = content_type


class UnknownMessageRoleError(SerializationError):
    """Raised when an unknown message role is encountered during decoding."""

    def __init__(self, role: str) -> None:
        super().__init__(f"Unknown message role: {role}")
        self.role = role


class SchemaMismatchError(SerializationError):
    """Raised when provided tools/format schema doesn't match serialized data.

    This error is raised during deserialization when:
    - The provided format's schema doesn't match the serialized format schema
    - The provided tools don't include all tools from the serialized data
      (tools must be a superset of serialized tools)

    For more specific error handling, use the subclasses:
    - IncompatibleToolsError: For tools schema mismatches
    - IncompatibleFormatError: For format schema mismatches
    """

    def __init__(self, message: str, *, field: str) -> None:
        """Initialize a SchemaMismatchError.

        Args:
            message: Description of the schema mismatch.
            field: The field that mismatched ("tools" or "format").
        """
        super().__init__(message)
        self.field = field


class IncompatibleToolsError(SchemaMismatchError):
    """Raised when provided tools don't match serialized tools schema.

    This error is raised during deserialization when:
    - A serialized tool is not found in the provided tools
    - A tool's parameters schema doesn't match
    - A tool's strict mode setting doesn't match
    """

    def __init__(self, message: str) -> None:
        """Initialize an IncompatibleToolsError.

        Args:
            message: Description of the tools mismatch.
        """
        super().__init__(message, field="tools")


class IncompatibleFormatError(SchemaMismatchError):
    """Raised when provided format doesn't match serialized format schema.

    This error is raised during deserialization when:
    - Serialized data has a format but no format was provided
    - The provided format's JSON schema doesn't match the serialized schema
    """

    def __init__(self, message: str) -> None:
        """Initialize an IncompatibleFormatError.

        Args:
            message: Description of the format mismatch.
        """
        super().__init__(message, field="format")
