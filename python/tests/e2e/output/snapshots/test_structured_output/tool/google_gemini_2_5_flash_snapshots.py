from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    SystemMessage,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "response": {
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
                    raw_message={
                        "parts": [
                            {
                                "video_metadata": None,
                                "thought": None,
                                "inline_data": None,
                                "file_data": None,
                                "thought_signature": b"\n\x8c\x05\x01\xd1\xed\x8aoD-\xd4$ve\x87\xb3\xe5d\xd6;[\x0fb\x18i+\x83\x80\xe8\x13\xa4:\x18^O\x99|D\x9f\xaf<\x83\xa6\xe4\xe1\x1fEYT\x92\x98\xee#\xb0\xc0\x9e\xc2=~^\x8e\xb5o\x10~\xa8am\x1c\x8e\xbf\xa68Y\x7f-\t\x0f:9\xdf\x06`\x85\xef\x062^\xc0\xc1\x14\n2\xa2\x82\xcf\x02X\xb9\x7f\xd7\x16P\xa0EU#P|\xe7\xfcd\x13\x816\x10NsT\xc7f\xec\x11\r\x0bz/\xa63\xd7\x86.\xae\x9e\x9e\x04\xbc\xe9\xc5g\xc4\xa3\xe4\xa5\xa1y+VT\xce\x85k\x07\xf48\xa8\xdc\xcf\xb4\x88^\x18\x89\xaf\xdb\xf9\xb1\xda\x1f\x7f$\x13\xf1>fG\xf1\xea^\xf5\xb2\xbaj\xb5\xf0\xf7\x7f.\x9dL\xa8p}a\xe0y[\xe7{\x7f\xc0a\xb3\x18\xd4\xd9\xc7 \x89\xd2\x99\x12\x02\xd9\xcbUx\xa8\xc3u\x94\xaa.Y6\xcf-1\x83\x07\x99\x1d\xe9J^\xb8\x10(\x91gT`G\x13\xadu\xd9\r\x00Y\x01\xfb\x0e\xe5T\x83t\n\xcc\rb/y=\xd7\xb9I\xe94\xb9`\xc3\xe97\x977H\x8e\x0f\xe5\xa1\xf7i\xc6s\x9e\xfc&u\xd3\xd2\xac\xe5i7\xda\x84\x7fi\xc4\x16_\"9.-\xf7\xd5\xcc\xca\x00\xbb\xf7%\xcf\xff\xc0R\x0e\x9a\x9dQ\xe8\\\x8d\xcb\x94O\x8fp\xf2\x15\x16\xe0\xa9$I89\xc0\x87\xe0:\xb4\xc7\x1f\x976\x0b\xd0\xb0S\x14\xa8\xd7\x8b\x8al\xe0 U\x02`\x96Z\xdd\xa5\xdd\xdf&\xcf\x01\xd3\xdb'\x8fq\xd8\x9di\x99\xa1=\x82\xae\x92.\xd1\xb8|\x99`\xb5C\x89\x8b*\xe7!b\x94\xdcx\xcc\x9b\xd3zO}\xe3G\xd2\x91\xbd\xe5_\xb2&y\x07\xa9l\xd4\x81J\x8d\x14\xde\xf2\xcdb\x15]\xe3\xff\xb6\xaf\x96\xc5`\x18U\x08o\xc0\x0c\x91\xa6\xfb\x8d\xee\xde\x93S\xba5\\\x99\xed\x83x;\xad\x83\x83\xf8\xebA\x15rST\x90\x96\x8c\xb5s\xe1\x17\xcb\x15\xd0\xcaK\xb2x\xa8Ms\xe1\xff;d\xf8\xbaQ~\r\xc3\xeeg\xa7\x1dq\xe8\xb2\x80\x1f\xd4N<9\x9e\xbb\n\xf4?\xe7\xfa\xadj\xf5\xb5\xd9\x94\x14\x0c\xc1bY\x91r\xd6\x1f\xe3\t\xa9\x8b\xd2\xd0.uD2\xf5\xbc\xf4\xd5\xa6DHQ\xdb\nm\xb5_\x92\x16UW?\xd2VBWX\xfe_|j~g28S\xad\xc7\x8d\x94\x19\xe0\xcf\xd6Q.\x01\xd2\x1f\xeb\xcd\x88\x96n\x8e\xad\x80I\x19\x90\xe7N\x00\xb2j\x05\xaa\x8cN\xbf*v\xd9\xb8Q\xf2\xc2gE1\x7f\xd1Z\xef\xb6\xdd4\x1f\xa5+\xdd%\xe6\xf8\xa1$\xce$\xafO\x17L\x87\xb1\x9cx\xc7\xd0h\xab\xffPj\xd8\x16",
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
                        "role": "model",
                    },
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
    }
)
async_snapshot = snapshot(
    {
        "response": {
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
                    raw_message={
                        "parts": [
                            {
                                "video_metadata": None,
                                "thought": None,
                                "inline_data": None,
                                "file_data": None,
                                "thought_signature": b'\n\xdc\x07\x01\xd1\xed\x8ao<\xd0\xc0n\xbf\xcd\x00\x88\x93\x83=\xa1\xda\x87\xd5\x89\xbb\xd01\x18\xed\xafu%$\xe9"\x02\xbe\x88\xde\x96\x00\xddG\x18\xed\xfe\x84\xf4\xccI\xf7\x867\x93\xd17\xfcP\xcbqU\xc9\xd98.T:"\tE\xf5\xf5\xe1`\x87\x94X=N\\W\xbc\x9d\x8d:\x18X*\xebN\x04W\x7f\xf1\xe5\x0b\n\x12\xcbW\x17Z\x1fy<X\xa7\xd7D\xf9\x1d-\x88y\xdbi#NI\x04\xe7\x8c\xcf\xab\x8f\x118p1\x9e\x95\xa1\xf6\x1deF\xe0T\xf5\xb307\x1e\x88^Z\xe5\xe0\xb8\xf7\x10B\x14\x86\xed\xbd\x98\xf7\x00\xd15c\xd7Mp\x15V\x91\xea\xf2hK\x90\x01F\x85A\x95\x9d\x0c\xbb\xf0\x14qS^\xf0W\xfe3\xf7\xac\xc9\xec\n_\x88\x14"Cz\xdd(}yS^\xbf\xee;~\xbd\xc5\x85\xcf\xad\xa15\xc2\r\x99\xab@\xd7\xb1T\xf6\xba\xc1\xee\x9fM\xbb\x18\xc6su\xd9;\xe5\x86^\x88\x8envG}\xeaw\x9f\xb0\n\x7fr\x84\xb8\xb9\x1fOg\x8e2Jc\xa8a\xc4kKc\xa6\x92\xec\xd1\xb7L\xa5\xe1\xf11\x82\xd3v\xbc\xe3\xeb\xae\tu\x98\xc5\x10\xb8G\x95\xdc\xb5\x84G\xe8r>/t\x80\x8b\xecW\xdd\x80\r\x9c\x9dGE\xa0\x12r9\x9d?\x02\xafA\x18\xe8\x84\xf4\xea\xad(\xbdr\x04`\x84\xf5\xa9W\x10\xc2g\xcd\x9b\x0f\xfb\xad\xcf*\x8e\x8cS\xa5\x9e\xbfy\x07\x91:\xf9nt\x0e)d\x87g\xe7\xeb\x802eP\xfe\xdbD\n\xb0\x0e\xe4\xaa\xec\xec\xd1\x1d\xc7\xc8\x12\xcdc\x11e\x1f\x18K\xffN6<\x7f:f\x95\xf3j\xd1b\xe3\xaf\x1fb\x1bdT>c\xb3\x99\x0b\x07\xee\xf0\xd8\xdc\x96=;8\xe36\xdc\x1d?\x9b\x9c\x06\x10\x17\xe1\xaaT\xb4\xaa\x12\rG9\xf1%^o\xcd\x0f\xc2nl\xe9]Fm\x8d \x9cHQ\xdb\xb2\xa0\xe0|\xd6W\x9f\x94\x0el\x9b\xd6u\xcd\xd9\xfa;\x1a\xb8M.$\x03\x9bA\xc4\xf4\x84I\x05\xf1\xa11\xc0u\xd3\xf5\xd0\x8a\x0fG\x90\xc6Ru\xef\xfdB\xa04\xb36\xfa\xad\x80z)pU\xf8\x9bT}\x80\xb6\xc8\xbeq\xaeE\x9bo\x9a\x15T\xcd,PR\xd4\x13\xf1\x83K\x01\xa1\xa3\xfc\xd4\xe2BH\xcd\x80VX\xd2y\xfd\x7f\x1b\x1d\xf1\xe3\x8an/\x88\xb3;\xfa9\x11\xec2\xf1B.\xd1\xcf\x0b\xffj\xb0\\\xc3?vQ\xc5A\xda\xfd$yKM\x8b\xd9,\xca\x86\xdb\xfd\xb8\x9f\x82\xf0\xea\xdf\xca]\xa2\xac/\xc9\x9f\xaa\xd4\x89*\xee\x11Z\xd7@_\xc8\xb5\x16\xaf\xc0\x81Jd\x8e\x1a\xd6\xaf\x85\xa2\xd1\x8fl\xfa\xa4T\x9b8\x00;\xd7\x84\xbdJ\x93\x96\xaaJ[\xd4w\x05\xb5\x10\xf3\xad;\x9a\xceZ1L\xee^\xc8\x98\xa1\xcc\x90uS\xdc\xf2I[q\xef\xb5C\x90\xd4__\xba\xb9\xef\xd3\xa3\x17\xfc\x9c\'\n\xe3\xecTT\xd8\xda\xc2\xa9\x01\xe1\xe3\x9baQe\xf0\xde\xcb\x95[$\r\x14\xa44\xd5]\x9d\x9d\x05\xa8s\xe8y\xa14[z`\xdcR`\xee\x80\x90i\x89j\x8eI\x96\xa1S\xf6\xca6\x84M\xcb\xa5\xfd\xb3\xef\xad\xaa\xda\xd4<o\xcc\xd9\x88I\x88\x90\xe6U\x7f\xc9{)\xfb\x9b\xb7\x9f\x0fv?G\xe3\x96\x10\xdf\xcd\xda\xde\x94\xb9\x0ftx\xf4\xb0\x81\x915Y\xe5\x1b\x99\xb5_z\xec\xf7\x1d3\xd3y\xbeGx\xe2\xbcI\xe7\x8f\xa6\x10W\x16N@8\xcaj\xaaw\xb3\xeb\xec\xd4\xb2/\x03&c\r)\xa72eP\xf5\x13\xe1^5\xd2\xb4\xa71\xbd\xd0\xab\xcb1\x08\xb9\x85K\x15\xf4tC1K\xb9\xb1\x0c\xe1\x89\xc3\xe5N\xde\xac\xd06\x05\xbbY\n06\xc7\xd4\xc8\xde/\xc1md\x90\x12:iu\x11\xf3\x84\xab"\x8e \xa4\x8dp\x88\xc8\xcaf\x14\x12\x8a\xc4+uy\x0e\xe4\x9d\xb93\xee\xcc\xc9\x1c\xdb\xb2\xa3\xe7\x06\xdb!\\\xe5\xb3s\x19v\xdf\r\xc5pq\x99}\x85\x16@\xddl\x00\xcc\xad\xba\x98\x08\xc9%I\x97ND\xa3L\x94\x16\x0e',
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
                        "role": "model",
                    },
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
    }
)
stream_snapshot = snapshot(
    {
        "response": {
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
                            text='{"title": "THE NAME OF THE WIND", "rating": 7, "author": {"first_name": "Patrick", "last_name": "Rothfuss"}}'
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
                                "thought_signature": b"\n$\x01\xd1\xed\x8ao\xa2\x8a\x01\xc1\x02R\xd4qhZ\xc9V\xf5\xdc\xdd\x04I\xbdX\x8e'*\xaa\x84\xd3\xbe:Jz\xd4g\ns\x01\xd1\xed\x8aoc\xee\x11\"{\xc8\xf5~\xa7\x9es\x9c\x19\x9aY\x98\xeb\xd4\xd7\x05\xb6\xfd\xea\xd4\x12\xc6\xdbN\x91k\xd5\xb8tO\x04\xbc\xe8\x07\xd2A\xc0\x96\xfb:\x0e\xfa\x9b\xa0\xfd\xb1\xa8\x11S\xbc\x1aZ\xe6\x05\x04\x86\x11\xc4\xc8pMN5\x1bC\x81\xdb\xf8\x84\xc5\xedn\xdal\x9a\xad,\xbc\x9c\xeen\xd0T*\xee\x89Tj1>\xafR\xebz\x92;\x97o`VOi\x9f\rQB\n\xf3\x01\x01\xd1\xed\x8aoY\x8fNl%g\xec\xbfD\xd6\x93\xda\x84\x8e\xfff\x0c\xf5(\xeeO\x00\xd5(\x0c\xb62%\x90\xd0\x1aJ\xf8\x00\xa85\xdb\xed\xf0\xba+\x1fa\xb5\xa3vm\xfc\xed\xa2\x16t\xfa\xa0\xf55\n\xe3\xf4\xa5\xa3\xcd\xefB\xb7\x835\xe8}\xe0\xa9\xe360%\x87_\xde\xa6\x86\x9dI)\xa1\xe58s\xc7\xe9\xbb36\xd7\xa9\x8a\x97r\xa5\xa7b7\xe0\xee@!\x88\x8c5\x98\xca\xab\xe7\rH\xbc\x8bm\xdb?\n\xa49\x8d\x9c\x0c\x14z\xa4\xa1\xa8\x02\xea\xef\x17\xb6'\xfa\x8a\xbe\\\xc8\x87$(L\xa5$_\x1c\xa2\x1a\xfa\xfc2R\xe1{z\x0f\xfe\xbf\x0b\xdf\xba*x\xa0I\xcd\xf5\x19\xe8\xa4Y<\xa2t/\xf1\n\xaf4\xa0*T\xd3\xd0\x94\x98\xa8wR\xbd\x0e\xb0o\xac]phuO\t\x15=\xdd0\x05\xff\xbeE\xfb\xd3H7\xd4Y|s\x1c\xa1x\t\xd15\x06\xdfr\xdf\xe9A=\x8f\xacB\x83\x88C\n\xde\x01\x01\xd1\xed\x8ao\xb3\xd7\x8e\xdd\x82\x0e0\x05\x98|\xfft\xe1\x84\xea<\xae\xa3+E\x0f\xcb\xa1\xf1!Vz4\xc2\xa8\xc8\x14p\t\xc5\x8e\x14oS\x1cdP\xf8\x9a\xea\x89I6-\xbb\xfb\xedk\xde\x97I\xe1(;\\\xa5\xa0\xaf\x7fT\x95\x97\xdc'\xee'\xf5\xee\xc0\x0e\xbbF\"\x88@|\xa5\xcb\xb6zo\x06\xaf*n\x8a,\xfc\x9dG}q\x18\xf5(\xd8\x1c\xc7\xacw\xbd\x91#\xc8\xa9Fe\xd8\xaf\xe1\xba0\n\xf8\xb0\xc8\x83\x95\x1dY\xe2\x1c\xfe\x99\x89\xca\x193\xa6\x97\\Y\x1f\x8e\xf5\x01\x975\x86\x1a\xc3G\x96]\x82\r\xd7\xee=yP$\x9e\x0b\x10\x86\x9af\xde\x13\xe8p\x01e_\xa65\xa3iw\xcb\xff\x83/\xb6\xb8C\xe7\n\xf7U*\xab,\xeb&l@%\x8c1\x93k2\xeb6\t\xb1\xb8\xbf\x1a5B\x0e\x9a\xe4\xb0(\xbb\x91\x1au\n\xbd\x01\x01\xd1\xed\x8ao\x85\xa0y\x15pS\xfc\xff\xa5\x11\xb9\x0f\n'\xf3$\xaf\xd5\xc2\xa4\xcc\xbf/B5k\xcf\xd7\x982-_\xda-f\xc6\t\x9cr\xb2\xd4p0f\x8dY'\x19\xf8\xa2\\\xf8^\xeb\x8cI\xbf\xfe\xb9!\xe4\x84Zl\xda*\xc3;\x93\x8d)\x7fR\xe4,\xb5\xd8\xe2+g\x90\xb7:\xc7|\x8f\xcfb\x99J[n\xf4\x15\x96$q\xdc\xb8\xbf\x8eq\xf1\xfaBk\x8e\xfd\xa7DV=\xbdk#\xb9~\xd2R>-\xaa*/j\xd4z\xc4\x92\x1e\x96\x1e;\xbe\x8fQp\xe1\xc5\xfaf \xf0\x11\x94\x9cl\xb0s65\x83\x16\x12\x93\x0e\xccN\x90+\x97)o0\xefWL\x8b=h\xb4\xdf\x81\xe5b\xfa\xbapEi.\x87\xfc3\n\x8e\x01\x01\xd1\xed\x8ao\x7fW\xf5i\x8fq\x156\x82\xdc*\x9f\xec@e|]\xe5.DQ8%\x16\x06|\xa8).\xee\x00\xcd\xa5\xbe\n\xd7\x87\xcaDQ\xdb\xb0\xb9l;\x91\x961\x91\t!\xfd\xf0\xbd\x15\xa3\xd8\xa3X\xb2\xbewZ\xce\xe3\x16B\xac\xc3`\xf5\x0f\x16\x9f\x85\x197T\x0e\xc4!\xc7a\x8b\xb5\xbb{\xcf\xbe\xee<\xfd\x9d\xad\xb14d\xc1\xdb_\xae\xc9\x82\xf0\x81\xf4\xff60\xb6\xf6,\xfcc\x12\x96v\xd2\x84\xc5\xebp\x80\x08\x87\x854UI\xf9>\xef\x16q\xf7*\xd9",
                                "code_execution_result": None,
                                "executable_code": None,
                                "function_call": {
                                    "id": None,
                                    "args": {
                                        "title": "THE NAME OF THE WIND",
                                        "rating": 7,
                                        "author": {
                                            "first_name": "Patrick",
                                            "last_name": "Rothfuss",
                                        },
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
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
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
                            text='{"title": "THE NAME OF THE WIND", "rating": 7, "author": {"first_name": "Patrick", "last_name": "Rothfuss"}}'
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
                                "thought_signature": b"\n$\x01\xd1\xed\x8ao\xc3N7\xf9=K\xb2\\`\xcaBL;\xcb<,<h\xbb\xc6\xee;\x9b1]\x19\xcb\xd7\xb7\xb0\xb6\ns\x01\xd1\xed\x8ao~8\x82\x96\xa6\x08#\x19\xc0\xda\n\xf6\xc1k@\x00\x84\xa6m?eF\x17\x9d\xd0\x96M\xc4\xe7\x1a\xdc\x97@ \x05f\x14\xc6\xd7m*I\xd4z\xcf\xdaQ\x81\x08\x99\xe0Mm5.\x10\xf3\xff\xa1\xe2W\n\x85\xec\x1a\x81g\xc2\xc3j-\x07\xb9T\r\xc1\xab\xf6\xbbT69Q\xda\xfe@\xef\xe9\xdc\x02?n\xbb\xd6\xdcz\x9f\xd8\xa52\rs\"\xc4~\x8cQ\x10U\xb6\n\xd0\x01\x01\xd1\xed\x8ao\xbe\x0fc\xf1\xcaVh\n\xe5\xe5\x84\x8a]\x1b\xce\x96\xc3\xe1l\xe3\x99'\xa2\x87J\xff\x18\x14\x8d\x96\xd0\x99F1xqd\xe15a\xfa\x11b+rF\x80j\xe2e\x98\x9a\x82\xcf\x83y6\x1c\x14\xda\x1c\xbe\xe4\xda\xff<\x9b\xf7~\xfe-\xba\xee*a:_\xf6?\x9bZ\xa2h8OQC\xc7\x89\x19\x1a;\xe2\x9c\x91\xbb\xeb\x81\x89\xfd\xa0/\xd4\x8a*%\x12n\xa9>\xc6\xa5\x13,\x178\x82\xaa\x02\x07\xb8\x9a\x93\x83K\x04\x05\x1d\xca\x9a\x91\xce\x8c\x96\x96\xa0\xab#\xcaV/\x7f\xed#\xa0\xdaE\xf3\x0b\xd8\x83b\xd7\x9b\xfd\x13\x03N\xc8\x92\x17\x02\x08\x8eK4\xbbYY(\xae=S\x87\x16\xd9T\xef\x9e\xcfw#'R\xeao\xab\xfa\x00\xcf\x93\xe3,\xf3Q\xbaM\x0b\x92w\xc9?\xd7\n\xc6\x01\x01\xd1\xed\x8ao\xeapsC\xca\x8bK\xe7K)\xff\x01\xfa\xbb3\xcc%\xad)\xee\x16<\x05\x11J\xf7$\xe8H\xf8\xa3\x19\x1b\xe2\xfd\xd0\xb5\xac\xbaV\xe0\xb6\x0c^\xdf\xf8\x8e\xad\x9d.\xc5\x9dF`'\xe2\xb1\x16\x10A\xc8\xc6|\xf1Vv\x03\xfa\xbd\xb5X\xf0\xc0\xe9\r\xb2\xd2\xbeL\xbe\xd0\xed2\xa7N\x02\x9c\xe9P\xce\x88\xe0\xe9U\xb2\xfc\xe4\\k\x82\xc4\xc1\xa3k\xa5\xbf\xba*9<\xc8z\xb6v\xdd\xfe\x07\x8c\xcfw\x85\xf7\xe7Z%\xdc\x11\xab9\xce\xf5\xf9\xceG\xd6y\xa0\x017\xc7\x0b\t\n!C\x93\x89s\xea\x84\x9b\xe6\x9b\x0e\xaaX\xc6\xcfm\xc6d\x10\xcas\xe5\xad\xf6\x07,C\x17\xb1\x19~\xe4\xd1?\x9b9\x94f4\xf5v\xf4)\xbe\xc1\xf2T\xca\x0f\xb8\n\x85\x02\x01\xd1\xed\x8ao\xaa)\xf8\xab\xd1\xd1w\x0f\xda#n\xf5\x08Y\xac)\xb8\\\x82\xccg\xf3\xf3\xb0X\xab4\xdb\xb1\x04\xa2H\xdf\xdb\x90\x16\xc3\xf2\x0c\xab\xf3'\xf8\xfdI\xa2\x13\xd8{-5\xa7p+=\x0e>9\xd3\xe5\xf2\x9dK\x0c\xeda\xa67E\x85\xef\x06,\x8d\xb5\x0f\t\x9d\xe4\xb7]\xa98p\xb5\xd8\xee\xa8\x93\xca.e,,-\xc8\x04h\x91oDem;\xa8w{\xef\xfa\x01\xdf$\xd1r?\xf9\xd6\x85\x916\xf7\xda\xbc\xc4\xae&9/l\x1d\x93\x07Q\xb1\x08\xbf\xd9<\x8b^!\xa1\xa8 \x04\xb9\xf5\xa3\xffO/1\xac\xea\xc6\xc0\xd0e\xd6\xc6-\x13\xc8\x97e\x0b\xc6\xe9\x94\xfd\x85\x91\xa1\xde<|A1\xa7\x04\xd4\x8a\xc7\x07\xfe\xb0\xe6\xb8o\xa1\xe4Gh\xde\xda\x9fq|\x10C\xfcK<\"\xe4\x97\xc2[d[\x9e~'\xcf\xca\xdb10\xebh\x1bF\xd0\xb9\xe4\xf9'\x94\x1eK\x13R\xb0\x80\xd3\xb9\x84\xde\x05\x94T\xc7\xfa\xca\xeb\xb9Y\xc5C\xe8\x14\xfbj\x00\x07p\n\xd1\x01\x01\xd1\xed\x8ao\xe2\x90>i\xbf\xc9B3\xe8V\xd4\xfe\x8d\x0fh\x9a\xd4\xf9\xe0\xc7\xbd\xcb\xb9\x91\xa8\x1a?.\xdeX\x7f(\x82&U\xf0\x19\xa0\xcbBIE=\xe2\xe0\x8f\xd3\xc0\x9a\xa0\x85\x8d\xae\xfa)z$\x9fb\xed\x99\xbe\x97\xec!5u\xc1V\xe3\x07\xcfbY\x8d\xdf\x8a\xa9\xe3iOb\xd0\x12Z\x08W?f?\xbf\xca\xf5Jt\xae\x82V\xba\xcc\xf4c9\xbe+8h\x89\x15\x9f\xb2c'\n\x01^2U\x86>KYSqv\x98\x86m\xda\xd9\xc8+\xb2=?\x16\xb3?\xa0H\xa9k|\x89\xc8.\xcb#\xde\xb9D\xcc\xe0k\xd7\x87G[\xbb\x06L^[\x1c\xeb\x08y\xe0.\xcd\xbe\x18\xe7\x9d3\x16\x16\xf8%`\xff\xa8\x98\x9f\xd0u\x0b\x87\x95m\xf5K\xfaB\xef\xb6e/\xdc\xf32\t\xb5\x9c\n\xc7\x01\x01\xd1\xed\x8ao\xf3\\\xc1X\xca\xe3q\x9e\xb3\xba\x99\x0c\xc8N\x05U=\x15P\xe5\x86\x90\n\xf8\xc4x\xc0fUE\xd8\xcde<8(\x0c\xaf\xc6'\x1f\x18Y!\xe9\xd8\xf6Y#\x0c?\x0e\x1b\tj&&\"=\xe5\x1f\t'\x8dF\x99\xb02\xf1\x15\xec79a\xdb\xc6\xbc\x9a\x96\xc0\x03{\xe8\xb1V\n\t\xeb5\xa6\\\xdd\xd6ne\x91S\xd1\xe5\xe12!\x98o\x17\xaf,{1\x8a\x8d\xaai\xa4\x90\x84\x85\xb1\x8d\xb8\xc7\xce\xa0Z\x80\xf9'\x02aF\x06q\xafy<\xb9\x9c\xdb2o\x81/;\x17\x99\xc6X~[\x07\xe3=m\xa15\xa6'\xc6\x9erO\tt\xd9\xfeF\x01\xb9\xbf|\xe4\x81\x80\x8e\xf8w\xfd4\xd2`Q\x96(\x9e_\x19\xba\xbe0\x9d\xccLs\xc5",
                                "code_execution_result": None,
                                "executable_code": None,
                                "function_call": {
                                    "id": None,
                                    "args": {
                                        "title": "THE NAME OF THE WIND",
                                        "rating": 7,
                                        "author": {
                                            "first_name": "Patrick",
                                            "last_name": "Rothfuss",
                                        },
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
    }
)
