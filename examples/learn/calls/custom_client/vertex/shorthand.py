from mirascope.core import vertex
from vertexai.generative_models import GenerativeModel


@vertex.call("", client=GenerativeModel(model_name="gemini-1.5-flash"))
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"
