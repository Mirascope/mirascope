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
            "model_id": "openai/gpt-4o:completions",
            "provider_model_name": "gpt-4o:completions",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 149,
                "output_tokens": 36,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "CompletionUsage(completion_tokens=36, prompt_tokens=149, total_tokens=185, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=0, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0))",
                "total_tokens": 185,
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
                            id="call_kORjJVpmh91BGUtfuEyWTNHq",
                            name="secret_retrieval_tool",
                            args='{"password": "mellon"}',
                        ),
                        ToolCall(
                            id="call_rwWftDkV0SjAa03c30QMCbHv",
                            name="secret_retrieval_tool",
                            args='{"password": "radiance"}',
                        ),
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:completions",
                    provider_model_name="gpt-4o:completions",
                    raw_message={
                        "role": "assistant",
                        "annotations": [],
                        "tool_calls": [
                            {
                                "id": "call_kORjJVpmh91BGUtfuEyWTNHq",
                                "function": {
                                    "arguments": '{"password": "mellon"}',
                                    "name": "secret_retrieval_tool",
                                },
                                "type": "function",
                            },
                            {
                                "id": "call_rwWftDkV0SjAa03c30QMCbHv",
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
                            id="call_kORjJVpmh91BGUtfuEyWTNHq",
                            name="secret_retrieval_tool",
                            result="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="call_rwWftDkV0SjAa03c30QMCbHv",
                            name="secret_retrieval_tool",
                            result="Life before Death",
                        ),
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Here are the secrets associated with the passwords you provided:

- For "mellon": "Welcome to Moria!"
- For "radiance": "Life before Death"\
"""
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:completions",
                    provider_model_name="gpt-4o:completions",
                    raw_message={
                        "content": """\
Here are the secrets associated with the passwords you provided:

- For "mellon": "Welcome to Moria!"
- For "radiance": "Life before Death"\
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
            "model_id": "openai/gpt-4o:completions",
            "provider_model_name": "gpt-4o:completions",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 149,
                "output_tokens": 32,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "CompletionUsage(completion_tokens=32, prompt_tokens=149, total_tokens=181, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=0, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0))",
                "total_tokens": 181,
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
                            id="call_eTrqJEDnTlTGliM458pkKaaQ",
                            name="secret_retrieval_tool",
                            args='{"password": "mellon"}',
                        ),
                        ToolCall(
                            id="call_vgAUPfwzgxIkCV15CYFmASwn",
                            name="secret_retrieval_tool",
                            args='{"password": "radiance"}',
                        ),
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:completions",
                    provider_model_name="gpt-4o:completions",
                    raw_message={
                        "role": "assistant",
                        "annotations": [],
                        "tool_calls": [
                            {
                                "id": "call_eTrqJEDnTlTGliM458pkKaaQ",
                                "function": {
                                    "arguments": '{"password": "mellon"}',
                                    "name": "secret_retrieval_tool",
                                },
                                "type": "function",
                            },
                            {
                                "id": "call_vgAUPfwzgxIkCV15CYFmASwn",
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
                            id="call_eTrqJEDnTlTGliM458pkKaaQ",
                            name="secret_retrieval_tool",
                            result="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="call_vgAUPfwzgxIkCV15CYFmASwn",
                            name="secret_retrieval_tool",
                            result="Life before Death",
                        ),
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
The secrets associated with the passwords are as follows:
- For "mellon": Welcome to Moria!
- For "radiance": Life before Death\
"""
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:completions",
                    provider_model_name="gpt-4o:completions",
                    raw_message={
                        "content": """\
The secrets associated with the passwords are as follows:
- For "mellon": Welcome to Moria!
- For "radiance": Life before Death\
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
            "model_id": "openai/gpt-4o:completions",
            "provider_model_name": "gpt-4o:completions",
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
                            id="call_NnkmjbtYL9gdZnGOMxYEl0A3",
                            name="secret_retrieval_tool",
                            args='{"password": "mellon"}',
                        ),
                        ToolCall(
                            id="call_uvC42eCVUOg2Y35G9FQKjAOB",
                            name="secret_retrieval_tool",
                            args='{"password": "radiance"}',
                        ),
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:completions",
                    provider_model_name="gpt-4o:completions",
                    raw_message=None,
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_NnkmjbtYL9gdZnGOMxYEl0A3",
                            name="secret_retrieval_tool",
                            result="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="call_uvC42eCVUOg2Y35G9FQKjAOB",
                            name="secret_retrieval_tool",
                            result="Life before Death",
                        ),
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
The secrets associated with the passwords are as follows:

- "mellon": Welcome to Moria!
- "radiance": Life before Death\
"""
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:completions",
                    provider_model_name="gpt-4o:completions",
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
                    "strict": None,
                }
            ],
            "usage": {
                "input_tokens": 149,
                "output_tokens": 30,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "None",
                "total_tokens": 179,
            },
            "n_chunks": 31,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "openai",
            "model_id": "openai/gpt-4o:completions",
            "provider_model_name": "gpt-4o:completions",
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
                            id="call_FrKwqXDWJFYAzpMNuKWtQ9PO",
                            name="secret_retrieval_tool",
                            args='{"password": "mellon"}',
                        ),
                        ToolCall(
                            id="call_Z9OUz90nWgDjqOmcMOQK5KbJ",
                            name="secret_retrieval_tool",
                            args='{"password": "radiance"}',
                        ),
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:completions",
                    provider_model_name="gpt-4o:completions",
                    raw_message=None,
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_FrKwqXDWJFYAzpMNuKWtQ9PO",
                            name="secret_retrieval_tool",
                            result="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="call_Z9OUz90nWgDjqOmcMOQK5KbJ",
                            name="secret_retrieval_tool",
                            result="Life before Death",
                        ),
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Here are the retrieved secrets for the passwords:

- For "mellon": Welcome to Moria!
- For "radiance": Life before Death\
"""
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:completions",
                    provider_model_name="gpt-4o:completions",
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
                    "strict": None,
                }
            ],
            "usage": {
                "input_tokens": 149,
                "output_tokens": 31,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "None",
                "total_tokens": 180,
            },
            "n_chunks": 32,
        }
    }
)
