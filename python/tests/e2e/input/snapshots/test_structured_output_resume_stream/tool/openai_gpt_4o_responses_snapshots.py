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
            "model_id": "openai/gpt-4o:responses",
            "provider_model_name": "gpt-4o:responses",
            "finish_reason": None,
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
                    content=[Text(text='{"output":7}')],
                    provider_id="openai",
                    model_id="openai/gpt-4o:responses",
                    provider_model_name="gpt-4o:responses",
                    raw_message=[
                        {
                            "arguments": '{"output":7}',
                            "call_id": "call_lQWOvv3zMMkSzW3VZAdYbKgD",
                            "name": "__mirascope_formatted_output_tool__",
                            "type": "function_call",
                            "id": "fc_0bef6de8dc88461900698a6de3939c81938f97a6ec58e4f61e",
                            "status": "completed",
                        }
                    ],
                ),
                UserMessage(
                    content=[Text(text="Ok, now choose a different lucky number")]
                ),
                AssistantMessage(
                    content=[Text(text='{"output":3}')],
                    provider_id="openai",
                    model_id="openai/gpt-4o:responses",
                    provider_model_name="gpt-4o:responses",
                    raw_message=[
                        {
                            "arguments": '{"output":3}',
                            "call_id": "call_Ylr2NoohzvnoLrcbctLjrGJP",
                            "name": "__mirascope_formatted_output_tool__",
                            "type": "function_call",
                            "id": "fc_031f356f68cef05900698a6de4cfac81958716b0fc4c4d629a",
                            "status": "completed",
                        }
                    ],
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
            "usage": {
                "input_tokens": 128,
                "output_tokens": 6,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "None",
                "total_tokens": 134,
            },
            "n_chunks": 7,
        }
    }
)
