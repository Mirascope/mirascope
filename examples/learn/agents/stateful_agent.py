from typing import Literal

from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel

from mirascope.core import BaseToolKit, openai, prompt_template, toolkit_tool


class Book(BaseModel):
    title: str
    author: str


class RecommendationTools(BaseToolKit):
    reading_level: str

    @toolkit_tool
    def recommend_book(self, book: Book) -> str:
        """Recommend a {self.reading_level} book."""
        return f"{book.title} by {book.author} is a great {self.reading_level} book!"


class Librarian(BaseModel):
    history: list[ChatCompletionMessageParam] = []
    books: dict[str, str] = {}
    user_reading_level: str = "unknown"

    def add_book(self, book: Book) -> str:
        """Adds a book to the collection."""
        self.books[book.title] = book.author
        return f"Added '{book.title}' by {book.author} to the collection."

    def remove_book(self, book: Book) -> str:
        """Removes a book from the collection."""
        self.books.pop(book.title, None)
        return f"Removed '{book.title}' by {book.author} from the collection."

    def update_reading_level(
        self, reading_level: Literal["beginner", "intermediate", "advanced"]
    ) -> str:
        """Updates the reading level of the user."""
        self.user_reading_level = reading_level
        return f"Updated reading level to {reading_level}."

    @openai.call(model="gpt-4o-mini", stream=True)
    @prompt_template(
        """
        SYSTEM:
        You are a helpful librarian assistant. You have access to the following tools:
        - `add_book`: Adds a book to your collection of books.
        - `remove_book`: Removes a book from your collection of books.
        - `update_reading_level`: Updates the reading level of the user.
        - `recommend_book`: Recommends a book based on the user's reading level. You will only have access to this tool once you determine the user's reading level.
        You should use these tools to update your book collection according to the user.
        For example, if the user mentions that they recently read a book that they liked, consider adding it to the collection.
        If the user didn't like a book, consider removing it from the collection.

        You currently have the following books in your collection:
        {self.books}

        MESSAGES: {self.history}
        USER: {query}
        """
    )
    def _call(self, query: str) -> openai.OpenAIDynamicConfig:
        tools = [self.add_book, self.remove_book, self.update_reading_level]
        if self.user_reading_level != "unknown":
            tools += RecommendationTools(
                reading_level=self.user_reading_level
            ).create_tools()
        return {"tools": tools}

    def _step(self, query: str) -> str:
        response = self._call(query)
        tools_and_outputs = []
        for chunk, tool in response:
            if tool:
                tools_and_outputs.append((tool, tool.call()))
            else:
                print(chunk.content, end="", flush=True)

        if response.user_message_param:
            self.history.append(response.user_message_param)
        self.history.append(response.message_param)
        if tools_and_outputs:
            self.history += response.tool_message_params(tools_and_outputs)
            return self._step("")
        else:
            return response.content

    def run(self):
        while True:
            query = input("User: ")
            if query.lower() == "exit":
                break

            print("Librarian: ", end="", flush=True)
            self._step(query)
            print("")


librarian = Librarian()
librarian.run()
