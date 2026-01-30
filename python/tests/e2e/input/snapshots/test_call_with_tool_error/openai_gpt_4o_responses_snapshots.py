from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
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
                "input_tokens": 65,
                "output_tokens": 25,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "ResponseUsage(input_tokens=65, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=25, output_tokens_details=OutputTokensDetails(reasoning_tokens=0), total_tokens=90)",
                "total_tokens": 90,
            },
            "messages": [
                UserMessage(
                    content=[
                        Text(
                            text="Use the test tool to retrieve the secret phrase. The passphrase is 'portal"
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="It seems like the passphrase you provided is incomplete due to formatting. Could you please provide the complete passphrase?"
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:responses",
                    provider_model_name="gpt-4o:responses",
                    raw_message=[
                        {
                            "id": "msg_02dd2500e3d14768006972e26ad6a48197ac5391c721c8de9c",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": "It seems like the passphrase you provided is incomplete due to formatting. Could you please provide the complete passphrase?",
                                    "type": "output_text",
                                    "logprobs": [],
                                }
                            ],
                            "role": "assistant",
                            "status": "completed",
                            "type": "message",
                        }
                    ],
                ),
            ],
            "format": None,
            "tools": [
                {
                    "name": "passphrase_test_tool",
                    "description": "A tool that must be called with a passphrase.",
                    "parameters": """\
{
  "properties": {
    "passphrase": {
      "title": "Passphrase",
      "type": "string"
    }
  },
  "required": [
    "passphrase"
  ],
  "additionalProperties": false,
  "defs": null
}\
""",
                    "strict": None,
                }
            ],
        },
        "tool_outputs": [],
    }
)
