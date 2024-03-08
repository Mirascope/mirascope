"""Classes for using tools with Mistral Chat APIs"""
from pydantic import BaseModel


class MistralTool(BaseModel):
    """Base class for Mistral tools."""
