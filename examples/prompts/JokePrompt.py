"""A prompt for telling jokes about {foo}."""
from mirascope import MirascopePromptTemplate


class JokePrompt(MirascopePromptTemplate):
    """
    tell me a joke about {foo}
    """

    foo: str
