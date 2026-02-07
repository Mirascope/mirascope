"""Tests for OpenAICompletionsProvider"""

import base64

import pytest
from inline_snapshot import snapshot
from pydantic import BaseModel

from mirascope import llm
from mirascope.llm.content.document import (
    Base64DocumentSource,
    Document,
    TextDocumentSource,
)
from mirascope.llm.exceptions import FeatureNotSupportedError
from mirascope.llm.providers.openai.completions._utils import (
    CompletionsModelFeatureInfo,
    encode_request,
    feature_info_for_openai_model,
)
from mirascope.llm.tools import Toolkit


def test_prepare_message_multiple_user_text_parts() -> None:
    """Test preparing an OpenAI request with multiple text parts in a user message.

    Included for code coverage.
    """

    messages = [
        llm.messages.user(["Hello there", "fellow humans"]),
    ]
    assert encode_request(
        model_id="openai/gpt-4o",
        messages=messages,
        format=None,
        tools=Toolkit(None),
        params={},
        feature_info=feature_info_for_openai_model("gpt-4o"),
        provider_id="openai:completions",
    ) == snapshot(
        (
            [
                llm.UserMessage(
                    content=[
                        llm.Text(text="Hello there"),
                        llm.Text(text="fellow humans"),
                    ]
                )
            ],
            None,
            {
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"text": "Hello there", "type": "text"},
                            {"text": "fellow humans", "type": "text"},
                        ],
                    }
                ],
            },
        )
    )


def test_prepare_message_multiple_assistant_text_parts() -> None:
    """Test preparing an OpenAI request with multiple text parts in an assistant message.

    Included for code coverage.
    """

    messages = [
        llm.messages.user("Hello there"),
        llm.messages.assistant(
            ["General ", "Kenobi"],
            model_id="openai/gpt-4o",
            provider_id="openai",
        ),
    ]
    assert encode_request(
        model_id="openai/gpt-4o",
        messages=messages,
        format=None,
        tools=Toolkit(None),
        params={},
        feature_info=feature_info_for_openai_model("gpt-4o"),
        provider_id="openai:completions",
    ) == snapshot(
        (
            [
                llm.UserMessage(content=[llm.Text(text="Hello there")]),
                llm.AssistantMessage(
                    content=[llm.Text(text="General "), llm.Text(text="Kenobi")],
                    provider_id="openai",
                    model_id="openai/gpt-4o",
                    provider_model_name=None,
                    raw_message=None,
                ),
            ],
            None,
            {
                "model": "gpt-4o",
                "messages": [
                    {"role": "user", "content": "Hello there"},
                    {
                        "role": "assistant",
                        "content": [
                            {"text": "General ", "type": "text"},
                            {"text": "Kenobi", "type": "text"},
                        ],
                    },
                ],
            },
        )
    )


def test_strict_unsupported_legacy_model() -> None:
    """Test the error thrown on a legacy model that doesn't support strict mode formatting.

    Included for code coverage.
    """

    messages = [llm.messages.user("I have a bad feeling about this...")]

    class Book(BaseModel):
        pass

    format = llm.format(Book, mode="strict")

    with pytest.raises(llm.FeatureNotSupportedError):
        encode_request(
            model_id="openai/gpt-4",
            messages=messages,
            format=format,
            tools=Toolkit(None),
            params={},
            feature_info=feature_info_for_openai_model("gpt-4"),
            provider_id="openai:completions",
        )


def test_unknown_model_defaults_to_tool_mode() -> None:
    """Test that unknown models (empty feature_info) default to tool mode."""
    messages = [llm.messages.user("Extract book info")]

    class Book(BaseModel):
        title: str

    # With empty feature_info and no explicit mode, should default to tool mode
    _, format_result, kwargs = encode_request(
        model_id="unknown/model",
        messages=messages,
        format=Book,  # Will use default mode
        tools=Toolkit(None),
        params={},
        feature_info=CompletionsModelFeatureInfo(),  # All None
        provider_id="openrouter",
    )

    # Should have tools (tool mode), not response_format (strict mode)
    assert format_result is not None
    assert format_result.mode == "tool"
    assert "tools" in kwargs
    assert "response_format" not in kwargs


