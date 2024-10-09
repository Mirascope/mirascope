from mirascope.core import (
    BaseDynamicConfig,
    BaseToolKit,
    prompt_template,
    toolkit_tool,
    vertex,
)


class BookTools(BaseToolKit):
    __namespace__ = "book_tools"

    reading_level: str

    @toolkit_tool
    def suggest_author(self, author: str) -> str:
        """Suggests an author for the user to read based on their reading level.

        User reading level: {self.reading_level}
        """
        return f"I would suggest you read some books by {author}"


@vertex.call("gemini-1.5-flash")
@prompt_template("What {genre} author should I read?")
def recommend_author(genre: str, reading_level: str) -> BaseDynamicConfig:
    toolkit = BookTools(reading_level=reading_level)
    return {"tools": toolkit.create_tools()}


response = recommend_author("fantasy", "beginner")
if tool := response.tool:
    print(tool.call())
    # Output: I would suggest you read some books by J.K. Rowling

response = recommend_author("fantasy", "advanced")
if tool := response.tool:
    print(tool.call())
    # Output: I would suggest you read some books by Brandon Sanderson
