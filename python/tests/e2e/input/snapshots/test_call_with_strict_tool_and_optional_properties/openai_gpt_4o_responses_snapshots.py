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
            "provider_id": "openai",
            "model_id": "openai/gpt-4o:responses",
            "provider_model_name": "gpt-4o:responses",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 124,
                "output_tokens": 24,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "ResponseUsage(input_tokens=124, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=24, output_tokens_details=OutputTokensDetails(reasoning_tokens=0), total_tokens=148)",
                "total_tokens": 148,
            },
            "messages": [
                UserMessage(
                    content=[Text(text="What's the weather like in San Francisco?")]
                ),
                AssistantMessage(
                    content=[
                        ToolCall(
                            id="call_guWIDINadhibniyiyQnbRyK7",
                            name="get_current_weather",
                            args='{"location":"San Francisco, CA","unit":"fahrenheit"}',
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:responses",
                    provider_model_name="gpt-4o:responses",
                    raw_message=[
                        {
                            "arguments": '{"location":"San Francisco, CA","unit":"fahrenheit"}',
                            "call_id": "call_guWIDINadhibniyiyQnbRyK7",
                            "name": "get_current_weather",
                            "type": "function_call",
                            "id": "fc_08ae84fb07f3f4f200696933a5b970819592fba17bc5ee0bb5",
                            "status": "completed",
                        }
                    ],
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
