from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    SystemMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "provider": "google",
        "model_id": "gemini-2.5-flash",
        "params": {},
        "finish_reason": None,
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
                        text='{"title": "THE NAME OF THE WIND", "author": "Patrick Rothfuss", "rating": 7}'
                    )
                ],
                provider="google",
                model_id="gemini-2.5-flash",
                raw_message={
                    "parts": [
                        {
                            "video_metadata": None,
                            "thought": None,
                            "inline_data": None,
                            "file_data": None,
                            "thought_signature": b"\n\xf7\x03\x01\xd1\xed\x8ao\xe9Ri\xf9\xe3\xc12d\xb8\xb2\xb0\x83Rf\x05\xbd\x8a+(\x91\xd5\xe2\xf8\xbeK\x16\x95\xf3\xd9h,\xe7\xb9!\xfa\x0eW\x99\x02^\x0ex\xdf\x01\x19lUiE\xc7\x8a8\xc2MaC\x88\xd2\x13\xc6\xbb\xdd\x9d\xbe\xf5\xc9\tef\xea\x191V\xfdI\xca\xb4\xc88t`<\xe2\x16J\xcf\x19L\xf2\x9f4\x1c\x0c\x8c!\x8f<\xd7\xfeP\xab$\xc3\xa8\xce\x90\x01\t?\x9d\x11ZC\\\x9e\xa8\xb50(\x1a{u\x0c\x1cX\x82\xe5\xaf\x7fI\x15cq\xb2\xdd\xdc/\xb7I\x199(\xb0\xbdNg\xd4x\xf3\x87l\xa6t\x97\xc6e\xc4\xbd\x93\xb7\x0cT \xf3\xc2v:\xb6c0\xdaVWV\xe0i\xe6\xd7\x96\xce;Hl\xed8\xc1!\x85q\xd2\x86\xcb-\x99/\x858\x87\xd1\xde3?v\xfdU!\x9d\xccvd\xef\xf1\xec\xb4\x1d\xcb\xd3n\x19\x18\xa9N\x9c \x88\xf4\xb5\ts\x962\x96Qe\xcb\xa0\xe1\x95\xcb\xc4\xf7\xf0\xe1\xfd\x9e\xba\x8e\x07p\xd0\x02\xdfX\xb4~\xa996\xfb\r\xf6\xf2t~\x02&]\xbdKxw\xd9\x04\xc3\xd0P\xbb\xf4\xde5~7\x8f\x9f\xa2\xa8@\x97\xe2\xf5\x0b\xec\xcc\x130h\xa5\xe4\xccq\x14\xd4\xb4\xa4\xb1T\x1b\xa7\x84\x1f\xd7o\xa7|\xe1\x92C\x8b~k\xbcm\xa1~Rb&~U\x88y\x9f\x9dK\x04\xe0g\xbf\x80\x94\x84o3\xe7$O\x9a\x92\xf4\xe0\xba\x00\xe1\x82\xe0\x1d\x8d\xc1@\xd8\x8b\xf8#\xa1\xf8\x1b&\xb0\x95\xb7\x90\xcaW6\xb2\x15\xd4\xa3\x8az^\xd1\x1a\xa0\x9eU\xe1\xfc\r\xca\x92a\xac\xbe\xc8\x0fTdX5f\x04(\x15LT\x19\xfc\xd4\xed\x06\xe1\xc5F>-\x9a\xd6ye\xdd\x04\xb6\x00\xa4#\x81\xa2\xa8\xa1h\\\x0b\x91\xd7U\xd2\xe4I\xa6Y\x95\x9f\x81m\xb8\xfaH]\x10\x1c\xc2\xc5\xbe\xa2(\x9a\x984p\\\xc8&\x18EU\x8acb\xd5\xf2\x08\x10\x99P\xe0BIx\x0c\xbc>>00\xb2\xfaX\xb0\x9b$\xba\nz\xe0\xd0\xc6\x8a",
                            "code_execution_result": None,
                            "executable_code": None,
                            "function_call": {
                                "id": None,
                                "args": {
                                    "title": "THE NAME OF THE WIND",
                                    "author": "Patrick Rothfuss",
                                    "rating": 7,
                                },
                                "name": "__mirascope_formatted_output_tool__",
                            },
                            "function_response": None,
                            "text": None,
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
)
