"""A prompt for recommending movies of a particular genre."""
from mirascope import BasePrompt


class MovieRecommendationPrompt(BasePrompt):
    prompt_template = """
    Please recommend a list of movies in the {genre} category. I want the list to only
    have 3 movies in total. Please order the list by the quality of the movie, with the
    highest quality movie first. I want the movie list to include the movie title as
    well as any notable actors in the movie. Please also include a short description of
    the movie.
    """

    genre: str
