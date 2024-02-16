"""A prompt for recommending movies of a particular genre."""
from mirascope.prompts import Prompt


class MovieRecommendationPrompt(Prompt):
    """Please recommend a list of movies in the {genre} category."""

    genre: str
