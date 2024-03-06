"""A prompt for recommending movies of a particular genre."""
from mirascope import tags
from mirascope.openai import OpenAIPrompt

prev_revision_id = "None"
revision_id = "0001"


@tags(["version:0001"])
class MovieRecommendationPrompt(OpenAIPrompt):
    """Please recommend a list of movies in the {genre} category."""

    genre: str
