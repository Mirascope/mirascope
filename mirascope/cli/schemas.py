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

    model_config = ConfigDict(extra="forbid")


class VersionTextFile(BaseModel):
    """Model for the version text file."""

    current_revision: Optional[str] = Field(default=None)
    latest_revision: Optional[str] = Field(default=None)
