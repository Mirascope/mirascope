from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    SystemMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider_id": "google",
            "model_id": "google/gemini-2.5-flash",
            "provider_model_name": "gemini-2.5-flash",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 125,
                "output_tokens": 51,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 41,
                "provider_tool_usage": None,
                "raw": """\
cache_tokens_details=None cached_content_token_count=None candidates_token_count=10 candidates_tokens_details=None prompt_token_count=125 prompt_tokens_details=[ModalityTokenCount(
  modality=<MediaModality.TEXT: 'TEXT'>,
  token_count=125
)] thoughts_token_count=41 tool_use_prompt_token_count=None tool_use_prompt_tokens_details=None total_token_count=176 traffic_type=None\
""",
                "total_tokens": 176,
            },
            "messages": [
                SystemMessage(
                    content=Text(
                        text="""\
Respond only with valid JSON that matches this exact schema:
{
  "description": "Wrapper for primitive type int",
  "properties": {
    "output": {
      "title": "Output",
      "type": "integer"
    }
  },
  "required": [
    "output"
  ],
  "title": "intOutput",
  "type": "object"
}\
"""
                    )
                ),
                UserMessage(
                    content=[Text(text="Choose a lucky number between 1 and 10")]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
{
  "output": 7
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
  "output": 7
}\
""",
                                "type": "text",
                            }
                        ],
                    },
                ),
                UserMessage(
                    content=[Text(text="Ok, now choose a different lucky number")]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
{
  "output": 3
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
  "output": 3
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
                "name": "int",
                "description": None,
                "schema": {
                    "description": "Wrapper for primitive type int",
                    "properties": {"output": {"title": "Output", "type": "integer"}},
                    "required": ["output"],
                    "title": "intOutput",
                    "type": "object",
                },
                "mode": "json",
                "formatting_instructions": """\
Respond only with valid JSON that matches this exact schema:
{
  "description": "Wrapper for primitive type int",
  "properties": {
    "output": {
      "title": "Output",
      "type": "integer"
    }
  },
  "required": [
    "output"
  ],
  "title": "intOutput",
  "type": "object"
}\
""",
            },
            "tools": [],
        }
    }
)
