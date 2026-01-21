"""The `llm.output_parser` decorator for creating custom output parsers."""

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Generic, TypeVar
from typing_extensions import TypeIs

if TYPE_CHECKING:
    from ..responses import AnyResponse

OutputT = TypeVar("OutputT")


class OutputParser(Generic[OutputT]):
    """Represents a custom output parser created with @llm.output_parser.

    This class wraps a parsing function and stores formatting instructions.
    It is created by the @llm.output_parser decorator and used as a format
    argument in LLM calls.

    Unlike BaseModel and primitive type formats that use structured outputs
    (JSON schema, tools, strict mode), OutputParser works with raw text responses
    and custom parsing logic.

    Example:
        ```python
        @llm.output_parser(
            formatting_instructions="Return XML: <book><title>...</title></book>"
        )
        def parse_book_xml(response: llm.AnyResponse) -> Book:
            text = "".join(part.text for part in response.texts)
            root = ET.fromstring(text)
            return Book(title=root.find("title").text, ...)

        @llm.call("openai/gpt-4o", format=parse_book_xml)
        def recommend_book(genre: str):
            return f"Recommend a {genre} book."

        response = recommend_book("fantasy")
        book = response.parse()  # Returns Book instance
        ```
    """

    def __init__(
        self,
        func: Callable[["AnyResponse"], OutputT],
        formatting_instructions: str,
    ) -> None:
        """Initialize the OutputParser.

        Args:
            func: The parsing function that takes a Response and returns parsed output.
            formatting_instructions: Instructions for the LLM on how to format output.
        """
        self.func = func
        self._formatting_instructions = formatting_instructions
        self.__name__ = func.__name__
        self.__doc__ = func.__doc__

    def formatting_instructions(self) -> str:
        """Return the formatting instructions for the LLM.

        These instructions are added to the system prompt to guide the LLM
        on how to format its output for parsing.

        Returns:
            The formatting instructions string.
        """
        return self._formatting_instructions

    def __call__(self, response: "AnyResponse") -> OutputT:
        """Parse the response using the wrapped function.

        Args:
            response: The response object from the LLM call.

        Returns:
            The parsed output of type OutputT.

        Raises:
            Any exception raised by the wrapped parsing function.
        """
        return self.func(response)


def output_parser(
    *,
    formatting_instructions: str,
) -> Callable[[Callable[["AnyResponse"], OutputT]], OutputParser[OutputT]]:
    """Decorator to create an output parser for custom format parsing.

    Use this decorator to create custom parsers for non-JSON formats like
    XML, YAML, CSV, or any custom text structure. The decorated function
    receives the full Response object and returns the parsed output.

    This is the recommended way to handle custom output formats that don't
    fit the JSON/BaseModel paradigm. The formatting instructions guide the
    LLM on how to structure its output, and the parsing function extracts
    the data you need.

    Args:
        formatting_instructions: Instructions for the LLM on how to format
            the output. These will be added to the system prompt.

    Returns:
        Decorator that converts a function into an OutputParser.

    Example:

        XML parsing:
        ```python
        @llm.output_parser(
            formatting_instructions='''
            Return the book information in this XML structure:
            <book>
                <title>Book Title</title>
                <author>Author Name</author>
                <rating>5</rating>
            </book>
            '''
        )
        def parse_book_xml(response: llm.AnyResponse) -> Book:
            import xml.etree.ElementTree as ET
            text = "".join(part.text for part in response.texts)
            root = ET.fromstring(text)
            return Book(
                title=root.find("title").text,
                author=root.find("author").text,
                rating=int(root.find("rating").text),
            )
        ```

    Example:

        CSV parsing:
        ```python
        @llm.output_parser(
            formatting_instructions='''
            Return book information as CSV format with header:
            title,author,rating
            Book 1,Author 1,5
            Book 2,Author 2,4
            '''
        )
        def parse_books_csv(response: llm.AnyResponse) -> list[Book]:
            text = "".join(part.text for part in response.texts)
            lines = text.strip().split('\\n')[1:]  # Skip header
            return [
                Book(
                    title=line.split(',')[0].strip(),
                    author=line.split(',')[1].strip(),
                    rating=int(line.split(',')[2]),
                )
                for line in lines
            ]
        ```
    """

    def decorator(
        func: Callable[["AnyResponse"], OutputT],
    ) -> OutputParser[OutputT]:
        return OutputParser(func, formatting_instructions)

    return decorator


def is_output_parser(obj: Any) -> TypeIs[OutputParser[Any]]:  # noqa: ANN401
    """Check if an object is an OutputParser.

    This is a type guard function that narrows the type of `obj` to
    `OutputParser[Any, Any]` when it returns True.

    Args:
        obj: The object to check.

    Returns:
        True if the object is an OutputParser instance, False otherwise.
    """
    return isinstance(obj, OutputParser)
