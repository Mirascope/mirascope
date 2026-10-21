"""Unit tests for Partial model generation."""

import threading
from typing import Annotated, Any, Literal, Union, cast

import pytest
from pydantic import BaseModel, Discriminator, Field, Tag

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


class _Node(BaseModel):
    name: str
    children: list[list["_Node"]] = []


class _Tree(BaseModel):
    label: str
    branches: list["_Tree"] = []
    parent: "_Tree | None" = None


class _Folder(BaseModel):
    name: str
    files: list["_File"] = []


class _File(BaseModel):
    name: str
    folder: "_Folder | None" = None


_Node.model_rebuild()
_Tree.model_rebuild()
_Folder.model_rebuild()
_File.model_rebuild()


def test_partial_recursive_model_in_nested_containers() -> None:
    """A model that contains itself inside `list[list[...]]` doesn't recurse forever."""
    PartialNode = cast(type[_Node], Partial[_Node])

    node = PartialNode.model_validate(
        {"name": "root", "children": [[{"name": "leaf"}]]}
    )
    assert node.name == "root"
    leaf = node.children[0][0]
    assert type(leaf) is PartialNode
    assert leaf.name == "leaf"
    assert leaf.children is None


def test_partial_self_referencing_model() -> None:
    """Direct self references (`list[Self]`, `Optional[Self]`) become the partial model."""
    PartialTree = cast(type[_Tree], Partial[_Tree])
    assert Partial[_Tree] is PartialTree

    tree: Any = PartialTree.model_validate(
        {"label": "a", "branches": [{"label": "b"}], "parent": {}}
    )
    assert type(tree.branches[0]) is PartialTree
    assert tree.branches[0].branches is None
    assert type(tree.parent) is PartialTree
    assert tree.parent.label is None


def test_partial_mutually_recursive_models() -> None:
    """Two models that contain each other resolve to each other's partial model."""
    PartialFolder = cast(type[_Folder], Partial[_Folder])
    PartialFile = cast(type[_File], Partial[_File])

    folder: Any = PartialFolder.model_validate(
        {"name": "docs", "files": [{"name": "a.md", "folder": {"name": "docs"}}]}
    )
    assert type(folder.files[0]) is PartialFile
    assert type(folder.files[0].folder) is PartialFolder
    assert folder.files[0].folder.files is None


class _Circle(BaseModel):
    kind: Literal["circle"]
    radius: float


class _Square(BaseModel):
    kind: Literal["square"]
    side: float


class _Canvas(BaseModel):
    shapes: list[Annotated[_Circle | _Square, Field(discriminator="kind")]]
    optional_shape: Annotated[_Circle | _Square, Field(discriminator="kind")] | None = (
        None
    )
    main: Annotated[_Circle | _Square, Field(discriminator="kind")]


def test_partial_discriminated_unions_in_containers() -> None:
    """A discriminated union nested in a container still builds, with partial members."""
    PartialCanvas = cast(type[_Canvas], Partial[_Canvas])

    canvas: Any = PartialCanvas.model_validate(
        {
            "shapes": [{"kind": "circle"}, {"kind": "square", "side": 2}],
            "optional_shape": {"kind": "circle", "radius": 1},
            "main": {"kind": "square"},
        }
    )
    assert [type(shape) for shape in canvas.shapes] == [
        Partial[_Circle],
        Partial[_Square],
    ]
    assert canvas.shapes[1].side == 2
    assert canvas.optional_shape.radius == 1
    assert canvas.main.side is None


def test_partial_recursive_model_still_builds() -> None:
    """Regression: `Partial[Model]` for a model with `list[list[Model]]` must not recurse."""
    PartialNode = cast(type[_Node], Partial[_Node])
    node = PartialNode.model_validate(
        {"name": "root", "children": [[{"name": "leaf"}]]}
    )
    assert node.children[0][0].name == "leaf"


