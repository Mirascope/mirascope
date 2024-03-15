"""A prompt for recommending movies of a particular genre."""

from mirascope import BasePrompt

prev_revision_id = "0001"
revision_id = "0002"


class MovieRecommendationPrompt(BasePrompt):
    prompt_template = "Please recommend a list of movies in the {genre} category."
    genre: str
