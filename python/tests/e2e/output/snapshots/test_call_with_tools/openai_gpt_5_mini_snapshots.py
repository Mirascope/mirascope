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
            "model_id": "openai/gpt-5-mini",
            "provider_model_name": "gpt-5-mini:responses",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 152,
                "output_tokens": 378,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 320,
                "raw": "ResponseUsage(input_tokens=152, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=378, output_tokens_details=OutputTokensDetails(reasoning_tokens=320), total_tokens=530)",
                "total_tokens": 530,
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
                            id="call_wYuoRZQG6MbpVXEVpUzBPCqj",
                            name="secret_retrieval_tool",
                            args='{"password":"mellon"}',
                        ),
                        ToolCall(
                            id="call_7z8b3CsYGHXyiMH5fekHUt4o",
                            name="secret_retrieval_tool",
                            args='{"password":"radiance"}',
                        ),
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini:responses",
                    raw_message=[
                        {
                            "id": "rs_081d9dfc404f353f0069492df7dbc081908cde95733c427937",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "arguments": '{"password":"mellon"}',
                            "call_id": "call_wYuoRZQG6MbpVXEVpUzBPCqj",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_081d9dfc404f353f0069492dfa30108190857c9290d8bfbea0",
                            "status": "completed",
                        },
                        {
                            "arguments": '{"password":"radiance"}',
                            "call_id": "call_7z8b3CsYGHXyiMH5fekHUt4o",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_081d9dfc404f353f0069492dfa7d4c81908c3f2bac4ed3493c",
                            "status": "completed",
                        },
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_wYuoRZQG6MbpVXEVpUzBPCqj",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="call_7z8b3CsYGHXyiMH5fekHUt4o",
                            name="secret_retrieval_tool",
                            value="Life before Death",
                        ),
                    ]
                ),
                AssistantMessage(
                    content=[
                        ToolCall(
                            id="call_lEYCK7jSglxwn3Hdy99UdGXj",
                            name="secret_retrieval_tool",
                            args='{"password":"mellon"}',
                        ),
                        ToolCall(
                            id="call_Jm1h5fS4zDS2zRDMNNnPgDN4",
                            name="secret_retrieval_tool",
                            args='{"password":"radiance"}',
                        ),
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini:responses",
                    raw_message=[
                        {
                            "id": "rs_081d9dfc404f353f0069492dfb5d8481909f77cfed4126f2e4",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "arguments": '{"password":"mellon"}',
                            "call_id": "call_lEYCK7jSglxwn3Hdy99UdGXj",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_081d9dfc404f353f0069492e00037481908606ff1b07ae887f",
                            "status": "completed",
                        },
                        {
                            "arguments": '{"password":"radiance"}',
                            "call_id": "call_Jm1h5fS4zDS2zRDMNNnPgDN4",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_081d9dfc404f353f0069492e00393881909fdf48978b0097ef",
                            "status": "completed",
                        },
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
            "model_id": "openai/gpt-5-mini",
            "provider_model_name": "gpt-5-mini:responses",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 142,
                "output_tokens": 250,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 192,
                "raw": "ResponseUsage(input_tokens=142, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=250, output_tokens_details=OutputTokensDetails(reasoning_tokens=192), total_tokens=392)",
                "total_tokens": 392,
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
                            id="call_5lEycjEmS9E5mOF1qg84K6Om",
                            name="secret_retrieval_tool",
                            args='{"password":"mellon"}',
                        ),
                        ToolCall(
                            id="call_gIbCDU4raIY1JmDIBxoo4rJk",
                            name="secret_retrieval_tool",
                            args='{"password":"radiance"}',
                        ),
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini:responses",
                    raw_message=[
                        {
                            "id": "rs_04cefb1511efd10e0069492e01bc9c8190b3d5c327018a96f2",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "arguments": '{"password":"mellon"}',
                            "call_id": "call_5lEycjEmS9E5mOF1qg84K6Om",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_04cefb1511efd10e0069492e037dec8190906abfb4b90ff6ae",
                            "status": "completed",
                        },
                        {
                            "arguments": '{"password":"radiance"}',
                            "call_id": "call_gIbCDU4raIY1JmDIBxoo4rJk",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_04cefb1511efd10e0069492e03afe08190a440b8eb63bc5ed8",
                            "status": "completed",
                        },
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_5lEycjEmS9E5mOF1qg84K6Om",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="call_gIbCDU4raIY1JmDIBxoo4rJk",
                            name="secret_retrieval_tool",
                            value="Life before Death",
                        ),
                    ]
                ),
                AssistantMessage(
                    content=[
                        ToolCall(
                            id="call_cC4ssN7GeAJbNqdpVw2PrpMd",
                            name="secret_retrieval_tool",
                            args='{"password":"mellon"}',
                        ),
                        ToolCall(
                            id="call_bIDdHS4Jx4BLqbFazLfgahBj",
                            name="secret_retrieval_tool",
                            args='{"password":"radiance"}',
                        ),
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini:responses",
                    raw_message=[
                        {
                            "id": "rs_04cefb1511efd10e0069492e049d588190908f2a3ecfd2c8b4",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "arguments": '{"password":"mellon"}',
                            "call_id": "call_cC4ssN7GeAJbNqdpVw2PrpMd",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_04cefb1511efd10e0069492e07beac819080e71ce1cdb51c6f",
                            "status": "completed",
                        },
                        {
                            "arguments": '{"password":"radiance"}',
                            "call_id": "call_bIDdHS4Jx4BLqbFazLfgahBj",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_04cefb1511efd10e0069492e07f8b4819096653bba5ed10f55",
                            "status": "completed",
                        },
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
            "model_id": "openai/gpt-5-mini",
            "provider_model_name": "gpt-5-mini:responses",
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
                            id="call_yNjBMcK6OeERutRkOCjACGnB",
                            name="secret_retrieval_tool",
                            args='{"password":"mellon"}',
                        ),
                        ToolCall(
                            id="call_mKDN3h0IACjeWNhSjiHtAQSz",
                            name="secret_retrieval_tool",
                            args='{"password":"radiance"}',
                        ),
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini:responses",
                    raw_message=[
                        {
                            "id": "rs_0de9de8974c181a00069492e0975bc8197bba6e6a7cee785ac",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "arguments": '{"password":"mellon"}',
                            "call_id": "call_yNjBMcK6OeERutRkOCjACGnB",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_0de9de8974c181a00069492e0c17008197b0e5195c5bbd6f34",
                            "status": "completed",
                        },
                        {
                            "arguments": '{"password":"radiance"}',
                            "call_id": "call_mKDN3h0IACjeWNhSjiHtAQSz",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_0de9de8974c181a00069492e0ccab08197bebd615c34b0c3c6",
                            "status": "completed",
                        },
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_yNjBMcK6OeERutRkOCjACGnB",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="call_mKDN3h0IACjeWNhSjiHtAQSz",
                            name="secret_retrieval_tool",
                            value="Life before Death",
                        ),
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Here are the secrets retrieved:

- mellon: "Welcome to Moria!"
- radiance: "Life before Death"\
"""
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini:responses",
                    raw_message=[
                        {
                            "id": "rs_0de9de8974c181a00069492e0db300819797225cc9f87653a8",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_0de9de8974c181a00069492e122f9881979481c1f624e8ceda",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
Here are the secrets retrieved:

- mellon: "Welcome to Moria!"
- radiance: "Life before Death"\
""",
                                    "type": "output_text",
                                    "logprobs": [],
                                }
                            ],
                            "role": "assistant",
                            "status": "completed",
                            "type": "message",
                        },
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
                "input_tokens": 287,
                "output_tokens": 351,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 320,
                "raw": "None",
                "total_tokens": 638,
            },
            "n_chunks": 27,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "openai",
            "model_id": "openai/gpt-5-mini",
            "provider_model_name": "gpt-5-mini:responses",
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
                            id="call_I0qVGo2FFWR9KuVGrNyCYUZS",
                            name="secret_retrieval_tool",
                            args='{"password":"mellon"}',
                        ),
                        ToolCall(
                            id="call_d7tN3cuHPYXz7UC1V6zWEDFM",
                            name="secret_retrieval_tool",
                            args='{"password":"radiance"}',
                        ),
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini:responses",
                    raw_message=[
                        {
                            "id": "rs_0e3d644283e3af3d0069492e13be288194a561672353944067",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "arguments": '{"password":"mellon"}',
                            "call_id": "call_I0qVGo2FFWR9KuVGrNyCYUZS",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_0e3d644283e3af3d0069492e15a75081948c61139063cbbc36",
                            "status": "completed",
                        },
                        {
                            "arguments": '{"password":"radiance"}',
                            "call_id": "call_d7tN3cuHPYXz7UC1V6zWEDFM",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_0e3d644283e3af3d0069492e15d9948194abbb2ca2a3c823f6",
                            "status": "completed",
                        },
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_I0qVGo2FFWR9KuVGrNyCYUZS",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="call_d7tN3cuHPYXz7UC1V6zWEDFM",
                            name="secret_retrieval_tool",
                            value="Life before Death",
                        ),
                    ]
                ),
                AssistantMessage(
                    content=[
                        ToolCall(
                            id="call_7myOe09av5usyouoJ7JKd3pF",
                            name="secret_retrieval_tool",
                            args='{"password":"mellon"}',
                        ),
                        ToolCall(
                            id="call_bX8GYw0LiLvI6t9UgMazJ9kX",
                            name="secret_retrieval_tool",
                            args='{"password":"radiance"}',
                        ),
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini:responses",
                    raw_message=[
                        {
                            "id": "rs_0e3d644283e3af3d0069492e177f388194998492afc57b7ca2",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "arguments": '{"password":"mellon"}',
                            "call_id": "call_7myOe09av5usyouoJ7JKd3pF",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_0e3d644283e3af3d0069492e199b7c8194b5dce95b2020b08f",
                            "status": "completed",
                        },
                        {
                            "arguments": '{"password":"radiance"}',
                            "call_id": "call_bX8GYw0LiLvI6t9UgMazJ9kX",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_0e3d644283e3af3d0069492e19d1808194b00899df27410013",
                            "status": "completed",
                        },
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
                "input_tokens": 148,
                "output_tokens": 186,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 128,
                "raw": "None",
                "total_tokens": 334,
            },
            "n_chunks": 17,
        }
    }
)
