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
            "provider_id": "google",
            "model_id": "google/gemini-2.5-flash",
            "provider_model_name": "gemini-2.5-flash",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 129,
                "output_tokens": 137,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 117,
                "raw": """\
cache_tokens_details=None cached_content_token_count=None candidates_token_count=20 candidates_tokens_details=None prompt_token_count=129 prompt_tokens_details=[ModalityTokenCount(
  modality=<MediaModality.TEXT: 'TEXT'>,
  token_count=129
)] thoughts_token_count=117 tool_use_prompt_token_count=None tool_use_prompt_tokens_details=None total_token_count=266 traffic_type=None\
""",
                "total_tokens": 266,
            },
            "messages": [
                UserMessage(
                    content=[Text(text="What's the weather like in San Francisco?")]
                ),
                AssistantMessage(
                    content=[
                        ToolCall(
                            id="google_unknown_tool_id",
                            name="get_current_weather",
                            args='{"location": "San Francisco, CA"}',
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
                                "function_call": {
                                    "id": None,
                                    "args": {"location": "San Francisco, CA"},
                                    "name": "get_current_weather",
                                    "partial_args": None,
                                    "will_continue": None,
                                },
                                "function_response": None,
                                "inline_data": None,
                                "text": None,
                                "thought": None,
                                "thought_signature": b"\n\x93\x04\x01r\xc8\xda||h\xfc}`\xe3\x05\xa0\x0e\xfd9\xd2\x07\xcaf\xb0R\xaa_P\x15\x0bq\x9b\x85x\x92\xb0|X\xacM\xd4\x887\x8b\xb0DHXSS\x16'\x046p\x82\xaaX\\\xca\x83\x84\x89A\xbf\xe8\xe7[\x95\xbd\x8d\xfb\xe0\x1dJ\x17\xa0\x15\xe6g\n\x05v\xce2\x08K\xbfV\x08\xb22\xdf\xbf\xd6#\xb3 \xb0G\xa7\xa1\xe8T\x1e\xe3\x0b?\xac\x0b8\xe9P\xc0\xb2f\x00\x0em\xbc\xb4\x1e\x90>\x12\x9e\x9e\x1e\x94\xd6\x9c\xf4\x8e\xac\x8e\xc0Ea6\xe8~9\x1b\x16\xca,\xa9v\x89\x12[V\xa3\xd2\x9b\xe1\xba\x8eb\xc2\x91\xa07\xacGR\xc6\x87\x8e\x06sO\xe7\xe5\xa4|\xdc\x1f\x80\x88\xddy\xd9\xcc\xa5\xde\xf2!\xcd\xc1\x1e\x99{\xdaW\xf1\x9c\xf6\xb8\x1b\xac\xad\xe1\x89b\xdd\x00\x93\xfc\xd3\x1eH\xad#\xd1\xd8\xe5;\x9c\xee\xc1QCZ\x10\x86\xfb\xe6\xbd\xd4\xebT*\x0885\xb2\xbbP\x1d5\xd1\xd2\\\x8f8\x8f\xc9\xba\xae\xa7\xe5\xdc\xe3\xec`\x07\xbd,\x1a\xc9r\xdd\xd5-\x1f\r\xc7\xc1g4\x8f\x88\x0e=U\xe8a\xbf\xaa\xcb\x11'X\x00\xcdFLM#\x7f\x93\xe1\xfb\xba\x16\x9f\x02\x9e\x85\xca\xee\xae5\xaa\x7f\xbd\xf4\x87\xd4]\x01\xed\xe4\xe9zH_\xb2$s\xc9\xa4$\xbb!B\xc5\xa7\xf1RN\xa4\xee\xcbiI6\xcf\x1d\xcc\x82\xe8x\xe1S\xc2c\x11\x17\xfe\xd63\x8eX\x06\xa8\x8b\xac2\xed8e\xf6a\xb5\xbb0mZ`g\x16&\xaf\xea\xd7M<uEn\xc5\x00\xce\x1dP~\xaeq/ \x97(\xc8\x9b\xbbc[D\xeeT\xfb\xfa\xe1\xf1\x9fUYa\xf8(\xa3\x96%q\xa4\xc5[y\xf0\x1f\n\xaa4q2;\xf9\xa6_\xfc4\x7fG\xed\xe0\xb16\xdaf\x03\xe1\xf7\x85e\x1c\xc7\x95*~\xb2R\xd0m\xde\x8c\xe1N\xde\xbf\xc1\x99\x08a\xbcrR\xc3\xad\"\x0f\xec\x18R$\x9e\x89k\xc9\x92\xe3\x07\x07Gv\x93\xcb\x1d\xeb\xc3\x83\xa5S\xf45\xd5\xbae\n)\x99?\xae\xbc\x04\xf9\x92\xb1\xc8\x07\"\xdfDaz\xb5\xf0\x1bhY6\xc8\xae\xe6\xecf\xc7i\x11\x191N\xd2",
                                "video_metadata": None,
                            }
                        ],
                        "role": "model",
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
