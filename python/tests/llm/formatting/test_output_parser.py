"""Tests for OutputParser class and @output_parser decorator."""

from mirascope import llm


def test_output_parser_decorator_creates_output_parser() -> None:
    """Test that @output_parser decorator creates an OutputParser instance."""

    @llm.output_parser(formatting_instructions="Return XML format")
    def parse_xml(response: llm.AnyResponse) -> str:
        """Parse XML response."""
        return "parsed"

    assert isinstance(parse_xml, llm.OutputParser)
    assert llm.formatting.is_output_parser(parse_xml)


def test_output_parser_formatting_instructions() -> None:
    """Test that OutputParser.formatting_instructions() returns correct instructions."""

    instructions = "Return book as XML: <book><title>...</title></book>"

    @llm.output_parser(formatting_instructions=instructions)
    def parse_book_xml(response: llm.AnyResponse) -> str:
        return "parsed"

    assert parse_book_xml.formatting_instructions() == instructions


def test_output_parser_call_invokes_wrapped_function() -> None:
    """Test that calling OutputParser invokes the wrapped function."""

    @llm.output_parser(formatting_instructions="Return XML")
    def parse_response(response: llm.AnyResponse) -> str:
        # Extract text from response
        return "".join(part.text for part in response.texts)

    # Create a mock response
    class MockResponse:
        texts = [llm.Text(text="Hello"), llm.Text(text=" World")]

    mock_response = MockResponse()
    result = parse_response(mock_response)  # type: ignore

    assert result == "Hello World"


def test_output_parser_preserves_function_name_and_doc() -> None:
    """Test that OutputParser preserves __name__ and __doc__ from wrapped function."""

    @llm.output_parser(formatting_instructions="Return XML")
    def my_custom_parser(response: llm.AnyResponse) -> str:
        """This is my custom parser docstring."""
        return "parsed"

    assert my_custom_parser.__name__ == "my_custom_parser"
    assert my_custom_parser.__doc__ == "This is my custom parser docstring."


def test_is_output_parser_returns_false_for_non_parsers() -> None:
    """Test that is_output_parser returns False for non-OutputParser objects."""

    def regular_function() -> None: ...

    class RegularClass: ...

    assert not llm.formatting.is_output_parser(regular_function)
    assert not llm.formatting.is_output_parser(RegularClass)
    assert not llm.formatting.is_output_parser(RegularClass())
    assert not llm.formatting.is_output_parser(None)
    assert not llm.formatting.is_output_parser("string")
    assert not llm.formatting.is_output_parser(123)


def test_output_parser_with_complex_logic() -> None:
    """Test OutputParser with more complex parsing logic."""

    @llm.output_parser(
        formatting_instructions="""
        Return numbers separated by commas:
        1,2,3,4,5
        """
    )
    def parse_numbers(response: llm.AnyResponse) -> list[int]:
        """Parse comma-separated numbers."""
        text = "".join(part.text for part in response.texts)
        return [int(n.strip()) for n in text.split(",") if n.strip()]

    class MockResponse:
        texts = [llm.Text(text="10, 20, 30")]

    result = parse_numbers(MockResponse())  # type: ignore
    assert result == [10, 20, 30]


def test_output_parser_empty_formatting_instructions() -> None:
    """Test OutputParser with empty formatting instructions."""

    @llm.output_parser(formatting_instructions="")
    def parser(response: llm.AnyResponse) -> str:
        return "test"

    assert parser.formatting_instructions() == ""
