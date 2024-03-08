"""Prompt for determining who to invite to party."""
from mirascope.wandb import WandbPrompt


class PartyInvite(WandbPrompt):
    """
    SYSTEM:
    You're a bouncer and you decide if people are allowed into the party. You only let
    people in if they're at least somewhat cool.

    USER:
    This person is {coolness} out of 10 cool. Should they be let into the party?
    """

    coolness: int
