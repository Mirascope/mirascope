import inspect
import shutil
import tempfile
from pathlib import Path
from typing import Any

import pytest

from docs.generate_provider_examples import (
    PROVIDER_INFO,
    generate_provider_examples,
    get_supported_providers,
    substitute_llm_call_decorator,
    substitute_llm_override,
    substitute_provider_import,
    substitute_provider_specific_content,
    substitute_provider_type,
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


def test_substitute_llm_override():
    content = inspect.cleandoc("""
    llm.override(
        recommend_book,
        provider="anthropic",
        model="claude-3-5-sonnet-latest",
        call_params={"temperature": 0.7},
    )("fantasy")
    """)
    expected_anthropic = inspect.cleandoc("""
    llm.override(
        recommend_book,
        provider="openai",
        model="gpt-4o-mini",
        call_params={"temperature": 0.7},
    )("fantasy")
    """)
    expected_google = inspect.cleandoc("""
    llm.override(
        recommend_book,
        provider="anthropic",
        model="claude-3-5-sonnet-latest",
        call_params={"temperature": 0.7},
    )("fantasy")
    """)
    assert substitute_llm_override(content, "anthropic") == expected_anthropic
    assert substitute_llm_override(content, "google") == expected_google
    assert substitute_llm_override(content, "openai") == content


def test_substitute_llm_override_exceptions():
    bad_provider = inspect.cleandoc("""
    llm.override(
        recommend_book,
        provider="gemini",
        model="claude-3-5-sonnet-latest",
        call_params={"temperature": 0.7},
    )("fantasy")
    """)
    bad_model = inspect.cleandoc("""
    llm.override(
        recommend_book,
        provider="anthropic",
        model="claude-3-5-haiku-latest",
        call_params={"temperature": 0.7},
    )("fantasy")
    """)
    with pytest.raises(ValueError, match="Could not find provider='anthropic"):
        substitute_llm_override(bad_provider, "openai")
    with pytest.raises(
        ValueError, match="Could not find model='claude-3-5-sonnet-latest'"
    ):
        substitute_llm_override(bad_model, "openai")


def test_substitute_provider_type():
    content = inspect.cleandoc("""
        cast(openai.OpenAICallResponse, response)
        """)
    expected = inspect.cleandoc("""
        cast(anthropic.AnthropicCallResponse, response)
        """)
    result = substitute_provider_type(content, "anthropic")
    assert result == expected


def test_substitute_provider_type_special_caps():
    content = inspect.cleandoc("""
        cast(openai.OpenAICallResponse, response)
        """)
    expected = inspect.cleandoc("""
        cast(litellm.LiteLLMCallResponse, response)
        """)
    assert substitute_provider_type(content, "litellm") == expected
    assert substitute_provider_type(content, "openai") == content


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
    assert substitute_provider_specific_content(content, "anthropic") == expected
    assert substitute_provider_specific_content(content, "openai") == content


def test_full_substitute_with_override():
    content = inspect.cleandoc("""
        from mirascope import llm
        from mirascope.core import prompt_template


        @llm.call(provider="openai", model="gpt-4o-mini")
        @prompt_template("Recommend a {genre} book")
        def recommend_book(genre: str): ...


        response = recommend_book("fantasy")
        print(response.content)

        override_response = llm.override(
            recommend_book,
            provider="anthropic",
            model="claude-3-5-sonnet-latest",
            call_params={"temperature": 0.7},
        )("fantasy")

        print(override_response.content)
        """)
    expected = inspect.cleandoc("""
        from mirascope import llm
        from mirascope.core import prompt_template


        @llm.call(provider="anthropic", model="claude-3-5-sonnet-latest")
        @prompt_template("Recommend a {genre} book")
        def recommend_book(genre: str): ...


        response = recommend_book("fantasy")
        print(response.content)

        override_response = llm.override(
            recommend_book,
            provider="openai",
            model="gpt-4o-mini",
            call_params={"temperature": 0.7},
        )("fantasy")

        print(override_response.content)
        """)
    result_anthropic = substitute_provider_specific_content(content, "anthropic")
    result_openai = substitute_provider_specific_content(content, "openai")
    assert result_anthropic == expected
    assert result_openai == content


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
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        examples_root = Path("examples")
        example = "learn/response_models/basic_usage"
        assert (examples_root / example / "shorthand.py").exists()
        snippets_dir = temp_path / "build/snippets"
        generate_provider_examples(
            example_dirs=[example],
            examples_root=examples_root,
            snippets_dir=snippets_dir,
        )

        anthropic_example = snippets_dir / example / "anthropic" / "shorthand.py"
        assert anthropic_example.exists()
        with open(anthropic_example) as f:
            content = f.read()
        assert "anthropic" in content
        assert "claude-3-5-sonnet-latest" in content
        assert "openai" not in content


def test_generate_provider_example_removes_existing_files():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        examples_root = Path("../examples")
        example = "learn/response_models/basic_usage"

        snippets_dir = temp_path / "build/snippets"
        errata = snippets_dir / "learn/response_models/basic_usage/anthropic/errata.py"
        errata.parent.mkdir(parents=True, exist_ok=True)
        errata.touch()
        generate_provider_examples(
            example_dirs=[example],
            examples_root=examples_root,
            snippets_dir=snippets_dir,
        )

        assert not errata.exists()


def test_generate_provider_example_overrides():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        examples_root = temp_path / "examples"
        example = "learn/response_models/basic_usage"
        example_dir = examples_root / example

        # copy contents of examples/learn/response_models/basic_usage/ to examples_root
        # so we can modify it by adding a dummy override
        shutil.copytree(Path("examples") / example, example_dir)

        assert (example_dir / "messages.py").exists()

        # pretend anthropic has an override for a basic method file
        (example_dir / "anthropic").mkdir(parents=True, exist_ok=True)
        (example_dir / "anthropic" / "messages.py").write_text("# Not Supported")

        # anthropic also has a special sdk file
        (example_dir / "anthropic" / "special_sdk.py").write_text("# Special Sauce")

        snippets_dir = temp_path / "build/snippets"
        generate_provider_examples(
            example_dirs=[example],
            examples_root=examples_root,
            snippets_dir=snippets_dir,
        )

        snippet_example = snippets_dir / example

        with open(snippet_example / "openai" / "messages.py") as f:
            openai_content = f.read()
            assert "Not Supported" not in openai_content
            assert "@llm.call" in openai_content

        with open(snippet_example / "anthropic" / "messages.py") as f:
            anthropic_content = f.read()
            assert "Not Supported" in anthropic_content
            assert "@llm.call" not in anthropic_content

        with open(snippet_example / "anthropic" / "special_sdk.py") as f:
            anthropic_content = f.read()
            assert "Special Sauce" in anthropic_content
