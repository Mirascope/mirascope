"""Contains the schema for files created by the mirascope cli."""
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class MirascopeSettings(BaseModel):
    """Model for the user's mirascope settings."""

    mirascope_location: str
    versions_location: str
    prompts_location: str
    version_file_name: str
    format_command: Optional[str] = None
    auto_tag: Optional[bool] = None

    model_config = ConfigDict(extra="forbid")


class VersionTextFile(BaseModel):
    """Model for the version text file."""

    current_revision: Optional[str] = Field(default=None)
    latest_revision: Optional[str] = Field(default=None)


class MirascopeCliVariables(BaseModel):
    """Prompt version variables used internally by mirascope."""

    prev_revision_id: Optional[str] = Field(default=None)
    revision_id: Optional[str] = Field(default=None)


class ClassInfo(BaseModel):
    name: str
    bases: list[str]
    body: str
    decorators: list[str]
    docstring: Optional[str]


class FunctionInfo(BaseModel):
    name: str
    args: list[str]
    returns: Optional[str]
    body: str
    decorators: list[str]
    docstring: Optional[str]
    is_async: bool
