from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    SystemMessage,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
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
                        text='{"author": "Patrick Rothfuss", "rating": 7, "title": "THE NAME OF THE WIND"}'
                    )
                ],
                provider="google",
                model_id="gemini-2.5-flash",
                raw_content=[
                    {
                        "video_metadata": None,
                        "thought": None,
                        "inline_data": None,
                        "file_data": None,
                        "thought_signature": b"\n\xae\x04\x01\xd1\xed\x8ao\xee\xce\xee7Ea\x99\x8f\xef\x8dD\x7f\x88\xfd\x1d\xbbjo\xafD\xe2\x0f\xf2V\xe4\x1f\t\xd4\xbbH\xf0\xc3\xbbU\xe5\xc9\x19\x03\xb3\xf6'\xbf9@Y\xf8\xf0\xbd\x13\xa8%8\xac\xa87\xb7`\x9b\xdf^I8\x8e\x10\x04~:F\xd8l\x82]\xeb\xf9t)\x07\x19\x9dr\x0f|@LCyU\xd2v\x93w\x01\x1a\x07S\xb1\x1c2\xc1\xe7K\x1f\xf0\x12\xc9\xc7#HhX\xfc\x9f@\xf6\x17\xad\x14\x86\xd0\t\x17JJ\xe8\x06a1\xee/y\xad\x1c\xa6y\x04Xivq\xe3X\xbb\xefr5\x07\x0c^wUv\xdc\x96\xa6%\x02\xac\x18\x1cPs\x1a\xaeE5\x93\xefc\x06r\xbd\x1eA\x15\xe5\x1adR\xd4\xa6\xd8Ql-\xa6\xf8\xf6o\xe9|k\xb5n5\x12\x96\x11\x16\x9d\xe6+\xdax\x96Z\x95\x15-\xd2\x10\xc4\xcaV\x97\x9e\x81A@(\xb9N\xe4f\x00j>\xca\xabh\x1f\xc1E\xbc\xa1;\x05#,hI!0K\x05H\xca[\x96\x8ac*\xba\x0b\xc1\xee%\xa93\xb4\xaa<r\x074\xbfyJ\xca\xe4\r\"o\x0f\x90\xb4u\r\xe1\x88l\xc8f\x91\xe1z\xb1 3\xf6\xf1\xc2\xe3\xff/\x84\x1b\xe8:\xb0u\xad_\x01;\x96Z\xdf\xd3\xf7\xdeUZ\xb7\xdf\xa7\x93\x8f}\xfcw\x9d\xbe\x80\xa8\x9b\x00v\xaf\xca\xa6\xaa\xc7J\xfe\x80\xa8\xd1M\xd7\xaaYC\x82eK\x17{\xaa\x08)IL)m\x1a6\xac\xa4\xdc\xf0K\xc7\x9a\x1b\xa8F13\x11\r\xa8\xc2\xc0VY\xc2v\xaa\xb2\xc6\xfe\x85>/\x99Y\xe3\x8c\xd0\x19\xb6\xf2\t\xb6\xc5[\x11yz\x11\t\xe3\xd1\xd3W\xbe\x88\xb5\x02c|\x94,c\xff\xfc\xee\xea\x1d\x13\xdd\xbd\xa9\x8f%\xeb\xd6\xaf\xd5\x9b\x0b\x90\xa2\x8e+\xda\xe3\xb8\xb4\xb0r\xd7\xe52\xf3\x0bY\xb0pY\xe2\x7f\xfb \xf7l\x14=75^\xc1:\xa0\x83\xe9\xa9\x8a\xf0g\x97\xd0\xc4W\x02\x15\x88\xfb\xef\xe1&:\x01x\x12b\xbe\xb0\xfc\x13f\x8euS=0\xa3\x18\xbf\x10w\xddi\xb0s\xbb\xdf\x95\x0eZqb\x9e\xc7\xee\xbd\x8b\x90iA\xf9\x05h.\xdf7\x98B+\x1f\x1d\xb5\x9f<\x18\x05v\x86W^\x99\xe4\xf1\x18\x7f\xc4\x1f\x99/\xb8U\x0f\xd6",
                        "code_execution_result": None,
                        "executable_code": None,
                        "function_call": {
                            "id": None,
                            "args": {
                                "author": "Patrick Rothfuss",
                                "rating": 7,
                                "title": "THE NAME OF THE WIND",
                            },
                            "name": "__mirascope_formatted_output_tool__",
                        },
                        "function_response": None,
                        "text": None,
                    }
                ],
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
async_snapshot = snapshot(
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
                        text='{"author": "Patrick Rothfuss", "rating": 7, "title": "THE NAME OF THE WIND"}'
                    )
                ],
                provider="google",
                model_id="gemini-2.5-flash",
                raw_content=[
                    {
                        "video_metadata": None,
                        "thought": None,
                        "inline_data": None,
                        "file_data": None,
                        "thought_signature": b"\n\xa3\x04\x01\xd1\xed\x8aok\n?\x02/\xde\xe9F\x89\xc5\xd5a=\xfd-\xdf\xb2\xa7\x11\xc1d\xe6\xbc9\xf7\x16\x87YeG\xf1Vx\xfe\xf2\x03\xeb\xc3~95;p\xbebzc)5\x00\xa8|\x1a\xcc\x0c]\x96\xae\xd0Q\x9e\xe4\x07 \xc1\x07\x95K\xfd\xcc\xbb\xde\x84\xb6\xa9\xc2\xa1N\x9fw#\x02*X\xd0b]\xdaD\xceJC\xcf\xaepd\x80\xa5\xf4d\x80 w\x08\x981Y\x8b+\x1f\xb0\xfa\x0c[\xfd\xabv\xea\x83U\xce\x11\xa5\xc6\x04\xe5\x92\xb3U\x13w\xe5W\xb5xxJ~\xd5\x93\xb6\xf80\x9d\x81oh\xa7K\x83\x85\x9cH\xf8\x85\xf2*\xc9!>}H\xf9\xde\xf2\xa8L\x03] \x9c\x12J\x9f\xba\x95=\xb7\x080\xa31\x02\x14\xb7 \x19H\x91\xfc\x0f$\xaa%\x06#2\xba\x15\"\xaeK=\xa1s\x04\x9a\xe6:\x1f\xba.\xba\xae\xe8GV.@lX\x12\xe6\x9d\x18\x03ua\xb0\xf2\xeb\x0c=\xbe\xad\x8d{\xf3\t\xbdv/!R\xbd\x8e\x99C\xb5\x07\xe0 w\xca\xed\xb76\xa1\xba\x96\xd6?w\x9b\x9f\xc8\x94\xb3\xd0G\x97\xb7\xe54\x88\x08%\x8aG_\x9c|>\xdb\xb2\x8c\x06{\xd1\xb4\x101>\xcd\xd1\xa1\xd1\x18\xef\xa9Ss\\T6T\xb2^\xe9\x89!\xed y\xf8n_\x9cit;z s\x98\x15\xbc\x9aO(\x95\x01Ua\x07%\xc2\xdb\x97\xc1G%{\x13\xdf\xd2G!+\xd8F,\xa2y\xbe\x9bmM\xa7b\xce`#\xa6\x0ed\xbec\x1e\xf6gS\x87\xfc\x97\xb7cqX?\x02\xc2\x1bk_\x8a\x80N3?6\xbd}t(4ht\xa0\x0f\x9ey\xc7\xb8\x95\xb5\x8aY\xddn4\xbc\xbf!\x04\xd4\x0b\x94\xa6.{\x9ds\xe9X\xcd\xe9\x19\xe0\x88\x80\xfeVX\xc7\xab\x87\x00\xea\x07\xf7\xc5J\xb4\xda\xf8\xa2h\xf8\xfek\xc4n\x11I\x81\xad\xc6\xa5hE\x87\x97\xade=q\x9c\xa4i\x052N'\x18\xe0\x8e\x9f?R\x02!\x9c\x18\x03A\xca\x9c\x02/'\x9f\xeb\x03P\xdeVtm\xd5_y\xec\x82P46\x1d\xdc\xc0\xee\x96\x9a\x07\xec\xd8\xb38\xdf@o=\x08\xe2\xe0\x19\xdeS!\x8d\xde\xe1\x02HE\xdd\x85\xab\x91\xe3\x90'",
                        "code_execution_result": None,
                        "executable_code": None,
                        "function_call": {
                            "id": None,
                            "args": {
                                "author": "Patrick Rothfuss",
                                "rating": 7,
                                "title": "THE NAME OF THE WIND",
                            },
                            "name": "__mirascope_formatted_output_tool__",
                        },
                        "function_response": None,
                        "text": None,
                    }
                ],
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
stream_snapshot = snapshot(
    {
        "provider": "google",
        "model_id": "gemini-2.5-flash",
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
                        text='{"author": "Patrick Rothfuss", "title": "THE NAME OF THE WIND", "rating": 7}'
                    )
                ],
                provider="google",
                model_id="gemini-2.5-flash",
                raw_content=[],
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
        "n_chunks": 3,
    }
)
async_stream_snapshot = snapshot(
    {
        "provider": "google",
        "model_id": "gemini-2.5-flash",
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
                        text='{"rating": 7, "author": "Patrick Rothfuss", "title": "THE NAME OF THE WIND"}'
                    )
                ],
                provider="google",
                model_id="gemini-2.5-flash",
                raw_content=[],
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
        "n_chunks": 3,
    }
)
