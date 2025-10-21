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
                            id="call_VP1Hss5Mco8swJxuCQgAwg1z",
                            name="secret_retrieval_tool",
                            args='{"password":"mellon"}',
                        ),
                        ToolCall(
                            id="call_PQt2R8pTpPM48nfEVptZquEE",
                            name="secret_retrieval_tool",
                            args='{"password":"radiance"}',
                        ),
                    ],
                    provider="openai:responses",
                    model_id="gpt-4o",
                    raw_message=[
                        {
                            "arguments": '{"password":"mellon"}',
                            "call_id": "call_VP1Hss5Mco8swJxuCQgAwg1z",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_05a638d56eea032f0068f8033d4fac81979b6232f3344d1333",
                            "status": "completed",
                        },
                        {
                            "arguments": '{"password":"radiance"}',
                            "call_id": "call_PQt2R8pTpPM48nfEVptZquEE",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_05a638d56eea032f0068f8033d6b8081979644045ac1177e20",
                            "status": "completed",
                        },
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_VP1Hss5Mco8swJxuCQgAwg1z",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="call_PQt2R8pTpPM48nfEVptZquEE",
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

- **mellon**: "Welcome to Moria!"
- **radiance**: "Life before Death"\
"""
                        )
                    ],
                    provider="openai:responses",
                    model_id="gpt-4o",
                    raw_message=[
                        {
                            "id": "msg_05a638d56eea032f0068f8033e766c81979ea1b4f5aa398368",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
Here are the secrets associated with the passwords:

- **mellon**: "Welcome to Moria!"
- **radiance**: "Life before Death"\
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
                            id="call_HGG1nGDs6kiMDFgFpKarnZx6",
                            name="secret_retrieval_tool",
                            args='{"password":"mellon"}',
                        ),
                        ToolCall(
                            id="call_lX21b6EAa5e8ypmLbkM2xKYV",
                            name="secret_retrieval_tool",
                            args='{"password":"radiance"}',
                        ),
                    ],
                    provider="openai:responses",
                    model_id="gpt-4o",
                    raw_message=[
                        {
                            "arguments": '{"password":"mellon"}',
                            "call_id": "call_HGG1nGDs6kiMDFgFpKarnZx6",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_0c4d870f86c990ad0068f80340b18c8196b32f72de4212f9a1",
                            "status": "completed",
                        },
                        {
                            "arguments": '{"password":"radiance"}',
                            "call_id": "call_lX21b6EAa5e8ypmLbkM2xKYV",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_0c4d870f86c990ad0068f80340dc648196be2aca7c3325eebe",
                            "status": "completed",
                        },
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_HGG1nGDs6kiMDFgFpKarnZx6",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="call_lX21b6EAa5e8ypmLbkM2xKYV",
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

- "mellon": Welcome to Moria!
- "radiance": Life before Death\
"""
                        )
                    ],
                    provider="openai:responses",
                    model_id="gpt-4o",
                    raw_message=[
                        {
                            "id": "msg_0c4d870f86c990ad0068f80342851081968addd63f6fb0a7ce",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
Here are the secrets:

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
                            id="call_8mWOlD2knIPTChQYr7GQ4Hxi",
                            name="secret_retrieval_tool",
                            args='{"password":"mellon"}',
                        ),
                        ToolCall(
                            id="call_3UNGcrPBkfEG8ueZGjz6s00h",
                            name="secret_retrieval_tool",
                            args='{"password":"radiance"}',
                        ),
                    ],
                    provider="openai:responses",
                    model_id="gpt-4o",
                    raw_message=[
                        {
                            "arguments": '{"password":"mellon"}',
                            "call_id": "call_8mWOlD2knIPTChQYr7GQ4Hxi",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_08622b4f543dc1510068f803450d1c819686d379e0da7b29d8",
                            "status": "completed",
                        },
                        {
                            "arguments": '{"password":"radiance"}',
                            "call_id": "call_3UNGcrPBkfEG8ueZGjz6s00h",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_08622b4f543dc1510068f803457c7081969163370cc2f28787",
                            "status": "completed",
                        },
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_8mWOlD2knIPTChQYr7GQ4Hxi",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="call_3UNGcrPBkfEG8ueZGjz6s00h",
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
                    raw_message=[
                        {
                            "id": "msg_08622b4f543dc1510068f80346cd088196a0679646c918d73a",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
Here are the secrets for the provided passwords:

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
                            id="call_q1t9XZMJIkrsHvmorg22clzL",
                            name="secret_retrieval_tool",
                            args='{"password":"mellon"}',
                        ),
                        ToolCall(
                            id="call_5l4sCPMYHaNlQDLW5DoksdHs",
                            name="secret_retrieval_tool",
                            args='{"password":"radiance"}',
                        ),
                    ],
                    provider="openai:responses",
                    model_id="gpt-4o",
                    raw_message=[
                        {
                            "arguments": '{"password":"mellon"}',
                            "call_id": "call_q1t9XZMJIkrsHvmorg22clzL",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_00c4f15a862212440068f8034908948193b1effcabcb862cb5",
                            "status": "completed",
                        },
                        {
                            "arguments": '{"password":"radiance"}',
                            "call_id": "call_5l4sCPMYHaNlQDLW5DoksdHs",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_00c4f15a862212440068f803492f848193aea4fcadd7119614",
                            "status": "completed",
                        },
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_q1t9XZMJIkrsHvmorg22clzL",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="call_5l4sCPMYHaNlQDLW5DoksdHs",
                            name="secret_retrieval_tool",
                            value="Life before Death",
                        ),
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
The secrets associated with the passwords are:

- "mellon": Welcome to Moria!
- "radiance": Life before Death\
"""
                        )
                    ],
                    provider="openai:responses",
                    model_id="gpt-4o",
                    raw_message=[
                        {
                            "id": "msg_00c4f15a862212440068f8034ad20c8193bdbd6456240d2773",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
The secrets associated with the passwords are:

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
            "n_chunks": 29,
        }
    }
)