def test_unknown_model_allows_explicit_strict() -> None:
    """Test that unknown models allow explicit strict mode without error."""
    messages = [llm.messages.user("Extract book info")]

    class Book(BaseModel):
        title: str

    # Explicit strict mode with unknown model should work
    _, format_result, kwargs = encode_request(
        model_id="unknown/model",
        messages=messages,
        format=llm.format(Book, mode="strict"),
        tools=Toolkit(None),
        params={},
        feature_info=CompletionsModelFeatureInfo(),  # All None
        provider_id="openrouter",
    )

    # Should have response_format (strict mode worked)
    assert format_result is not None
    assert format_result.mode == "strict"
    assert "response_format" in kwargs
    response_format = kwargs["response_format"]
    assert not isinstance(response_format, type(NotImplemented))  # Not Omit
    assert response_format["type"] == "json_schema"  # pyright: ignore[reportIndexIssue]


def test_known_unsupported_model_rejects_strict() -> None:
    """Test that models with strict_support=False reject strict mode with correct provider_id."""
    messages = [llm.messages.user("Extract book info")]

    class Book(BaseModel):
        title: str

    # Explicit strict mode with known unsupported model should raise error
    with pytest.raises(llm.FeatureNotSupportedError) as exc_info:
        encode_request(
            model_id="openai/gpt-4",
            messages=messages,
            format=llm.format(Book, mode="strict"),
            tools=Toolkit(None),
            params={},
            feature_info=CompletionsModelFeatureInfo(strict_support=False),
            provider_id="custom-provider",
        )

    # Verify the provider_id in the error comes from the argument
    assert exc_info.value.provider_id == "custom-provider"
    assert exc_info.value.feature == "formatting_mode:strict"


def test_encode_base64_document() -> None:
    """Test encoding a base64 document source as file for OpenAI Completions."""
    doc = Document(
        source=Base64DocumentSource(
            type="base64_document_source",
            data="JVBERi0xLjQ=",
            media_type="application/pdf",
        )
    )
    messages = [llm.messages.user(["Read this", doc])]
    _, _, kwargs = encode_request(
        model_id="openai/gpt-4o",
        messages=messages,
        format=None,
        tools=Toolkit(None),
        params={},
        feature_info=feature_info_for_openai_model("gpt-4o"),
        provider_id="openai:completions",
    )
    assert kwargs == snapshot(
        {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"text": "Read this", "type": "text"},
                        {
                            "type": "file",
                            "file": {
                                "file_data": "data:application/pdf;base64,JVBERi0xLjQ=",
                                "filename": "document.pdf",
                            },
                        },
                    ],
                }
            ],
        }
    )


def test_encode_text_document() -> None:
    """Test encoding a text document source as file for OpenAI Completions."""
    doc = Document(
        source=TextDocumentSource(
            type="text_document_source",
            data="Hello, world!",
            media_type="text/plain",
        )
    )
    messages = [llm.messages.user(["Read this", doc])]
    _, _, kwargs = encode_request(
        model_id="openai/gpt-4o",
        messages=messages,
        format=None,
        tools=Toolkit(None),
        params={},
        feature_info=feature_info_for_openai_model("gpt-4o"),
        provider_id="openai:completions",
    )
    encoded = base64.b64encode(b"Hello, world!").decode("utf-8")
    assert kwargs == snapshot(
        {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"text": "Read this", "type": "text"},
                        {
                            "type": "file",
                            "file": {
                                "file_data": f"data:text/plain;base64,{encoded}",
                                "filename": "document.txt",
                            },
                        },
                    ],
                }
            ],
        }
    )


def test_encode_url_document_throws() -> None:
    """Test that URL document source throws FeatureNotSupportedError for Completions."""
    doc = Document.from_url("https://example.com/doc.pdf")
    messages = [llm.messages.user(["Read this", doc])]

    with pytest.raises(FeatureNotSupportedError):
        encode_request(
            model_id="openai/gpt-4o",
            messages=messages,
            format=None,
            tools=Toolkit(None),
            params={},
            feature_info=feature_info_for_openai_model("gpt-4o"),
            provider_id="openai:completions",
        )
