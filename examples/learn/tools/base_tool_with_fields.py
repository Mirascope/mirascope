from pydantic import Field

from mirascope.core import BaseTool, openai, prompt_template


class FormatBook(BaseTool):
    title: str = Field(..., description="Book title in ALL CAPS")
    author: str = Field(..., description="Author as 'Last, First'")

    def call(self) -> str:
        return f"{self.title} by {self.author}"


@openai.call("gpt-4o-mini", tools=[FormatBook])
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


response = recommend_book("fantasy")
if tools := response.tools:
    for tool in tools:
        print(tool.call())
else:
    print(response.content)
