"""A prompt for recommending movies of a particular genre."""

from mirascope import tags
from mirascope.prompts import Prompt

prev_revision_id = "0001"
revision_id = "0002"


@tags(["version:0002"])
class MovieRecommendationPrompt(Prompt):
    """Please recommend a list of movies in the {genre} category."""

    genre: str
