"""A call for recommending movies of a particular genre."""

from mirascope import tags
from mirascope.openai import OpenAICall, OpenAICallParams

prev_revision_id = None
revision_id = "0001"
number = 1
chat = OpenAICall()
a_list = [1, 2, 3]


@tags(["movie_project", "version:0001"])
class MovieRecommender(OpenAICall):
    """An LLM call for recommending movies, using OpenAI."""

    prompt_template = """
    SYSTEM:
    You are the world's most knowledgeable movie buff. You know everything there is to
    know about movies. You have likely seen every movie ever made. Your incredible
    talent is your ability to recommend movies to people using only the genre of the
    movie. The reason people love your recommendations so much is that they always
    include succinct and clear descriptions of the movie. You also make sure to pique
    their interest by mentioning any famous actors in the movie that might be of
    interest.

    USER:
    Please recommend 3 movies in the {genre} cetegory.
    """
    genre: str
    call_params = OpenAICallParams(model="gpt-3.5-turbo")
