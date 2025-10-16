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
                raw_content=[
                    {
                        "video_metadata": None,
                        "thought": None,
                        "inline_data": None,
                        "file_data": None,
                        "thought_signature": b"\n$\x01\xd1\xed\x8ao\x18\xdf\xfcJ\xf3V\x80\xf3\xf2m\xa9w\x80@;\xd0\xec\xcdO\xc7\x92\xe9\xb9Z\xe5G\xf8\xfd\xa2\xde\xa8\n\x88\x01\x01\xd1\xed\x8aoo\n\xf4\x0c\x0bi\xdc\xf1U_\x8d\x8bc\x15QQ\x99\xe0\xd9\x15%\xdc\x7f\xd9\xf0\xfc\x19\x90\xd4KN\x03\xed^\xe7\xbbC\xdd\x92*\xf6\x9a-[\xdcd(\x84\xfdK2\x07\x08CG$\xad7\xa0\x1f\x04\xd6\x8b\x0b\x95 \x9c#\xf8\xb9\xe8\xe6\xb9\xd1E\x17v\xa1E\xa3\xe9\xdd)\xec\xe3\x98]\x00\xc2;'*\xb1\xef\x9c]\x8eUV\xe9\r\xce\x15\x81\xc1,\x07|\xae\xfd&\xe7\xb34\xe3fYD\x02\xc5rdiw\xe85\xfe\x8b\xad\xe8\x12\n\xe4\x01\x01\xd1\xed\x8ao\xea\xd1\xd3\x03p)\xcb\xe4ir\xf3\xb0\xc2\xac\x92\xb0B\xc4\xb0\xe9v\x89\xfe:`%\x1a\xb8\x91\xad\r#\xac\xa9 1\xf0\x00\xd5\xd5\xaf\xd4V\x1f\xa5t\\\xf9\xb1\x16\\4\x0b\xbd+5\xc0:\x91\xb0\xf6\xd8\xde\x957\xd0\xe2\xd9\x9f\xf2\x95+9\xff%x\x01\xca\xcaOQ\xd2\x10\x97\x17x\x00\xa3\\8\xd0q\xb06m\xd8\xd4\x8c\x1d\xc1%\xbe9\xb5\x1f\xd2\xc9\\B\x80\xd5\x96v\x9d;\xa0\xab\xb1.el4\xb0\x0b^G\xc3\x9c\n6\xf2\xc9\x90\x14\xd5\x14\x83\xdf\xfaS\xcc\xcd\xaa\x0f\xdc\xd5\xa2\xcaMC%\x0e\xc5\x15\xff\x11\xb5@c\x9f\xcc>\xc6\x8e\xa2\\\x1ajl\x80 \xca^\x11\x0e3o5\x11\x9e\xbaN\x11\xd5-\x18\x0b\x12\x0bC1\xb8\xbc\xe2\xb5\x0b\xc6\xf5\n\xb9\xc5\xe2f\x83K\xe9\xaf~\x90\xad\xe7(&\xb1\x19\xca<\xc5h\x9c\xd8\xab\xc1\n\xcc\x01\x01\xd1\xed\x8ao\x8ee&c/U\x83k\xed&\x07\x8e\xc7\xe80\x89\xbb%\xedJ\x948\x1a\x08(\x8f\x9b\x98\xae\xe3\n\x84\xf1\x10\xf2\xe0\x89\xea\x1b\xadP\xb7\x1b\xb9M*\xc4\xea\xd4\xb8\xec?n\x94\x95\x10C+\xe4\x05\xce\xe1\xa8\x84\xa8\x89K7\x19M\xc7\xb3\x86\x05)_\xe1\xd2F\xe4X*y\x92g[\xae\xf6\xe1\xb5z\x1ad\xcb\xaa\xce[\xce\xce\xc3\xcd\x81\xe1\x05!\x1d?~\x8e\x96\xaf\xb3 \xbd\xaf\x88)Q\x92\xd8\x0e?\x00\xa8B\xf5\x1e1Xy\x7fG{\x08S\x9a8\xd6\xf1\x8f\x98NI\xdc\x0e\x98\xa2\xa8CU\x97\xf7\xcf\x0e\xfd\xd7\x00pT\x08\x9a\xdb\xa7w\xd6\xd5&\x97DC\xadhM\xa3vJ\xe6\xfe\xadu l9OnpK\x91\x87\x8a:M|B\x89\x9d>J \n\xce\x01\x01\xd1\xed\x8ao2J|t\xf8\x90\"x4\xc4[0\"C\xa8\x98\xe8]\xe5/\x18\x11\x17\x8a\xb0a\xdd\xfc\xa2\x87\xb1\x19X:\x1c\x99\xd0\xd93S\xd8\xe7O\xa7\x1f:W\xc8\x99P\xde\xd2\xe52>\xbe\xddY\xab\x03d@;\x85F\xe8#_\xafG\x00\xd92\xc2K\x88\x9ev\xe4\xa1E\xa8\xddV\xc6\x9f\xf9b\xa1j\xe8\xd6*\x97\xb2\x16\x1e\x7f$\x96\xd1\x1fc\xa7\x89\xe5\xd5^\xda\x9a\xadC\x0b1\x18\x91\x17\xffeh\xd2n|\x92;\x04iO\xa1\xac\xc5\xfc.#\xfe\x00\xddr}[$F\xf5\x8c\xd5\x8d\xda.\x97\xd5V\xb2sB\x12t\x02Vr\x81pt\xbc\xb5\xd55f\xfc\xc9\x8b\x90D\xf0\xe7\x8f\xf2\xc8\xae1I\x93.\xb9 ~I\xcfw\xf1V\x05\xb1\xfd\xb5\xb7~\xa2\xbb!\x10q\n?\x01\xd1\xed\x8ao\x13c\xa5\x83>\x18\xa8F\xe2rT\xd7\x8f\x91q\xcfA\x87\xf6B\xd1\x91\x86r\xf3\xb48!\xb8\x83\xf2D\xd1\xed\x95\xe7\x9c\xc4'd\x87\xa2'd\xe1\x19\xa1r\xca5I2\xb6\xa1\xe9\x90\xb1\xa0",
                        "code_execution_result": None,
                        "executable_code": None,
                        "function_call": {
                            "id": None,
                            "args": {
                                "author": "Patrick Rothfuss",
                                "title": "THE NAME OF THE WIND",
                                "rating": 7,
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
                raw_content=[
                    {
                        "video_metadata": None,
                        "thought": None,
                        "inline_data": None,
                        "file_data": None,
                        "thought_signature": b'\n$\x01\xd1\xed\x8ao`w\xf8\x96\x827"\xeb\x88\xd3\x1bHy\xb1\xa0d\xb2\x17\x0e\xeb\xa2\xe2Q=\xf2\xfc\x96\xcb|p\xb6\n\x8b\x01\x01\xd1\xed\x8ao\xd4\xf0\'\xbc\xd7\x0cq\x8c\xe9\x01\x02xu}\x9d\xce`\x15\xa0F\xc8\xd0#o\xba\x8d\x96\x0e\xcc\x88\xad<\xd3\x97\xb5"\x85A\x80SQy`\xd5Y>\xee\xd63\xd1l\xd50\x8a\xceb\xa1\x99\xf8!\xa0\xc2\xf48/\xbe\xc8\xb3\xbf\xf4\x07\xfc\x13\xd1\x18\xe5\x0c\xc0y\x8d\x16mg\xa5\x9b\xa8iSS0``\xf5Ac\xf6\xb33\xf6g\xca\xfb\x1b\xf6\xc9(\xa6Rz\xe0\x86\xdb\xbd\x80\xe3\xa3\xe2Wp\x84m\xde\x04\xaa\xf9\x18\x81\xc0\xc86g\xd8\xa1\xa4\n\xc6\x01\x01\xd1\xed\x8ao\xd2\xcd\xbe\x81\x02\x8bH\tx\xc99\xa6\xbf\xd5\xa9\xa2\xf64\xd8w\xa8\xd8\x03\x7f\x1d\xba\x7f9\xea\xe8\x9d\xdf\xf7l,\xce\x12\xc9\xaeT\xc7\xff\x16}\xaen\xfe\x90\t;Bk8\x05\xbb\x98\xfd\x0b\xa5\x9d\x17\x08\xea\x19\x92|\x0e\xf5\xf9\xba\xa1\xe6\x1e\xfaD\xf2\xfd\xacnvr>TT\x82\x88\xb6\x88\xbc\x89\xb9\xa3\x8c\x99\xf7~\x8eE\'\xcf\x11/*.\xc5\xf7-p>9G\xf46\xb4]\xc0\xe1\xdbr\xc0\x89\x90\xa0\r\x06\t\xf3(\xe8\xbe\xa3roW]5\xe7\\xW\x99\xcbQ\xe1\xdc\x8d\x98\x06a\x96\xd9\xa9\x84\xc5J-g\xefU\x00H\x0b\xa5Ap\x85\x92\xcaI8\xf5|\xdd|\xa0q\xf23\xc4%\x91\xec\xa2Z(n\x8ayU\xfbT\xde9\n\xd6\x01\x01\xd1\xed\x8ao\xb6\x8c\x80\x89\x93tn\xad\xbeu\xd0x\x82\'s\x95"\r\x8d\x18\xb4\x11\xea\x08\xf4GE\x1fCH\x8a\xe5\xc9\x01\x84Y\xe7\xa5\xdb\x04\x02\x11\x80\xc9\xb7\xdf\x008s~\x88\xe0\xfaiR\x882Y\x9f\x98\x16!\xa9\xb8"\x19\xdc\xc2N5\x12V\xdfC\xc8\x10\x04\xdfn\xff\x91\xc7iQ\xb75\xc4\x08\xbc\xa2\xe0\xbe\xee\x04H)\x87\xd5\xec\xbc\xae?\x08Q\x1ej?\xe4\xf3\xdbb\x92|\x8a\xa3o\xdb\xc7\xa8\x0f~K\x9c\xaf\x0fg}"\xbb\xc8\x9d&\xb0\xc3\x04\xcc\xc2nr\xb9\xbffZYK\x84\xb02~\xe1\x83\x97\xca\xf2\xa0E0.\x8c\x9b\xe7\xdc.(\xd9\xd0\xb3\xadu\xf86C\xd3\x89\xdb\xb4\xf0\x97(\x19O\xc0\xcah|\x9aP\xc7\xa8\xab\xc6]u\x0c\xbb\xa6K\x9bn1\xf7\xfbK]\xd4\xde}\xcc\xa1\n\x85\x01\x01\xd1\xed\x8ao+b\x7f\xff\x17\x9e\xa9\x18\xd2\xdd\xd9P\x85\x0e\x0c\xc0Y:\xf6c~\x87,_X\xeab7\xc2+\xef\n\xb4\x9f\xde"\x07\n\x8c\xa08[ouCo\xd2sL\x8d\x93\x00\xa1\xf2\xb1\x81\x9dS\xb8\xb1\x10\xb7\xe5\x1e\xef@]\t\x06@\t\xd2\xe3\x93\xadI\xce\xbf=\x91T\xc3h&e\x8c\x9c\xcaB\xb0\xd8\xa4\xcf\xfc\x1e\xc72:\x19\xba:\x7f\xd9Rs^\xfe\x1cxNn\x17v`\xd3\xd4\x8e\xd0\xb6kaF\xaf\xf8\x95\x8f\xcfH',
                        "code_execution_result": None,
                        "executable_code": None,
                        "function_call": {
                            "id": None,
                            "args": {
                                "rating": 7,
                                "author": "Patrick Rothfuss",
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
        "n_chunks": 3,
    }
)
