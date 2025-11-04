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
        "response": {
            "provider": "azure-openai:completions",
            "model_id": "gpt-4o-mini",
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
                            id="call_52zLtnGOqmPxewMwWssmqug3",
                            name="secret_retrieval_tool",
                            args='{"password": "mellon"}',
                        ),
                        ToolCall(
                            id="call_5XEcx0xRpnYi6VgaMJ38xBTd",
                            name="secret_retrieval_tool",
                            args='{"password": "radiance"}',
                        ),
                    ],
                    provider="azure-openai:completions",
                    model_id="gpt-4o-mini",
                    raw_message={
                        "role": "assistant",
                        "annotations": [],
                        "tool_calls": [
                            {
                                "id": "call_52zLtnGOqmPxewMwWssmqug3",
                                "function": {
                                    "arguments": '{"password": "mellon"}',
                                    "name": "secret_retrieval_tool",
                                },
                                "type": "function",
                            },
                            {
                                "id": "call_5XEcx0xRpnYi6VgaMJ38xBTd",
                                "function": {
                                    "arguments": '{"password": "radiance"}',
                                    "name": "secret_retrieval_tool",
                                },
                                "type": "function",
                            },
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_52zLtnGOqmPxewMwWssmqug3",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="call_5XEcx0xRpnYi6VgaMJ38xBTd",
                            name="secret_retrieval_tool",
                            value="Life before Death",
                        ),
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
The secrets retrieved are as follows:

- For the password **mellon**: "Welcome to Moria!"
- For the password **radiance**: "Life before Death"\
"""
                        )
                    ],
                    provider="azure-openai:completions",
                    model_id="gpt-4o-mini",
                    raw_message={
                        "content": """\
The secrets retrieved are as follows:

- For the password **mellon**: "Welcome to Moria!"
- For the password **radiance**: "Life before Death"\
""",
                        "role": "assistant",
                        "annotations": [],
                    },
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
    }
)
async_snapshot = snapshot(
    {
        "response": {
            "provider": "azure-openai:completions",
            "model_id": "gpt-4o-mini",
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
                            id="call_cRni6nXvReg1170V2zEXKz8l",
                            name="secret_retrieval_tool",
                            args='{"password": "mellon"}',
                        ),
                        ToolCall(
                            id="call_Bynldl9qZBrkplLQVzsTYcsE",
                            name="secret_retrieval_tool",
                            args='{"password": "radiance"}',
                        ),
                    ],
                    provider="azure-openai:completions",
                    model_id="gpt-4o-mini",
                    raw_message={
                        "role": "assistant",
                        "annotations": [],
                        "tool_calls": [
                            {
                                "id": "call_cRni6nXvReg1170V2zEXKz8l",
                                "function": {
                                    "arguments": '{"password": "mellon"}',
                                    "name": "secret_retrieval_tool",
                                },
                                "type": "function",
                            },
                            {
                                "id": "call_Bynldl9qZBrkplLQVzsTYcsE",
                                "function": {
                                    "arguments": '{"password": "radiance"}',
                                    "name": "secret_retrieval_tool",
                                },
                                "type": "function",
                            },
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_cRni6nXvReg1170V2zEXKz8l",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="call_Bynldl9qZBrkplLQVzsTYcsE",
                            name="secret_retrieval_tool",
                            value="Life before Death",
                        ),
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
The secrets retrieved are as follows:

- For the password **"mellon"**: **"Welcome to Moria!"**
- For the password **"radiance"**: **"Life before Death"**\
"""
                        )
                    ],
                    provider="azure-openai:completions",
                    model_id="gpt-4o-mini",
                    raw_message={
                        "content": """\
The secrets retrieved are as follows:

- For the password **"mellon"**: **"Welcome to Moria!"**
- For the password **"radiance"**: **"Life before Death"**\
""",
                        "role": "assistant",
                        "annotations": [],
                    },
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
    }
)
stream_snapshot = snapshot(
    {
        "response": {
            "provider": "azure-openai:completions",
            "model_id": "gpt-4o-mini",
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
                            id="call_9QsvKeFs2Hh2LOXUcTopzGYt",
                            name="secret_retrieval_tool",
                            args='{"password": "mellon"}',
                        ),
                        ToolCall(
                            id="call_hYkffisled3NgODdvqa1tZAv",
                            name="secret_retrieval_tool",
                            args='{"password": "radiance"}',
                        ),
                    ],
                    provider="azure-openai:completions",
                    model_id="gpt-4o-mini",
                    raw_message=None,
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_9QsvKeFs2Hh2LOXUcTopzGYt",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="call_hYkffisled3NgODdvqa1tZAv",
                            name="secret_retrieval_tool",
                            value="Life before Death",
                        ),
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
The secrets retrieved are as follows:

- For the password "mellon": **Welcome to Moria!**
- For the password "radiance": **Life before Death**\
"""
                        )
                    ],
                    provider="azure-openai:completions",
                    model_id="gpt-4o-mini",
                    raw_message=None,
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
            "n_chunks": 38,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider": "azure-openai:completions",
            "model_id": "gpt-4o-mini",
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
                            id="call_cqx109lBFdovuPalf7A6miqP",
                            name="secret_retrieval_tool",
                            args='{"password": "mellon"}',
                        ),
                        ToolCall(
                            id="call_B6dQIS7NWqiTuYbRs2oz5IP6",
                            name="secret_retrieval_tool",
                            args='{"password": "radiance"}',
                        ),
                    ],
                    provider="azure-openai:completions",
                    model_id="gpt-4o-mini",
                    raw_message=None,
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_cqx109lBFdovuPalf7A6miqP",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="call_B6dQIS7NWqiTuYbRs2oz5IP6",
                            name="secret_retrieval_tool",
                            value="Life before Death",
                        ),
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
The secrets associated with the provided passwords are as follows:

- For the password "mellon": **Welcome to Moria!**
- For the password "radiance": **Life before Death**\
"""
                        )
                    ],
                    provider="azure-openai:completions",
                    model_id="gpt-4o-mini",
                    raw_message=None,
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
            "n_chunks": 42,
        }
    }
)
