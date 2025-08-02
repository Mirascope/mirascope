"""Tests for Anthropic conversions module."""

import pytest
from anthropic import types as anthropic_types

from mirascope.llm.clients.anthropic.converter import AnthropicConverter
from mirascope.llm.content import (
    Audio,
    AudioUrl,
    Document,
    Image,
    ImageUrl,
    Text,
    ToolCall,
    ToolOutput,
)
from mirascope.llm.messages import assistant, system, user
from mirascope.llm.responses import FinishReason


class TestEncodeContent:
    """Test encode_content function."""

    def test_encode_single_text(self):
        """Test encoding single text content returns string."""
        content = [Text(text="Hello world")]
        result = AnthropicConverter.encode_content(content)
        assert result == "Hello world"

    def test_encode_multiple_text(self):
        """Test encoding multiple text parts returns list."""
        content = [Text(text="Hello"), Text(text=" world")]
        result = AnthropicConverter.encode_content(content)

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0] == anthropic_types.TextBlock(text="Hello", type="text")
        assert result[1] == anthropic_types.TextBlock(text=" world", type="text")

    def test_encode_image_not_implemented(self):
        """Test encoding image raises NotImplementedError."""
        content = [Image(mime_type="image/png", data="fake_data")]
        with pytest.raises(
            NotImplementedError, match="Have not implemented conversion for \\$image"
        ):
            AnthropicConverter.encode_content(content)

    def test_encode_image_url_not_implemented(self):
        """Test encoding image URL raises NotImplementedError."""
        content = [ImageUrl(url="https://example.com/image.png", mime_type="image/png")]
        with pytest.raises(
            NotImplementedError,
            match="Have not implemented conversion for \\$image_url",
        ):
            AnthropicConverter.encode_content(content)

    def test_encode_audio_not_implemented(self):
        """Test encoding audio raises NotImplementedError."""
        content = [Audio(mime_type="audio/mp3", data="fake_data")]
        with pytest.raises(
            NotImplementedError, match="Have not implemented conversion for \\$audio"
        ):
            AnthropicConverter.encode_content(content)

    def test_encode_audio_url_not_implemented(self):
        """Test encoding audio URL raises NotImplementedError."""
        content = [AudioUrl(url="https://example.com/audio.mp3", mime_type="audio/mp3")]
        with pytest.raises(
            NotImplementedError,
            match="Have not implemented conversion for \\$audio_url",
        ):
            AnthropicConverter.encode_content(content)

    def test_encode_document_not_implemented(self):
        """Test encoding document raises NotImplementedError."""
        content = [Document(mime_type="application/pdf", data="fake_data")]
        with pytest.raises(
            NotImplementedError, match="Have not implemented conversion for \\$document"
        ):
            AnthropicConverter.encode_content(content)

    def test_encode_tool_call_not_implemented(self):
        """Test encoding tool call raises NotImplementedError."""
        content = [ToolCall(id="call_123", name="test_func", args={})]
        with pytest.raises(
            NotImplementedError,
            match="Have not implemented conversion for \\$tool_call",
        ):
            AnthropicConverter.encode_content(content)

    def test_encode_tool_output_not_implemented(self):
        """Test encoding tool output raises NotImplementedError."""
        content = [ToolOutput(id="call_123", value="result")]
        with pytest.raises(
            NotImplementedError,
            match="Have not implemented conversion for \\$tool_output",
        ):
            AnthropicConverter.encode_content(content)


class TestEncodeMessages:
    """Test encode_messages function."""

    def test_encode_with_system_message(self):
        """Test encoding with system message at start."""
        messages = [system("You are helpful"), user("Hello")]
        system_msg, converted = AnthropicConverter.encode_messages(messages)

        assert system_msg == "You are helpful"
        assert len(converted) == 1
        assert converted[0]["role"] == "user"
        assert converted[0]["content"] == "Hello"

    def test_encode_without_system_message(self):
        """Test encoding without system message."""
        messages = [user("Hello"), assistant("Hi there!")]
        system_msg, converted = AnthropicConverter.encode_messages(messages)

        assert system_msg is None
        assert len(converted) == 2
        assert converted[0]["role"] == "user"
        assert converted[1]["role"] == "assistant"

    def test_encode_skipped_system_message_logs_warning(self, caplog):
        """Test that non-first system messages are skipped and warning is logged."""
        messages = [
            user("Hello"),
            system("This should be skipped"),
            assistant("Hi there!"),
        ]

        with caplog.at_level("WARNING"):
            system_msg, converted = AnthropicConverter.encode_messages(messages)

        assert system_msg is None
        assert len(converted) == 2
        assert converted[0]["role"] == "user"
        assert converted[1]["role"] == "assistant"

        assert len(caplog.records) == 1
        assert "Non-first system message at index 1 is being skipped" in caplog.text


class TestDecodeContent:
    """Test decode_content function."""

    def test_decode_text_block(self):
        """Test decoding text block."""
        content = anthropic_types.TextBlock(text="Hello", type="text")
        result = AnthropicConverter.decode_assistant_content(content)

        assert isinstance(result, Text)
        assert result.text == "Hello"

    def test_decode_unsupported_type(self):
        """Test decoding unsupported content type raises NotImplementedError."""

        class UnsupportedBlock:
            type = "unsupported"

        with pytest.raises(
            NotImplementedError,
            match="Support for content type `unsupported` is not yet implemented",
        ):
            AnthropicConverter.decode_assistant_content(UnsupportedBlock())  # type: ignore


class TestDecodeMessage:
    """Test decode_message function."""

    def test_decode_message(self):
        """Test decoding anthropic message."""
        anthropic_message = anthropic_types.Message(
            id="msg_123",
            role="assistant",
            content=[anthropic_types.TextBlock(text="Hello", type="text")],
            model="claude-3-sonnet",
            stop_reason="end_turn",
            stop_sequence=None,
            type="message",
            usage=anthropic_types.Usage(input_tokens=10, output_tokens=5),
        )

        result = AnthropicConverter.decode_assistant_message(anthropic_message)

        assert result.role == "assistant"
        assert len(result.content) == 1
        assert isinstance(result.content[0], Text)
        assert result.content[0].text == "Hello"


class TestDecodeFinishReason:
    """Test decode_finish_reason function."""

    def test_decode_all_supported_reasons(self):
        """Test decoding all supported stop reasons."""
        test_cases = [
            ("end_turn", FinishReason.END_TURN),
            ("max_tokens", FinishReason.MAX_TOKENS),
            ("stop_sequence", FinishReason.STOP),
            ("tool_use", FinishReason.TOOL_USE),
            ("refusal", FinishReason.REFUSAL),
        ]

        for anthropic_reason, expected_reason in test_cases:
            result = AnthropicConverter.decode_finish_reason(anthropic_reason)  # type: ignore
            assert result == expected_reason

        # Test unknown reason
        result = AnthropicConverter.decode_finish_reason("unknown_reason")  # type: ignore
        assert result == FinishReason.UNKNOWN

    def test_decode_no_reason(self):
        assert AnthropicConverter.decode_finish_reason(None) == FinishReason.UNKNOWN
