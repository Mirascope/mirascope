"""Contains the models for the mirascope application."""
from typing import Optional

from pydantic import BaseModel, Field


class VersionTextFile(BaseModel):
    """Model for the version text file."""

    current_revision: Optional[str] = Field(default=None)
    latest_revision: Optional[str] = Field(default=None)

class MirascopeSettings(BaseModel):
    """Model for the user's mirascope settings."""

    mirascope_location: str
    versions_location: str
    prompts_location: str
    version_file_name: str
