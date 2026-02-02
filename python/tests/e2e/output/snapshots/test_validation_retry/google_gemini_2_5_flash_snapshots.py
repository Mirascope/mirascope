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
            "provider_id": "google",
            "model_id": "google/gemini-2.5-flash",
            "provider_model_name": "gemini-2.5-flash",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 215,
                "output_tokens": 82,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 70,
                "provider_tool_usage": None,
                "raw": """\
cache_tokens_details=None cached_content_token_count=None candidates_token_count=12 candidates_tokens_details=None prompt_token_count=215 prompt_tokens_details=[ModalityTokenCount(
  modality=<MediaModality.TEXT: 'TEXT'>,
  token_count=215
)] thoughts_token_count=70 tool_use_prompt_token_count=None tool_use_prompt_tokens_details=None total_token_count=297 traffic_type=None\
""",
                "total_tokens": 297,
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
  "value": 731
}\
"""
                        )
                    ],
                    provider_id="google",
                    model_id="google/gemini-2.5-flash",
                    provider_model_name="gemini-2.5-flash",
                    raw_message={
                        "parts": [
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": """\
{
  "value": 731
}\
""",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            }
                        ],
                        "role": "model",
                    },
                ),
                UserMessage(
                    content=[
                        Text(
                            text="""\
Your response failed schema validation:
1 validation error for LuckyNumber
value
  Value error, The number must be exactly 173, but got 731 [type=value_error, input_value=731, input_type=int]
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
                    provider_id="google",
                    model_id="google/gemini-2.5-flash",
                    provider_model_name="gemini-2.5-flash",
                    raw_message={
                        "parts": [
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": """\
{
  "value": 173
}\
""",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            }
                        ],
                        "role": "model",
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
            "provider_id": "google",
            "model_id": "google/gemini-2.5-flash",
            "provider_model_name": "gemini-2.5-flash",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 215,
                "output_tokens": 62,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 50,
                "provider_tool_usage": None,
                "raw": """\
cache_tokens_details=None cached_content_token_count=None candidates_token_count=12 candidates_tokens_details=None prompt_token_count=215 prompt_tokens_details=[ModalityTokenCount(
  modality=<MediaModality.TEXT: 'TEXT'>,
  token_count=215
)] thoughts_token_count=50 tool_use_prompt_token_count=None tool_use_prompt_tokens_details=None total_token_count=277 traffic_type=None\
""",
                "total_tokens": 277,
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
  "value": 731
}\
"""
                        )
                    ],
                    provider_id="google",
                    model_id="google/gemini-2.5-flash",
                    provider_model_name="gemini-2.5-flash",
                    raw_message={
                        "parts": [
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": """\
{
  "value": 731
}\
""",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            }
                        ],
                        "role": "model",
                    },
                ),
                UserMessage(
                    content=[
                        Text(
                            text="""\
Your response failed schema validation:
1 validation error for LuckyNumber
value
  Value error, The number must be exactly 173, but got 731 [type=value_error, input_value=731, input_type=int]
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
                    provider_id="google",
                    model_id="google/gemini-2.5-flash",
                    provider_model_name="gemini-2.5-flash",
                    raw_message={
                        "parts": [
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": """\
{
  "value": 173
}\
""",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            }
                        ],
                        "role": "model",
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
            "provider_id": "google",
            "model_id": "google/gemini-2.5-flash",
            "provider_model_name": "gemini-2.5-flash",
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
  "value": 573
}\
"""
                        )
                    ],
                    provider_id="google",
                    model_id="google/gemini-2.5-flash",
                    provider_model_name="gemini-2.5-flash",
                    raw_message={
                        "parts": [
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": """\
{
  "value": 57\
""",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": """\
3
}\
""",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                        ],
                        "role": "model",
                    },
                ),
                UserMessage(
                    content=[
                        Text(
                            text="""\
Your response failed schema validation:
1 validation error for LuckyNumber
value
  Value error, The number must be exactly 173, but got 573 [type=value_error, input_value=573, input_type=int]
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
                    provider_id="google",
                    model_id="google/gemini-2.5-flash",
                    provider_model_name="gemini-2.5-flash",
                    raw_message={
                        "parts": [
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": """\
{
  "value": 173
}\
""",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            }
                        ],
                        "role": "model",
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
                "input_tokens": 215,
                "output_tokens": 12,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 84,
                "provider_tool_usage": None,
                "raw": "None",
                "total_tokens": 227,
            },
            "n_chunks": 3,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "google",
            "model_id": "google/gemini-2.5-flash",
            "provider_model_name": "gemini-2.5-flash",
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
  "value": 731
}\
"""
                        )
                    ],
                    provider_id="google",
                    model_id="google/gemini-2.5-flash",
                    provider_model_name="gemini-2.5-flash",
                    raw_message={
                        "parts": [
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": """\
{
  "value": 7\
""",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": """\
31
}\
""",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                        ],
                        "role": "model",
                    },
                ),
                UserMessage(
                    content=[
                        Text(
                            text="""\
Your response failed schema validation:
1 validation error for LuckyNumber
value
  Value error, The number must be exactly 173, but got 731 [type=value_error, input_value=731, input_type=int]
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
                    provider_id="google",
                    model_id="google/gemini-2.5-flash",
                    provider_model_name="gemini-2.5-flash",
                    raw_message={
                        "parts": [
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": """\
{
  "value": 173
}\
""",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            }
                        ],
                        "role": "model",
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
                "input_tokens": 215,
                "output_tokens": 12,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 73,
                "provider_tool_usage": None,
                "raw": "None",
                "total_tokens": 227,
            },
            "n_chunks": 3,
        }
    }
)
