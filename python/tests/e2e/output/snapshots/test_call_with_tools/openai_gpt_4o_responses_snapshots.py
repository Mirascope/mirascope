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
                "provider_tool_usage": None,
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
                            id="call_QSN7tSAfBLgrTP3cvjbf7kTZ",
                            name="secret_retrieval_tool",
                            args='{"password":"mellon"}',
                        ),
                        ToolCall(
                            id="call_nZTyOck74QejXCmecXxhMUly",
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
                            "call_id": "call_QSN7tSAfBLgrTP3cvjbf7kTZ",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_028350e31aaf0a710069689afbffb08196a20c6cc653b43055",
                            "status": "completed",
                        },
                        {
                            "arguments": '{"password":"radiance"}',
                            "call_id": "call_nZTyOck74QejXCmecXxhMUly",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_028350e31aaf0a710069689afc1b148196a52c957be576462f",
                            "status": "completed",
                        },
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_QSN7tSAfBLgrTP3cvjbf7kTZ",
                            name="secret_retrieval_tool",
                            result="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="call_nZTyOck74QejXCmecXxhMUly",
                            name="secret_retrieval_tool",
                            result="Life before Death",
                        ),
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Here are the secrets associated with the passwords:

- **mellon:** Welcome to Moria!
- **radiance:** Life before Death\
"""
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:responses",
                    provider_model_name="gpt-4o:responses",
                    raw_message=[
                        {
                            "id": "msg_028350e31aaf0a710069689afce0c48196945204ab94a5df55",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
Here are the secrets associated with the passwords:

- **mellon:** Welcome to Moria!
- **radiance:** Life before Death\
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
                    "strict": None,
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
                "provider_tool_usage": None,
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
                            id="call_uj2BmjGnWhsBAOpIAuAu6d5k",
                            name="secret_retrieval_tool",
                            args='{"password":"mellon"}',
                        ),
                        ToolCall(
                            id="call_z5VXOQKNUG60zWVODYsibWMe",
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
                            "call_id": "call_uj2BmjGnWhsBAOpIAuAu6d5k",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_010c7d30f06da8d20069689b1c3788819480b4e6e7376b165e",
                            "status": "completed",
                        },
                        {
                            "arguments": '{"password":"radiance"}',
                            "call_id": "call_z5VXOQKNUG60zWVODYsibWMe",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_010c7d30f06da8d20069689b1c620081949255a245b7a02342",
                            "status": "completed",
                        },
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_uj2BmjGnWhsBAOpIAuAu6d5k",
                            name="secret_retrieval_tool",
                            result="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="call_z5VXOQKNUG60zWVODYsibWMe",
                            name="secret_retrieval_tool",
                            result="Life before Death",
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
                            "id": "msg_010c7d30f06da8d20069689b1d0b408194b6f1877d7bfd0a52",
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
                    "strict": None,
                }
            ],
        }
    }
)
stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "openai",
            "model_id": "openai/gpt-4o:responses",
            "provider_model_name": "gpt-4o:responses",
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
                            id="call_X6173PYkiubC8YJRPzr8osHX",
                            name="secret_retrieval_tool",
                            args='{"password":"mellon"}',
                        ),
                        ToolCall(
                            id="call_OiUVT2dz7nh3PHrEPGnvLPyi",
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
                            "call_id": "call_X6173PYkiubC8YJRPzr8osHX",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_087fd66e6fa25afd0069689b33ab908193943bbfb9aea1ff4c",
                            "status": "completed",
                        },
                        {
                            "arguments": '{"password":"radiance"}',
                            "call_id": "call_OiUVT2dz7nh3PHrEPGnvLPyi",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_087fd66e6fa25afd0069689b33c1288193970a49066a9cda57",
                            "status": "completed",
                        },
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_X6173PYkiubC8YJRPzr8osHX",
                            name="secret_retrieval_tool",
                            result="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="call_OiUVT2dz7nh3PHrEPGnvLPyi",
                            name="secret_retrieval_tool",
                            result="Life before Death",
                        ),
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Here are the secrets associated with the passwords:

- **mellon:** Welcome to Moria!
- **radiance:** Life before Death\
"""
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:responses",
                    provider_model_name="gpt-4o:responses",
                    raw_message=[
                        {
                            "id": "msg_087fd66e6fa25afd0069689b346fb8819394caa5e641b11cc3",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
Here are the secrets associated with the passwords:

- **mellon:** Welcome to Moria!
- **radiance:** Life before Death\
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
                    "strict": None,
                }
            ],
            "usage": {
                "input_tokens": 136,
                "output_tokens": 30,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "None",
                "total_tokens": 166,
            },
            "n_chunks": 30,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "openai",
            "model_id": "openai/gpt-4o:responses",
            "provider_model_name": "gpt-4o:responses",
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
                            id="call_Mt0FqdmvVvd3mTf0F8W4P2RY",
                            name="secret_retrieval_tool",
                            args='{"password":"mellon"}',
                        ),
                        ToolCall(
                            id="call_59gFXjMPHdM2VDqtYbGOQdVc",
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
                            "call_id": "call_Mt0FqdmvVvd3mTf0F8W4P2RY",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_0173e3e44c05ae890069689b5a9dec81938ec07c66db748acd",
                            "status": "completed",
                        },
                        {
                            "arguments": '{"password":"radiance"}',
                            "call_id": "call_59gFXjMPHdM2VDqtYbGOQdVc",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_0173e3e44c05ae890069689b5ab43c8193abec78581d4df239",
                            "status": "completed",
                        },
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_Mt0FqdmvVvd3mTf0F8W4P2RY",
                            name="secret_retrieval_tool",
                            result="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="call_59gFXjMPHdM2VDqtYbGOQdVc",
                            name="secret_retrieval_tool",
                            result="Life before Death",
                        ),
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
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
                            "id": "msg_0173e3e44c05ae890069689b5b69f8819385a0a2adfc883d6e",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
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
                    "strict": None,
                }
            ],
            "usage": {
                "input_tokens": 136,
                "output_tokens": 23,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "None",
                "total_tokens": 159,
            },
            "n_chunks": 23,
        }
    }
)
