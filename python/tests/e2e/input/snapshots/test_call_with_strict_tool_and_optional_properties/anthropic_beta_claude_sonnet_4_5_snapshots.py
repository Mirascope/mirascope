from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    ToolCall,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider_id": "anthropic",
            "model_id": "anthropic-beta/claude-sonnet-4-5",
            "provider_model_name": "claude-sonnet-4-5",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 677,
                "output_tokens": 58,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "BetaUsage(cache_creation=BetaCacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=677, output_tokens=58, server_tool_use=None, service_tier='standard')",
                "total_tokens": 735,
            },
            "messages": [
                UserMessage(
                    content=[Text(text="What's the weather like in San Francisco?")]
                ),
                AssistantMessage(
                    content=[
                        ToolCall(
                            id="toolu_018mMkRcHDPE2cc1hfmknQzZ",
                            name="get_current_weather",
                            args='{"location": "San Francisco, CA"}',
                        )
                    ],
                    provider_id="anthropic",
                    model_id="anthropic-beta/claude-sonnet-4-5",
                    provider_model_name="claude-sonnet-4-5",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "id": "toolu_018mMkRcHDPE2cc1hfmknQzZ",
                                "input": {"location": "San Francisco, CA"},
                                "name": "get_current_weather",
                                "type": "tool_use",
                            }
                        ],
                    },
                ),
            ],
            "format": None,
            "tools": [
                {
                    "name": "get_current_weather",
                    "description": """\
Get the current weather in a given location.

Args:
    location: The city and state, e.g. San Francisco, CA
    unit: The temperature unit to use (fahrenheit or celsius)\
""",
                    "parameters": """\
{
  "properties": {
    "location": {
      "description": "The city and state, e.g. San Francisco, CA",
      "title": "Location",
      "type": "string"
    },
    "unit": {
      "default": "fahrenheit",
      "description": "The temperature unit to use (fahrenheit or celsius)",
      "title": "Unit",
      "type": "string"
    }
  },
  "required": [
    "location"
  ],
  "additionalProperties": false,
  "defs": null
}\
""",
                    "strict": True,
                }
            ],
        }
    }
)
