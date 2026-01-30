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
            "model_id": "anthropic/claude-haiku-4-5",
            "provider_model_name": "claude-haiku-4-5",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 40,
                "output_tokens": 37,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "Usage(cache_creation=CacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=40, output_tokens=37, server_tool_use=None, service_tier='standard')",
                "total_tokens": 77,
            },
            "messages": [
                SystemMessage(
                    content=Text(
                        text="Return book as XML: <book><title>Mistborn</title><rating>7</rating></book>"
                    )
                ),
                UserMessage(content=[Text(text="The Name of the Wind, Rating 7")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
```xml
<book>
  <title>The Name of the Wind</title>
  <rating>7</rating>
</book>
```\
"""
                        )
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-haiku-4-5",
                    provider_model_name="claude-haiku-4-5",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "citations": None,
                                "text": """\
```xml
<book>
  <title>The Name of the Wind</title>
  <rating>7</rating>
</book>
```\
""",
                                "type": "text",
                            }
                        ],
                    },
                ),
            ],
            "format": {
                "name": "parse_book",
                "description": None,
                "schema": {},
                "mode": "parser",
                "formatting_instructions": "Return book as XML: <book><title>Mistborn</title><rating>7</rating></book>",
            },
            "tools": [],
        }
    }
)
