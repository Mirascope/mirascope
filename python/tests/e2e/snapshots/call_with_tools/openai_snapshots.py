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
        "provider": "openai",
        "model_id": "gpt-4o",
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
                        id="call_e9676KhayWDvRXCfQ5Y6ouEv",
                        name="secret_retrieval_tool",
                        args='{"password": "mellon"}',
                    ),
                    ToolCall(
                        id="call_EtNjCu91wUlwZThgJys5ly5I",
                        name="secret_retrieval_tool",
                        args='{"password": "radiance"}',
                    ),
                ]
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="call_e9676KhayWDvRXCfQ5Y6ouEv",
                        name="secret_retrieval_tool",
                        value="Welcome to Moria!",
                    ),
                    ToolOutput(
                        id="call_EtNjCu91wUlwZThgJys5ly5I",
                        name="secret_retrieval_tool",
                        value="Life before Death",
                    ),
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
The secrets associated with the passwords are as follows:

- For "mellon": "Welcome to Moria!"
- For "radiance": "Life before Death"\
"""
                    )
                ]
            ),
        ],
    },
)
async_snapshot = snapshot(
    {
        "provider": "openai",
        "model_id": "gpt-4o",
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
                        id="call_upCrDNFw8UdaGdRyY8fqVyYM",
                        name="secret_retrieval_tool",
                        args='{"password": "mellon"}',
                    ),
                    ToolCall(
                        id="call_I00hxdEaZr4CAI1HxETVFzqx",
                        name="secret_retrieval_tool",
                        args='{"password": "radiance"}',
                    ),
                ]
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="call_upCrDNFw8UdaGdRyY8fqVyYM",
                        name="secret_retrieval_tool",
                        value="Welcome to Moria!",
                    ),
                    ToolOutput(
                        id="call_I00hxdEaZr4CAI1HxETVFzqx",
                        name="secret_retrieval_tool",
                        value="Life before Death",
                    ),
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
The secrets associated with the passwords are as follows:

- For the password "mellon": "Welcome to Moria!"
- For the password "radiance": "Life before Death"\
"""
                    )
                ]
            ),
        ],
    },
)
stream_snapshot = snapshot(
    {
        "provider": "openai",
        "model_id": "gpt-4o",
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
                        id="call_6uFnrGhupkVdiog6zEFWZmS6",
                        name="secret_retrieval_tool",
                        args='{"password": "mellon"}',
                    ),
                    ToolCall(
                        id="call_2L3I0nsJHAAuhYEVJsHP2iIu",
                        name="secret_retrieval_tool",
                        args='{"password": "radiance"}',
                    ),
                ]
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="call_6uFnrGhupkVdiog6zEFWZmS6",
                        name="secret_retrieval_tool",
                        value="Welcome to Moria!",
                    ),
                    ToolOutput(
                        id="call_2L3I0nsJHAAuhYEVJsHP2iIu",
                        name="secret_retrieval_tool",
                        value="Life before Death",
                    ),
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
The secrets associated with the provided passwords are:

- For "mellon": Welcome to Moria!
- For "radiance": Life before Death\
"""
                    )
                ]
            ),
        ],
        "n_chunks": 33,
    },
)
async_stream_snapshot = snapshot(
    {
        "provider": "openai",
        "model_id": "gpt-4o",
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
                        id="call_7yIAwnwYflanhxxfzJzmNJZD",
                        name="secret_retrieval_tool",
                        args='{"password": "mellon"}',
                    ),
                    ToolCall(
                        id="call_x3Q6jWGjZqFFllwV6iQfXhQG",
                        name="secret_retrieval_tool",
                        args='{"password": "radiance"}',
                    ),
                ]
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="call_7yIAwnwYflanhxxfzJzmNJZD",
                        name="secret_retrieval_tool",
                        value="Welcome to Moria!",
                    ),
                    ToolOutput(
                        id="call_x3Q6jWGjZqFFllwV6iQfXhQG",
                        name="secret_retrieval_tool",
                        value="Life before Death",
                    ),
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
Here are the secrets associated with the provided passwords:

- Password "mellon": "Welcome to Moria!"
- Password "radiance": "Life before Death"\
"""
                    )
                ]
            ),
        ],
        "n_chunks": 37,
    },
)
