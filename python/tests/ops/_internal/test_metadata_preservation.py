"""Tests for function metadata preservation across decorators."""

from mirascope import llm, ops
from mirascope._utils import copy_function_metadata


def test_trace_preserves_function_metadata() -> None:
    """Test that @ops.trace preserves __name__, __doc__, __annotations__."""

    @ops.trace
    def my_function(x: int, y: str) -> float:
        """My docstring."""
        return float(x)

    assert my_function.__name__ == "my_function"
    assert my_function.__doc__ == "My docstring."
    assert my_function.__annotations__ == {"x": int, "y": str, "return": float}
    assert hasattr(my_function, "__wrapped__")


def test_trace_with_llm_tool_stacking() -> None:
    """Test that @llm.tool works on top of @ops.trace."""

    @llm.tool
    @ops.trace
    def calculate(a: float, b: float) -> float:
        """Add two numbers."""
        return a + b

    # Should create a Tool with correct name/description
    assert calculate.name == "calculate"
    assert "Add two numbers" in calculate.description


def test_llm_call_preserves_function_metadata() -> None:
    """Test that @llm.call preserves function metadata."""

    @llm.call("openai/gpt-4o-mini")
    def recommend_book(genre: str) -> str:
        """Recommend a book in the given genre."""
        return f"Recommend a {genre} book"

    assert recommend_book.__name__ == "recommend_book"
    assert recommend_book.__doc__ == "Recommend a book in the given genre."
    assert "genre" in recommend_book.__annotations__
    assert hasattr(recommend_book, "__wrapped__")


def test_llm_prompt_preserves_function_metadata() -> None:
    """Test that @llm.prompt preserves function metadata."""

    @llm.prompt
    def my_prompt(topic: str) -> str:
        """Generate content about a topic."""
        return f"Tell me about {topic}"

    assert my_prompt.__name__ == "my_prompt"
    assert my_prompt.__doc__ == "Generate content about a topic."
    assert "topic" in my_prompt.__annotations__
    assert hasattr(my_prompt, "__wrapped__")


def test_trace_on_llm_call_preserves_metadata() -> None:
    """Test that @ops.trace on @llm.call preserves function metadata."""

    @ops.trace
    @llm.call("openai/gpt-4o-mini")
    def recommend_book(genre: str) -> str:
        """Recommend a book in the given genre."""
        return f"Recommend a {genre} book"

    assert recommend_book.__name__ == "recommend_book"
    assert recommend_book.__doc__ == "Recommend a book in the given genre."
    assert hasattr(recommend_book, "__wrapped__")


def test_async_trace_preserves_function_metadata() -> None:
    """Test that @ops.trace preserves metadata for async functions."""

    @ops.trace
    async def my_async_function(x: int) -> str:
        """Async docstring."""
        return str(x)

    assert my_async_function.__name__ == "my_async_function"
    assert my_async_function.__doc__ == "Async docstring."
    assert my_async_function.__annotations__ == {"x": int, "return": str}
    assert hasattr(my_async_function, "__wrapped__")


def test_llm_tool_preserves_function_metadata() -> None:
    """Test that @llm.tool preserves function metadata."""

    @llm.tool
    def my_tool(x: int, y: str) -> str:
        """Tool docstring."""
        return f"{x}: {y}"

    assert my_tool.__name__ == "my_tool"
    assert my_tool.__doc__ == "Tool docstring."
    assert hasattr(my_tool, "__wrapped__")


def test_copy_function_metadata_handles_missing_attributes() -> None:
    """Test that copy_function_metadata handles sources missing some attributes."""

    class MinimalSource:
        """A source with only __name__ and no other standard attrs."""

        __name__ = "minimal"

    class Target:
        pass

    target = Target()
    source = MinimalSource()

    # Should not raise, even though source is missing most attributes
    copy_function_metadata(target, source)

    # Should have copied __name__
    assert target.__name__ == "minimal"  # pyright: ignore[reportAttributeAccessIssue]
    # Should have set __wrapped__
    assert target.__wrapped__ is source  # pyright: ignore[reportAttributeAccessIssue]


def test_async_llm_call_preserves_function_metadata() -> None:
    """Test that @llm.call preserves function metadata for async functions."""

    @llm.call("openai/gpt-4o-mini")
    async def async_recommend_book(genre: str) -> str:
        """Recommend a book asynchronously."""
        return f"Recommend a {genre} book"

    assert async_recommend_book.__name__ == "async_recommend_book"
    assert async_recommend_book.__doc__ == "Recommend a book asynchronously."
    assert "genre" in async_recommend_book.__annotations__
    assert hasattr(async_recommend_book, "__wrapped__")


