from mirascope.core import groq, prompt_template
from mirascope.integrations.langfuse import with_langfuse


@with_langfuse()
@groq.call("llama-3.3-70b-versatile")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


print(recommend_book("fantasy"))
