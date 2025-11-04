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
                            id="call_ItUb0ok6QKqLmF3waT7Wi7Du",
                            name="secret_retrieval_tool",
                            args='{"password":"mellon"}',
                        ),
                        ToolCall(
                            id="call_kOPG7p73gWiOqGWGRpEAaVqP",
                            name="secret_retrieval_tool",
                            args='{"password":"radiance"}',
                        ),
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "arguments": '{"password":"mellon"}',
                            "call_id": "call_ItUb0ok6QKqLmF3waT7Wi7Du",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_09bcedb16f2020fb00690c2182cf208196bf4632743bd1c7db",
                            "status": "completed",
                        },
                        {
                            "arguments": '{"password":"radiance"}',
                            "call_id": "call_kOPG7p73gWiOqGWGRpEAaVqP",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_09bcedb16f2020fb00690c2183763c8196973eda953e08c699",
                            "status": "completed",
                        },
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_ItUb0ok6QKqLmF3waT7Wi7Du",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="call_kOPG7p73gWiOqGWGRpEAaVqP",
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

- For **mellon**: "Welcome to Moria!"
- For **radiance**: "Life before Death."\
"""
                        )
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "id": "msg_09dad9c01511a20600690c21846f1c819380a5e1b353cde515",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
Here are the secrets associated with the provided passwords:

- For **mellon**: "Welcome to Moria!"
- For **radiance**: "Life before Death."\
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
                            id="call_olTOmZG3hjrL4mfFimLNXDLB",
                            name="secret_retrieval_tool",
                            args='{"password":"mellon"}',
                        ),
                        ToolCall(
                            id="call_uhxuIcjvuJzGdGOirll5TQfA",
                            name="secret_retrieval_tool",
                            args='{"password":"radiance"}',
                        ),
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "arguments": '{"password":"mellon"}',
                            "call_id": "call_olTOmZG3hjrL4mfFimLNXDLB",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_03a9d3c0de08f30400690c218c5e3481978454674c2a104f0f",
                            "status": "completed",
                        },
                        {
                            "arguments": '{"password":"radiance"}',
                            "call_id": "call_uhxuIcjvuJzGdGOirll5TQfA",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_03a9d3c0de08f30400690c218cbc8c8197955ee64661323819",
                            "status": "completed",
                        },
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_olTOmZG3hjrL4mfFimLNXDLB",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="call_uhxuIcjvuJzGdGOirll5TQfA",
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
                            "id": "msg_0d296d4219e08ab700690c218d82508195bbabde0107ab3ab8",
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
                            id="call_ZxvfEKOUAaNm2rIvu0CXWN1z",
                            name="secret_retrieval_tool",
                            args='{"password":"mellon"}',
                        ),
                        ToolCall(
                            id="call_hWZOQA612mDihMo08n25NxOp",
                            name="secret_retrieval_tool",
                            args='{"password":"radiance"}',
                        ),
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "arguments": '{"password":"mellon"}',
                            "call_id": "call_ZxvfEKOUAaNm2rIvu0CXWN1z",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_07118ddc121e2f0e00690c2192dbf48190a6219dda3bb83475",
                            "status": "completed",
                        },
                        {
                            "arguments": '{"password":"radiance"}',
                            "call_id": "call_hWZOQA612mDihMo08n25NxOp",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_07118ddc121e2f0e00690c21932ce08190870dd2d8f46ca57b",
                            "status": "completed",
                        },
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_ZxvfEKOUAaNm2rIvu0CXWN1z",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="call_hWZOQA612mDihMo08n25NxOp",
                            name="secret_retrieval_tool",
                            value="Life before Death",
                        ),
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Here are the retrieved secrets:

- For the password **"mellon"**: Welcome to Moria!
- For the password **"radiance"**: Life before Death.\
"""
                        )
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "id": "msg_0054527b5059002200690c2193f900819791ad404a952e41e6",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
Here are the retrieved secrets:

- For the password **"mellon"**: Welcome to Moria!
- For the password **"radiance"**: Life before Death.\
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
            "n_chunks": 40,
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
                            id="call_dHxC2hJ2VSzsv1mT9p0O3sz2",
                            name="secret_retrieval_tool",
                            args='{"password":"mellon"}',
                        ),
                        ToolCall(
                            id="call_sYmAHEeR0k4HHdrKtHjFGiSb",
                            name="secret_retrieval_tool",
                            args='{"password":"radiance"}',
                        ),
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "arguments": '{"password":"mellon"}',
                            "call_id": "call_dHxC2hJ2VSzsv1mT9p0O3sz2",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_06ba060e161e277400690c219a5f208196a73deac08af95e41",
                            "status": "completed",
                        },
                        {
                            "arguments": '{"password":"radiance"}',
                            "call_id": "call_sYmAHEeR0k4HHdrKtHjFGiSb",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_06ba060e161e277400690c219ab77c8196a01b5a1eb8bfc43d",
                            "status": "completed",
                        },
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_dHxC2hJ2VSzsv1mT9p0O3sz2",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="call_sYmAHEeR0k4HHdrKtHjFGiSb",
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
                            "id": "msg_0df6eaceff5d918c00690c219b62a481968817890e853c8368",
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
