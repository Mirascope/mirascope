from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel

from mirascope.core import openai, prompt_template


class Book(BaseModel):
    title: str
    author: str


class Librarian(BaseModel):
    history: list[ChatCompletionMessageParam] = []
    books: dict[str, str] = {}

    def add_book(self, book: Book) -> str:
        """Adds a book to the collection."""
        self.books[book.title] = book.author
        return f"Added '{book.title}' by {book.author} to the collection."

    def remove_book(self, book: Book) -> str:
        """Removes a book from the collection."""
        self.books.pop(book.title, None)
        return f"Removed '{book.title}' by {book.author} from the collection."

    @openai.call(model="gpt-4o-mini")
    @prompt_template(
        """
        SYSTEM:
        You are a helpful librarian assistant. You have access to the following tools:
        - `add_book`: Adds a book to your collection of books.
        - `remove_book`: Removes a book from your collection of books.
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
        return {"tools": [self.add_book, self.remove_book]}

    def _step(self, query: str) -> str:
        response = self._call(query)
        tools_and_outputs = []
        if tools := response.tools:
            for tool in tools:
                tools_and_outputs.append((tool, tool.call()))

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

            result = self._step(query)
            print(f"Librarian: {result}")


librarian = Librarian()
librarian.run()
