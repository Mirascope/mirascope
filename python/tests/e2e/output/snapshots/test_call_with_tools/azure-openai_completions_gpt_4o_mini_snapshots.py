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
                            id="call_Ogl4xrgYelrGfioRoTJoXCF0",
                            name="secret_retrieval_tool",
                            args='{"password": "mellon"}',
                        ),
                        ToolCall(
                            id="call_J8hE6f1cZ8sJIzw3FCswowSI",
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
                                "id": "call_Ogl4xrgYelrGfioRoTJoXCF0",
                                "function": {
                                    "arguments": '{"password": "mellon"}',
                                    "name": "secret_retrieval_tool",
                                },
                                "type": "function",
                            },
                            {
                                "id": "call_J8hE6f1cZ8sJIzw3FCswowSI",
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
                            id="call_Ogl4xrgYelrGfioRoTJoXCF0",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="call_J8hE6f1cZ8sJIzw3FCswowSI",
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
                            id="call_S8F3EFC1Ao4SMZhW7spIhT5e",
                            name="secret_retrieval_tool",
                            args='{"password": "mellon"}',
                        ),
                        ToolCall(
                            id="call_FFJsWSmK1GQiGvy65uqsd6TF",
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
                                "id": "call_S8F3EFC1Ao4SMZhW7spIhT5e",
                                "function": {
                                    "arguments": '{"password": "mellon"}',
                                    "name": "secret_retrieval_tool",
                                },
                                "type": "function",
                            },
                            {
                                "id": "call_FFJsWSmK1GQiGvy65uqsd6TF",
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
                            id="call_S8F3EFC1Ao4SMZhW7spIhT5e",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="call_FFJsWSmK1GQiGvy65uqsd6TF",
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
                            id="call_GF8LHohCf34vryrD5mTlArH8",
                            name="secret_retrieval_tool",
                            args='{"password": "mellon"}',
                        ),
                        ToolCall(
                            id="call_7KowxRhncpXrPLQpuAMemn0y",
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
                            id="call_GF8LHohCf34vryrD5mTlArH8",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="call_7KowxRhncpXrPLQpuAMemn0y",
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
            "n_chunks": 41,
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
                            id="call_zhhetoCnaZn4MWoAqXek56ng",
                            name="secret_retrieval_tool",
                            args='{"password": "mellon"}',
                        ),
                        ToolCall(
                            id="call_GLvRyVwYmNA4Vauif3CcpRmG",
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
                            id="call_zhhetoCnaZn4MWoAqXek56ng",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="call_GLvRyVwYmNA4Vauif3CcpRmG",
                            name="secret_retrieval_tool",
                            value="Life before Death",
                        ),
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
The secrets associated with each password are as follows:

- For the password **mellon**: "Welcome to Moria!"
- For the password **radiance**: "Life before Death"\
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
