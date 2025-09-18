from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    FinishReason,
    Text,
    ToolCall,
    ToolOutput,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-0",
        "params": {},
        "finish_reason": FinishReason.END_TURN,
        "messages": [
            UserMessage(
                content=[
                    Text(
                        text="Please retrieve the secrets associated with each of these passwords: mellon,radiance"
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="I'll retrieve the secrets for both passwords you provided."
                    ),
                    ToolCall(
                        id="toolu_01CeTQJNTjiT4HL9tmJDNmzz",
                        name="secret_retrieval_tool",
                        args='{"password": "mellon"}',
                    ),
                    ToolCall(
                        id="toolu_012VGQd2jGxW2itWj5Th7UUg",
                        name="secret_retrieval_tool",
                        args='{"password": "radiance"}',
                    ),
                ]
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="toolu_01CeTQJNTjiT4HL9tmJDNmzz",
                        name="secret_retrieval_tool",
                        value="Welcome to Moria!",
                    ),
                    ToolOutput(
                        id="toolu_012VGQd2jGxW2itWj5Th7UUg",
                        name="secret_retrieval_tool",
                        value="Life before Death",
                    ),
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
Here are the secrets retrieved for each password:

- **Password "mellon"**: "Welcome to Moria!"
- **Password "radiance"**: "Life before Death"\
"""
                    )
                ]
            ),
        ],
        "format_type": None,
    }
)
async_snapshot = snapshot(
    {
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-0",
        "params": {},
        "finish_reason": FinishReason.END_TURN,
        "messages": [
            UserMessage(
                content=[
                    Text(
                        text="Please retrieve the secrets associated with each of these passwords: mellon,radiance"
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="I'll retrieve the secrets for both passwords you provided."
                    ),
                    ToolCall(
                        id="toolu_015wEY9dTFpeTkRYRQzVbgkb",
                        name="secret_retrieval_tool",
                        args='{"password": "mellon"}',
                    ),
                    ToolCall(
                        id="toolu_01TQZgfPZfyj2BLoWfeQsDgm",
                        name="secret_retrieval_tool",
                        args='{"password": "radiance"}',
                    ),
                ]
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="toolu_015wEY9dTFpeTkRYRQzVbgkb",
                        name="secret_retrieval_tool",
                        value="Welcome to Moria!",
                    ),
                    ToolOutput(
                        id="toolu_01TQZgfPZfyj2BLoWfeQsDgm",
                        name="secret_retrieval_tool",
                        value="Life before Death",
                    ),
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
Here are the secrets retrieved for each password:

- Password "mellon": **Welcome to Moria!**
- Password "radiance": **Life before Death**\
"""
                    )
                ]
            ),
        ],
        "format_type": None,
    }
)
stream_snapshot = snapshot(
    {
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-0",
        "finish_reason": FinishReason.END_TURN,
        "messages": [
            UserMessage(
                content=[
                    Text(
                        text="Please retrieve the secrets associated with each of these passwords: mellon,radiance"
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="I'll retrieve the secrets for both passwords you provided."
                    ),
                    ToolCall(
                        id="toolu_01TPySBmFWpXZVQc5V6Us51W",
                        name="secret_retrieval_tool",
                        args='{"password": "mellon"}',
                    ),
                    ToolCall(
                        id="toolu_01FKGEfPZwGRuHzEUxWuS1bp",
                        name="secret_retrieval_tool",
                        args='{"password": "radiance"}',
                    ),
                ]
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="toolu_01TPySBmFWpXZVQc5V6Us51W",
                        name="secret_retrieval_tool",
                        value="Welcome to Moria!",
                    ),
                    ToolOutput(
                        id="toolu_01FKGEfPZwGRuHzEUxWuS1bp",
                        name="secret_retrieval_tool",
                        value="Life before Death",
                    ),
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
Here are the secrets retrieved for each password:

- **Password "mellon"**: Welcome to Moria!
- **Password "radiance"**: Life before Death\
"""
                    )
                ]
            ),
        ],
        "format_type": None,
        "n_chunks": 6,
    }
)
async_stream_snapshot = snapshot(
    {
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-0",
        "finish_reason": FinishReason.END_TURN,
        "messages": [
            UserMessage(
                content=[
                    Text(
                        text="Please retrieve the secrets associated with each of these passwords: mellon,radiance"
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="I'll retrieve the secrets for both passwords you provided."
                    ),
                    ToolCall(
                        id="toolu_01Gvz4bHysNVipHuht4PfmXV",
                        name="secret_retrieval_tool",
                        args='{"password": "mellon"}',
                    ),
                    ToolCall(
                        id="toolu_0143zdh9UY7iBMrEvEh9PaP8",
                        name="secret_retrieval_tool",
                        args='{"password": "radiance"}',
                    ),
                ]
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="toolu_01Gvz4bHysNVipHuht4PfmXV",
                        name="secret_retrieval_tool",
                        value="Welcome to Moria!",
                    ),
                    ToolOutput(
                        id="toolu_0143zdh9UY7iBMrEvEh9PaP8",
                        name="secret_retrieval_tool",
                        value="Life before Death",
                    ),
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
Here are the secrets retrieved for each password:

- Password "mellon": **Welcome to Moria!**
- Password "radiance": **Life before Death**\
"""
                    )
                ]
            ),
        ],
        "format_type": None,
        "n_chunks": 6,
    }
)
