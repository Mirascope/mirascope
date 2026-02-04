"""Test data generation for migration agent evaluation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


def _empty_list() -> list[str]:
    return []


@dataclass
class MigrationTestCase:
    """A test case for evaluating migration quality."""

    name: str
    input_code: str
    expected_patterns: list[str] = field(default_factory=_empty_list)
    version: str = "v1"  # "v0" or "v1"
    difficulty: str = "simple"  # "simple", "medium", "complex"
    source: str = "synthetic"  # "synthetic" or "examples"


# V0 synthetic test cases covering all v0 patterns
V0_SYNTHETIC_CASES: list[MigrationTestCase] = [
    MigrationTestCase(
        name="v0_basic_call_class",
        input_code='''"""Basic v0 class-based call."""
from mirascope.openai import OpenAICall


class BookRecommender(OpenAICall):
    prompt_template = "Recommend a {genre} book."
    genre: str


recommender = BookRecommender(genre="fantasy")
response = recommender.call()
print(response.content)
''',
        expected_patterns=[
            "v0_provider_import",
            "v0_call_class",
            "v0_prompt_template_attr",
            "response_content_access",
        ],
        version="v0",
        difficulty="simple",
    ),
    MigrationTestCase(
        name="v0_extractor_class",
        input_code='''"""V0 extractor for structured output."""
from mirascope.openai import OpenAIExtractor
from pydantic import BaseModel


class Book(BaseModel):
    title: str
    author: str


class BookExtractor(OpenAIExtractor[Book]):
    extract_schema: type[Book] = Book
    prompt_template = "Recommend a {genre} book."
    genre: str


extractor = BookExtractor(genre="fantasy")
book = extractor.extract()
print(f"{book.title} by {book.author}")
''',
        expected_patterns=[
            "v0_provider_import",
            "v0_extractor_class",
            "v0_prompt_template_attr",
            "v0_extract_method",
        ],
        version="v0",
        difficulty="medium",
    ),
    MigrationTestCase(
        name="v0_tool_class",
        input_code='''"""V0 provider-specific tool."""
from mirascope.openai import OpenAITool


class FormatBook(OpenAITool):
    title: str
    author: str

    def call(self) -> str:
        return f"{self.title} by {self.author}"


result = FormatBook(title="1984", author="George Orwell").call()
print(result)
''',
        expected_patterns=[
            "v0_provider_import",
            "v0_tool_class",
        ],
        version="v0",
        difficulty="simple",
    ),
    MigrationTestCase(
        name="v0_async_call",
        input_code='''"""V0 async call pattern."""
import asyncio
from mirascope.openai import OpenAICall


class BookRecommender(OpenAICall):
    prompt_template = "Recommend a {genre} book."
    genre: str


async def main():
    recommender = BookRecommender(genre="fantasy")
    response = await recommender.call_async()
    print(response.content)


asyncio.run(main())
''',
        expected_patterns=[
            "v0_provider_import",
            "v0_call_class",
            "v0_prompt_template_attr",
            "v0_call_async_method",
            "response_content_access",
        ],
        version="v0",
        difficulty="medium",
    ),
    MigrationTestCase(
        name="v0_response_dump",
        input_code='''"""V0 response dump pattern."""
from mirascope.openai import OpenAICall


class BookRecommender(OpenAICall):
    prompt_template = "Recommend a {genre} book."
    genre: str


recommender = BookRecommender(genre="fantasy")
response = recommender.call()
data = response.dump()
print(data)
''',
        expected_patterns=[
            "v0_provider_import",
            "v0_call_class",
            "v0_prompt_template_attr",
            "v0_response_dump",
        ],
        version="v0",
        difficulty="simple",
    ),
    MigrationTestCase(
        name="v0_anthropic_call",
        input_code='''"""V0 Anthropic class-based call."""
from mirascope.anthropic import AnthropicCall


class Chatbot(AnthropicCall):
    prompt_template = "You are a helpful assistant. User: {message}"
    message: str


chatbot = Chatbot(message="Hello!")
response = chatbot.call()
print(response.content)
''',
        expected_patterns=[
            "v0_provider_import",
            "v0_call_class",
            "v0_prompt_template_attr",
            "response_content_access",
        ],
        version="v0",
        difficulty="simple",
    ),
]

# V1 synthetic test cases covering all v1 patterns
V1_SYNTHETIC_CASES: list[MigrationTestCase] = [
    MigrationTestCase(
        name="v1_basic_call",
        input_code='''"""Basic v1 decorator-based call."""
from mirascope.core import openai


@openai.call("gpt-4o-mini")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


response = recommend_book("fantasy")
print(response.content)
''',
        expected_patterns=[
            "v1_provider_import",
            "v1_provider_call_decorator",
            "response_content_access",
        ],
        version="v1",
        difficulty="simple",
    ),
    MigrationTestCase(
        name="v1_base_tool",
        input_code='''"""V1 class-based tool with BaseTool."""
from mirascope.core.base import BaseTool


class FormatBook(BaseTool):
    """Format a book recommendation."""

    title: str
    author: str

    def call(self) -> str:
        return f"{self.title} by {self.author}"
''',
        expected_patterns=[
            "v1_base_tool_import",
            "v1_base_tool_class",
        ],
        version="v1",
        difficulty="simple",
    ),
    MigrationTestCase(
        name="v1_streaming",
        input_code='''"""V1 streaming pattern."""
from mirascope.core import openai


@openai.call("gpt-4o-mini", stream=True)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


for chunk in recommend_book("fantasy"):
    print(chunk.content, end="")
''',
        expected_patterns=[
            "v1_provider_import",
            "v1_provider_call_decorator",
            "v1_stream_param_in_decorator",
            "response_content_access",
        ],
        version="v1",
        difficulty="medium",
    ),
    MigrationTestCase(
        name="v1_prompt_template",
        input_code='''"""V1 prompt_template decorator."""
from mirascope.core import openai, prompt_template


@prompt_template()
def book_prompt(genre: str) -> str:
    return f"Recommend a {genre} book"


@openai.call("gpt-4o-mini")
@book_prompt
def recommend_book(genre: str): ...


response = recommend_book("fantasy")
print(response.content)
''',
        expected_patterns=[
            "v1_provider_import",
            "v1_provider_call_decorator",
            "v1_prompt_template_decorator",
            "response_content_access",
        ],
        version="v1",
        difficulty="medium",
    ),
    MigrationTestCase(
        name="v1_messages_continuation",
        input_code='''"""V1 message continuation pattern."""
from mirascope.core import openai


@openai.call("gpt-4o-mini")
def chat(query: str) -> str:
    return query


response = chat("Hello")
print(response.content)

# Continue conversation
@openai.call("gpt-4o-mini")
def followup(query: str, prev_response) -> str:
    return query


response2 = followup("Tell me more", messages=response.messages)
print(response2.content)
''',
        expected_patterns=[
            "v1_provider_import",
            "v1_provider_call_decorator",
            "v1_messages_kwarg",
            "response_content_access",
        ],
        version="v1",
        difficulty="complex",
    ),
    MigrationTestCase(
        name="v1_tool_with_agent_loop",
        input_code='''"""V1 tool with agent loop."""
from mirascope.core import openai
from mirascope.core.base import BaseTool


class GetWeather(BaseTool):
    """Get the weather for a location."""

    location: str

    def call(self) -> str:
        return f"Weather in {self.location}: Sunny, 72F"


@openai.call("gpt-4o-mini", tools=[GetWeather])
def assistant(query: str) -> str:
    return query


response = assistant("What's the weather in NYC?")
while response.tool:
    tool_result = response.tool.call()
    response = assistant(query, messages=response.messages + [
        {"role": "tool", "content": tool_result}
    ])
print(response.content)
''',
        expected_patterns=[
            "v1_provider_import",
            "v1_base_tool_import",
            "v1_provider_call_decorator",
            "v1_base_tool_class",
            "v1_messages_kwarg",
            "response_tool_single",
            "response_content_access",
        ],
        version="v1",
        difficulty="complex",
    ),
    MigrationTestCase(
        name="v1_anthropic_call",
        input_code='''"""V1 Anthropic decorator-based call."""
from mirascope.core import anthropic


@anthropic.call("claude-3-5-sonnet-20240620")
def analyze_text(text: str) -> str:
    return f"Analyze this text: {text}"


response = analyze_text("Hello world")
print(response.content)
''',
        expected_patterns=[
            "v1_provider_import",
            "v1_provider_call_decorator",
            "response_content_access",
        ],
        version="v1",
        difficulty="simple",
    ),
]


def load_examples_from_path(
    base_path: Path,
    version_filter: str | None = None,
) -> list[MigrationTestCase]:
    """Load examples from a given path.

    Args:
        base_path: Path to search for Python files.
        version_filter: Optional filter for "v0" or "v1" patterns only.

    Returns:
        List of MigrationTestCase objects loaded from example files.
    """
    from mirascope.cli.migrate.patterns import scan_file_for_patterns

    if not base_path.exists():
        return []

    test_cases: list[MigrationTestCase] = []

    for filepath in base_path.glob("**/*.py"):
        # Skip common non-source directories
        if any(
            part in filepath.parts
            for part in [".venv", "__pycache__", "node_modules", ".git"]
        ):
            continue

        try:
            content = filepath.read_text()
        except (OSError, UnicodeDecodeError):
            continue

        # Skip files without mirascope imports
        if "mirascope" not in content:
            continue

        # Scan for patterns
        patterns = scan_file_for_patterns(filepath)
        if not patterns:
            continue

        # Determine version from patterns
        pattern_versions = {p.version for p in patterns}
        if "v0" in pattern_versions:
            version = "v0"
        elif "v1" in pattern_versions:
            version = "v1"
        else:
            version = "v0/v1"

        # Apply version filter
        if version_filter and version_filter not in version:
            continue

        # Determine difficulty based on pattern count and types
        pattern_types = {p.pattern_type for p in patterns}
        if len(patterns) <= 2:
            difficulty = "simple"
        elif len(patterns) <= 5:
            difficulty = "medium"
        else:
            difficulty = "complex"

        # Create test case
        try:
            rel_path = filepath.relative_to(base_path)
            name = f"example_{rel_path.stem}"
        except ValueError:
            name = f"example_{filepath.stem}"

        test_cases.append(
            MigrationTestCase(
                name=name,
                input_code=content,
                expected_patterns=list(pattern_types),
                version=version,
                difficulty=difficulty,
                source="examples",
            )
        )

    return test_cases


def load_v1_examples_from_cloud(
    base_path: Path | None = None,
) -> list[MigrationTestCase]:
    """Load v1 examples from cloud/public/examples/v1/.

    Args:
        base_path: Optional base path override. If None, auto-detects from cwd.

    Returns:
        List of MigrationTestCase objects loaded from example files.
    """
    if base_path is None:
        # Try to find the cloud examples relative to the package
        possible_paths = [
            Path.cwd() / "cloud" / "public" / "examples" / "v1",
            Path(__file__).parent.parent.parent.parent.parent.parent
            / "cloud"
            / "public"
            / "examples"
            / "v1",
        ]
        for path in possible_paths:
            if path.exists():
                base_path = path
                break

    if base_path is None:
        return []

    return load_examples_from_path(base_path, version_filter="v1")


def load_v0_examples_from_eddie() -> list[MigrationTestCase]:
    """Load v0 examples from the eddie project (if available).

    Returns:
        List of MigrationTestCase objects with v0 patterns.
    """
    # Try common locations for the eddie project
    possible_paths = [
        Path.home() / "Mirascope" / "GitHub" / "eddie",
        Path.cwd().parent / "eddie",
    ]

    for path in possible_paths:
        if path.exists():
            return load_examples_from_path(path, version_filter="v0")

    return []


def get_synthetic_v0_cases() -> list[MigrationTestCase]:
    """Get synthetic v0 test cases."""
    return V0_SYNTHETIC_CASES.copy()


def get_synthetic_v1_cases() -> list[MigrationTestCase]:
    """Get synthetic v1 test cases."""
    return V1_SYNTHETIC_CASES.copy()


def get_all_test_cases(
    include_examples: bool = True,
    include_synthetic: bool = True,
    v0_only: bool = False,
    v1_only: bool = False,
) -> list[MigrationTestCase]:
    """Get all available test cases.

    Args:
        include_examples: Include test cases from cloud/public/examples/v1/ and eddie.
        include_synthetic: Include synthetic test cases.
        v0_only: Only include v0 test cases.
        v1_only: Only include v1 test cases.

    Returns:
        List of MigrationTestCase objects.
    """
    cases: list[MigrationTestCase] = []

    if include_synthetic:
        if not v1_only:
            cases.extend(get_synthetic_v0_cases())
        if not v0_only:
            cases.extend(get_synthetic_v1_cases())

    if include_examples:
        if not v0_only:
            cases.extend(load_v1_examples_from_cloud())
        if not v1_only:
            cases.extend(load_v0_examples_from_eddie())

    return cases


def get_test_cases_by_difficulty(
    difficulty: str,
    include_examples: bool = True,
    include_synthetic: bool = True,
) -> list[MigrationTestCase]:
    """Get test cases filtered by difficulty.

    Args:
        difficulty: One of "simple", "medium", "complex".
        include_examples: Include test cases from examples.
        include_synthetic: Include synthetic test cases.

    Returns:
        Filtered list of MigrationTestCase objects.
    """
    all_cases = get_all_test_cases(
        include_examples=include_examples,
        include_synthetic=include_synthetic,
    )
    return [c for c in all_cases if c.difficulty == difficulty]
