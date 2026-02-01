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
            "model_id": "openai/gpt-4o:completions",
            "provider_model_name": "gpt-4o:completions",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 130,
                "output_tokens": 23,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "CompletionUsage(completion_tokens=23, prompt_tokens=130, total_tokens=153, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=0, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0))",
                "total_tokens": 153,
            },
            "messages": [
                UserMessage(
                    content=[Text(text="What's the weather like in San Francisco?")]
                ),
                AssistantMessage(
                    content=[
                        ToolCall(
                            id="call_c4yXh9W3Zrvkf4Jfp1Dia6HS",
                            name="get_current_weather",
                            args='{"location":"San Francisco, CA","unit":"fahrenheit"}',
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:completions",
                    provider_model_name="gpt-4o:completions",
                    raw_message={
                        "role": "assistant",
                        "annotations": [],
                        "tool_calls": [
                            {
                                "id": "call_c4yXh9W3Zrvkf4Jfp1Dia6HS",
                                "function": {
                                    "arguments": '{"location":"San Francisco, CA","unit":"fahrenheit"}',
                                    "name": "get_current_weather",
                                },
                                "type": "function",
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
