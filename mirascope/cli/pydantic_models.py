"""Contains the pydantic models for the mirascope cli."""
from pydantic import BaseModel


class MirascopeSettings(BaseModel):
    """Model for the user's mirascope settings."""

    mirascope_location: str
    versions_location: str
    prompts_location: str
    version_file_name: str
