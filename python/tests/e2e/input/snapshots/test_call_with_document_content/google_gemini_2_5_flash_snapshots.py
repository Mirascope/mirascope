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
            "provider_id": "google",
            "model_id": "google/gemini-2.5-flash",
            "provider_model_name": "gemini-2.5-flash",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 273,
                "output_tokens": 49,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 39,
                "provider_tool_usage": None,
                "raw": """\
cache_tokens_details=None cached_content_token_count=None candidates_token_count=10 candidates_tokens_details=None prompt_token_count=273 prompt_tokens_details=[ModalityTokenCount(
  modality=<MediaModality.TEXT: 'TEXT'>,
  token_count=15
), ModalityTokenCount(
  modality=<MediaModality.DOCUMENT: 'DOCUMENT'>,
  token_count=258
)] thoughts_token_count=39 tool_use_prompt_token_count=None tool_use_prompt_tokens_details=None total_token_count=322 traffic_type=None\
""",
                "total_tokens": 322,
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
                        Text(text='The document contains the text "Hello, world!".')
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
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": 'The document contains the text "Hello, world!".',
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            }
                        ],
                        "role": "model",
                    },
                ),
            ],
            "format": None,
            "tools": [],
        }
    }
)
