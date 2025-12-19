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
            "provider_id": "openai",
            "model_id": "openai/gpt-4o:responses",
            "provider_model_name": "gpt-4o:responses",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 136,
                "output_tokens": 30,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "ResponseUsage(input_tokens=136, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=30, output_tokens_details=OutputTokensDetails(reasoning_tokens=0), total_tokens=166)",
                "total_tokens": 166,
            },
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
                            id="call_bzXaB1HDWsWy7n6bMrxJzNNa",
                            name="secret_retrieval_tool",
                            args='{"password":"mellon"}',
                        ),
                        ToolCall(
                            id="call_Dd4wvykCr6NttXKxRK0BFH96",
                            name="secret_retrieval_tool",
                            args='{"password":"radiance"}',
                        ),
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:responses",
                    provider_model_name="gpt-4o:responses",
                    raw_message=[
                        {
                            "arguments": '{"password":"mellon"}',
                            "call_id": "call_bzXaB1HDWsWy7n6bMrxJzNNa",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_05020a9191cad7ac0068f966b1446c8190b34b78d6f788eeec",
                            "status": "completed",
                        },
                        {
                            "arguments": '{"password":"radiance"}',
                            "call_id": "call_Dd4wvykCr6NttXKxRK0BFH96",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_05020a9191cad7ac0068f966b16f80819088f6dab6c16c4653",
                            "status": "completed",
                        },
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_bzXaB1HDWsWy7n6bMrxJzNNa",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="call_Dd4wvykCr6NttXKxRK0BFH96",
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

- For password "mellon": Welcome to Moria!
- For password "radiance": Life before Death\
"""
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:responses",
                    provider_model_name="gpt-4o:responses",
                    raw_message=[
                        {
                            "id": "msg_05020a9191cad7ac0068f966b29f2c8190b17e1e76b16eb31c",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
Here are the secrets:

- For password "mellon": Welcome to Moria!
- For password "radiance": Life before Death\
""",
                                    "type": "output_text",
                                    "logprobs": [],
                                }
                            ],
                            "role": "assistant",
                            "status": "completed",
                            "type": "message",
                        }
                    ],
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
            "provider_id": "openai",
            "model_id": "openai/gpt-4o:responses",
            "provider_model_name": "gpt-4o:responses",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 136,
                "output_tokens": 28,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "ResponseUsage(input_tokens=136, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=28, output_tokens_details=OutputTokensDetails(reasoning_tokens=0), total_tokens=164)",
                "total_tokens": 164,
            },
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
                            id="call_MqvcNQ1vcN1deGFjDbYja1zn",
                            name="secret_retrieval_tool",
                            args='{"password":"mellon"}',
                        ),
                        ToolCall(
                            id="call_EqSzc4ybAc3ffmvwzL4rrdkg",
                            name="secret_retrieval_tool",
                            args='{"password":"radiance"}',
                        ),
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:responses",
                    provider_model_name="gpt-4o:responses",
                    raw_message=[
                        {
                            "arguments": '{"password":"mellon"}',
                            "call_id": "call_MqvcNQ1vcN1deGFjDbYja1zn",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_019289b83a1261ca0068f966b5b4848195a23104951bd770cd",
                            "status": "completed",
                        },
                        {
                            "arguments": '{"password":"radiance"}',
                            "call_id": "call_EqSzc4ybAc3ffmvwzL4rrdkg",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_019289b83a1261ca0068f966b6cab881958f1e435d61dcbd63",
                            "status": "completed",
                        },
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_MqvcNQ1vcN1deGFjDbYja1zn",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="call_EqSzc4ybAc3ffmvwzL4rrdkg",
                            name="secret_retrieval_tool",
                            value="Life before Death",
                        ),
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
The secrets for the passwords are:

