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
                        id="call_df3svYLONNdt3Qb2FXFeXwZ3",
                        name="secret_retrieval_tool",
                        args='{"password":"mellon"}',
                    ),
                    ToolCall(
                        id="call_JXegss0AyNLShfYnQsxPJn0L",
                        name="secret_retrieval_tool",
                        args='{"password":"radiance"}',
                    ),
                ],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "arguments": '{"password":"mellon"}',
                        "call_id": "call_df3svYLONNdt3Qb2FXFeXwZ3",
                        "name": "secret_retrieval_tool",
                        "type": "function_call",
                        "id": "fc_0678b7a1f79ace020068f2990428ec81909e1710e0e4e3401a",
                        "status": "completed",
                    },
                    {
                        "arguments": '{"password":"radiance"}',
                        "call_id": "call_JXegss0AyNLShfYnQsxPJn0L",
                        "name": "secret_retrieval_tool",
                        "type": "function_call",
                        "id": "fc_0678b7a1f79ace020068f29904560c819083a6a47c77485600",
                        "status": "completed",
                    },
                ],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="call_df3svYLONNdt3Qb2FXFeXwZ3",
                        name="secret_retrieval_tool",
                        value="Welcome to Moria!",
                    ),
                    ToolOutput(
                        id="call_JXegss0AyNLShfYnQsxPJn0L",
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

- For "mellon": Welcome to Moria!
- For "radiance": Life before Death\
"""
                    )
                ],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "id": "msg_0678b7a1f79ace020068f299051d0881909f69455ee8292f19",
                        "content": [
                            {
                                "annotations": [],
                                "text": """\
Here are the secrets:

- For "mellon": Welcome to Moria!
- For "radiance": Life before Death\
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
                        id="call_0zCTbx6FQ8k3esy7neFHKDjp",
                        name="secret_retrieval_tool",
                        args='{"password":"mellon"}',
                    ),
                    ToolCall(
                        id="call_a3DD38dIZ9K96s31Lpz58GrI",
                        name="secret_retrieval_tool",
                        args='{"password":"radiance"}',
                    ),
                ],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "arguments": '{"password":"mellon"}',
                        "call_id": "call_0zCTbx6FQ8k3esy7neFHKDjp",
                        "name": "secret_retrieval_tool",
                        "type": "function_call",
                        "id": "fc_0dc7d3cef7c1431c0068f2990fd68881978b81fcd8142e8363",
                        "status": "completed",
                    },
                    {
                        "arguments": '{"password":"radiance"}',
                        "call_id": "call_a3DD38dIZ9K96s31Lpz58GrI",
                        "name": "secret_retrieval_tool",
                        "type": "function_call",
                        "id": "fc_0dc7d3cef7c1431c0068f2990ff8c0819789ad43821741a0ce",
                        "status": "completed",
                    },
                ],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="call_0zCTbx6FQ8k3esy7neFHKDjp",
                        name="secret_retrieval_tool",
                        value="Welcome to Moria!",
                    ),
                    ToolOutput(
                        id="call_a3DD38dIZ9K96s31Lpz58GrI",
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
                raw_content=[
                    {
                        "id": "msg_0dc7d3cef7c1431c0068f299112d808197b24e445fcb80e82f",
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
                        id="call_41CfEqEOHhPeIwSwoLhT7x8y",
                        name="secret_retrieval_tool",
                        args='{"password":"mellon"}',
                    ),
                    ToolCall(
                        id="call_rprZSnKbUBINpIEDeVwZ3bTN",
                        name="secret_retrieval_tool",
                        args='{"password":"radiance"}',
                    ),
                ],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "arguments": '{"password":"mellon"}',
                        "call_id": "call_41CfEqEOHhPeIwSwoLhT7x8y",
                        "name": "secret_retrieval_tool",
                        "type": "function_call",
                        "id": "fc_0888af4740f553150068f2991f6f948195bff3a4a088b1994e",
                        "status": "completed",
                    },
                    {
                        "arguments": '{"password":"radiance"}',
                        "call_id": "call_rprZSnKbUBINpIEDeVwZ3bTN",
                        "name": "secret_retrieval_tool",
                        "type": "function_call",
                        "id": "fc_0888af4740f553150068f2991f84108195bf556ee9ddb31f6e",
                        "status": "completed",
                    },
                ],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="call_41CfEqEOHhPeIwSwoLhT7x8y",
                        name="secret_retrieval_tool",
                        value="Welcome to Moria!",
                    ),
                    ToolOutput(
                        id="call_rprZSnKbUBINpIEDeVwZ3bTN",
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

- **mellon**: Welcome to Moria!
- **radiance**: Life before Death\
"""
                    )
                ],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "id": "msg_0888af4740f553150068f299207a98819598f085926027eddb",
                        "content": [
                            {
                                "annotations": [],
                                "text": """\
Here are the secrets associated with the passwords:

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
        "n_chunks": 32,
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
                        id="call_e9IFshyCDcsOO3BqCLkU1m3R",
                        name="secret_retrieval_tool",
                        args='{"password":"mellon"}',
                    ),
                    ToolCall(
                        id="call_Vmt8WWTUEzCQGmrrMtWYP1Yr",
                        name="secret_retrieval_tool",
                        args='{"password":"radiance"}',
                    ),
                ],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "arguments": '{"password":"mellon"}',
                        "call_id": "call_e9IFshyCDcsOO3BqCLkU1m3R",
                        "name": "secret_retrieval_tool",
                        "type": "function_call",
                        "id": "fc_0f52f42decbdc1ed0068f2992bd6c48196a0d3120f7d8bc429",
                        "status": "completed",
                    },
                    {
                        "arguments": '{"password":"radiance"}',
                        "call_id": "call_Vmt8WWTUEzCQGmrrMtWYP1Yr",
                        "name": "secret_retrieval_tool",
                        "type": "function_call",
                        "id": "fc_0f52f42decbdc1ed0068f2992bf3b48196a3cd4b48032593ca",
                        "status": "completed",
                    },
                ],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="call_e9IFshyCDcsOO3BqCLkU1m3R",
                        name="secret_retrieval_tool",
                        value="Welcome to Moria!",
                    ),
                    ToolOutput(
                        id="call_Vmt8WWTUEzCQGmrrMtWYP1Yr",
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

- For "mellon": Welcome to Moria!
- For "radiance": Life before Death\
"""
                    )
                ],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "id": "msg_0f52f42decbdc1ed0068f2992d02688196b4453f9dff18fb02",
                        "content": [
                            {
                                "annotations": [],
                                "text": """\
Here are the secrets:

- For "mellon": Welcome to Moria!
- For "radiance": Life before Death\
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
        "n_chunks": 28,
    }
)
