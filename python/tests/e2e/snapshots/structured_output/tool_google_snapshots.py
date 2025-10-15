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
                    text="Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output."
                )
            ),
            UserMessage(
                content=[
                    Text(
                        text="Please recommend the most popular book by Patrick Rothfuss"
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text='{"rating": 7, "author": {"last_name": "Rothfuss", "first_name": "Patrick"}, "title": "THE NAME OF THE WIND"}'
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
                        "thought_signature": b"\n\xf6\x05\x01\xd1\xed\x8ao\xf4\xa5\x8eq\xf4\xdf\xef\x88\x81\x14vdN\x00Y\xb7\x93A\x16\xc5V\xcaHl\x05%D\x17\x0e\xfa\x1e\xeb`\xfb\xdav\x0f\x1b\xbd\xc1y\x1b2\x853a\xaf\xfeU\xe5:6\xa8\xff@w\xa87\x0c%\x10\xad\th\x97\xe6u\xdb\xbdd\xad\xd9\xb2\x1f\x08o-\x85 \x07\x8c\xc45T\x06)\xe7\xe9^{\xcf\xdd\xb6~<I\xdd\xa6\x17n9\xf2\xdc\x8clg\xbc\x87WE\x9e\x072\xe1\xa3\xcd\xb8\x8eOy\x9dA\x07\xe9\xfdm-z\xe1\"F\xfb\xac6\xccdI}\xdf\x99\xb3\x1a\xce\xbc\xdb\xe4_\xbc\xfd\t+\x8ch\xf28\"tb$\xa3\xdc\xd0\xf5!\xf3\xacj\xbc\x82\xb5\xfe.m)\xb0\xf4\x81$\x12W3u_\x1bF\xae\x8e;\x97\xc9\xf1\x96Un\xd2\x84\xebR2\xf4\xe3'\x98\xf7(\xaa&\xc3_\x93D\xe6\x1c\x15\xae\x1f\x96O\xab\xbf\x9dn\xef\xdc9dnC\xf4\xacY\xdf\xcaZ\xfal\xd1\xe3E\x83\x85\xb7\x81l\xbd\x8dX\x13\xe0co\xd1\xfa\xb4\x05\x85\xdc\xf7$[\x17\xed\x90\xad6S\xd0\x89\xc3\x80iH\xce\xa8\x1a\xcd:\xdc!\x82\xc3t\xf3^\xe2\x15,YcnC\x12{^[&\xdd\x94\x84\x94;\xddWy\xc3T\x80\xc8\xf8V\x7f\x01R\xb6d\xda\xfc\xf0e\xf5@\xc7\xb2\xd6^3=\xfe\x16\xa19x\xf2\x1e\xcc$\xacFs3K\x9f\x17\x82\xe1<\x9c\x83\x90\x12\xef/\xc4\xd2\xe4\x0b\x0ed\x17.?Y\xd7\xc4\x07\xbe\xd7\xff\x0b\xeb\xbe\xf0\x16\xbeq\xf4\x9e\xc6\x80\x9c\x01_\x8f\xe8\xaf\x84\xe0~\xb2B\xa8\x1d\xfe{kC\xaf\x14Y\x90!!\xf8N\x15\xa6\xaba\x98\x7f)h\xfc8\xa9\x02\xc0\xcc\xcfG\xf5\xde\x03\xdc+*\xe7?\x8d\x7f4[Y\xe6=\xaar\xb3\x93Y\x83\xb1*\xce\x9cht\xf1]L\xe2\xb3\x13\x9cH\xc7x\xf1\xed\xe1\xf9\xa53\x98;\xb1BlD\xe7i\x94y;\x10\x00(\x19$\xf1b\x1e\x16YV!\x96Z\xa4\xf1^\x08m\xb6\xc2$<\x14\xa9)\x83Y\xc3U\x11\xc7\xfd\xa0\x1a\x92\x820\x9a\x17\x85\x91\xecV\x82,3\x83\x1e5\xf5\x1f8\x9b\xdc\x0eJ\xb6F3\x07\xc4\xfa\xb9\xc9Q[\x9d\xd17\t\xfeG\x96#\x88\xc7\xd2\xde%&\x94n&\x04\x808\xe6\xb4\x01A\x8c\xf8\x1cW\xa7\xfc\xadr/'j\xf0\xb6j\xa2l\xfa{\xff\"kx\xa9\xacAU\xf3\xd5\xee\xa5\xbd\xc6%'%\xd8K\xf9\xcc\x84\xd2\x8ayYk\xbc\xd1\xb8P\x80\x7f\xadA\t\xe8o\xc6V\x0fsO\xd8\xd8\xb6\x8b\xfb\xd1\n\x11\x91\x1eG^j\x0b\xd2\xa0\x86\xae\x06\xcfw\xa1\x9f\xb5\xa9\xbf\x14m\x17\xe9\xed\x9c\xa4B\x92d{\x00Q\xee\x19g\x93r\x89\xad\x106\x16\x8e3\xf7\xd8\xa8\xcf\xdad\xbb<\x0bQ*\x17\x83I\xae\x1f\np{\xbc\\\xc9\xe8\xb8\xf6\xbe\xabO\xef(+\xa0\x80\x82\xaa\xc4\xd9`\x078c\xfd\xa3\xa9\xda\x0f\xd9P\xd7uI\xc0\xb0|p\xb2M\x1dF\xb3l\x07\xcd\xc37&\x0eM\x8b\xf84\x05b\xb2dr",
                        "code_execution_result": None,
                        "executable_code": None,
                        "function_call": {
                            "id": None,
                            "args": {
                                "rating": 7,
                                "author": {
                                    "last_name": "Rothfuss",
                                    "first_name": "Patrick",
                                },
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
            "description": "A book with a rating. The title should be in all caps!",
            "schema": {
                "$defs": {
                    "Author": {
                        "description": "The author of a book.",
                        "properties": {
                            "first_name": {"title": "First Name", "type": "string"},
                            "last_name": {"title": "Last Name", "type": "string"},
                        },
                        "required": ["first_name", "last_name"],
                        "title": "Author",
                        "type": "object",
                    }
                },
                "description": "A book with a rating. The title should be in all caps!",
                "properties": {
                    "title": {"title": "Title", "type": "string"},
                    "author": {"$ref": "#/$defs/Author"},
                    "rating": {
                        "description": "For testing purposes, the rating should be 7",
                        "title": "Rating",
                        "type": "integer",
                    },
                },
                "required": ["title", "author", "rating"],
                "title": "Book",
                "type": "object",
            },
            "mode": "tool",
            "formatting_instructions": "Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output.",
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
                    text="Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output."
                )
            ),
            UserMessage(
                content=[
                    Text(
                        text="Please recommend the most popular book by Patrick Rothfuss"
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text='{"author": {"first_name": "Patrick", "last_name": "Rothfuss"}, "rating": 7, "title": "THE NAME OF THE WIND"}'
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
                        "thought_signature": b'\n\x99\x05\x01\xd1\xed\x8ao\x1c \xc9\x0b\x9c\x8b\xdb\xc3\xd1\xb0y\x97I\x85\xad\x85N\x1e\xcco\x0cXJi\x13M\xcd\xb7\'\x08\x16\xee=R;h\xeb\xf7\xb2)I\x14\x17\xe8\x88\xed\t\xd1\xbd\x83\xb0\xe6\'\x13=\x8b\x86n\xeb\xe9\x1c\x84\x19\x89/Rt+\x98\xf8b\xdfdJ\x9bfx>\x1a\x963\xba$\xc0\xb0\x9d\xf9\x1e\xbb\xdc"\xb8\x8a>\x00\xc2V\t\x0f\xbfc \xe0M@\x02\x0cUbZ\xf8{\x17\xa9\xc6V]\xe0Y\x8a!-\x89\x08\t\x06M>\xfbus;x\xc7\xf7v\xf5\r\xf1\x9ba\xd3}!;\xb5\x0eh\xf1\x15Kj\x02N\xf2m\x1d0\x9cA\xc5\xb9e\xcc$W\xd8\x17[\r{\xb5\xea\xec\x86/\xfe\x02\xdf\xd9\xe3\x88[\x1a9\x17\xe9]^"Ni\x1d\xa1\xe0\x05\xba\xafv\xa5\x9b\x00\x8b\x11%\x8d\xcf\xe0\xcd\xbd\xce\x81jb\x97\xba\xf3\x0f]\xbb\xbb6\xee4}\xc4\x84\x9b\xc9O\x00?o\xdf\x0c\xe8\x16\x88\x9d\x1f,\x0e\xae\xf9\x94d\xe0\xea\xa2\xed\x94y\x18?\x1d\\\xac,\xa7\xef\x9d\x80\xf9\xe1\xc0\xe5\xf7;[E\xf58\x95\x86\xb1\xe3\x98rfmu\xa0\xfd\xd0#O>-\xd9\x8e\xb5\x1e\xeb\xc4\x02\xea\x89\x88\x89`W\x81J\xaeL\x05le\xb4\x7f\x93-\x8c3c(\x9c\x19\xfe\xf4\x9b^\x1c^M\xa6\x1f\x1c\xbdC\x0e<1\xe2\x15a\xa9\x0c\xa4\xdag\xeb\xec\xa8.\x1cft\x16\xbd\x86IbD\xfb\xdfz\xc8{5\xe6G\xc3\x98e\x820\x9e]\xc3J?\x16\xaf\xf8\x01\xe4\x12i\x15\xadv\x05\x1c\xe6\xf6\xf3\xeb\xa0\xecB\x9f\xd2\x08\xd4\xba\xdf\x15\x9a\xa1\xf5\xed\xa0%\xe3\x9b\xe4\x91;\x81\x9f\x8a\xc3]xI\xf7\x89\xd7S\x80]\xd4\x039+\x9eh\xc5\x0f\xaa\x97\\\n\xe9\xa9/\x8e\xc7\xcb!\x9c\x8d\xcbP\xdeG\xd7\x0bWd\x98\xbe\xf7>W\xcd\xadb\x80U\x1eA\xc6mr]\xab\xa7\x90\x07\x1d*\x14\xb5\xeb2FJ+\xc8\xfbZ\xf8\xddB\xbak\x8aHeX)fpS\xc0\xef\xdd(\xae\x1c\x07\xd86\xe2\xde\xf8c\x14s\xdf\x9e\xbb\xb2\x11\xd4T\xa9\xaa\xcf\x9be\xbd\xc9W\x87\xf1\x9d.\x07\x84\xe5\x87\xf1\xa6M\x86\xe2 \x96\x1a9\xdc\x82\xce\x12\xb3\x95\xe4Vd\xabG\\2\x93\xdc\x9b?i<\x16\r\x96t\x87\xaa\xc1\xae\xbbY\xc0.p\xe1m\xe9y\x82\xba\x18\x15-@a\x87\x88\xaaV\xcbZ]\x97\x9b\xa8\xf3t(\xad\xde\xb2\xc0\xc7H_\x9aaR\x03p\xd3"4\xec?k\xd4\xff\xc8>\x1d\x14\xe4$\xcf\xf5\xca6,\xcbB\x01\xb3\x1d\xccw\xd5[\xc0\xca\xbb\xfb\xb4\x1c=0\xd9J\xe5\xf5\x18\xce\xa6\xf4\xd8\xc5\x15SU',
                        "code_execution_result": None,
                        "executable_code": None,
                        "function_call": {
                            "id": None,
                            "args": {
                                "author": {
                                    "first_name": "Patrick",
                                    "last_name": "Rothfuss",
                                },
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
            "description": "A book with a rating. The title should be in all caps!",
            "schema": {
                "$defs": {
                    "Author": {
                        "description": "The author of a book.",
                        "properties": {
                            "first_name": {"title": "First Name", "type": "string"},
                            "last_name": {"title": "Last Name", "type": "string"},
                        },
                        "required": ["first_name", "last_name"],
                        "title": "Author",
                        "type": "object",
                    }
                },
                "description": "A book with a rating. The title should be in all caps!",
                "properties": {
                    "title": {"title": "Title", "type": "string"},
                    "author": {"$ref": "#/$defs/Author"},
                    "rating": {
                        "description": "For testing purposes, the rating should be 7",
                        "title": "Rating",
                        "type": "integer",
                    },
                },
                "required": ["title", "author", "rating"],
                "title": "Book",
                "type": "object",
            },
            "mode": "tool",
            "formatting_instructions": "Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output.",
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
                    text="Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output."
                )
            ),
            UserMessage(
                content=[
                    Text(
                        text="Please recommend the most popular book by Patrick Rothfuss"
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text='{"author": {"last_name": "Rothfuss", "first_name": "Patrick"}, "rating": 7, "title": "THE NAME OF THE WIND"}'
                    )
                ],
                provider="google",
                model_id="gemini-2.5-flash",
                raw_content=[],
            ),
        ],
        "format": {
            "name": "Book",
            "description": "A book with a rating. The title should be in all caps!",
            "schema": {
                "$defs": {
                    "Author": {
                        "description": "The author of a book.",
                        "properties": {
                            "first_name": {"title": "First Name", "type": "string"},
                            "last_name": {"title": "Last Name", "type": "string"},
                        },
                        "required": ["first_name", "last_name"],
                        "title": "Author",
                        "type": "object",
                    }
                },
                "description": "A book with a rating. The title should be in all caps!",
                "properties": {
                    "title": {"title": "Title", "type": "string"},
                    "author": {"$ref": "#/$defs/Author"},
                    "rating": {
                        "description": "For testing purposes, the rating should be 7",
                        "title": "Rating",
                        "type": "integer",
                    },
                },
                "required": ["title", "author", "rating"],
                "title": "Book",
                "type": "object",
            },
            "mode": "tool",
            "formatting_instructions": "Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output.",
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
                    text="Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output."
                )
            ),
            UserMessage(
                content=[
                    Text(
                        text="Please recommend the most popular book by Patrick Rothfuss"
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text='{"author": {"last_name": "Rothfuss", "first_name": "Patrick"}, "rating": 7, "title": "THE NAME OF THE WIND"}'
                    )
                ],
                provider="google",
                model_id="gemini-2.5-flash",
                raw_content=[],
            ),
        ],
        "format": {
            "name": "Book",
            "description": "A book with a rating. The title should be in all caps!",
            "schema": {
                "$defs": {
                    "Author": {
                        "description": "The author of a book.",
                        "properties": {
                            "first_name": {"title": "First Name", "type": "string"},
                            "last_name": {"title": "Last Name", "type": "string"},
                        },
                        "required": ["first_name", "last_name"],
                        "title": "Author",
                        "type": "object",
                    }
                },
                "description": "A book with a rating. The title should be in all caps!",
                "properties": {
                    "title": {"title": "Title", "type": "string"},
                    "author": {"$ref": "#/$defs/Author"},
                    "rating": {
                        "description": "For testing purposes, the rating should be 7",
                        "title": "Rating",
                        "type": "integer",
                    },
                },
                "required": ["title", "author", "rating"],
                "title": "Book",
                "type": "object",
            },
            "mode": "tool",
            "formatting_instructions": "Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output.",
        },
        "tools": [],
        "n_chunks": 3,
    }
)
