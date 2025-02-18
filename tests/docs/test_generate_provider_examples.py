import inspect
import tempfile
from pathlib import Path
from typing import Any

import pytest

from docs.generate_provider_examples import (
    PROVIDER_INFO,
    generate_provider_examples,
    get_supported_providers,
    substitute_llm_call_decorator,
    substitute_provider_cast,
    substitute_provider_import,
    substitute_provider_specific_content,
)


def test_substitute_llm_call_decorator_single_line():
    content = inspect.cleandoc("""
        from mirascope import llm

        @llm.call(provider="openai", model="gpt-4o-mini", response_model=Book)
        def extract_book(text: str):
            pass
        """)
    expected = inspect.cleandoc("""
        from mirascope import llm

        @llm.call(provider="anthropic", model="claude-3-5-sonnet-latest", response_model=Book)
        def extract_book(text: str):
            pass
        """)
    result = substitute_llm_call_decorator(content, "anthropic")
    assert result == expected


def test_substitute_llm_call_decorator_multi_line():
    content = inspect.cleandoc("""
        from mirascope import llm

        @llm.call(
            provider="openai",
            model="gpt-4o-mini",
            response_model=Book
        )
        def extract_book(text: str):
            pass
        """)
    expected = inspect.cleandoc("""
        from mirascope import llm

        @llm.call(
            provider="anthropic",
            model="claude-3-5-sonnet-latest",
            response_model=Book
        )
        def extract_book(text: str):
            pass
        """)
    result = substitute_llm_call_decorator(content, "anthropic")
    assert result == expected


def test_substitute_llm_call_decorator_wrong_provider():
    content = inspect.cleandoc("""
        @llm.call(provider="azure", model="gpt-4o-mini", response_model=Book)
        def extract_book(text: str):
            pass
        """)
    with pytest.raises(ValueError, match="Could not find provider='openai'"):
        substitute_llm_call_decorator(content, "anthropic")


def test_substitute_llm_call_decorator_wrong_model():
    content = inspect.cleandoc("""
        @llm.call(provider="openai", model="wrong-model", response_model=Book)
        def extract_book(text: str):
            pass
        """)
    with pytest.raises(ValueError, match="Could not find model='gpt-4o-mini'"):
        substitute_llm_call_decorator(content, "anthropic")


def test_substitute_llm_call_decorator_multiple_decorators():
    content = inspect.cleandoc("""
        @llm.call(provider="openai", model="gpt-4o-mini")
        def func1(): pass

        @llm.call(provider="openai", model="gpt-4o-mini")
        def func2(): pass
        """)
    expected = inspect.cleandoc("""
        @llm.call(provider="anthropic", model="claude-3-5-sonnet-latest")
        def func1(): pass

        @llm.call(provider="anthropic", model="claude-3-5-sonnet-latest")
        def func2(): pass
        """)
    result = substitute_llm_call_decorator(content, "anthropic")
    assert result == expected


def test_substitute_provider_import():
    content = inspect.cleandoc("""
        from mirascope.core import openai
        """)
    expected = inspect.cleandoc("""
        from mirascope.core import anthropic
        """)
    result = substitute_provider_import(content, "anthropic")
    assert result == expected


def test_substitute_provider_import_multi_import():
    content = inspect.cleandoc("""
        from mirascope.core import Foo, openai, Bar
        """)
    expected = inspect.cleandoc("""
        from mirascope.core import Foo, anthropic, Bar
        """)
    result = substitute_provider_import(content, "anthropic")
    assert result == expected


def test_substitute_provider_cast():
    content = inspect.cleandoc("""
        cast(openai.OpenAICallResponse, response)
        """)
    expected = inspect.cleandoc("""
        cast(anthropic.AnthropicCallResponse, response)
        """)
    result = substitute_provider_cast(content, "anthropic")
    assert result == expected


def test_substitute_provider_cast_litellm():
    content = inspect.cleandoc("""
        cast(openai.OpenAICallResponse, response)
        """)
    expected = inspect.cleandoc("""
        cast(litellm.LiteLLMCallResponse, response)
        """)
    result = substitute_provider_cast(content, "litellm")
    assert result == expected


