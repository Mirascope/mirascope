from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    SystemMessage,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "response": {
            "provider_id": "anthropic",
            "model_id": "anthropic/claude-sonnet-4-0",
            "provider_model_name": "claude-sonnet-4-0",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 221,
                "output_tokens": 13,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "Usage(cache_creation=CacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=221, output_tokens=13, server_tool_use=None, service_tier='standard')",
                "total_tokens": 234,
            },
            "messages": [
                SystemMessage(
                    content=Text(
                        text="""\
Respond only with valid JSON that matches this exact schema:
{
  "description": "A lucky number chosen by the model.",
  "properties": {
    "value": {
      "title": "Value",
      "type": "integer"
    }
  },
  "required": [
    "value"
  ],
  "title": "LuckyNumber",
  "type": "object"
}\
"""
                    )
                ),
                UserMessage(
                    content=[Text(text="Pick a random number between 1 and 1000")]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
{
  "value": 347
}\
"""
                        )
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "citations": None,
                                "text": """\
{
  "value": 347
}\
""",
                                "type": "text",
                            }
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        Text(
                            text="""\
Your response failed schema validation:
1 validation error for LuckyNumber
value
  Value error, The number must be exactly 173, but got 347 [type=value_error, input_value=347, input_type=int]
    For further information visit https://errors.pydantic.dev/2.12/v/value_error

Please correct these issues and respond again.\
"""
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
{
  "value": 173
}\
"""
                        )
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "citations": None,
                                "text": """\
{
  "value": 173
}\
""",
                                "type": "text",
                            }
                        ],
                    },
                ),
            ],
            "format": {
                "name": "LuckyNumber",
                "description": "A lucky number chosen by the model.",
                "schema": {
                    "description": "A lucky number chosen by the model.",
                    "properties": {"value": {"title": "Value", "type": "integer"}},
                    "required": ["value"],
                    "title": "LuckyNumber",
                    "type": "object",
                },
                "mode": "json",
                "formatting_instructions": """\
Respond only with valid JSON that matches this exact schema:
{
  "description": "A lucky number chosen by the model.",
  "properties": {
    "value": {
      "title": "Value",
      "type": "integer"
    }
  },
  "required": [
    "value"
  ],
  "title": "LuckyNumber",
  "type": "object"
}\
""",
            },
            "tools": [],
        }
    }
)
async_snapshot = snapshot(
    {
        "response": {
            "provider_id": "anthropic",
            "model_id": "anthropic/claude-sonnet-4-0",
            "provider_model_name": "claude-sonnet-4-0",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 226,
                "output_tokens": 18,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "Usage(cache_creation=CacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=226, output_tokens=18, server_tool_use=None, service_tier='standard')",
                "total_tokens": 244,
            },
            "messages": [
                SystemMessage(
                    content=Text(
                        text="""\
Respond only with valid JSON that matches this exact schema:
{
  "description": "A lucky number chosen by the model.",
  "properties": {
    "value": {
      "title": "Value",
      "type": "integer"
    }
  },
  "required": [
    "value"
  ],
  "title": "LuckyNumber",
  "type": "object"
}\
"""
                    )
                ),
                UserMessage(
                    content=[Text(text="Pick a random number between 1 and 1000")]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
```json
{
  "value": 427
}
```\
"""
                        )
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "citations": None,
                                "text": """\
```json
{
  "value": 427
}
```\
""",
                                "type": "text",
                            }
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        Text(
                            text="""\
Your response failed schema validation:
1 validation error for LuckyNumber
value
  Value error, The number must be exactly 173, but got 427 [type=value_error, input_value=427, input_type=int]
    For further information visit https://errors.pydantic.dev/2.12/v/value_error

Please correct these issues and respond again.\
"""
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
```json
{
  "value": 173
}
```\
"""
                        )
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "citations": None,
                                "text": """\
```json
{
  "value": 173
}
```\
""",
                                "type": "text",
                            }
                        ],
                    },
                ),
            ],
            "format": {
                "name": "LuckyNumber",
                "description": "A lucky number chosen by the model.",
                "schema": {
                    "description": "A lucky number chosen by the model.",
                    "properties": {"value": {"title": "Value", "type": "integer"}},
                    "required": ["value"],
                    "title": "LuckyNumber",
                    "type": "object",
                },
                "mode": "json",
                "formatting_instructions": """\
Respond only with valid JSON that matches this exact schema:
{
  "description": "A lucky number chosen by the model.",
  "properties": {
    "value": {
      "title": "Value",
      "type": "integer"
    }
  },
  "required": [
    "value"
  ],
  "title": "LuckyNumber",
  "type": "object"
}\
""",
            },
            "tools": [],
        }
    }
)
stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "anthropic",
            "model_id": "anthropic/claude-sonnet-4-0",
            "provider_model_name": "claude-sonnet-4-0",
            "finish_reason": None,
            "messages": [
                SystemMessage(
                    content=Text(
                        text="""\
Respond only with valid JSON that matches this exact schema:
{
  "description": "A lucky number chosen by the model.",
  "properties": {
    "value": {
      "title": "Value",
      "type": "integer"
    }
  },
  "required": [
    "value"
  ],
  "title": "LuckyNumber",
  "type": "object"
}\
"""
                    )
                ),
                UserMessage(
                    content=[Text(text="Pick a random number between 1 and 1000")]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
```json
{
  "value": 742
}
```\
"""
                        )
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "text",
                                "text": """\
```json
{
  "value": 742
}
```\
""",
                            }
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        Text(
                            text="""\
Your response failed schema validation:
1 validation error for LuckyNumber
value
  Value error, The number must be exactly 173, but got 742 [type=value_error, input_value=742, input_type=int]
    For further information visit https://errors.pydantic.dev/2.12/v/value_error

Please correct these issues and respond again.\
"""
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
```json
{
  "value": 173
}
```\
"""
                        )
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "text",
                                "text": """\
```json
{
  "value": 173
}
```\
""",
                            }
                        ],
                    },
                ),
            ],
            "format": {
                "name": "LuckyNumber",
                "description": "A lucky number chosen by the model.",
                "schema": {
                    "description": "A lucky number chosen by the model.",
                    "properties": {"value": {"title": "Value", "type": "integer"}},
                    "required": ["value"],
                    "title": "LuckyNumber",
                    "type": "object",
                },
                "mode": "json",
                "formatting_instructions": """\
Respond only with valid JSON that matches this exact schema:
{
  "description": "A lucky number chosen by the model.",
  "properties": {
    "value": {
      "title": "Value",
      "type": "integer"
    }
  },
  "required": [
    "value"
  ],
  "title": "LuckyNumber",
  "type": "object"
}\
""",
            },
            "tools": [],
            "usage": {
                "input_tokens": 226,
                "output_tokens": 18,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "None",
                "total_tokens": 244,
            },
            "n_chunks": 6,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "anthropic",
            "model_id": "anthropic/claude-sonnet-4-0",
            "provider_model_name": "claude-sonnet-4-0",
            "finish_reason": None,
            "messages": [
                SystemMessage(
                    content=Text(
                        text="""\
Respond only with valid JSON that matches this exact schema:
{
  "description": "A lucky number chosen by the model.",
  "properties": {
    "value": {
      "title": "Value",
      "type": "integer"
    }
  },
  "required": [
    "value"
  ],
  "title": "LuckyNumber",
  "type": "object"
}\
"""
                    )
                ),
                UserMessage(
                    content=[Text(text="Pick a random number between 1 and 1000")]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
{
  "value": 742
}\
"""
                        )
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "text",
                                "text": """\
{
  "value": 742
}\
""",
                            }
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        Text(
                            text="""\
Your response failed schema validation:
1 validation error for LuckyNumber
value
  Value error, The number must be exactly 173, but got 742 [type=value_error, input_value=742, input_type=int]
    For further information visit https://errors.pydantic.dev/2.12/v/value_error

Please correct these issues and respond again.\
"""
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
{
  "value": 173
}\
"""
                        )
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "text",
                                "text": """\
{
  "value": 173
}\
""",
                            }
                        ],
                    },
                ),
            ],
            "format": {
                "name": "LuckyNumber",
                "description": "A lucky number chosen by the model.",
                "schema": {
                    "description": "A lucky number chosen by the model.",
                    "properties": {"value": {"title": "Value", "type": "integer"}},
                    "required": ["value"],
                    "title": "LuckyNumber",
                    "type": "object",
                },
                "mode": "json",
                "formatting_instructions": """\
Respond only with valid JSON that matches this exact schema:
{
  "description": "A lucky number chosen by the model.",
  "properties": {
    "value": {
      "title": "Value",
      "type": "integer"
    }
  },
  "required": [
    "value"
  ],
  "title": "LuckyNumber",
  "type": "object"
}\
""",
            },
            "tools": [],
            "usage": {
                "input_tokens": 221,
                "output_tokens": 13,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "None",
                "total_tokens": 234,
            },
            "n_chunks": 6,
        }
    }
)
