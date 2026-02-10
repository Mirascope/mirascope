from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Base64DocumentSource,
    Document,
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
                "input_tokens": 29,
                "output_tokens": 20,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "ResponseUsage(input_tokens=29, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=20, output_tokens_details=OutputTokensDetails(reasoning_tokens=0), total_tokens=49)",
                "total_tokens": 49,
            },
            "messages": [
                UserMessage(
                    content=[
                        Text(
                            text="What text is in this PDF document? Reply in one short sentence."
                        ),
                        Document(
                            source=Base64DocumentSource(
                                type="base64_document_source",
                                data="JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCgoyIDAgb2JqCjw8IC9UeXBlIC9QYWdlcyAvS2lkcyBbMyAwIFJdIC9Db3VudCAxID4+CmVuZG9iagoKMyAwIG9iago8PCAvVHlwZSAvUGFnZSAvUGFyZW50IDIgMCBSIC9NZWRpYUJveCBbMCAwIDYxMiA3OTJdCiAgIC9Db250ZW50cyA0IDAgUiAvUmVzb3VyY2VzIDw8IC9Gb250IDw8IC9GMSA1IDAgUiA+PiA+PiA+PgplbmRvYmoKCjQgMCBvYmoKPDwgL0xlbmd0aCA0NCA+PgpzdHJlYW0KQlQgL0YxIDI0IFRmIDEwMCA3MDAgVGQgKEhlbGxvLCB3b3JsZCEpIFRqIEVUCmVuZHN0cmVhbQplbmRvYmoKCjUgMCBvYmoKPDwgL1R5cGUgL0ZvbnQgL1N1YnR5cGUgL1R5cGUxIC9CYXNlRm9udCAvSGVsdmV0aWNhID4+CmVuZG9iagoKeHJlZgowIDYKMDAwMDAwMDAwMCA2NTUzNSBmCjAwMDAwMDAwMDkgMDAwMDAgbgowMDAwMDAwMDU4IDAwMDAwIG4KMDAwMDAwMDExNSAwMDAwMCBuCjAwMDAwMDAyNjYgMDAwMDAgbgowMDAwMDAwMzYwIDAwMDAwIG4KCnRyYWlsZXIKPDwgL1NpemUgNiAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYKNDM0CiUlRU9G",
                                media_type="application/pdf",
                            )
                        ),
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="I can't see the contents of the PDF, but I can help with other questions or tasks!"
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:responses",
                    provider_model_name="gpt-4o:responses",
                    raw_message=[
                        {
                            "id": "msg_0373be2aff90ed83006986f69e2fd0819c83ea9811f3bce6a1",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": "I can't see the contents of the PDF, but I can help with other questions or tasks!",
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
