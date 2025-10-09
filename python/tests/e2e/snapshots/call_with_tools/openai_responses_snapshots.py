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
        "provider": "openai:responses",
        "model_id": "gpt-4o",
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
                        id="call_7cAklJuLUxQkgoFAqmZ2peya",
                        name="secret_retrieval_tool",
                        args='{"password":"mellon"}',
                    ),
                    ToolCall(
                        id="call_JgZ8uwtmQeASH4VEEGdXe6B0",
                        name="secret_retrieval_tool",
                        args='{"password":"radiance"}',
                    ),
                ],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="call_7cAklJuLUxQkgoFAqmZ2peya",
                        name="secret_retrieval_tool",
                        value="Welcome to Moria!",
                    ),
                    ToolOutput(
                        id="call_JgZ8uwtmQeASH4VEEGdXe6B0",
                        name="secret_retrieval_tool",
                        value="Life before Death",
                    ),
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
Here are the secrets associated with each password:

- **mellon**: Welcome to Moria!
- **radiance**: Life before Death\
"""
                    )
                ],
                provider="openai:responses",
                model_id="gpt-4o",
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
        "provider": "openai:responses",
        "model_id": "gpt-4o",
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
                        id="call_ZTFw1ftgYUpehUw5tMZ9KeX3",
                        name="secret_retrieval_tool",
                        args='{"password":"mellon"}',
                    ),
                    ToolCall(
                        id="call_5JTY0cbL1VaMtYlj4pYmTIzA",
                        name="secret_retrieval_tool",
                        args='{"password":"radiance"}',
                    ),
                ],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="call_ZTFw1ftgYUpehUw5tMZ9KeX3",
                        name="secret_retrieval_tool",
                        value="Welcome to Moria!",
                    ),
                    ToolOutput(
                        id="call_5JTY0cbL1VaMtYlj4pYmTIzA",
                        name="secret_retrieval_tool",
                        value="Life before Death",
                    ),
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
Here are the secrets associated with the passwords:

- Password `"mellon"`: Welcome to Moria!
- Password `"radiance"`: Life before Death\
"""
                    )
                ],
                provider="openai:responses",
                model_id="gpt-4o",
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
        "provider": "openai:responses",
        "model_id": "gpt-4o",
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
                        id="call_LctPBs1R2tGhln7TBf1ZEX3C",
                        name="secret_retrieval_tool",
                        args='{"password":"mellon"}',
                    ),
                    ToolCall(
                        id="call_UbMbQSvY6TYya8s058rrMZyv",
                        name="secret_retrieval_tool",
                        args='{"password":"radiance"}',
                    ),
                ],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="call_LctPBs1R2tGhln7TBf1ZEX3C",
                        name="secret_retrieval_tool",
                        value="Welcome to Moria!",
                    ),
                    ToolOutput(
                        id="call_UbMbQSvY6TYya8s058rrMZyv",
                        name="secret_retrieval_tool",
                        value="Life before Death",
                    ),
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
Here are the secrets:

- **mellon**: Welcome to Moria!
- **radiance**: Life before Death\
"""
                    )
                ],
                provider="openai:responses",
                model_id="gpt-4o",
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
        "n_chunks": 28,
    }
)
async_stream_snapshot = snapshot(
    {
        "provider": "openai:responses",
        "model_id": "gpt-4o",
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
                        id="call_afDFm1ADaw5j77gb2E1SRjEh",
                        name="secret_retrieval_tool",
                        args='{"password":"mellon"}',
                    ),
                    ToolCall(
                        id="call_i17I4phd6PznExMGe5BjiVef",
                        name="secret_retrieval_tool",
                        args='{"password":"radiance"}',
                    ),
                ],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="call_afDFm1ADaw5j77gb2E1SRjEh",
                        name="secret_retrieval_tool",
                        value="Welcome to Moria!",
                    ),
                    ToolOutput(
                        id="call_i17I4phd6PznExMGe5BjiVef",
                        name="secret_retrieval_tool",
                        value="Life before Death",
                    ),
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
Here are the secrets for the provided passwords:

- **mellon**: Welcome to Moria!
- **radiance**: Life before Death\
"""
                    )
                ],
                provider="openai:responses",
                model_id="gpt-4o",
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
        "n_chunks": 32,
    }
)
