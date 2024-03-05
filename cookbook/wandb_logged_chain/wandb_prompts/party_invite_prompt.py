"""Prompt for determining who to invite to party."""
from mirascope.wandb import WandbPrompt


class PartyInvitePrompt(WandbPrompt):
    """
    SYSTEM:
    You're a bouncer and you let people into the party only if they're at least somewhat
    cool.

    USER:
    If I were to say how cool this person is out of 10, I'd say {coolness}. Should they
    be let into the party?
    """

    coolness: int
