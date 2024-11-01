from mirascope.core import prompt_template, vertex
from vertexai.generative_models import GenerativeModel


@vertex.call("")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str) -> vertex.VertexDynamicConfig:
    return {
        "client": GenerativeModel(model_name="gemini-1.5-flash"),
    }
