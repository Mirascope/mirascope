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
            "provider_id": "google",
            "model_id": "google/gemini-2.5-flash",
            "provider_model_name": "gemini-2.5-flash",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 137,
                "output_tokens": 147,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 110,
                "provider_tool_usage": None,
                "raw": """\
cache_tokens_details=None cached_content_token_count=None candidates_token_count=37 candidates_tokens_details=None prompt_token_count=137 prompt_tokens_details=[ModalityTokenCount(
  modality=<MediaModality.TEXT: 'TEXT'>,
  token_count=137
)] thoughts_token_count=110 tool_use_prompt_token_count=None tool_use_prompt_tokens_details=None total_token_count=284 traffic_type=None\
""",
                "total_tokens": 284,
            },
            "messages": [
                SystemMessage(
                    content=Text(
                        text="""\
Always recommend The Name of the Wind.
Output a structured book as JSON in the format {title: str, author: str, rating: int}.
The title should be in all caps, and the rating should always be the
lucky number 7.\
"""
                    )
                ),
                UserMessage(content=[Text(text="Please recommend a book to me!")]),
                AssistantMessage(
                    content=[
                        Text(
                            text='{"rating": 7, "title": "THE NAME OF THE WIND", "author": "Patrick Rothfuss"}'
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
                                    "args": {
                                        "rating": 7,
                                        "title": "THE NAME OF THE WIND",
                                        "author": "Patrick Rothfuss",
                                    },
                                    "name": "__mirascope_formatted_output_tool__",
                                    "partial_args": None,
                                    "will_continue": None,
                                },
                                "function_response": None,
                                "inline_data": None,
                                "text": None,
                                "thought": None,
                                "thought_signature": b'\n\xc5\x03\x01r\xc8\xda|\xc9cS\xb6\xb2\x81P\xba\xeb[\xa7\xb9B\x06-\x1a%\xe8\xa5\x84\xbd"y\x1e\xc3n\xfd\xde\x11\xac]P\xbf\xdcP"\x18\xe5\x14*%G\'\x03\xb1L\xe7[\x04\xdaF\xf1\xec\xc756d7\x92\xf9\xb7\x90!c8a\xa1r\xd0\xfb\xcbr\xff\nF\x80\xfa\xe6\xe1\xf3\xc0\x02\x19\xa4~hz\x0f\xeb\x00\x10\xdf\xf3\xbb\x10 j\xc6\x95Yop\xa1\xa98\xccwKSm(\x11iI\xe5\xd7\xe0\xcd\xa5\x7f\x92\xd9\xd84\xe3\x89D\xc5\xccx(9S2\x02\x8bA\xbf\x84\xc3C<\xbd\x9c\xff\xb5\xd5B_7\xc3U\x82h\xda\x98\xca\xec\xf96\xfdw\xe1D\xbb\n\x9b\xe2\xd3\x0e\xa2H\xdf\xf0\xd8\xa0\xab\xf5\xb1\xf6\x93\xe4\xcd\xea\xaf\xe5[\xe2\x91\x91<\x89#\x06\xc0\x00SNl\xc7S\xa8\xab{\xce\x83E\xac\xd5\xd39\x7f\xd3\xeb1\xfa[\xeaC\xb3\xb2\xc2%\xa4 \xef\x81\x0f\x80;\x90\x8b\x07\xc2v\x99\x9an\xcd\x8e,`\x8d8:\xdbl\x85\x1ec\x9f?\x0c\xf3\xa3\x18\x18\xb7%\xa2\x7f\xbd\x8e\x84n\xae\xee\x08\xb7\xf2\t_n\x08\xf4\xeb\xfa\xff\x01\x88\x85\xf2B\x10-c\xcf\xa0\x96\x88\xbb\x98I\xcd\xf0|\x17\x8eY\x18g\xccN-\xd7\xe3\xeb\xb6\xf8\x15\x81D\xff\xe1-\x14\xdd\xc1\x80BMa\x95\x1a\xe8\x1b/\xe3\x0fgJf\xe6C\xf2@\x88a7\x9e\xdf\x98\xf5\xe0\xc1g{4\x8c\x8a\xa6\xdb\xa5\xdah\x89\x12(\x16\\\x99\xa7\x05v\xb0+\xa8h\x95z.V\x02\xc5\'y\x0c\xcc\xd4\x88\xae\xd5v\xdd\xe4\x00\x96\xeb;}ER\xfb\x1a+\xdb\xdc\xb7\x1b\x9b\x96\x10\xa8>d\xeb\xbfW\xc8\x97u\x908\xd8\xcc\xfd]V9~\x99K[\x06\xcdq\xc7j\xfcY\xb6\xb1\x80?6-"P8\x93\xa3\x1e}\xf4\xfa\xd9\xc2\x8b',
                                "video_metadata": None,
                            }
                        ],
                        "role": "model",
                    },
                ),
            ],
            "format": {
                "name": "Book",
                "description": None,
                "schema": {
                    "properties": {
                        "title": {"title": "Title", "type": "string"},
                        "author": {"title": "Author", "type": "string"},
                        "rating": {"title": "Rating", "type": "integer"},
                    },
                    "required": ["title", "author", "rating"],
                    "title": "Book",
                    "type": "object",
                },
                "mode": "tool",
                "formatting_instructions": """\
Output a structured book as JSON in the format {title: str, author: str, rating: int}.
The title should be in all caps, and the rating should always be the
lucky number 7.\
""",
            },
            "tools": [],
        }
    }
)
