from mirascope import Messages, prompt_template
from pydantic import BaseModel


class Book(BaseModel):
    title: str
    author: str


@prompt_template()
def recommend_book_prompt(book: Book) -> Messages.Type:
    return Messages.User(
        f"I read {book.title} by {book.author}. What should I read next?"
    )


book = Book(title="The Name of the Wind", author="Patrick Rothfuss")
print(recommend_book_prompt(book))
# Output: [BaseMessageParam(role='user', content='I read The Name of the Wind by Patrick Rothfuss. What should I read next?')]
