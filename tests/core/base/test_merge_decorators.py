from collections.abc import Callable

import pytest

from mirascope.core import merge_decorators


def test_single_decorator():
    """Test basic functionality with a single decorator."""

    def capitalize_result(f: Callable[[str], str]) -> Callable[[str], str]:
        def wrapper(*args: str, **kwargs: str) -> str:
            result = f(*args, **kwargs)
            return result.upper()

        return wrapper

    merged = merge_decorators(capitalize_result)()

    @merged
    def greet(name: str) -> str:
        """Return a greeting message."""
        return f"hello {name}"

    result = greet("world")
    assert result == "HELLO WORLD"
    assert greet.__doc__ == "Return a greeting message."
    assert greet.__name__ == "greet"


def test_multiple_decorators():
    """Test with multiple decorators and verify execution order."""
    traces: list[str] = []

    def decorator_a(f: Callable) -> Callable:
        def wrapper(*args: object, **kwargs: object) -> object:
            traces.append("a")
            return f(*args, **kwargs)

        return wrapper

    def decorator_b(f: Callable) -> Callable:
        def wrapper(*args: object, **kwargs: object) -> object:
            traces.append("b")
            return f(*args, **kwargs)

        return wrapper

    def decorator_c(f: Callable) -> Callable:
        def wrapper(*args: object, **kwargs: object) -> object:
            traces.append("c")
            return f(*args, **kwargs)

        return wrapper

    merged = merge_decorators(decorator_a, decorator_b, decorator_c)()

    @merged
    def func() -> str:
        """Test function."""
        traces.append("func")
        return "result"

    result = func()
    assert result == "result"
    # Decorators are applied in the order they are passed to merge_decorators
    assert traces == ["a", "b", "c", "func"]
    assert func.__doc__ == "Test function."
    assert func.__name__ == "func"


def test_decorator_with_arguments():
    """Test decorators that take arguments."""

    def multiply(n: int) -> Callable:
        def decorator(f: Callable[[int], int]) -> Callable[[int], int]:
            def wrapper(x: int) -> int:
                return f(x) * n

            return wrapper

        return decorator

    def add(n: int) -> Callable:
        def decorator(f: Callable[[int], int]) -> Callable[[int], int]:
            def wrapper(x: int) -> int:
                return f(x) + n

            return wrapper

        return decorator

    # First multiply by 2, then add 3: (x * 2) + 3
    merged = merge_decorators(multiply(2), add(3))()

    @merged
    def calculate(x: int) -> int:
        """Calculate a value."""
        return x

    assert calculate(5) == 16
    assert calculate.__doc__ == "Calculate a value."
    assert calculate.__name__ == "calculate"


def test_nested_metadata_preservation():
    """Test that metadata is preserved through nested decorator applications."""

    def outer_decorator(text: str) -> Callable:
        def decorator(f: Callable) -> Callable:
            def wrapper(*args: object, **kwargs: object) -> object:
                return f"{text}: {f(*args, **kwargs)}"

            return wrapper

        return decorator

    def inner_decorator(f: Callable) -> Callable:
        def wrapper(*args: object, **kwargs: object) -> object:
            return f"wrapped({f(*args, **kwargs)})"

        return wrapper

    merged = merge_decorators(outer_decorator("hello"), inner_decorator)()

    @merged
    def example(x: str) -> str:
        """Example function with detailed docstring."""
        return x

    result = example("world")
    assert result == "hello: wrapped(world)"
    assert example.__doc__ == "Example function with detailed docstring."
    assert example.__name__ == "example"


def test_error_propagation():
    """Test that errors are properly propagated through the decorator chain."""

    def error_decorator(f: Callable) -> Callable:
        def wrapper(*args: object, **kwargs: object) -> None:
            raise ValueError("Test error")

        return wrapper

    merged = merge_decorators(error_decorator)()

    @merged
    def func() -> str:
        """Function that should raise an error."""
        return "success"  # pragma: no cover

    with pytest.raises(ValueError, match="Test error"):
        func()
    assert func.__doc__ == "Function that should raise an error."
    assert func.__name__ == "func"


def test_async_function_compatibility():
    """Test compatibility with async functions."""
    import asyncio

    def log_decorator(f: Callable) -> Callable:
        async def wrapper(*args: object, **kwargs: object) -> object:
            result = await f(*args, **kwargs)
            return f"logged: {result}"

        return wrapper

    merged = merge_decorators(log_decorator)()

    @merged
    async def async_func(x: str) -> str:
        """Async test function."""
        return x

    result = asyncio.run(async_func("test"))
    assert result == "logged: test"
    assert async_func.__doc__ == "Async test function."
    assert async_func.__name__ == "async_func"


def test_metadata_preservation():
    """Test that the original function's metadata is preserved."""

    def decorator(f: Callable[[int], str]) -> Callable[[int], str]:
        def wrapper(x: int) -> str:
            return f(x)

        return wrapper

    merged = merge_decorators(decorator)()

    @merged
    def func(x: int) -> str:
        """Convert int to str."""
        return str(x)

    # Original function's type hints are preserved
    from typing import get_type_hints

    type_hints = get_type_hints(func)
    assert type_hints["x"] is int
    assert type_hints["return"] is str
    assert func.__doc__ == "Convert int to str."
    assert func.__name__ == "func"
    assert func(16) == "16"
