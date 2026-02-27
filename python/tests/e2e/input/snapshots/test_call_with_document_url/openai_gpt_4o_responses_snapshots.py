from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Document,
    Text,
    URLDocumentSource,
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
                "input_tokens": 26,
                "output_tokens": 15,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "ResponseUsage(input_tokens=26, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=15, output_tokens_details=OutputTokensDetails(reasoning_tokens=0), total_tokens=41)",
                "total_tokens": 41,
            },
            "messages": [
                UserMessage(
                    content=[
                        Text(
                            text="What is this PDF about? Reply in one short sentence."
                        ),
                        Document(
                            source=URLDocumentSource(
                                type="url_document_source",
                                url="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
                            )
                        ),
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="The PDF is likely a placeholder or sample file used for testing purposes."
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:responses",
                    provider_model_name="gpt-4o:responses",
                    raw_message=[
                        {
                            "id": "msg_0b9ce8c5e6f6dbd9006986f69ff4a8819cbef4eccd37857b09",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": "The PDF is likely a placeholder or sample file used for testing purposes.",
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
            "tools": [],
        }
    }
)
