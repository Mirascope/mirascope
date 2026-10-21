"""Unit tests for Partial model generation."""

from typing import Union, cast

from pydantic import BaseModel

from mirascope import llm
from mirascope.llm.formatting import Partial


def test_partial_basemodel() -> None:
    """Test that Partial makes all fields optional with None defaults."""

    class Book(BaseModel):
        title: str
        author: str
        pages: int

    PartialBook = Partial[Book]

    # All fields should be optional
    # Cast to access model_fields on dynamically created class
    partial_book_cls = cast(type[Book], PartialBook)
    assert not partial_book_cls.model_fields["title"].is_required()
    assert not partial_book_cls.model_fields["author"].is_required()
    assert not partial_book_cls.model_fields["pages"].is_required()

    # Can instantiate with partial data
    partial = cast(Book, PartialBook(title="The Name of the Wind"))
    assert partial.title == "The Name of the Wind"
    assert partial.author is None
    assert partial.pages is None

    # Can instantiate with empty data
    empty = cast(Book, PartialBook())
    assert empty.title is None
    assert empty.author is None
    assert empty.pages is None

    # Can instantiate with all data
    full = cast(
        Book,
        PartialBook(title="The Name of the Wind", author="Patrick Rothfuss", pages=662),
    )
    assert full.title == "The Name of the Wind"
    assert full.author == "Patrick Rothfuss"
    assert full.pages == 662


def test_partial_nested_models() -> None:
    """Test that nested BaseModel fields are also converted to Partial."""

    class Author(BaseModel):
        first_name: str
        last_name: str
        birth_year: int

    class Book(BaseModel):
        title: str
        author: Author
        pages: int

    PartialBook = Partial[Book]

    # Can instantiate with partial nested data
    partial = cast(
        Book,
        PartialBook(title="The Name of the Wind", author={"first_name": "Patrick"}),
    )
    assert partial.title == "The Name of the Wind"
    assert partial.author is not None
    # Access nested model attributes directly
    author = partial.author
    assert author.first_name == "Patrick"
    assert author.last_name is None
    assert author.birth_year is None
    assert partial.pages is None

    # Can instantiate with None for nested model
    no_author = cast(Book, PartialBook(title="The Name of the Wind"))
    assert no_author.title == "The Name of the Wind"
    assert no_author.author is None


def test_partial_generic_list() -> None:
    """Test that generic types with BaseModel args are handled correctly."""

    class Book(BaseModel):
        title: str
        author: str

    class Library(BaseModel):
        name: str
        books: list[Book]

    PartialLibrary = Partial[Library]

    # Can instantiate with partial list data
    partial = cast(
        Library,
        PartialLibrary(name="City Library", books=[{"title": "The Name of the Wind"}]),
    )
    assert partial.name == "City Library"
    assert partial.books is not None
    assert len(partial.books) == 1
    # Access list item attributes directly
    book = partial.books[0]
    assert book.title == "The Name of the Wind"
    assert book.author is None


def test_partial_generic_dict() -> None:
    """Test that generic dict types with BaseModel values are handled correctly."""

    class Book(BaseModel):
        title: str
        author: str

    class Catalog(BaseModel):
        name: str
        books_by_id: dict[str, Book]

    PartialCatalog = Partial[Catalog]

    # Can instantiate with partial dict data
    partial = cast(
        Catalog,
        PartialCatalog(
            name="Library Catalog", books_by_id={"1": {"title": "The Name of the Wind"}}
        ),
    )
    assert partial.name == "Library Catalog"
    assert partial.books_by_id is not None
    assert "1" in partial.books_by_id
    # Access dict value attributes directly
    book = partial.books_by_id["1"]
    assert book.title == "The Name of the Wind"
    assert book.author is None


def test_partial_caching() -> None:
    """Test that partial models are cached to avoid regeneration."""

    class Book(BaseModel):
        title: str
        author: str

    PartialBook1 = Partial[Book]
    PartialBook2 = Partial[Book]

    # Should return the same cached model
    assert PartialBook1 is PartialBook2


def test_partial_non_basemodel() -> None:
    """Test that non-BaseModel types are returned unchanged."""
    assert Partial[str] is str
    assert Partial[int] is int
    # Note: Generic types like list[str] may not pass identity checks due to how
    # Python handles generic type aliases, but they are functionally unchanged
    assert Partial[list[str]] == list[str]


def test_partial_deeply_nested() -> None:
    """Test deeply nested structures are fully converted to partial."""

    class Address(BaseModel):
        street: str
        city: str

    class Author(BaseModel):
        name: str
        address: Address

    class Book(BaseModel):
        title: str
        author: Author

    PartialBook = Partial[Book]

    # Can instantiate with deeply nested partial data
    partial = cast(
        Book,
        PartialBook(
            title="The Name of the Wind",
            author={"name": "Patrick", "address": {"city": "Madison"}},
        ),
    )
    assert partial.title == "The Name of the Wind"
    assert partial.author is not None
    # Access nested models directly
    author = partial.author
    assert author.name == "Patrick"
    assert author.address is not None
    address = author.address
    assert address.city == "Madison"
    assert address.street is None


def test_partial_nested_model_unions() -> None:
    """Partial nested models support native and typing unions without losing members."""

    class Author(BaseModel):
        name: str
        year: int

    class Book(BaseModel):
        author: Author | None
        attribution: Author | str
        legacy_author: Union[Author, None]  # noqa: UP007 - exercise typing.Union

    PartialBook = cast(type[Book], llm.Partial[Book])
    assert PartialBook.model_validate(
        {
            "author": {"name": "Patrick"},
            "attribution": {"name": "Patrick"},
            "legacy_author": {"name": "Patrick"},
        }
    ).model_dump() == {
        "author": {"name": "Patrick", "year": None},
        "attribution": {"name": "Patrick", "year": None},
        "legacy_author": {"name": "Patrick", "year": None},
    }
    assert PartialBook.model_validate({"attribution": "anonymous"}).model_dump() == {
        "author": None,
        "attribution": "anonymous",
        "legacy_author": None,
    }
    assert PartialBook.model_validate({"author": None}).model_dump() == {
        "author": None,
        "attribution": None,
        "legacy_author": None,
    }


def test_partial_nested_generics() -> None:
    """Partial models reach `BaseModel`s nested in unions of containers and in containers of containers."""

    class Book(BaseModel):
        title: str
        author: str

    class Shelf(BaseModel):
        optional_books: list[Book] | None
        rows: list[list[Book]]
        by_genre: dict[str, list[Book]]

    PartialShelf = cast(type[Shelf], Partial[Shelf])

    shelf = PartialShelf.model_validate(
        {
            "optional_books": [{"title": "A"}],
            "rows": [[{"title": "B"}]],
            "by_genre": {"fantasy": [{"title": "C"}]},
        }
    )

    assert shelf.optional_books is not None
    assert shelf.optional_books[0].title == "A"
    assert shelf.optional_books[0].author is None
    assert shelf.rows[0][0].title == "B"
    assert shelf.rows[0][0].author is None
    assert shelf.by_genre["fantasy"][0].title == "C"
    assert shelf.by_genre["fantasy"][0].author is None
