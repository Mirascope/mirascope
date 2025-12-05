"""Tests for serialization version handling."""

import pytest
from inline_snapshot import snapshot

from mirascope.llm.serialization.version import (
    CURRENT_VERSION,
    SerializationVersion,
    get_current_version,
)


def test_parse_valid_version() -> None:
    """Test parsing a valid version string."""
    version = SerializationVersion.parse("1.0")
    assert (version.major, version.minor) == snapshot((1, 0))


def test_parse_higher_version() -> None:
    """Test parsing a higher version string."""
    version = SerializationVersion.parse("2.5")
    assert (version.major, version.minor) == snapshot((2, 5))


def test_parse_invalid_format_too_few_parts() -> None:
    """Test parsing with too few parts."""
    with pytest.raises(ValueError, match="Invalid version format"):
        SerializationVersion.parse("1")


def test_parse_invalid_format_too_many_parts() -> None:
    """Test parsing with too many parts."""
    with pytest.raises(ValueError, match="Invalid version format"):
        SerializationVersion.parse("1.0.0")


def test_parse_invalid_format_non_numeric() -> None:
    """Test parsing with non-numeric values."""
    with pytest.raises(ValueError, match="Invalid version format"):
        SerializationVersion.parse("a.b")


def test_str_representation() -> None:
    """Test string representation."""
    version = SerializationVersion(major=1, minor=2)
    assert str(version) == snapshot("1.2")


def test_is_compatible_with_same_major() -> None:
    """Test compatibility with same major version."""
    v1 = SerializationVersion(major=1, minor=0)
    v2 = SerializationVersion(major=1, minor=5)
    assert v1.is_compatible_with(v2) is True
    assert v2.is_compatible_with(v1) is True


def test_is_incompatible_with_different_major() -> None:
    """Test incompatibility with different major version."""
    v1 = SerializationVersion(major=1, minor=0)
    v2 = SerializationVersion(major=2, minor=0)
    assert v1.is_compatible_with(v2) is False
    assert v2.is_compatible_with(v1) is False


def test_frozen() -> None:
    """Test that SerializationVersion is immutable."""
    version = SerializationVersion(major=1, minor=0)
    with pytest.raises(AttributeError):
        version.major = 2  # type: ignore[misc]


def test_current_version_format() -> None:
    """Test that CURRENT_VERSION is in valid format."""
    version = SerializationVersion.parse(CURRENT_VERSION)
    assert version.major >= 1
    assert version.minor >= 0


def test_get_current_version() -> None:
    """Test get_current_version returns parsed version."""
    version = get_current_version()
    assert isinstance(version, SerializationVersion)
    assert str(version) == CURRENT_VERSION
