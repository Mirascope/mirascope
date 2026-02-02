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
            "provider_id": "openai",
            "model_id": "openai/gpt-4o:responses",
            "provider_model_name": "gpt-4o:responses",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 259,
                "output_tokens": 77,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "ResponseUsage(input_tokens=259, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=77, output_tokens_details=OutputTokensDetails(reasoning_tokens=0), total_tokens=336)",
                "total_tokens": 336,
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
  "type": "object",
  "value": 523
}\
"""
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:responses",
                    provider_model_name="gpt-4o:responses",
                    raw_message=[
                        {
                            "id": "msg_0b7cca57772e10810069811834134c819483c9708e654f78db",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
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
  "type": "object",
  "value": 523
}\
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
                UserMessage(
                    content=[
                        Text(
                            text="""\
Your response failed schema validation:
1 validation error for LuckyNumber
value
  Value error, The number must be exactly 173, but got 523 [type=value_error, input_value=523, input_type=int]
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
  "type": "object",
  "value": 173
}\
"""
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:responses",
                    provider_model_name="gpt-4o:responses",
                    raw_message=[
                        {
                            "id": "msg_0b7cca57772e10810069811835fff481949ecd481b72d53c19",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
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
  "type": "object",
  "value": 173
}\
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
            "provider_id": "openai",
            "model_id": "openai/gpt-4o:responses",
            "provider_model_name": "gpt-4o:responses",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 192,
                "output_tokens": 10,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "ResponseUsage(input_tokens=192, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=10, output_tokens_details=OutputTokensDetails(reasoning_tokens=0), total_tokens=202)",
                "total_tokens": 202,
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
  "value": 527
}\
"""
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:responses",
                    provider_model_name="gpt-4o:responses",
                    raw_message=[
                        {
                            "id": "msg_0ba50e502a78d1ff00698117130a408190863dc2b07bf86d5a",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
{
  "value": 527
}\
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
                UserMessage(
                    content=[
                        Text(
                            text="""\
Your response failed schema validation:
1 validation error for LuckyNumber
value
  Value error, The number must be exactly 173, but got 527 [type=value_error, input_value=527, input_type=int]
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
                    provider_id="openai",
                    model_id="openai/gpt-4o:responses",
                    provider_model_name="gpt-4o:responses",
                    raw_message=[
                        {
                            "id": "msg_0ba50e502a78d1ff006981171418b88190812df6a1b9b7ebcf",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
{
  "value": 173
}\
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
            "provider_id": "openai",
            "model_id": "openai/gpt-4o:responses",
            "provider_model_name": "gpt-4o:responses",
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
  "type": "object",
  "value": 732
}\
"""
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:responses",
                    provider_model_name="gpt-4o:responses",
                    raw_message=[
                        {
                            "id": "msg_046307f1c43b3f910069811717b4f48196b53d4b849e18cc44",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
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
  "type": "object",
  "value": 732
}\
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
                UserMessage(
                    content=[
                        Text(
                            text="""\
Your response failed schema validation:
1 validation error for LuckyNumber
value
  Value error, The number must be exactly 173, but got 732 [type=value_error, input_value=732, input_type=int]
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
  "type": "object",
  "value": 173
}\
"""
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:responses",
                    provider_model_name="gpt-4o:responses",
                    raw_message=[
                        {
                            "id": "msg_046307f1c43b3f910069811718d40481969ff6e09a64dba9c3",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
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
  "type": "object",
  "value": 173
}\
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
                "input_tokens": 259,
                "output_tokens": 77,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "None",
                "total_tokens": 336,
            },
            "n_chunks": 78,
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
  "type": "object",
   "value": 527
}\
"""
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:responses",
                    provider_model_name="gpt-4o:responses",
                    raw_message=[
                        {
                            "id": "msg_01010f339bb73f14006981171d57e88193a439922170f15182",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
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
  "type": "object",
   "value": 527
}\
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
                UserMessage(
                    content=[
                        Text(
                            text="""\
Your response failed schema validation:
1 validation error for LuckyNumber
value
  Value error, The number must be exactly 173, but got 527 [type=value_error, input_value=527, input_type=int]
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
  "type": "object",
  "value": 173
}\
"""
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:responses",
                    provider_model_name="gpt-4o:responses",
                    raw_message=[
                        {
                            "id": "msg_01010f339bb73f14006981171edaa48193b35e5a62ae1400d6",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
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
  "type": "object",
  "value": 173
}\
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
                "input_tokens": 259,
                "output_tokens": 77,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "None",
                "total_tokens": 336,
            },
            "n_chunks": 78,
        }
    }
)
