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
            "provider_id": "anthropic",
            "model_id": "anthropic/claude-sonnet-4-5",
            "provider_model_name": "claude-sonnet-4-5",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 141,
                "output_tokens": 18,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "Usage(cache_creation=CacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=141, output_tokens=18, server_tool_use=None, service_tier='standard', inference_geo='not_available')",
                "total_tokens": 159,
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
```json
{
  "output": 7
}
```\
"""
                        )
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-5",
                    provider_model_name="claude-sonnet-4-5",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "citations": None,
                                "text": """\
```json
{
  "output": 7
}
```\
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
```json
{
  "output": 3
}
```\
"""
                        )
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-5",
                    provider_model_name="claude-sonnet-4-5",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "citations": None,
                                "text": """\
```json
{
  "output": 3
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
