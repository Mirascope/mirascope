from pydantic import BaseModel, Field

from mirascope.core import openai, prompt_template


class DeduplicatedGenres(BaseModel):
    duplicates: list[list[str]] = Field(
        ..., description="A list containing lists of semantically equivalent items"
    )
    genres: list[str] = Field(
        ..., description="The list of genres with semantic duplicates removed"
    )


movie_genres = [
    "sci-fi",
    "romance",
    "love story",
    "action",
    "horror",
    "heist",
    "crime",
    "science fiction",
    "fantasy",
    "scary",
]


@openai.call(model="gpt-4o-mini", response_model=DeduplicatedGenres)
@prompt_template(
    """
    SYSTEM:
    Your job is to take a list of movie genres and clean it up by removing items
    which are semantically equivalent to one another. When coming across multiple items
    which refer to the same genre, keep the genre name which is most commonly used.
    For example, "sci-fi" and "science fiction" are the same genre.

    USER:
    {genres}
    """
)
def deduplicate_genres(genres: list[str]): ...


response = deduplicate_genres(movie_genres)
assert isinstance(response, DeduplicatedGenres)
print(response.genres)


class Book(BaseModel):
    title: str
    author: str
    genre: str


duplicate_books = [
    Book(title="The War of the Worlds", author="H. G. Wells", genre="scifi"),
    Book(title="War of the Worlds", author="H.G. Wells", genre="science fiction"),
    Book(title="The Sorcerer's stone", author="J. K. Rowling", genre="fantasy"),
    Book(
        title="Harry Potter and The Sorcerer's stone",
        author="J. K. Rowling",
        genre="fantasy",
    ),
    Book(title="The Name of the Wind", author="Patrick Rothfuss", genre="fantasy"),
    Book(title="'The Name of the Wind'", author="Patrick Rofuss", genre="fiction"),
]


@openai.call(model="gpt-4o", response_model=list[Book])
@prompt_template(
    """
    SYSTEM:
    Your job is to take a database of books and clean it up by removing items which are
    semantic duplicates. Look out for typos, formatting differences, and categorizations.
    For example, "Mistborn" and "Mistborn: The Final Empire" are the same book 
    but "Mistborn: Shadows of Self" is not.
    Then return all the unique books.

    USER:
    {books}
    """
)
def deduplicate_books(books: list[Book]): ...


books = deduplicate_books(duplicate_books)
assert isinstance(books, list)
for book in books:
    print(book)
