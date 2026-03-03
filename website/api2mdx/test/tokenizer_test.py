"""Tests for the tokenizer module."""

from api2mdx.tokenizer import Token, TokenType, tokenize


def test_tokenize_simple_types() -> None:
    """Test tokenizing simple type expressions."""
    # Test simple built-in types
    assert tokenize("str") == [Token(TokenType.IDENTIFIER, "str")]

    assert tokenize("int") == [Token(TokenType.IDENTIFIER, "int")]

    # Test custom types
    assert tokenize("MyClass") == [Token(TokenType.IDENTIFIER, "MyClass")]

    # Test with whitespace
    assert tokenize("  str  ") == [Token(TokenType.IDENTIFIER, "str")]

    # Test fully qualified name
    assert tokenize("module.submodule.MyClass") == [
        Token(TokenType.IDENTIFIER, "module.submodule.MyClass")
    ]


def test_tokenize_generic_types() -> None:
    """Test tokenizing generic type expressions."""
    # Test List[str]
    assert tokenize("List[str]") == [
        Token(TokenType.IDENTIFIER, "List"),
        Token(TokenType.OPEN_BRACKET, "["),
        Token(TokenType.IDENTIFIER, "str"),
        Token(TokenType.CLOSE_BRACKET, "]"),
    ]

    # Test Dict[str, int]
    assert tokenize("Dict[str, int]") == [
        Token(TokenType.IDENTIFIER, "Dict"),
        Token(TokenType.OPEN_BRACKET, "["),
        Token(TokenType.IDENTIFIER, "str"),
        Token(TokenType.COMMA, ","),
        Token(TokenType.IDENTIFIER, "int"),
        Token(TokenType.CLOSE_BRACKET, "]"),
    ]

    # Test with whitespace
    assert tokenize("Dict[ str , int ]") == [
        Token(TokenType.IDENTIFIER, "Dict"),
        Token(TokenType.OPEN_BRACKET, "["),
        Token(TokenType.IDENTIFIER, "str"),
        Token(TokenType.COMMA, ","),
        Token(TokenType.IDENTIFIER, "int"),
        Token(TokenType.CLOSE_BRACKET, "]"),
    ]


def test_tokenize_nested_types() -> None:
    """Test tokenizing nested type expressions."""
    # Test List[Dict[str, int]]
    assert tokenize("List[Dict[str, int]]") == [
        Token(TokenType.IDENTIFIER, "List"),
        Token(TokenType.OPEN_BRACKET, "["),
        Token(TokenType.IDENTIFIER, "Dict"),
        Token(TokenType.OPEN_BRACKET, "["),
        Token(TokenType.IDENTIFIER, "str"),
        Token(TokenType.COMMA, ","),
        Token(TokenType.IDENTIFIER, "int"),
        Token(TokenType.CLOSE_BRACKET, "]"),
        Token(TokenType.CLOSE_BRACKET, "]"),
    ]

    # Test Dict[str, List[int]]
    assert tokenize("Dict[str, List[int]]") == [
        Token(TokenType.IDENTIFIER, "Dict"),
        Token(TokenType.OPEN_BRACKET, "["),
        Token(TokenType.IDENTIFIER, "str"),
        Token(TokenType.COMMA, ","),
        Token(TokenType.IDENTIFIER, "List"),
        Token(TokenType.OPEN_BRACKET, "["),
        Token(TokenType.IDENTIFIER, "int"),
        Token(TokenType.CLOSE_BRACKET, "]"),
        Token(TokenType.CLOSE_BRACKET, "]"),
    ]


def test_tokenize_union_types() -> None:
    """Test tokenizing union type expressions."""
    # Test str | int
    assert tokenize("str | int") == [
        Token(TokenType.IDENTIFIER, "str"),
        Token(TokenType.PIPE, "|"),
        Token(TokenType.IDENTIFIER, "int"),
    ]

    # Test Union[str, int]
    assert tokenize("Union[str, int]") == [
        Token(TokenType.IDENTIFIER, "Union"),
        Token(TokenType.OPEN_BRACKET, "["),
        Token(TokenType.IDENTIFIER, "str"),
        Token(TokenType.COMMA, ","),
        Token(TokenType.IDENTIFIER, "int"),
        Token(TokenType.CLOSE_BRACKET, "]"),
    ]

    # Test complex union: Dict[str, int] | List[str] | None
    assert tokenize("Dict[str, int] | List[str] | None") == [
        Token(TokenType.IDENTIFIER, "Dict"),
        Token(TokenType.OPEN_BRACKET, "["),
        Token(TokenType.IDENTIFIER, "str"),
        Token(TokenType.COMMA, ","),
        Token(TokenType.IDENTIFIER, "int"),
        Token(TokenType.CLOSE_BRACKET, "]"),
        Token(TokenType.PIPE, "|"),
        Token(TokenType.IDENTIFIER, "List"),
        Token(TokenType.OPEN_BRACKET, "["),
        Token(TokenType.IDENTIFIER, "str"),
        Token(TokenType.CLOSE_BRACKET, "]"),
        Token(TokenType.PIPE, "|"),
        Token(TokenType.IDENTIFIER, "None"),
    ]

    # Test nested union inside a generic: Foo | List[Foo | Bar]
    assert tokenize("Foo | List[Foo | Bar]") == [
        Token(TokenType.IDENTIFIER, "Foo"),
        Token(TokenType.PIPE, "|"),
        Token(TokenType.IDENTIFIER, "List"),
        Token(TokenType.OPEN_BRACKET, "["),
        Token(TokenType.IDENTIFIER, "Foo"),
        Token(TokenType.PIPE, "|"),
        Token(TokenType.IDENTIFIER, "Bar"),
        Token(TokenType.CLOSE_BRACKET, "]"),
    ]


def test_tokenize_tuple_types() -> None:
    """Test tokenizing tuple type expressions."""
    # Test [str, int]
    assert tokenize("[str, int]") == [
        Token(TokenType.OPEN_BRACKET, "["),
        Token(TokenType.IDENTIFIER, "str"),
        Token(TokenType.COMMA, ","),
        Token(TokenType.IDENTIFIER, "int"),
        Token(TokenType.CLOSE_BRACKET, "]"),
    ]

    # Test Tuple[str, int]
    assert tokenize("Tuple[str, int]") == [
        Token(TokenType.IDENTIFIER, "Tuple"),
        Token(TokenType.OPEN_BRACKET, "["),
        Token(TokenType.IDENTIFIER, "str"),
        Token(TokenType.COMMA, ","),
        Token(TokenType.IDENTIFIER, "int"),
        Token(TokenType.CLOSE_BRACKET, "]"),
    ]


def test_tokenize_callable_types() -> None:
    """Test tokenizing callable type expressions."""
    # Test Callable[[str, int], bool]
    assert tokenize("Callable[[str, int], bool]") == [
        Token(TokenType.IDENTIFIER, "Callable"),
        Token(TokenType.OPEN_BRACKET, "["),
        Token(TokenType.OPEN_BRACKET, "["),
        Token(TokenType.IDENTIFIER, "str"),
        Token(TokenType.COMMA, ","),
        Token(TokenType.IDENTIFIER, "int"),
        Token(TokenType.CLOSE_BRACKET, "]"),
        Token(TokenType.COMMA, ","),
        Token(TokenType.IDENTIFIER, "bool"),
        Token(TokenType.CLOSE_BRACKET, "]"),
    ]
