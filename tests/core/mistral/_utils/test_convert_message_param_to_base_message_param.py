from unittest.mock import Mock, patch

import pytest

from mirascope.core.mistral._utils._convert_message_param_to_base_message_param import (
    convert_message_param_to_base_message_param,
)


class DummyTextChunk:
    def __init__(self, text: str):
        self.text = text


class DummyImageURLChunk:
    def __init__(self, image_url: str):
        self.image_url = image_url


class DummyReferenceChunk:
    pass


def test_mistral_convert_content_image_url_chunk_invalid_format():
    """
    Test mistral_convert_content with ImageURLChunk but invalid data URL format.
    """
    image_url_chunk = DummyImageURLChunk("not_a_data_url")
    content = [image_url_chunk]

    with (
        patch(
            "mirascope.core.mistral._utils._convert_message_param_to_base_message_param.ImageURLChunk",
            DummyImageURLChunk,
        ),
        patch(
            "mirascope.core.mistral._utils._convert_message_param_to_base_message_param.TextChunk",
            DummyTextChunk,
        ),
        pytest.raises(
            ValueError, match="image_url is not in a supported data URL format"
        ),
    ):
        convert_message_param_to_base_message_param(Mock(content=content))  # pyright: ignore [reportArgumentType]


def test_mistral_convert_content_reference_chunk():
    """
    Test mistral_convert_content with ReferenceChunk which is not supported.
    """
    reference_chunk = DummyReferenceChunk()
    content = [reference_chunk]

    # Patch ReferenceChunk
    with (
        patch(
            "mirascope.core.mistral._utils._convert_message_param_to_base_message_param.ReferenceChunk",
            DummyReferenceChunk,
        ),
        patch(
            "mirascope.core.mistral._utils._convert_message_param_to_base_message_param.TextChunk",
            DummyTextChunk,
        ),
        patch(
            "mirascope.core.mistral._utils._convert_message_param_to_base_message_param.ImageURLChunk",
            DummyImageURLChunk,
        ),
        pytest.raises(ValueError, match="ReferenceChunk is not supported"),
    ):
        convert_message_param_to_base_message_param(Mock(content=content))  # pyright: ignore [reportArgumentType]
