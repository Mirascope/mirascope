import base64
from unittest.mock import patch

import pytest

from mirascope.core import BaseMessageParam
from mirascope.core.base import ImagePart

# Import the target function from mistral utils
from mirascope.core.mistral._utils._convert_assistant_message_content_to_base_message_param import (
    _assistant_message_content_to_base_message_param as mistral_convert_content,
)


class DummyTextChunk:
    def __init__(self, text: str):
        self.text = text


class DummyImageURLChunk:
    def __init__(self, image_url: str):
        self.image_url = image_url


class DummyReferenceChunk:
    pass


@pytest.mark.parametrize("content_str", ["Just a simple text", "Another text"])
def test_mistral_convert_content_text_only(content_str: str):
    """
    Test mistral_convert_content with text content (simple string).
    """
    result = mistral_convert_content(content_str)
    assert isinstance(result, BaseMessageParam)
    assert result.role == "assistant"
    assert result.content == content_str


def test_mistral_convert_content_text_chunk():
    """
    Test mistral_convert_content with a TextChunk.
    """
    text_chunk = DummyTextChunk("hello")
    content = [text_chunk]

    # Patch TextChunk so that isinstance(chunk, TextChunk) returns True for DummyTextChunk
    with patch(
        "mirascope.core.mistral._utils._convert_assistant_message_content_to_base_message_param.TextChunk",
        DummyTextChunk,
    ):
        result = mistral_convert_content(content)  # pyright: ignore [reportArgumentType]
    assert isinstance(result, BaseMessageParam)
    assert result.content == "hello"


def test_mistral_convert_content_image_url_chunk():
    """
    Test mistral_convert_content with ImageURLChunk containing valid data URL.
    """
    png_data = b"\x89PNG\r\n\x1a\n"
    base64_data = base64.b64encode(png_data).decode("ascii")
    data_url = f"data:image/png;base64,{base64_data}"
    image_url_chunk = DummyImageURLChunk(data_url)
    content = [image_url_chunk]

    # Patch ImageURLChunk
    with (
        patch(
            "mirascope.core.mistral._utils._convert_assistant_message_content_to_base_message_param.ImageURLChunk",
            DummyImageURLChunk,
        ),
        patch(
            "mirascope.core.mistral._utils._convert_assistant_message_content_to_base_message_param.TextChunk",
            DummyTextChunk,
        ),
    ):
        result = mistral_convert_content(content)  # pyright: ignore [reportArgumentType]

    assert isinstance(result, BaseMessageParam)
    assert len(result.content) == 1
    assert isinstance(result.content[0], ImagePart)
    assert result.content[0].media_type == "image/png"


def test_mistral_convert_content_image_url_chunk_invalid_format():
    """
    Test mistral_convert_content with ImageURLChunk but invalid data URL format.
    """
    image_url_chunk = DummyImageURLChunk("not_a_data_url")
    content = [image_url_chunk]

    with (
        patch(
            "mirascope.core.mistral._utils._convert_assistant_message_content_to_base_message_param.ImageURLChunk",
            DummyImageURLChunk,
        ),
        patch(
            "mirascope.core.mistral._utils._convert_assistant_message_content_to_base_message_param.TextChunk",
            DummyTextChunk,
        ),
        pytest.raises(
            ValueError, match="image_url is not in a supported data URL format"
        ),
    ):
        mistral_convert_content(content)  # pyright: ignore [reportArgumentType]


def test_mistral_convert_content_reference_chunk():
    """
    Test mistral_convert_content with ReferenceChunk which is not supported.
    """
    reference_chunk = DummyReferenceChunk()
    content = [reference_chunk]

    # Patch ReferenceChunk
    with (
        patch(
            "mirascope.core.mistral._utils._convert_assistant_message_content_to_base_message_param.ReferenceChunk",
            DummyReferenceChunk,
        ),
        patch(
            "mirascope.core.mistral._utils._convert_assistant_message_content_to_base_message_param.TextChunk",
            DummyTextChunk,
        ),
        patch(
            "mirascope.core.mistral._utils._convert_assistant_message_content_to_base_message_param.ImageURLChunk",
            DummyImageURLChunk,
        ),
        pytest.raises(ValueError, match="ReferenceChunk is not supported"),
    ):
        mistral_convert_content(content)  # pyright: ignore [reportArgumentType]


def test_mistral_convert_content_unknown_type():
    """
    Test mistral_convert_content with unknown chunk type.
    """

    class UnknownChunk:
        pass

    unknown_chunk = UnknownChunk()
    content = [unknown_chunk]

    # Patch all known chunk classes so unknown won't match
    with (
        patch(
            "mirascope.core.mistral._utils._convert_assistant_message_content_to_base_message_param.TextChunk",
            DummyTextChunk,
        ),
        patch(
            "mirascope.core.mistral._utils._convert_assistant_message_content_to_base_message_param.ImageURLChunk",
            DummyImageURLChunk,
        ),
        patch(
            "mirascope.core.mistral._utils._convert_assistant_message_content_to_base_message_param.ReferenceChunk",
            DummyReferenceChunk,
        ),
        pytest.raises(ValueError, match="Unsupported ContentChunk type"),
    ):
        mistral_convert_content(content)  # pyright: ignore [reportArgumentType]


def test_mistral_convert_content_single_textpart_simplify():
    """
    If there is only one TextPart, mistral_convert_content should return text directly.
    """
    text_chunk = DummyTextChunk("single text")
    content = [text_chunk]

    with patch(
        "mirascope.core.mistral._utils._convert_assistant_message_content_to_base_message_param.TextChunk",
        DummyTextChunk,
    ):
        result = mistral_convert_content(content)  # pyright: ignore [reportArgumentType]
    # single TextPart => text directly
    assert isinstance(result, BaseMessageParam)
    assert result.content == "single text"
