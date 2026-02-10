"""Tests for OpenAIResponsesProvider"""

import base64

from inline_snapshot import snapshot

from mirascope import llm
from mirascope.llm.content.document import (
    Base64DocumentSource,
    Document,
    TextDocumentSource,
)
from mirascope.llm.providers.openai.responses._utils import encode_request
from mirascope.llm.tools import Toolkit


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
    _, _, kwargs = encode_request(
        model_id="openai/gpt-4o",
        messages=messages,
        format=None,
        tools=Toolkit(None),
        params={},
    )
    assert kwargs == snapshot(
        {
            "model": "gpt-4o",
            "input": [
                {"role": "user", "content": "Hello there"},
                {"role": "assistant", "content": "General "},
                {"role": "assistant", "content": "Kenobi"},
            ],
        }
    )


def test_prepare_message_multiple_system_messages() -> None:
    """Test preparing an OpenAI request with multiple system messages."""

    messages = [
        llm.messages.user("Hello there"),
        llm.messages.system("Be concise."),
        llm.messages.system("On second thought, be verbose."),
    ]
    _, _, kwargs = encode_request(
        model_id="openai/gpt-4o",
        messages=messages,
        format=None,
        tools=Toolkit(None),
        params={},
    )
    assert kwargs == snapshot(
        {
            "model": "gpt-4o",
            "input": [
                {"role": "user", "content": "Hello there"},
                {"role": "developer", "content": "Be concise."},
                {"role": "developer", "content": "On second thought, be verbose."},
            ],
        }
    )


def test_encode_base64_document() -> None:
    """Test encoding a base64 document source as input_file for OpenAI Responses."""
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
    )
    assert kwargs == snapshot(
        {
            "model": "gpt-4o",
            "input": [
                {
                    "content": [
                        {"text": "Read this", "type": "input_text"},
                        {
                            "type": "input_file",
                            "file_data": "data:application/pdf;base64,JVBERi0xLjQ=",
                            "filename": "document.pdf",
                        },
                    ],
                    "role": "user",
                    "type": "message",
                }
            ],
        }
    )


def test_encode_text_document() -> None:
    """Test encoding a text document source as input_file for OpenAI Responses."""
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
    )
    encoded = base64.b64encode(b"Hello, world!").decode("utf-8")
    assert kwargs == snapshot(
        {
            "model": "gpt-4o",
            "input": [
                {
                    "content": [
                        {"text": "Read this", "type": "input_text"},
                        {
                            "type": "input_file",
                            "file_data": f"data:text/plain;base64,{encoded}",
                            "filename": "document.txt",
                        },
                    ],
                    "role": "user",
                    "type": "message",
                }
            ],
        }
    )


def test_encode_url_document() -> None:
    """Test encoding a URL document source as input_file with file_url for OpenAI Responses."""
    doc = Document.from_url("https://example.com/doc.pdf")
    messages = [llm.messages.user(["Read this", doc])]
    _, _, kwargs = encode_request(
        model_id="openai/gpt-4o",
        messages=messages,
        format=None,
        tools=Toolkit(None),
        params={},
    )
    assert kwargs == snapshot(
        {
            "model": "gpt-4o",
            "input": [
                {
                    "content": [
                        {"text": "Read this", "type": "input_text"},
                        {
                            "type": "input_file",
                            "file_url": "https://example.com/doc.pdf",
                        },
                    ],
                    "role": "user",
                    "type": "message",
                }
            ],
        }
    )
