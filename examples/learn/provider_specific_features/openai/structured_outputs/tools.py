from mirascope.core import BaseTool, openai
from mirascope.core.openai import OpenAIToolConfig


class FormatBook(BaseTool):
    title: str
    author: str

    tool_config = OpenAIToolConfig(strict=True)

    def call(self) -> str:
        return f"{self.title} by {self.author}"


@openai.call(
    "gpt-4o-2024-08-06", tools=[FormatBook], call_params={"tool_choice": "required"}
)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


response = recommend_book("fantasy")
if tool := response.tool:
    print(tool.call())