def test_substitute_provider_specific_content():
    content = inspect.cleandoc("""
        from mirascope import BaseMessageParam, llm
        from mirascope.core import openai
        from pydantic import BaseModel


        class Book(BaseModel):
            title: str
            author: str


        @llm.call(provider="openai", model="gpt-4o-mini", response_model=Book)
        def extract_book(text: str) -> list[BaseMessageParam]:
            return [BaseMessageParam(role="user", content=f"Extract {text}")]


        book = extract_book("The Name of the Wind by Patrick Rothfuss")
        print(book)
        # Output: title='The Name of the Wind' author='Patrick Rothfuss'

        response = cast(openai.OpenAICallResponse, book._response)  # pyright: ignore[reportAttributeAccessIssue]
        print(response.model_dump())
        # > {'metadata': {}, 'response': {'id': ...}, ...}
        """)
    expected = inspect.cleandoc("""
        from mirascope import BaseMessageParam, llm
        from mirascope.core import anthropic
        from pydantic import BaseModel


        class Book(BaseModel):
            title: str
            author: str


        @llm.call(provider="anthropic", model="claude-3-5-sonnet-latest", response_model=Book)
        def extract_book(text: str) -> list[BaseMessageParam]:
            return [BaseMessageParam(role="user", content=f"Extract {text}")]


        book = extract_book("The Name of the Wind by Patrick Rothfuss")
        print(book)
        # Output: title='The Name of the Wind' author='Patrick Rothfuss'

        response = cast(anthropic.AnthropicCallResponse, book._response)  # pyright: ignore[reportAttributeAccessIssue]
        print(response.model_dump())
        # > {'metadata': {}, 'response': {'id': ...}, ...}
        """)
    result = substitute_provider_specific_content(content, "anthropic")
    assert result == expected


def test_substitute_fails_invalid_provider():
    content = inspect.cleandoc("""
        @llm.call(provider="openai", model="gpt-4o-mini")
        def func(): pass
        """)
    bad_provider: Any = "InvalidProvider"
    with pytest.raises(ValueError, match="Provider InvalidProvider not found"):
        substitute_provider_specific_content(content, bad_provider)


def test_supported_providers_matches_mkdocs():
    actual = []

    with open("mkdocs.yml") as f:
        in_extra = False
        in_providers = False
        for line in f:
            if line.strip() == "extra:":
                in_extra = True
            elif in_extra and "supported_llm_providers:" in line:
                in_providers = True
            elif in_providers and line.strip().startswith("- "):
                actual.append(line.strip()[2:])
            elif in_providers and not line.strip().startswith("- "):
                break
    assert set(actual) == {info.title for info in PROVIDER_INFO.values()}


def test_substitute_llm_call_decorator_all_providers():
    base_content = inspect.cleandoc("""
        @llm.call(provider="openai", model="gpt-4o-mini")
        def func(): pass
        """)

    providers = get_supported_providers()

    for info in providers:
        result = substitute_llm_call_decorator(base_content, info.provider)
        assert info.provider in result
        assert info.model in result
        assert "func(): pass" in result


def test_generate_provider_example():
    # Create a temporary directory for the test
    with tempfile.TemporaryDirectory() as temp_dir:
        # Convert the temporary directory path to a Path object
        temp_path = Path(temp_dir)

        examples_root = Path("examples")
        example = "learn/response_models/basic_usage"
        assert (examples_root / example / "shorthand.py").exists()
        config = {"extra": {"provider_example_dirs": [example]}}
        snippets_dir = temp_path / "build/snippets"
        generate_provider_examples(
            config=config, examples_root=examples_root, snippets_dir=snippets_dir
        )

        anthropic_example = snippets_dir / example / "anthropic" / "shorthand.py"
        assert anthropic_example.exists()
        with open(anthropic_example) as f:
            content = f.read()
        assert "anthropic" in content
        assert "claude-3-5-sonnet-latest" in content
        assert "openai" not in content


def test_generate_provider_example_removes_existing_files():
    # Create a temporary directory for the test
    with tempfile.TemporaryDirectory() as temp_dir:
        # Convert the temporary directory path to a Path object
        temp_path = Path(temp_dir)

        examples_root = Path("../examples")
        example = "learn/response_models/basic_usage"

        config = {"extra": {"provider_example_dirs": [example]}}
        snippets_dir = temp_path / "build/snippets"
        errata = snippets_dir / "learn/response_models/basic_usage/anthropic/errata.py"
        errata.parent.mkdir(parents=True, exist_ok=True)
        errata.touch()
        generate_provider_examples(
            config=config, examples_root=examples_root, snippets_dir=snippets_dir
        )

        assert not errata.exists()
