from mirascope.core import Messages, vertex
from vertexai.generative_models import GenerativeModel


@vertex.call("")
def recommend_book(genre: str) -> vertex.VertexDynamicConfig:
    return {
        "messages": [Messages.User(f"Recommend a {genre} book")],
        "client": GenerativeModel(model_name="gemini-1.5-flash"),
    }
