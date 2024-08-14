from mirascope.core import BaseToolKit, openai, prompt_template, toolkit_tool


class BookToolkit(BaseToolKit):
    genre: str

    @toolkit_tool
    def format_book(self, title: str, author: str) -> str:
        """Format a {self.genre} book recommendation."""
        return f"{title} by {author} ({self.genre})"


@openai.call("gpt-4o-mini")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str) -> openai.OpenAIDynamicConfig:
    toolkit = BookToolkit(genre=genre)
    return {"tools": toolkit.create_tools()}


response = recommend_book("mystery")
if response.tool:
    print(response.tool.call())
