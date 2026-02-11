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
            "provider_id": "openai",
            "model_id": "openai/gpt-4o:completions",
            "provider_model_name": "gpt-4o:completions",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 131,
                "output_tokens": 5,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "CompletionUsage(completion_tokens=5, prompt_tokens=131, total_tokens=136, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=0, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0))",
                "total_tokens": 136,
            },
            "messages": [
                SystemMessage(
                    content=Text(
                        text="Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output."
                    )
                ),
                UserMessage(
                    content=[Text(text="Choose a lucky number between 1 and 10")]
                ),
                AssistantMessage(
                    content=[Text(text='{"output": 7}')],
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
                                    "args": {"output": 7},
                                    "name": "__mirascope_formatted_output_tool__",
                                    "partial_args": None,
                                    "will_continue": None,
                                },
                                "function_response": None,
                                "inline_data": None,
                                "text": None,
                                "thought": None,
                                "thought_signature": b"\n\xab\x02\x01\xbe>\xf6\xfb\x83\xd3;\x0e\x89X\xee\xc3\xa7\xaa\x16\xd8G'\x8f\x00\x92\x19\x11\x9d\xa3\x9e]G_\xc9\x8dJE;\xa8LJ\xcb\tf\xdc\xd4\xf7\x1fD\x91\xb9\xcc\x1f\x01\xcb'\x03\x0f\xc5B[Z5-l\xcf\xddS\ng\x85,\xb7S\x86\x05\xb2\x15\x17S\x9b\xc0\xc7\x8f\xb2R\xb5 \x9f\x0b\x0b\x8d\xedi\xabR\x19\xc5\xc0\x8b\x07@K\t\x84\xa1c+z\xbb\xd8QL+\x7f<Y\xda\x8ce&L\xe0\xa0\xfe\x8e\xb7\x14\xb6\xe1nk\x7fl\x8b\xc0G\xc7\x9f[$9\xe7x\xdd\xd6'\xc8+fG\x12z\x17\xaa\xa4E\xf8*\\\xa6L\xc6\x16\x1a\xea*\xf7I\nX\x10q\x1a\xeb\xdf,o\xbeF3dJC\xf9\xd85!(0\x9d\xbf\x9d\xbb\xdd\x99\x17\xc88 \xceZ\xbd\xc3\x17\x17!\xb45\x17\xcd\x9d)\x1f\xe6\x01\xdd\x82\x8b\x08\xd5/\x189_/\xf0@\x05\xed[:s\xbc\xe68\x07\xbcJ\xc5\xa5\xa7\x0c\x98\"\xde\xa2[&\xdb*\x9f\xea\xe1\xc1\x00\xb0\xa2\xd2nQ\x95o\xa8\x98\xfa\xfd\xae\x91\xab\x9d\xc6\x89\xc9l8I\x80\xfdM\xa9\xaa\xb9\xaeT\x02\x8d\x84]z{\xe1]\xd2f\x98\x89\x01L\x06\x9f\xf6",
                                "video_metadata": None,
                            }
                        ],
                        "role": "model",
                    },
                ),
                UserMessage(
                    content=[Text(text="Ok, now choose a different lucky number")]
                ),
                AssistantMessage(
                    content=[Text(text='{"output":3}')],
                    provider_id="openai",
                    model_id="openai/gpt-4o:completions",
                    provider_model_name="gpt-4o:completions",
                    raw_message={
                        "role": "assistant",
                        "annotations": [],
                        "tool_calls": [
                            {
                                "id": "call_sripKxDkHxxngN8KPJ9BpXBD",
                                "function": {
                                    "arguments": '{"output":3}',
                                    "name": "__mirascope_formatted_output_tool__",
                                },
                                "type": "function",
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
                "mode": "tool",
                "formatting_instructions": "Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output.",
            },
            "tools": [],
        }
    }
)
