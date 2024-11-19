from mirascope.core import BaseMessageParam, vertex
from vertexai.generative_models import GenerativeModel


@vertex.call("")
def recommend_book(genre: str) -> vertex.VertexDynamicConfig:
    return {
        "messages": [
            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
        ],
        "client": GenerativeModel(model_name="gemini-1.5-flash"),
    }
