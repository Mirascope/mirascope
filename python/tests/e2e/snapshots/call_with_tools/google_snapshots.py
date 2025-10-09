from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    SystemMessage,
    Text,
    ToolCall,
    ToolOutput,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "provider": "google",
        "model_id": "gemini-2.5-flash",
        "params": {},
        "finish_reason": None,
        "messages": [
            SystemMessage(content=Text(text="Use parallel tool calling.")),
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
                ],
                provider="google",
                model_id="gemini-2.5-flash",
                raw_content=[],
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
                        text="""\
Welcome to Moria!
Life before Death\
"""
                    )
                ],
                provider="google",
                model_id="gemini-2.5-flash",
                raw_content=[],
            ),
        ],
        "format": None,
        "tools": [
            {
                "name": "secret_retrieval_tool",
                "description": "A tool that requires a password to retrieve a secret.",
                "parameters": """\
{
  "properties": {
    "password": {
      "title": "Password",
      "type": "string"
    }
  },
  "required": [
    "password"
  ],
  "additionalProperties": false,
  "defs": null
}\
""",
                "strict": False,
            }
        ],
    }
)
async_snapshot = snapshot(
    {
        "provider": "google",
        "model_id": "gemini-2.5-flash",
        "params": {},
        "finish_reason": None,
        "messages": [
            SystemMessage(content=Text(text="Use parallel tool calling.")),
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
                ],
                provider="google",
                model_id="gemini-2.5-flash",
                raw_content=[],
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
                        text="""\
I've retrieved the secrets for the provided passwords:

For the password "mellon", the secret is "Welcome to Moria!"
For the password "radiance", the secret is "Life before Death"\
"""
                    )
                ],
                provider="google",
                model_id="gemini-2.5-flash",
                raw_content=[],
            ),
        ],
        "format": None,
        "tools": [
            {
                "name": "secret_retrieval_tool",
                "description": "A tool that requires a password to retrieve a secret.",
                "parameters": """\
{
  "properties": {
    "password": {
      "title": "Password",
      "type": "string"
    }
  },
  "required": [
    "password"
  ],
  "additionalProperties": false,
  "defs": null
}\
""",
                "strict": False,
            }
        ],
    }
)
stream_snapshot = snapshot(
    {
        "provider": "google",
        "model_id": "gemini-2.5-flash",
        "finish_reason": None,
        "messages": [
            SystemMessage(content=Text(text="Use parallel tool calling.")),
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
                ],
                provider="google",
                model_id="gemini-2.5-flash",
                raw_content=[],
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
                        text='I have retrieved the following secrets: "Welcome to Moria!" and "Life before Death".\n'
                    )
                ],
                provider="google",
                model_id="gemini-2.5-flash",
                raw_content=[],
            ),
        ],
        "format": None,
        "tools": [
            {
                "name": "secret_retrieval_tool",
                "description": "A tool that requires a password to retrieve a secret.",
                "parameters": """\
{
  "properties": {
    "password": {
      "title": "Password",
      "type": "string"
    }
  },
  "required": [
    "password"
  ],
  "additionalProperties": false,
  "defs": null
}\
""",
                "strict": False,
            }
        ],
        "n_chunks": 3,
    }
)
async_stream_snapshot = snapshot(
    {
        "provider": "google",
        "model_id": "gemini-2.5-flash",
        "finish_reason": None,
        "messages": [
            SystemMessage(content=Text(text="Use parallel tool calling.")),
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
                ],
                provider="google",
                model_id="gemini-2.5-flash",
                raw_content=[],
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
                        text='I have retrieved the following secrets: "Welcome to Moria!" and "Life before Death".\n'
                    )
                ],
                provider="google",
                model_id="gemini-2.5-flash",
                raw_content=[],
            ),
        ],
        "format": None,
        "tools": [
            {
                "name": "secret_retrieval_tool",
                "description": "A tool that requires a password to retrieve a secret.",
                "parameters": """\
{
  "properties": {
    "password": {
      "title": "Password",
      "type": "string"
    }
  },
  "required": [
    "password"
  ],
  "additionalProperties": false,
  "defs": null
}\
""",
                "strict": False,
            }
        ],
        "n_chunks": 3,
    }
)
without_raw_content_snapshot = snapshot(
    {
        "provider": "google",
        "model_id": "gemini-2.5-flash",
        "params": {},
        "finish_reason": None,
        "messages": [
            SystemMessage(content=Text(text="Use parallel tool calling.")),
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
                ],
                provider="google",
                model_id="gemini-2.5-flash",
                raw_content=[],
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
                        text='I have retrieved the following secrets: "Welcome to Moria!" and "Life before Death".\n'
                    )
                ],
                provider="google",
                model_id="gemini-2.5-flash",
                raw_content=[],
            ),
        ],
        "format": None,
        "tools": [
            {
                "name": "secret_retrieval_tool",
                "description": "A tool that requires a password to retrieve a secret.",
                "parameters": """\
{
  "properties": {
    "password": {
      "title": "Password",
      "type": "string"
    }
  },
  "required": [
    "password"
  ],
  "additionalProperties": false,
  "defs": null
}\
""",
                "strict": False,
            }
        ],
    }
)
