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
                "output_tokens": 174,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 137,
                "raw": """\
cache_tokens_details=None cached_content_token_count=None candidates_token_count=37 candidates_tokens_details=None prompt_token_count=137 prompt_tokens_details=[ModalityTokenCount(
  modality=<MediaModality.TEXT: 'TEXT'>,
  token_count=137
)] thoughts_token_count=137 tool_use_prompt_token_count=None tool_use_prompt_tokens_details=None total_token_count=311 traffic_type=None\
""",
                "total_tokens": 311,
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
                            text='{"rating": 7, "author": "Patrick Rothfuss", "title": "THE NAME OF THE WIND"}'
                        )
                    ],
                    provider_id="google",
                    model_id="google/gemini-2.5-flash",
                    provider_model_name="gemini-2.5-flash",
                    raw_message={
                        "parts": [
                            {
                                "function_call": {
                                    "id": None,
                                    "args": {
                                        "rating": 7,
                                        "author": "Patrick Rothfuss",
                                        "title": "THE NAME OF THE WIND",
                                    },
                                    "name": "__mirascope_formatted_output_tool__",
                                },
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": None,
                                "thought": None,
                                "thought_signature": b'\n\xfd\x03\x01\xd1\xed\x8ao\xb0t\xf7j;\xf9\xf1Ji\xd3\xb4e\xf5om_\xa0z\x06\x9dsVc\x19\'\x95(*\xf3x\xb1\xef\xb0\xd4r\xbbk"\xc4\x07\xc73*\xae\xae\xedO7x\xfd-;\x8c\x85mU\x06\xd1\xe6\xc4\x0e\xde0\x16M8\x95P\xb0\x02\xc61\x8a_\xc8\xe9\x94\xa4\x11\xbe\x9bx\xe1\xda\x03t\xc3M\xca\x89>B\xa2?\x91J\x94#DMo\xf9n\x97\xe7\xb2\xeaM\x8d\x90\xe9\xe6\xc0\xe8\xb8\xdf\xf2\x06\x04\xc8F\xb4\xfdb\x87\xbcI\xf6\xbd\xb3\xbd\x9e\xd9\x91\xfa\xf4\xackVN\x9d\x03\xf4\x90rg\x0c\xc2E%\xfe\x8c{\xb7D}@\xe0\\m\xf0`\x86\xbd\xf6\xab\xa6\x15K\x9cO\x90\xba\x97\x85.\x9e\xd9\xae\xdeh\xc5\x9d\xe6\x89\xa7\xe9\xcc\xfbX\xe3!\xdb\xa7E\xa4\xf4\xb9\xf2\t\x91^#\x9a\xb5S\x95x\xbb\xa6U\x0f_\x13_l2\xd7\x8a\x1f)\xc0A\xf6\x146\x7f\x92#\r\x8f\xaf\x93o\x8f\xb0@SG\xf9\xcfd\xfc?x0\x90w\xae\xfd\x8cO\xb4v\xc7:W\xd6\xb9\x0f|\x8a<Q\xbc\xa8\xf5C\xa4\x99\xa3\x80\xff\xb1>O8\xdc\xdf\x12]\xdf\xeb\xf7\xe8\x8b\xd5\x07\x8c\xe6\x02/\xf6\x86\xfd\nF\xef\xff\x90gS\x926\xa6k\x1f\x16\x9b\xf0\xf6\x10=k\xefu\x88\xd7\xccS\xc8\xa0$z\xfa\xec\x84+\x86\x86O\xc9\xe8\x99}\x87\x9bL"\x00w\xcf\x03#\xe7h\x9e\x00R\x15\xf0\x85\xdc\x86:4kB.70\xa6\x1cdt*\xd4\xf8\x1c\xef\xf7\x95!a\x87x\xa1\xa7\xcd\xfaS\xb7yY\x925\x0c\xb4\x8c{\xf2\xc3\x9b\\\xed\xeduO:\xc1\x1a?\xc2\xdf\xe9\x19\xd4[\xe2\xb8\x19wNE\xa1\x85\xaa\x15\xa0z\xed\x82\xe4\x85\xef\x91\xa2.\x9a&\xef\xb4\xe8\xc9/\xa1\xb2{_l\\-\xf3@\xf8=>\xc4\x19\x99\x01\xabk\xd2o]\x90\xfb\xb4\xed\x188\xc3\xac\xcc\xb4\xa1PTf\xe3Y\xdb\x06\xdf\xab\xf5Za\x0c\xfbYx;}_\xd6\x94\x88\xd8U\xf5\x8c\xef6\xf2\xaeF*\x1f:\x826F',
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
