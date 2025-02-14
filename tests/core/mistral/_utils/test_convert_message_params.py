"""Tests the `mistral._utils.convert_message_params` function."""

import pytest
from mistralai.models import (
    AssistantMessage,
    FunctionCall,
    ImageURL,
    ImageURLChunk,
    SystemMessage,
    TextChunk,
    ToolCall,
    ToolMessage,
    UserMessage,
)
from mistralai.types.basemodel import Unset

from mirascope.core.base import (
    AudioPart,
    BaseMessageParam,
    ImagePart,
    ImageURLPart,
    TextPart,
    ToolCallPart,
    ToolResultPart,
)
from mirascope.core.mistral._utils._convert_message_params import convert_message_params


def test_convert_message_params() -> None:
    """Tests the `convert_message_params` function."""

    message_params: list[
        BaseMessageParam | AssistantMessage | SystemMessage | ToolMessage | UserMessage
    ] = [
        UserMessage(content="Hello"),
        BaseMessageParam(role="user", content="Hello"),
        BaseMessageParam(role="user", content=[TextPart(type="text", text="Hello")]),
        BaseMessageParam(role="assistant", content="Hello"),
        BaseMessageParam(role="system", content="Hello"),
        BaseMessageParam(role="tool", content="Hello"),
        AssistantMessage(
            content="Hello", tool_calls=Unset(), prefix=False, role="assistant"
        ),
        SystemMessage(content="Hello", role="system"),
        ToolMessage(content="Hello", tool_call_id=Unset(), name=Unset(), role="tool"),
        BaseMessageParam(
            role="user",
            content=[
                TextPart(type="text", text="Hello"),
                ToolResultPart(
                    type="tool_result", id="tool_id", content="result", name="tool_name"
                ),
                ImagePart(
                    type="image", media_type="image/jpeg", image=b"image", detail="auto"
                ),
                ToolCallPart(type="tool_call", name="tool_name", args={"arg": "val"}),
                ImageURLPart(
                    type="image_url", url="http://example.com/img", detail="ignored"
                ),
            ],
        ),
    ]
    converted_message_params = convert_message_params(message_params)
    assert converted_message_params == [
        UserMessage(content="Hello", role="user"),
        UserMessage(content="Hello", role="user"),
        UserMessage(content=[TextChunk(text="Hello", TYPE="text")], role="user"),
        AssistantMessage(
            content="Hello", tool_calls=Unset(), prefix=False, role="assistant"
        ),
        SystemMessage(content="Hello", role="system"),
        ToolMessage(content="Hello", tool_call_id=Unset(), name=Unset(), role="tool"),
        AssistantMessage(
            content="Hello", tool_calls=Unset(), prefix=False, role="assistant"
        ),
        SystemMessage(content="Hello", role="system"),
        ToolMessage(content="Hello", tool_call_id=Unset(), name=Unset(), role="tool"),
        UserMessage(
            content=[
                TextChunk(text="Hello", TYPE="text"),
            ],
            role="user",
        ),
        ToolMessage(
            content="result", tool_call_id="tool_id", name="tool_name", role="tool"
        ),
        AssistantMessage(
            content=[
                ImageURLChunk(
                    image_url=ImageURL(
                        url="data:image/jpeg;base64,aW1hZ2U=", detail="auto"
                    )
                )
            ],
            tool_calls=[
                ToolCall(
                    function=FunctionCall(name="tool_name", arguments={"arg": "val"}),
                    id=None,
                    type="function",
                )
            ],
            prefix=False,
            role="assistant",
        ),
        UserMessage(
            content=[
                ImageURLChunk(image_url="http://example.com/img", TYPE="image_url")
            ],
            role="user",
        ),
    ]

    with pytest.raises(
        ValueError,
        match="Mistral currently only supports text and image parts. Part provided: audio",
    ):
        convert_message_params(
            [
                BaseMessageParam(
                    role="user",
                    content=[
                        AudioPart(
                            type="audio",
                            media_type="audio/wav",
                            audio=b"audio",
                        )
                    ],
                ),
            ]
        )

    with pytest.raises(
        ValueError,
        match="Invalid role: invalid_role",
    ):
        convert_message_params(
            [
                BaseMessageParam(role="invalid_role", content="Hello"),
            ]
        )

    with pytest.raises(
        ValueError,
        match="Unsupported image media type: image/svg."
        " Mistral currently only supports JPEG, PNG, GIF, and WebP images.",
    ):
        convert_message_params(
            [
                BaseMessageParam(
                    role="user",
                    content=[
                        ImagePart(
                            type="image",
                            media_type="image/svg",
                            image=b"image",
                            detail="auto",
                        )
                    ],
                )
            ]
        )


def test_tool_call_no_content() -> None:
    """Tests conversion of a tool_call part when there is no preceding content."""
    message = BaseMessageParam(
        role="user",
        content=[
            ToolCallPart(
                type="tool_call", name="my_tool", args={"param": "value"}, id="tc123"
            )
        ],
    )
    result = convert_message_params([message])
    expected = AssistantMessage(
        content=None,
        tool_calls=[
            ToolCall(
                function=FunctionCall(name="my_tool", arguments={"param": "value"}),
                id="tc123",
                type="function",
            )
        ],
        prefix=False,
        role="assistant",
    )
    assert result == [expected]
