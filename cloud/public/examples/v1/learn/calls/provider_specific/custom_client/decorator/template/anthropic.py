from anthropic import Anthropic # [!code highlight]
from mirascope.core import anthropic, prompt_template


@anthropic.call("claude-3-5-sonnet-latest", client=Anthropic()) # [!code highlight]
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...
