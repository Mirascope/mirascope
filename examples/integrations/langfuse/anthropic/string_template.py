from mirascope.core import anthropic, prompt_template
from mirascope.integrations.langfuse import with_langfuse


@with_langfuse()
@anthropic.call("claude-3-5-sonnet-20240620")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


print(recommend_book("fantasy"))
