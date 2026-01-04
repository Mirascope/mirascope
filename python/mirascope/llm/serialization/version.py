"""Version handling for serialization format.

TODO: Consider per-message versioning for future flexibility.

Currently we use a single global version at the SerializedResponse level.
In the future, we may want to support per-message versioning to allow:
- Mixed version messages in the same response (e.g., v1.2 messages loaded from DB
  alongside new v1.3 messages)
- Independent evolution of different serialized representations
  (SerializedToolSchema, Message, etc.)

The recommended approach is message-level versioning as a balance between:
- Per-content versioning (too much overhead)
- Global-only versioning (less flexibility for mixed-version scenarios)

Each Message could have its own version header, allowing the decoder to invoke
legacy logic per-message when needed.
"""

from dataclasses import dataclass

CURRENT_VERSION = "1.0"
"""Current serialization format version."""


@dataclass(frozen=True)
class SerializationVersion:
    """Represents a serialization format version.

    The version uses semantic versioning with major and minor components.
    Major version changes indicate breaking schema changes.
    Minor version changes indicate backward-compatible additions.
    """

    major: int
    """Major version number. Breaking changes increment this."""

    minor: int
    """Minor version number. Compatible additions increment this."""

    @classmethod
    def parse(cls, version: str) -> "SerializationVersion":
        """Parse a version string into a SerializationVersion.

        Args:
            version: A version string in "MAJOR.MINOR" format.

        Returns:
            A SerializationVersion instance.

        Raises:
            ValueError: If the version string is not in valid format.
        """
        try:
            parts = version.split(".")
            if len(parts) != 2:
                raise ValueError(f"Invalid version format: {version}")
            return cls(int(parts[0]), int(parts[1]))
        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid version format: {version}") from e

    def __str__(self) -> str:
        """Return the version as a string."""
        return f"{self.major}.{self.minor}"

    def is_compatible_with(self, other: "SerializationVersion") -> bool:
        """Check if this version is compatible with another version.

        Compatibility requires matching major versions. A decoder can read
        any format with the same major version (newer minor versions may
        have additional fields that are ignored).

        Args:
            other: The version to check compatibility with.

        Returns:
            True if the versions are compatible.
        """
        return self.major == other.major


def get_current_version() -> SerializationVersion:
    """Get the current serialization format version.

    Returns:
        The current SerializationVersion.
    """
    return SerializationVersion.parse(CURRENT_VERSION)
