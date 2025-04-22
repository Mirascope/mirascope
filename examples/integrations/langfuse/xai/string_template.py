from mirascope.core import prompt_template, xai
from mirascope.integrations.langfuse import with_langfuse


@with_langfuse()
@xai.call("grok-3-mini")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


print(recommend_book("fantasy"))
