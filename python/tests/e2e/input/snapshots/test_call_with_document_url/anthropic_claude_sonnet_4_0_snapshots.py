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
            "provider_id": "anthropic",
            "model_id": "anthropic/claude-sonnet-4-0",
            "provider_model_name": "claude-sonnet-4-0",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 1617,
                "output_tokens": 16,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "Usage(cache_creation=CacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=1617, output_tokens=16, server_tool_use=None, service_tier='standard', inference_geo='not_available')",
                "total_tokens": 1633,
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
                            text="This is a dummy or placeholder PDF file with no actual content."
                        )
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "citations": None,
                                "text": "This is a dummy or placeholder PDF file with no actual content.",
                                "type": "text",
                            }
                        ],
                    },
                ),
            ],
            "format": None,
            "tools": [],
        }
    }
)
