from mirascope.core import mistral, prompt_template
from mirascope.integrations.langfuse import with_langfuse


@with_langfuse()
@mistral.call("mistral-large-latest")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


print(recommend_book("fantasy"))
