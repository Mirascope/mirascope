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
            "provider": "azure-openai:responses",
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
                            id="call_OEVIhxzWb41yDD3ohAksEhL1",
                            name="secret_retrieval_tool",
                            args='{"password":"mellon"}',
                        ),
                        ToolCall(
                            id="call_SNm2RreNI5AB0TceKmdBQH8U",
                            name="secret_retrieval_tool",
                            args='{"password":"radiance"}',
                        ),
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "arguments": '{"password":"mellon"}',
                            "call_id": "call_OEVIhxzWb41yDD3ohAksEhL1",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_057158d91a7eed9200690ac3d0c4b4819492089651695a42ee",
                            "status": "completed",
                        },
                        {
                            "arguments": '{"password":"radiance"}',
                            "call_id": "call_SNm2RreNI5AB0TceKmdBQH8U",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_057158d91a7eed9200690ac3d119948194aa244a9dce62bed0",
                            "status": "completed",
                        },
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_OEVIhxzWb41yDD3ohAksEhL1",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="call_SNm2RreNI5AB0TceKmdBQH8U",
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

- **mellon**: Welcome to Moria!
- **radiance**: Life before Death.\
"""
                        )
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "id": "msg_001888a10221afd400690ac3d22790819397e1cc9ac83d9a87",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
Here are the secrets associated with the provided passwords:

- **mellon**: Welcome to Moria!
- **radiance**: Life before Death.\
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
            "provider": "azure-openai:responses",
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
                            id="call_Q8IuRD2nZDn1KlbZzNd949KA",
                            name="secret_retrieval_tool",
                            args='{"password":"mellon"}',
                        ),
                        ToolCall(
                            id="call_FvKkXuE6jU9BJLWSg4fz4dKC",
                            name="secret_retrieval_tool",
                            args='{"password":"radiance"}',
                        ),
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "arguments": '{"password":"mellon"}',
                            "call_id": "call_Q8IuRD2nZDn1KlbZzNd949KA",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_0cf63076bbe8855d00690ac3d465f48197abf4b3bab850d249",
                            "status": "completed",
                        },
                        {
                            "arguments": '{"password":"radiance"}',
                            "call_id": "call_FvKkXuE6jU9BJLWSg4fz4dKC",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_0cf63076bbe8855d00690ac3d4ad6481979b7afcb828368810",
                            "status": "completed",
                        },
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_Q8IuRD2nZDn1KlbZzNd949KA",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="call_FvKkXuE6jU9BJLWSg4fz4dKC",
                            name="secret_retrieval_tool",
                            value="Life before Death",
                        ),
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Here are the secrets associated with the passwords you provided:

- **mellon**: Welcome to Moria!
- **radiance**: Life before Death.\
"""
                        )
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "id": "msg_049338625c3c4d4200690ac3d57c008196969e2e3a89be5a18",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
Here are the secrets associated with the passwords you provided:

- **mellon**: Welcome to Moria!
- **radiance**: Life before Death.\
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
            "provider": "azure-openai:responses",
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
                            id="call_Qvs6PXEti629i1WaPDDv3ukv",
                            name="secret_retrieval_tool",
                            args='{"password":"mellon"}',
                        ),
                        ToolCall(
                            id="call_CZiatFzEcdqMPk0JGl0oU5HJ",
                            name="secret_retrieval_tool",
                            args='{"password":"radiance"}',
                        ),
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "arguments": '{"password":"mellon"}',
                            "call_id": "call_Qvs6PXEti629i1WaPDDv3ukv",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_01a788ba3a95f1e400690ac3d7256881949c880d4e4d1b625f",
                            "status": "completed",
                        },
                        {
                            "arguments": '{"password":"radiance"}',
                            "call_id": "call_CZiatFzEcdqMPk0JGl0oU5HJ",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_01a788ba3a95f1e400690ac3d777d88194aae92f76e876a087",
                            "status": "completed",
                        },
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_Qvs6PXEti629i1WaPDDv3ukv",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="call_CZiatFzEcdqMPk0JGl0oU5HJ",
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
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "id": "msg_0c2ada146c09bf1d00690ac3d81f388190a8a178c27a90835e",
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
            "n_chunks": 32,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider": "azure-openai:responses",
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
                            id="call_TxpG5OtPPE5oAkrgiDcSefLd",
                            name="secret_retrieval_tool",
                            args='{"password":"mellon"}',
                        ),
                        ToolCall(
                            id="call_7w2KGJTavwdgET2r0tHKkjeB",
                            name="secret_retrieval_tool",
                            args='{"password":"radiance"}',
                        ),
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "arguments": '{"password":"mellon"}',
                            "call_id": "call_TxpG5OtPPE5oAkrgiDcSefLd",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_0281a718f166a71800690ac3da994c8193a98d9c9acb3758b7",
                            "status": "completed",
                        },
                        {
                            "arguments": '{"password":"radiance"}',
                            "call_id": "call_7w2KGJTavwdgET2r0tHKkjeB",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_0281a718f166a71800690ac3daf59081938756785a6020e1da",
                            "status": "completed",
                        },
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_TxpG5OtPPE5oAkrgiDcSefLd",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="call_7w2KGJTavwdgET2r0tHKkjeB",
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
- **radiance**: Life before Death.\
"""
                        )
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "id": "msg_0fe88c44fa0927a100690ac3db985881968fd1a3677bfd6886",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
Here are the secrets associated with each password:

- **mellon**: Welcome to Moria!
- **radiance**: Life before Death.\
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
            "n_chunks": 33,
        }
    }
)
