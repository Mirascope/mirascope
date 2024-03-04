"""Prompt to ask who I am."""
from pydantic import BaseModel

from mirascope.integrations.wandb import WandbPrompt


class Person(BaseModel):
    """Person model."""

    person: str


class WhoPrompt(WandbPrompt):
    """Who is {person}?"""

    person: str
