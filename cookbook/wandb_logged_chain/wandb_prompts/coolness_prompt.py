"""Prompt for determining coolness."""
from pydantic import BaseModel

from mirascope.wandb import WandbPrompt


class CoolRating(BaseModel):
    """Coolness rating out of 10."""

    coolness: int


class Coolness(WandbPrompt):
    """
    SYSTEM: You determine coolness on a scale of 1 to 10. If the person's name is Brian,
    they get an automatic 10 out of 10, otherwise, they get a random whole number
    between 1 and 9.

    USER: How cool is {person}?
    """

    person: str