def test_partial_discriminated_union_in_container_still_builds() -> None:
    """Regression: a discriminated union in a container must not raise PydanticUserError."""
    PartialCanvas = cast(type[_Canvas], Partial[_Canvas])
    canvas: Any = PartialCanvas.model_validate(
        {
            "shapes": [{"kind": "circle", "radius": 1}],
            "main": {"kind": "square", "side": 2},
        }
    )
    assert canvas.shapes[0].radius == 1
    assert canvas.main.side == 2


def _shape_kind(value: Any) -> str:  # noqa: ANN401
    return value["kind"] if isinstance(value, dict) else value.kind


class _TaggedCanvas(BaseModel):
    shapes: list[
        Annotated[
            Annotated[_Circle, Tag("circle")] | Annotated[_Square, Tag("square")],
            Discriminator(_shape_kind),
        ]
    ]


def test_partial_callable_discriminated_unions_in_containers() -> None:
    """Callable discriminators and tags are dropped along with field discriminators."""
    PartialTaggedCanvas = cast(type[_TaggedCanvas], Partial[_TaggedCanvas])
    canvas: Any = PartialTaggedCanvas.model_validate(
        {"shapes": [{"kind": "circle"}, {"kind": "square", "side": 2}]}
    )
    assert [type(shape) for shape in canvas.shapes] == [
        Partial[_Circle],
        Partial[_Square],
    ]


def test_partial_failed_build_leaves_no_state(monkeypatch: pytest.MonkeyPatch) -> None:
    """A failing build doesn't leave half-built models in the cache or the in-progress map."""
    from mirascope.llm.formatting import partial as partial_module

    class Inner(BaseModel):
        value: int

    class Outer(BaseModel):
        inner: Inner

    def failing_create_model(*args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
        if kwargs.get("__base__") is BaseModel and "value" not in kwargs:
            raise RuntimeError("boom")
        return original_create_model(*args, **kwargs)

    original_create_model = partial_module.create_model
    monkeypatch.setattr(partial_module, "create_model", failing_create_model)

    with pytest.raises(RuntimeError, match="boom"):
        Partial[Outer]

    assert partial_module._partial_models_in_progress == {}  # pyright: ignore[reportPrivateUsage]
    assert partial_module._partial_models_created == {}  # pyright: ignore[reportPrivateUsage]
    assert Inner not in partial_module._partial_model_cache  # pyright: ignore[reportPrivateUsage]
    assert Outer not in partial_module._partial_model_cache  # pyright: ignore[reportPrivateUsage]


def test_partial_failed_rebuild_leaves_no_state(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """If resolving the forward references fails, the unfinished models aren't cached."""
    from mirascope.llm.formatting import partial as partial_module

    class Leaf(BaseModel):
        value: int

    class Branch(BaseModel):
        leaf: Leaf

    def failing_rebuild(cls: type[BaseModel], **kwargs: Any) -> None:  # noqa: ANN401
        raise RuntimeError("rebuild boom")

    monkeypatch.setattr(BaseModel, "model_rebuild", classmethod(failing_rebuild))

    with pytest.raises(RuntimeError, match="rebuild boom"):
        Partial[Branch]

    assert partial_module._partial_models_created == {}  # pyright: ignore[reportPrivateUsage]
    assert Leaf not in partial_module._partial_model_cache  # pyright: ignore[reportPrivateUsage]
    assert Branch not in partial_module._partial_model_cache  # pyright: ignore[reportPrivateUsage]


class _Shared(BaseModel):
    name: str
    children: list["_Shared"] = []
    siblings: list[list["_Shared"]] = []


_Shared.model_rebuild()


def test_partial_is_safe_to_build_from_several_threads() -> None:
    """Concurrent first uses of a recursive model all get the same, complete model."""
    results: list[Any] = []
    errors: list[BaseException] = []
    barrier = threading.Barrier(8)

    def build() -> None:
        try:
            barrier.wait()
            results.append(Partial[_Shared])
        except BaseException as error:  # noqa: BLE001
            errors.append(error)

    threads = [threading.Thread(target=build) for _ in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert errors == []
    assert len({id(result) for result in results}) == 1
    shared: Any = results[0].model_validate({"name": "a", "children": [{"name": "b"}]})
    assert type(shared.children[0]) is results[0]
