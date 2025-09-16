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
        "provider": "google",
        "model_id": "gemini-2.0-flash",
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
                    ToolCall(
                        id="<unknown>",
                        name="secret_retrieval_tool",
                        args='{"password": "mellon"}',
                    ),
                    ToolCall(
                        id="<unknown>",
                        name="secret_retrieval_tool",
                        args='{"password": "radiance"}',
                    ),
                ]
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="<unknown>",
                        name="secret_retrieval_tool",
                        value="Welcome to Moria!",
                    ),
                    ToolOutput(
                        id="<unknown>",
                        name="secret_retrieval_tool",
                        value="Life before Death",
                    ),
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="The secret for the password 'mellon' is 'Welcome to Moria!' and the secret for the password 'radiance' is 'Life before Death'.\n"
                    )
                ]
            ),
        ],
    },
)
async_snapshot = snapshot(
    {
        "provider": "google",
        "model_id": "gemini-2.0-flash",
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
                    ToolCall(
                        id="<unknown>",
                        name="secret_retrieval_tool",
                        args='{"password": "mellon"}',
                    ),
                    ToolCall(
                        id="<unknown>",
                        name="secret_retrieval_tool",
                        args='{"password": "radiance"}',
                    ),
                ]
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="<unknown>",
                        name="secret_retrieval_tool",
                        value="Welcome to Moria!",
                    ),
                    ToolOutput(
                        id="<unknown>",
                        name="secret_retrieval_tool",
                        value="Life before Death",
                    ),
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text='The secret for the password "mellon" is "Welcome to Moria!" and the secret for the password "radiance" is "Life before Death".\n'
                    )
                ]
            ),
        ],
    },
)
stream_snapshot = snapshot(
    {
        "provider": "google",
        "model_id": "gemini-2.0-flash",
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
                    ToolCall(
                        id="<unknown>",
                        name="secret_retrieval_tool",
                        args='{"password": "mellon"}',
                    ),
                    ToolCall(
                        id="<unknown>",
                        name="secret_retrieval_tool",
                        args='{"password": "radiance"}',
                    ),
                ]
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="<unknown>",
                        name="secret_retrieval_tool",
                        value="Welcome to Moria!",
                    ),
                    ToolOutput(
                        id="<unknown>",
                        name="secret_retrieval_tool",
                        value="Life before Death",
                    ),
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="The secret for the password 'mellon' is 'Welcome to Moria!' and the secret for the password 'radiance' is 'Life before Death'.\n"
                    )
                ]
            ),
        ],
        "n_chunks": 5,
    },
)
async_stream_snapshot = snapshot(
    {
        "provider": "google",
        "model_id": "gemini-2.0-flash",
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
                    ToolCall(
                        id="<unknown>",
                        name="secret_retrieval_tool",
                        args='{"password": "mellon"}',
                    ),
                    ToolCall(
                        id="<unknown>",
                        name="secret_retrieval_tool",
                        args='{"password": "radiance"}',
                    ),
                ]
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="<unknown>",
                        name="secret_retrieval_tool",
                        value="Welcome to Moria!",
                    ),
                    ToolOutput(
                        id="<unknown>",
                        name="secret_retrieval_tool",
                        value="Life before Death",
                    ),
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text='The secret for the password "mellon" is "Welcome to Moria!" and the secret for the password "radiance" is "Life before Death".\n'
                    )
                ]
            ),
        ],
        "n_chunks": 5,
    },
)
