from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
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
                "input_tokens": 69,
                "output_tokens": 54,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "CompletionUsage(completion_tokens=54, prompt_tokens=69, total_tokens=123, completion_tokens_details=None, prompt_tokens_details=None)",
                "total_tokens": 123,
            },
            "messages": [
                UserMessage(content=[Text(text="")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="<reasoning>The user didn't say anything. It's an empty prompt. As assistant, we must respond politely, asking to clarify.</reasoning>It looks like your message came through empty. Could you let me know how I can help you today?"
                        )
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/openai.gpt-oss-20b-1:0",
                    provider_model_name="openai.gpt-oss-20b-1:0",
                    raw_message={
                        "content": "<reasoning>The user didn't say anything. It's an empty prompt. As assistant, we must respond politely, asking to clarify.</reasoning>It looks like your message came through empty. Could you let me know how I can help you today?",
                        "role": "assistant",
                    },
                ),
            ],
            "format": None,
            "tools": [],
        }
    }
)
