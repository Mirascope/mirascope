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
            "provider_id": "bedrock",
            "model_id": "bedrock/openai.gpt-oss-20b-1:0",
            "provider_model_name": "openai.gpt-oss-20b-1:0",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 209,
                "output_tokens": 57,
                "cache_read_tokens": 32,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "CompletionUsage(completion_tokens=57, prompt_tokens=209, total_tokens=266, completion_tokens_details=None, prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=32))",
                "total_tokens": 266,
            },
            "messages": [
                UserMessage(
                    content=[Text(text="What's the weather like in San Francisco?")]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text='<reasoning>We need to call get_current_weather with location "San Francisco, CA" and unit "fahrenheit" (default).</reasoning>'
                        ),
                        ToolCall(
                            id="chatcmpl-tool-8f8eeaab35f80f8b",
                            name="get_current_weather",
                            args='{"location":"San Francisco, CA","unit":"fahrenheit"}',
                        ),
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/openai.gpt-oss-20b-1:0",
                    provider_model_name="openai.gpt-oss-20b-1:0",
                    raw_message={
                        "content": '<reasoning>We need to call get_current_weather with location "San Francisco, CA" and unit "fahrenheit" (default).</reasoning>',
                        "role": "assistant",
                        "tool_calls": [
                            {
                                "id": "chatcmpl-tool-8f8eeaab35f80f8b",
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
