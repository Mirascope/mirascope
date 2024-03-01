"""Prompt for determining who to invite to party."""
from mirascope import messages
from mirascope.integrations.wandb import WandbPrompt


@messages
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
