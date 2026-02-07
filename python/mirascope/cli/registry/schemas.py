"""Pydantic schemas for registry items."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class RegistryFile(BaseModel):
    """A file in a registry item."""

    path: str
    target: str
    content: str = ""
    type: str = ""


class RegistryDependencies(BaseModel):
    """Dependencies for a registry item."""

    pip: list[str] = []
    npm: list[str] = []


class RegistryVersionConstraint(BaseModel):
    """Version constraints for a registry item."""

    minVersion: str | None = None
    maxVersion: str | None = None


class RegistryItem(BaseModel):
    """A registry item."""

    name: str
    type: str
    title: str = ""
    description: str = ""
    version: str = "1.0.0"
    language: str = ""
    categories: list[str] = []
    mirascope: dict[str, RegistryVersionConstraint] = {}
    files: list[RegistryFile] = []
    dependencies: RegistryDependencies = RegistryDependencies()
    registryDependencies: list[str] = []

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RegistryItem:
        """Create a RegistryItem from a dictionary."""
        return cls.model_validate(data)


class RegistryIndexItem(BaseModel):
    """An item in the registry index."""

    name: str
    type: str
    path: str
    description: str = ""


class RegistryIndex(BaseModel):
    """The registry index."""

    name: str
    version: str
    homepage: str = ""
    items: list[RegistryIndexItem] = []

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RegistryIndex:
        """Create a RegistryIndex from a dictionary."""
        return cls.model_validate(data)
