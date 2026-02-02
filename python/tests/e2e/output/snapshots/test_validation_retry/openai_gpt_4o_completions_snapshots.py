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
            "model_id": "openai/gpt-4o:completions",
            "provider_model_name": "gpt-4o:completions",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 192,
                "output_tokens": 9,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "CompletionUsage(completion_tokens=9, prompt_tokens=192, total_tokens=201, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=0, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0))",
                "total_tokens": 201,
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
  "value": 467
}\
"""
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:completions",
                    provider_model_name="gpt-4o:completions",
                    raw_message={
                        "content": """\
{
  "value": 467
}\
""",
                        "role": "assistant",
                        "annotations": [],
                    },
                ),
                UserMessage(
                    content=[
                        Text(
                            text="""\
Your response failed schema validation:
1 validation error for LuckyNumber
value
  Value error, The number must be exactly 173, but got 467 [type=value_error, input_value=467, input_type=int]
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
                    model_id="openai/gpt-4o:completions",
                    provider_model_name="gpt-4o:completions",
                    raw_message={
                        "content": """\
{
  "value": 173
}\
""",
                        "role": "assistant",
                        "annotations": [],
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
            "provider_id": "openai",
            "model_id": "openai/gpt-4o:completions",
            "provider_model_name": "gpt-4o:completions",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 192,
                "output_tokens": 9,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "CompletionUsage(completion_tokens=9, prompt_tokens=192, total_tokens=201, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=0, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0))",
                "total_tokens": 201,
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
  "value": 348
}\
"""
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:completions",
                    provider_model_name="gpt-4o:completions",
                    raw_message={
                        "content": """\
{
  "value": 348
}\
""",
                        "role": "assistant",
                        "annotations": [],
                    },
                ),
                UserMessage(
                    content=[
                        Text(
                            text="""\
Your response failed schema validation:
1 validation error for LuckyNumber
value
  Value error, The number must be exactly 173, but got 348 [type=value_error, input_value=348, input_type=int]
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
                    model_id="openai/gpt-4o:completions",
                    provider_model_name="gpt-4o:completions",
                    raw_message={
                        "content": """\
{
  "value": 173
}\
""",
                        "role": "assistant",
                        "annotations": [],
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
            "provider_id": "openai",
            "model_id": "openai/gpt-4o:completions",
            "provider_model_name": "gpt-4o:completions",
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
  "value": 623
}\
"""
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:completions",
                    provider_model_name="gpt-4o:completions",
                    raw_message=None,
                ),
                UserMessage(
                    content=[
                        Text(
                            text="""\
Your response failed schema validation:
1 validation error for LuckyNumber
value
  Value error, The number must be exactly 173, but got 623 [type=value_error, input_value=623, input_type=int]
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
                    model_id="openai/gpt-4o:completions",
                    provider_model_name="gpt-4o:completions",
                    raw_message=None,
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
                "input_tokens": 192,
                "output_tokens": 9,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "None",
                "total_tokens": 201,
            },
            "n_chunks": 11,
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
  "value": 389
}\
"""
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:completions",
                    provider_model_name="gpt-4o:completions",
                    raw_message=None,
                ),
                UserMessage(
                    content=[
                        Text(
                            text="""\
Your response failed schema validation:
1 validation error for LuckyNumber
value
  Value error, The number must be exactly 173, but got 389 [type=value_error, input_value=389, input_type=int]
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
                    model_id="openai/gpt-4o:completions",
                    provider_model_name="gpt-4o:completions",
                    raw_message=None,
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
                "input_tokens": 192,
                "output_tokens": 9,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "None",
                "total_tokens": 201,
            },
            "n_chunks": 11,
        }
    }
)
