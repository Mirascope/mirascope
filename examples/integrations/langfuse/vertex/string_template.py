from mirascope.core import prompt_template, vertex
from mirascope.integrations.langfuse import with_langfuse


@with_langfuse()
@vertex.call("gemini-1.5-flash")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


print(recommend_book("fantasy"))