- "mellon": Welcome to Moria!
- "radiance": Life before Death\
"""
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:responses",
                    provider_model_name="gpt-4o:responses",
                    raw_message=[
                        {
                            "id": "msg_019289b83a1261ca0068f966b87fa88195986a24eb8e39c47f",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
The secrets for the passwords are:

- "mellon": Welcome to Moria!
- "radiance": Life before Death\
""",
                                    "type": "output_text",
                                    "logprobs": [],
                                }
                            ],
                            "role": "assistant",
                            "status": "completed",
                            "type": "message",
                        }
                    ],
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
            "provider_id": "openai",
            "provider_model_name": "gpt-4o:responses",
            "model_id": "openai/gpt-4o:responses",
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
                            id="call_sKC7OABqf2A2PTLCm0CLeRWV",
                            name="secret_retrieval_tool",
                            args='{"password":"mellon"}',
                        ),
                        ToolCall(
                            id="call_OdR3s3xop0vtgkDyWRMLafuH",
                            name="secret_retrieval_tool",
                            args='{"password":"radiance"}',
                        ),
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:responses",
                    provider_model_name="gpt-4o:responses",
                    raw_message=[
                        {
                            "arguments": '{"password":"mellon"}',
                            "call_id": "call_sKC7OABqf2A2PTLCm0CLeRWV",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_0c3b09d20eedf2d30068f966bad8b88190af96d232f504ef1f",
                            "status": "completed",
                        },
                        {
                            "arguments": '{"password":"radiance"}',
                            "call_id": "call_OdR3s3xop0vtgkDyWRMLafuH",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_0c3b09d20eedf2d30068f966bafd288190a9045fdc554de6d5",
                            "status": "completed",
                        },
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_sKC7OABqf2A2PTLCm0CLeRWV",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="call_OdR3s3xop0vtgkDyWRMLafuH",
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
                    provider_id="openai",
                    model_id="openai/gpt-4o:responses",
                    provider_model_name="gpt-4o:responses",
                    raw_message=[
                        {
                            "id": "msg_0c3b09d20eedf2d30068f966bc0afc81909ccc6a383749530f",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
Here are the secrets associated with each password:

- **mellon**: Welcome to Moria!
- **radiance**: Life before Death\
""",
                                    "type": "output_text",
                                    "logprobs": [],
                                }
                            ],
                            "role": "assistant",
                            "status": "completed",
                            "type": "message",
                        }
                    ],
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
            "usage": {
                "input_tokens": 136,
                "output_tokens": 32,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 168,
            },
            "n_chunks": 32,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "openai",
            "provider_model_name": "gpt-4o:responses",
            "model_id": "openai/gpt-4o:responses",
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
                            id="call_4l0LYGshWqEvG3DEq9hY8PKo",
                            name="secret_retrieval_tool",
                            args='{"password":"mellon"}',
                        ),
                        ToolCall(
                            id="call_hG4DmWUygGVSGrsCV3zwCiZU",
                            name="secret_retrieval_tool",
                            args='{"password":"radiance"}',
                        ),
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:responses",
                    provider_model_name="gpt-4o:responses",
                    raw_message=[
                        {
                            "arguments": '{"password":"mellon"}',
                            "call_id": "call_4l0LYGshWqEvG3DEq9hY8PKo",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_03573e2d83248b7c0068f966be406c8194b614ddb98cfce9fe",
                            "status": "completed",
                        },
                        {
                            "arguments": '{"password":"radiance"}',
                            "call_id": "call_hG4DmWUygGVSGrsCV3zwCiZU",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_03573e2d83248b7c0068f966be7e148194868e9cbe2160c4ec",
                            "status": "completed",
                        },
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_4l0LYGshWqEvG3DEq9hY8PKo",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="call_hG4DmWUygGVSGrsCV3zwCiZU",
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

- Password "mellon": Welcome to Moria!
- Password "radiance": Life before Death\
"""
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:responses",
                    provider_model_name="gpt-4o:responses",
                    raw_message=[
                        {
                            "id": "msg_03573e2d83248b7c0068f966bf89d081949ff26b5e39341c99",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
Here are the secrets:

- Password "mellon": Welcome to Moria!
- Password "radiance": Life before Death\
""",
                                    "type": "output_text",
                                    "logprobs": [],
                                }
                            ],
                            "role": "assistant",
                            "status": "completed",
                            "type": "message",
                        }
                    ],
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
            "usage": {
                "input_tokens": 136,
                "output_tokens": 28,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 164,
            },
            "n_chunks": 28,
        }
    }
)
