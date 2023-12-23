"""A prompt to recommend a movie based on a given genre."""
from mirascope import Prompt


class MovieRecommendationPrompt(Prompt):
    """
    Please recommend a list of movies in the {genre} category.
    """

    genre: str
