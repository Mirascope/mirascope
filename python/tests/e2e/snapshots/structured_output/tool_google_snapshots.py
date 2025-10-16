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
                raw_content=[
                    {
                        "video_metadata": None,
                        "thought": None,
                        "inline_data": None,
                        "file_data": None,
                        "thought_signature": b"\n$\x01\xd1\xed\x8aoS\xa9j\x93\xb0\xa2\xd9\xc2\x94\xd0\x07\x7f9g\x93K@\xfa\"w\xe3\x04w\x16\xc4\xe0[\xeaJ\x18\xbc\nl\x01\xd1\xed\x8aoW\xee\xa0\x87\xc5\xf6\xd2\xd840\x94\x04i^\xbb\xc6\xf4\xeb0j\\~\xd6\xe6Ty=k\xd8\xee\xb0\x8a\xa4aVB\xdd\x18\x0f\x84~\x9e\xb8H\x19\xa9@\x0b\xb0~[\x98!\xa7\x98\x91Y\"\xfdO\x86\xad\xfc\xa4dp\x1d\x97\xdb\xadA\x0bw\xd1?1\xf1\x9fiz}\x16\x8f\xee\xa3;\xa9\xf2\xaa\xe17\x11\x126\xd8\x0c\xb5A\x12\x08\xbb\xf7\xd2\n\xea\x01\x01\xd1\xed\x8ao\xacjo\xb2`\xb1\x06:|\xee\x0f\xd7\x85\xa5K\x9e\x99\xe8w'\xc2g\xd5\xe4\xd5\xe8\x90\xbcr\x01\xba\xfda\xafi}b^_'+\xdc\x96x*\x0e\xcb\xef\x81/\xcb\x9a'n\x01L.o}\x19\x00\xa7\x83\xf7\x08\xdf\n\x991 W\xb8\x92I<\xca\x92+\xc6L\xe6?@p\xcc\xd9\x93e\xe0\xe8\x9b\x06\xbaw\xd1\x8c\xe2<\xcf>\x82}\xc0\xdf4\xb1\xca\xbd\xba\xb3\x80\xb6}\xa9^\x19\x12\x8c\x8cxB\xae\xefE2\x07\x85\xec\x8c_S\xa5\xa5Bt~\xf7P\xb0\x04\xd5\xc5\t;\x96\x1e\xe3\x14\x90?\x93\xde \xb0\xfe\xa4x\xf3\xdf\xd8X\xf8:Q\xe2\xb6o\xfd\x0c]\xe4TM\x91\xb9\xeb'\xb5\xa8\xc7\x83\x14\xc2\xc0uw\xe5\x10{\xc4\xa5\x17\xed\xa0_)Z\xbe\xe2\xaa\xcd\xae\x9bO\x91Nq\x8eV\xbb,\xf8\xc4#!\xfe1\x8a\xe6\xcc\x02\x92\xaf\x0e\xa2\xf9II\x90\n\xee\x01\x01\xd1\xed\x8ao\xcb\xb9\x10\xec\xc0r\xf3\xfb9\x87\xc0\x8b\x07/\xc5\xd1\xd1\xc3\xdb>\xd4\x0e\xe4X\xd5\xd8\xd4\x13VG\xfc%\xc0\xb2\xdf\xcc\xe4hT\xb1%f7\xb1\xfbA\x08(+\xb6\xea]j\xaf\x90,\xe2\x87mz\xc5\x1d\x87\xbfR?\xdb\xbc\\\xcd5\x16\x1c8:\x06\xd0\x05\xed\x86\x7fl\xf5B\x02{\xeee\xe2\xffm\x9e0R4/{a:f\xa3\x7f\xb6\x12\xf9]`\x86)\xb0\xa3\xb6G\xfdz\x16l\xf0Z\x93\xe0\xe8\xaf\xf4+7\x8a\x9fq\xc6\x0c\xb7\x82\x7f\x8bF\n\xaf\x96YIA\xec\xe0\xa1\x93\xa3\xa6\x11\xfb\x87\xbc\x85i\xa4\xd8\x96\"\xa5\xb5\x12\x95#\xba\xad\x82\xceA\x85{\x90\xd7\xbc\x96\xba\x02Y\xcfm\n\xba)\xba\x13\xc0b0\xb7\x9c\x92+J,~\xf3$\xbe\x1d\x9c\x17\x07[\x91\xc3\xb2\x1ej\x10\x8e^\xb7\x8cq\xedU2\xa0k\xeb\xbe\x96T_\xc4n_\xd0s\x0b\xdd\x0b1\xcb\n\x8d\x02\x01\xd1\xed\x8aoMB\x83t\xb5\xc96\xed\x91pBT\x0c5\x10\x08\xde|\xbdkHS5\xd7\xb4w\x90\x03QF\xf7\xa6%\x13A\xa1/\xc9:\xf9s\xf1Z\x00x\xe51a\xe1-\xe0\x0b\x1e\xc4\x98m\xa1\x92\x1c\x95\xedG{\xd6T\x800\x96^\x05\xf8y<\xa3\xd5\xcfj\x0e\xd1\xba\xaa\x19\x14Tt\xd8\xf0\x94\x92X\xf09\xcb\x01\x0e\x84R\xeeetp\xef\xcb*\x02l\xdd\xe6_\xaa?0\x97)\xed/!\xdfUW\x85\"\x9a\x86.l\xf9\xe5\xa6m\xa1\xb1\x90^\x98<\x1e\xd1GY\x85\x08/\x01\xc8yy\x8a\xb9\xb6N\xa9\x7fK\xe9\x16iT\xa7\x0ev,\x9a\x05\xff@GY\x1b\x94\xc1{\xcb\xbd\xb2\xa3\xb4\xf2\xdc\x1c\x88cd\xf2l\x1e\r\x86\xa9\xea\xfc#\xca\xcc\x89\x00\xaf\xac\xaa\xb7\xb0\xc1\xc41\x18@\xfa\x1c\"\x01\x98bS\xc3\\\x98P\xe6s-\x10\xd55\xf8\x047\x9e\x9f\xbd\x80\xba\xb3L\x9a\xe6%\xb9\x86\x03\xac\xfc\xbe\x99\xba\xfdZ\xeam\x137\xa2\xd7\xde\x0b\x9e\x96\xcd2\xae\xcb\xbb\xdd\x9c\xfa\n\xe2\x01\x01\xd1\xed\x8ao\x8d\xa5S\xed\xd7\xe7\xebEb\xa8\xbc\xfafx\xf1\x18j\xb0~\xa6$ZN\xcb\xfd\xe9\xc7\xdb/?<)\xbbv\xc2{\x0f\xf0[49-\xa3\xf4\xe7l\n\xd8\xbeZ^i\xf1y\x0b^\x853\x86\xde\xf7>#\x01\xdb0Q\xd5\xcbt\xfc\x01\xb1\x97\xc5\xaaO\xa2p8\xea\xbed?\xfe\xef\x9f-\xc4\x19\xfb\x9c\xbf\xd7\x05\xbb\xbf?1\xbe6=\x01\xd2eiB\\\xd7GT0\xb0\x11\x82\xe1\xaalSf\x9b\x0b\xaf\xe2\x07\xfb\xc1\xb5\xf6\xe15\xb3\x15{sV\xb0y 6LK|M\xa2\x1c\xd6\\\xbf\xc0\"\xc9\x96Q\xe13m@LK\xe4\x11~8\xb5\x84\\:\xc3\xdf\xcf\x0c\xfct\x17\xa5\xafc\x83\x8f'\xd9\xa0\xbe\\\x891#\xa2\xabOkc\x1e\xe8;\xd2\x14e\xf6\xa5\x96;;$OY\xa2k\xa6)\x156\xce/l\x96N{\xdfH\n\xcf\x01\x01\xd1\xed\x8ao\xa7\x13\xfft9R\x86\x1b\x17\xbf\xdbN\xa2Qv\x05\x01\x93\xb5\xf8\xa1X\xcf\xf2w&\x82\xb8\xeel\xb6\x17j\xaa\xc2\x0b~N\x1b\xa8\xc6\x82D\x83\x16\\\xe8oIc\xd5\xf1\xa9\xa7\xbe\t2\xc7\xf9<\xa9?\x9a\xb5?\xce\x0cG\x83\x18\xf2\xa7\x9aq\xc4!L\xcd|\xabu\x1f\xf9\xa0\xf7\xf8'\x8b\x9a\xcb!6\x94\x82I[\x1c\x88N\xe5\x1fS\xc2\xcf\x87\xa3\xe4\xbb\xa5[\xc8)K3\x9b\xae\xe7\x90\"\xaeWI\xc5\x03\xef\t\xb0\xc9\xd6\xff|\x00q:-X\x8e%\xa8\x10\x92\x8a\xf3\xe2a\xc7\x02\xa0\xee\xff\n\x8aa!f\x04v?\xae/\xbew\x9f<\\\xac\xd6J\x83\xe8\xd5\x9e,\xf0'r\xa4G~b\xe3\xfe\x13\xd6\xa2\xe3\xc7\x93$V\xd0\xb7\xe7\x95\xb4\xed\xd3\xe6\x02\\\xd6i\nV\x01\xd1\xed\x8ao]Ot\xf4\xdf\xda'$\x12=<\xce.G\xaa\x18\x029\xdd\xf0\xc4\xb1\x05+D\xe7\xb4\xf7i\x0f\xfe\xaeW\xa8m\x08\xf6\xee\xd3kY\xde\xf6\xf3\xa8 c\xa4\xca]\x08\x9d)p\xdb+3H\x94\xd0\xe0U]\xff\xdc\xac\xf3{3\xba\x15\xda!O\"\x0ch`\x8d\xcb\x1a",
                        "code_execution_result": None,
                        "executable_code": None,
                        "function_call": {
                            "id": None,
                            "args": {
                                "author": {
                                    "last_name": "Rothfuss",
                                    "first_name": "Patrick",
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
                raw_content=[
                    {
                        "video_metadata": None,
                        "thought": None,
                        "inline_data": None,
                        "file_data": None,
                        "thought_signature": b'\n$\x01\xd1\xed\x8ao\xfe\xa7\x86\xaf= \xf6\x17<\x9aS\x8d+gDJAq\xd0\xb0\x90\xdcw\xee}\x08.\xcf\x8f;-\ny\x01\xd1\xed\x8ao\x10y\x96\xeds@ \xec36\x92\xbd\xb7w\xa5/@3x\xb9}\xf8\x87\x90\xbe\x16H\xd5D\x83\xc6\xc4c\xc1\x89\xa0\xf15fQ\xaf\x1bW\xba0\xdd\x809\x0c\x07\xe5h\xe4\x07\x06Ii"y\x1a\x81d\xfaPA\xf1AT)h!\xe0\x8do\xd41&\xf2r\xb7y\x8f\xe8I\xde\xf5\xf3\xb33\x9eiv%\xb4\xd3~\x1a{\xa1MWS\x05\x10\x9c"\xa4b\x80\x92M\x928\x91C\xb9\n\xc9\x01\x01\xd1\xed\x8ao\x9e58^\x8e\x8f:\xe2\x9bl\x87\xcb2\xa5\xfa\xb8E\xac\x9c\xe9\x0e2\x16\xdc"s\xfb<\n(\xe6\'\xb5\xd1\x9b\x0e\x15\xb0\xc4\xfd\xd3\xb2\xd9?\xf5\xc2\xebp\x1e\xcd\xdf\xccJ\xc2 1t\xffI\xbfV\xc8~y\x05K\x1c\x11l\xc4\x9f\xbc\xf6\xb1\x05-\x97\x07\xc3\xe4\x9bd<8\xb61L\x80d\xca\xed\xd7\xb4\xc8\x18\x86\xc9b\xdb\xe1\xc8\x0f\xde&\xbe\xe7r\x12\xb9\xd7\x9eTo\xdd>v\xcb\xdc\xf54\x99:\xef\x9c\xad\xa0\x1bWl\xb5\xbb\x1f|\xd3\x8f\n\xdd\xe5\xc4;\xb7%\x88\x8b\xed:\x7f\x8b\x9e\xf4\xa9J\xa8\xe8\x91Xw\xe0&F\x16\x9dL\n\xcd\xad\xd1qO\xbb\x05\xeb\x12\x06\xd9\x15\xf0\xb2\x9e\x8bO\xb7\x9e\xec\x14\x94\xa8\x07\xe8C\xb9\xcd\x9c}t\xdc\n\xe5\x01\x01\xd1\xed\x8ao\x97\xbc\x0fK_s\xdf,Q{\x90\xa5\x19x\xf0\xac\xdb\x015\x07\xac\x11\x9d\xda\x95@\xc4\x92\xc7\x9f\xe9\r\x1b\x9e\x04u\x82\xdd\xf6\x0f\x08\x07\xebM\xfe-\xd9\xbe\x15p\xe1\x1c\x04\xc1\x8a\x97\x08\xf4\xf9\x15$l\x90\xb1x\x93\xe5\xf0\xf7hC\xc14)\xf0h\xcb\xc9{\x8e\\"\xc3m\x973\x05\x8dE]\x92\xf2\x07\x17v=\xa4D\x16\x89\xddYF\x85\xbf\x18\xdb^\x9d\xa5\x8f\xe1"\xc2\x9d\x0e\xa2\xee\xf8\xfe\x9aw>\x9b\r\x17\xc2\xdeF\xccJ\x8e\xcef\x8a\xf9\xc7f\xf9\xb6\xe4dBk4{\x9b\xcc[\xb5\x15f\xf6\xfb\x9c\x1aY\xba-\xdc\x8d5!HH\xe1\x0f$\x0f\x1fV$\xf4\xd5Tv\xcf\xf6\x93*\x0f\xc9+\xdf-(\x99\xfd\x94\x180T}M&\xb6"o`X\xafc\xbd\xf4\xdbA\xf3Cp\xa6\xfa=\xa3j\xa3\x119\xed\xfd\xd0\n\xa8Nw\n\xc3\x01\x01\xd1\xed\x8ao\xefm\xd5YQ\xd3 \'B\x89\xa5A\xdeK<\xe3\xd2\xbeT\x8aV\xa6\x14\x80\xe1\xce,u\xfe\xb7%xc\xad^\x1a\xf3\xff\xf2\xb9\xb1\xbc1\xd8w\x01\xc3\xef\xd9\x8a\xc2\xc2\xd9n\xca\xb0\x0eZ\xa5\x97\xdf\x0b\xb4e\x9b\x02\xda\xdax\xb9\xf6\xa0\xcf\xdc\xd6\xa9Ra\xf8\xa2\xe9p4\xe1\xe1\xe0\xf6\xceB\xf7\xd0&\xfa\xf7\xde\xb7\xa1\xd9\x8a\x1d,\xea\x9e>^\\L/\xc8XOB\xe6:y@yb\xea*\x96\x89\xebWq\xea!\x98t8\xae\xd9\xf5\x08\x9f\xfb\xc4\xb4\xf1\xaf\xe2-<\xff\xe5\xbc\x1c\xde* \xa7\xa5\x0c\x00\xd6W\x95\xab\xc2h!b@5)0\xfa>\x95H6\x93 \xe7\xcf\xbd\xb9\rnQ\x9a\xc7Y\xd5)\x0bF\xe5>\xe5\n~\x01\xd1\xed\x8ao\x01x\x16}\xd5}\xd5\xc4\xb5\xea\x7fw:\xccZ!\x05\x814\x80\xea\x9arJ\xb6\x916\xb7{\xf7\xe1\xf5G\t\x16,\x8a\xdbbv[\x13\xc2w\xfc\x19s\xba\xdf\xe8\xafAI\xf3-\x15V6\xf3\xe7\xd9\x99\xa6hP\xa6\xc5^\x8e\xf4(m\xae\xda98\x8ftT\x93J\x95\x12;\xae\x7f\x03\x90\xed\xc9\xf6\x8c\xee\x13V\x80\xceW\xcf\xd0K\x83\xbe&\x99bE\x1dA\xaa\xe8\xff\x81)\xf8?\x102HQr',
                        "code_execution_result": None,
                        "executable_code": None,
                        "function_call": {
                            "id": None,
                            "args": {
                                "author": {
                                    "last_name": "Rothfuss",
                                    "first_name": "Patrick",
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
        "n_chunks": 3,
    }
)
