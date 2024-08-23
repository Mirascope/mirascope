from pydantic import BaseModel

from mirascope.core import openai, prompt_template


class Book(BaseModel):
    title: str
    author: str


class Librarian(BaseModel):
    books: list[Book]

    @openai.call("gpt-4o-mini")
    @prompt_template(
        """
        SYSTEM: You can recommend the following books: {self.books}
        USER: I just read {previous_book.title} by {previous_book.author}. What should I read next?
        """
    )
    def recommend_book(self, previous_book: Book): ...