def test_async_llm_prompt_preserves_function_metadata() -> None:
    """Test that @llm.prompt preserves function metadata for async functions."""

    @llm.prompt
    async def async_prompt(topic: str) -> str:
        """Async prompt docstring."""
        return f"Tell me about {topic}"

    assert async_prompt.__name__ == "async_prompt"
    assert async_prompt.__doc__ == "Async prompt docstring."
    assert "topic" in async_prompt.__annotations__
    assert hasattr(async_prompt, "__wrapped__")


def test_context_llm_call_preserves_function_metadata() -> None:
    """Test that @llm.call preserves function metadata for context functions."""

    @llm.call("openai/gpt-4o-mini")
    def context_call(ctx: llm.Context[str], topic: str) -> str:
        """Context call docstring."""
        return f"{ctx.deps}: {topic}"

    assert context_call.__name__ == "context_call"
    assert context_call.__doc__ == "Context call docstring."
    assert hasattr(context_call, "__wrapped__")


def test_async_context_llm_call_preserves_function_metadata() -> None:
    """Test that @llm.call preserves function metadata for async context functions."""

    @llm.call("openai/gpt-4o-mini")
    async def async_context_call(ctx: llm.Context[str], topic: str) -> str:
        """Async context call docstring."""
        return f"{ctx.deps}: {topic}"

    assert async_context_call.__name__ == "async_context_call"
    assert async_context_call.__doc__ == "Async context call docstring."
    assert hasattr(async_context_call, "__wrapped__")


def test_context_llm_prompt_preserves_function_metadata() -> None:
    """Test that @llm.prompt preserves function metadata for context functions."""

    @llm.prompt
    def context_prompt(ctx: llm.Context[str], topic: str) -> str:
        """Context prompt docstring."""
        return f"{ctx.deps}: {topic}"

    assert context_prompt.__name__ == "context_prompt"
    assert context_prompt.__doc__ == "Context prompt docstring."
    assert hasattr(context_prompt, "__wrapped__")


def test_async_context_llm_prompt_preserves_function_metadata() -> None:
    """Test that @llm.prompt preserves function metadata for async context functions."""

    @llm.prompt
    async def async_context_prompt(ctx: llm.Context[str], topic: str) -> str:
        """Async context prompt docstring."""
        return f"{ctx.deps}: {topic}"

    assert async_context_prompt.__name__ == "async_context_prompt"
    assert async_context_prompt.__doc__ == "Async context prompt docstring."
    assert hasattr(async_context_prompt, "__wrapped__")


def test_trace_on_async_llm_call_preserves_metadata() -> None:
    """Test that @ops.trace on async @llm.call preserves function metadata."""

    @ops.trace
    @llm.call("openai/gpt-4o-mini")
    async def async_recommend(genre: str) -> str:
        """Async recommend docstring."""
        return f"Recommend a {genre} book"

    assert async_recommend.__name__ == "async_recommend"
    assert async_recommend.__doc__ == "Async recommend docstring."
    assert hasattr(async_recommend, "__wrapped__")


def test_trace_on_context_llm_call_preserves_metadata() -> None:
    """Test that @ops.trace on context @llm.call preserves function metadata."""

    @ops.trace
    @llm.call("openai/gpt-4o-mini")
    def context_recommend(ctx: llm.Context[str], genre: str) -> str:
        """Context recommend docstring."""
        return f"{ctx.deps}: {genre}"

    assert context_recommend.__name__ == "context_recommend"
    assert context_recommend.__doc__ == "Context recommend docstring."
    assert hasattr(context_recommend, "__wrapped__")


def test_trace_on_async_context_llm_call_preserves_metadata() -> None:
    """Test that @ops.trace on async context @llm.call preserves function metadata."""

    @ops.trace
    @llm.call("openai/gpt-4o-mini")
    async def async_context_recommend(ctx: llm.Context[str], genre: str) -> str:
        """Async context recommend docstring."""
        return f"{ctx.deps}: {genre}"

    assert async_context_recommend.__name__ == "async_context_recommend"
    assert async_context_recommend.__doc__ == "Async context recommend docstring."
    assert hasattr(async_context_recommend, "__wrapped__")
