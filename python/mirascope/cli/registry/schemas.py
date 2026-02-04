"""Pydantic schemas for registry items and configuration."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class RegistryFile(BaseModel):
    """A file within a registry item."""

    path: str
    """Source path within the registry item."""
    target: str
    """Target path where the file will be written."""
    content: str = ""
    """File content (populated in built registry items)."""
    type: str = ""
    """Optional file type annotation."""


class RegistryDependencies(BaseModel):
    """Dependencies required by a registry item."""

    pip: list[str] = []
    """Python pip packages."""
    npm: list[str] = []
    """npm packages."""


class RegistryVersionConstraint(BaseModel):
    """Version constraints for Mirascope compatibility."""

    minVersion: str | None = None
    """Minimum compatible version."""
    maxVersion: str | None = None
    """Maximum compatible version."""


class RegistryItem(BaseModel):
    """A registry item (tool, agent, prompt, or integration)."""

    name: str
    """Unique item name."""
    type: str
    """Item type (e.g., 'registry:tool', 'registry:agent')."""
    title: str = ""
    """Human-readable title."""
    description: str = ""
    """Description of the item."""
    version: str = "1.0.0"
    """Item version."""
    language: str = ""
    """Language this item is for (python or typescript)."""
    categories: list[str] = []
    """Categories for filtering/searching."""
    mirascope: dict[str, RegistryVersionConstraint] = {}
    """Mirascope version constraints by language."""
    files: list[RegistryFile] = []
    """Files included in this item."""
    dependencies: RegistryDependencies = RegistryDependencies()
    """External dependencies."""
    registryDependencies: list[str] = []
    """Other registry items this depends on."""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RegistryItem:
        """Create a RegistryItem from a dictionary."""
        return cls.model_validate(data)


class RegistryIndexItem(BaseModel):
    """An item entry in the registry index."""

    name: str
    """Item name."""
    type: str
    """Item type."""
    path: str
    """Path within the registry."""
    description: str = ""
    """Optional description."""


class RegistryIndex(BaseModel):
    """The registry index containing all available items."""

    name: str
    """Registry name."""
    version: str
    """Registry version."""
    homepage: str = ""
    """Registry homepage URL."""
    items: list[RegistryIndexItem] = []
    """All items in the registry."""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RegistryIndex:
        """Create a RegistryIndex from a dictionary."""
        return cls.model_validate(data)


class MirascopeConfig(BaseModel):
    """Mirascope project configuration (mirascope.json)."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    schema_: str | None = Field(default=None, alias="$schema")
    """JSON schema URL."""
    language: str = "python"
    """Project language (python or typescript)."""
    registry: str = "https://mirascope.com/registry"
    """Registry URL."""
    paths: dict[str, str] = {}
    """Path mappings for item types."""
