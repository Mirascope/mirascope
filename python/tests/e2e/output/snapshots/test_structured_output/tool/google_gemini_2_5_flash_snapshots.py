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
            "provider_id": "google",
            "model_id": "google/gemini-2.5-flash",
            "provider_model_name": "gemini-2.5-flash",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 217,
                "output_tokens": 247,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 198,
                "raw": """\
cache_tokens_details=None cached_content_token_count=None candidates_token_count=49 candidates_tokens_details=None prompt_token_count=217 prompt_tokens_details=[ModalityTokenCount(
  modality=<MediaModality.TEXT: 'TEXT'>,
  token_count=217
)] thoughts_token_count=198 tool_use_prompt_token_count=None tool_use_prompt_tokens_details=None total_token_count=464 traffic_type=None\
""",
                "total_tokens": 464,
            },
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
                            text='{"author": {"first_name": "Patrick", "last_name": "Rothfuss"}, "title": "THE NAME OF THE WIND", "rating": 7}'
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
                                        "author": {
                                            "first_name": "Patrick",
                                            "last_name": "Rothfuss",
                                        },
                                        "title": "THE NAME OF THE WIND",
                                        "rating": 7,
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
                                "thought_signature": b"\n\xd8\x05\x01\xd1\xed\x8ao\xd7(\x17x2\xee;\xdc<\x1ap8\x13\x88e\xd6\x99Cz\x9d\x88\xfbq\x82\x84\xd4\xeb\xc6Qp\xe7\xfc\xa0\xd0\xa0\xa7N\xfeC\xf6\n\xf5\x88\xdf\xb1\xfd\x82a\x93M2v.@:Q\xe9\xde\x11\xd910\xadK\x10f\x90\xee\x10o\xffz\xdc\xb0R\x82>\xb1\x1d-\x8d\xe7\x9e;\xd9~\xbf\xfc\x89\x84)\x1a\xaetf\xfe\x8b\x01\xc0\x83\xb9J\x97`\x86\x03\xab\xd2w\x81c \xe43\xb8l\xf4?@!\xa1\x1e3\xef\x86\xf9f\x1d\xd9Tl\xe9\x1b\x17\x9b~\xc8\xb5\xb1\x9e\x01\x8e\xdc\x0c\xec\x97[4\xf2)\x02^\xa7%\x8f3\x97)2+\xa6\xd0\x0b@*\x82\xe91\xab\xe6M\x0b\xcb\xe4\x85\x9b\xefy\xf4\x98\x1bV\x9b!\xc4a\x84\x18\xfe\xc3\xda\xeb\x12%\xffL\x0c\xb2\xb7\x15 \xee\x83\x7f\x01C\xf4\x11Y6\xf0\xadS\xe5T`\xcf<g\xdd\xbf\x99\xfd\x8d\x90\xeb\xe2\r\x1cV6\x8e\xc0k\r@\xce\x9b\xfd\x06d\xef\xe4\xef\xba\x94\xc9\xff\x86\x96\xc3\xdc'\xd9\xfe2\x96(\x9bS\xf7D\xc3%r\xba\xd7q\xd2p\xcf\xc0E\x83\x8c\xf0\x05\x03\xac\xe7M\x19\xb6R\x91\x15\xa0\x8cT\x81w1\xe9\xe1Z\x81\x1e\x02\xa5\xf5\x18\x8b\x115\xda\x1alH\xfc\xd2Z\xaa2\x9b\xdb2\x0e\x1b\x19\x10\xd7\xdb\xb9\xc7\xed\x95\xc1\x87\x1e\xac\xabn\xe3\xb3\xeb\xec\xe3c\xecOd\xa3\xbf\x13\xf4=\t\x8d\xdc|\xa4\xb9;\xb3\xf1\x06u.u \xbb\"\xb6I\x9f\xe4cQ\x16R\x9d\xde\x97\xde\xce\xe8\xb0\xf5gWT!\xee\xcc\xe3N\r\x8d\xb6\x08\xc4\x1f_l\xbbcv\x85\x16\xde\x0c[T\x05`\xc4AN7\xa7?\xc7\x16 \xcc\x0c\xc2\xf1\xdeZ\x8e~\xc7\x9f\x84\x08\xda\x00\x08\x94\xbf\x91`)S*=N\xdcAg\x1b\xa5N\xbc\xb5Q\n\x0cn\t{\x8a@\xb8B\x13\x9ak,\x19\xef\xe4`F%\xa2C\xc3\x1e\xc0&\x01\x92\xe5\xeam\x8e\xd8\xee\x06\xff@\xf8\xb8\x1d\x17\xef\x92@\x9f\x08\xd9\xef3\xd2ea\xf4,fD\xfb\xe8\x1e@\x1b\xad\x9d\xab\x1e\xb1\x0bB\x8fy\x0cv\xc49/\xff\x13\x1c\xdeT\xe1\\\xa0\xdaf\x8dU\xe2P{\xe7\x84\x92\xfc~\x12$\xf4\x10\x93\xb4\x0e\xae_\x96\xc8\xf8d\xd5\xa7\xff\xafy\x04\x00\xc7\x8e\xf3\x1c\x9e\x90PW\x90\xd1\x84lM@\xc1\xa6&3\x91\xc8\x99,\xff\x0bWH%\xed\xbc\x04Y\xf9\x9a\x1d7\xf9`\xb6\xcf\xff\x94\x81N\x99\xfb\xa39\xd4\x84@\xecszc\xe2\x1a\xc2J\xac\xfa\xe5\xf3#\nN&D\x01\x85r\xa1\x17\xf5>1\xe1,U\xb5c\xbf\x9a.F\xae\x01\x03\x00\xa5\xc7$V\xae\x1b\x12Y[\xb7n\xd1\x94\xf9\xa1\x03N\xda\xa7\xbe\x8dL{\x82\xb0\x184d\xe7\xf6\xfbu\xa0\xfd\xc2*\x01n\xf5\x8fzh?\xa5~d+W\xbc\xe6\xb1!\xb4\xbbm\xc7U\x9e\xb9\xb3H\xc2\x14LoE\xc1\x06\n\xd0\xffu\xfb\xe3",
                                "video_metadata": None,
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
            "provider_id": "google",
            "model_id": "google/gemini-2.5-flash",
            "provider_model_name": "gemini-2.5-flash",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 217,
                "output_tokens": 218,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 169,
                "raw": """\
cache_tokens_details=None cached_content_token_count=None candidates_token_count=49 candidates_tokens_details=None prompt_token_count=217 prompt_tokens_details=[ModalityTokenCount(
  modality=<MediaModality.TEXT: 'TEXT'>,
  token_count=217
)] thoughts_token_count=169 tool_use_prompt_token_count=None tool_use_prompt_tokens_details=None total_token_count=435 traffic_type=None\
""",
                "total_tokens": 435,
            },
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
                            text='{"rating": 7, "author": {"first_name": "Patrick", "last_name": "Rothfuss"}, "title": "THE NAME OF THE WIND"}'
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
                                        "author": {
                                            "first_name": "Patrick",
                                            "last_name": "Rothfuss",
                                        },
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
                                "thought_signature": b"\n\x94\x05\x01\xd1\xed\x8aoKY}\xbf<I\xb4\x0f\x7f({\xd4~2{\x0e\xf9\x0c\x1bB<\x13C\x9b\x98\x040\x19\xba-\xb4\x04\x86\x98\x1eX\x0c\xc6\xed\xb5\xe3JG\x17\r\x89\xc9\xecL\xa6\xb3H\xae\x96*\xe6\xceY\xad\xa8K\x1e\x82\x08E\x93hS\x044tf\xd3m \x10\x9f\x02#\x88\xfb\x8b\xf6]]\xc7\xfd\xa3S\x04\x12u_\x85 \xe5V\x99\xe2\x80\x17#\x85\xb2\xe0\x92;\xf3\x81\x04\x10\x86V;+!^\x0ep\xfd'{L\xc3w\r_\x16[\x18\xeb\xdf\x05/\xce\x1bpf\xb7r\r\xba\xdb\xb6D\x9blm\xef\x96\xa79\x00h\x01_\x13g\xb9\x98\x0bB0\x1dg\xcb:\xfb\xe9M\x9d|Z\"\xf3/\xa0o\x82R\xb2\xc07\xac\xdem+>\xd6W\xe8u\xb9.A>\xed7n\x80\xc6\xcbk\xde.x\xb9\r\x86\xff \xf8a\xb5D\x06%\xa6Zt\xa1t`\xb7=\xd4\xfd\x80\x8b.3\x1ba\xc3\x91\x16\xc9{\x87\xddv\xc6*B\xf8\x85MO\xb3\xe3\x88\x9e\xa6h6q\xf19\xa2\x90`I\xd1ya\x99\xf1\xb3(B\xaf\x9e\x18\xbe\x1a4@\xb6\x9d\x0e\xe1}\xca\xd6\xb0\\\x06Vr[\x8a\t\xf3\x86\xcb\x7f\x0eJb-Sh\r\x14\n;\x9b\xa1\t\xfe+\x17}\xb5\x90\xe5\x06\xdf@fb\x9d\xbboF\xe1\xbd\xb1\xa7\x9a\xed\xc8\x8d\xden\xae\xba\xab\xfer\x1f0(\x9c\xe1f&\xeb\xf9)\xb4>\tt\x02\xb3<{GE9?\x0e}\x9c\xcf^g\xc4E\xc7\xa1\xb1U\x1e\xd3\x1d:\xe1\xaec}\xdb\xd8\xd4\xac\xe8\xbfWN\xb4yh%\x9c\x97.\xc3\x1e^\xab\x82\xd2\x18\xb45\x9e.f\x83}\xc1=rI>\xdf\xa2\xa5.\xab\x0f\xd8O\xd6%\x90B\xea\x8b[\xd7+\x8b\xa2B\xfe\x0beY\xa7o\xbew\xd1\xe1\xc1v\xc4AX\xef\xf8\xd7\xecWx\xf3:\xb9^g[~\x90\xf2\xf3\xe7p\xe5,\x01\xf1\x85z\xf1D\x9c@\xd7\x99#&\xa8\xfb\xba\xd8\xe6y\xd9'4\x14\xd05b\xd5:\xa5QB\xf1\x98q\xe6X\x86\xff\x10;\xddw\xc4I\xab\xdeE\xf1\x9dn\xda\x84bk\x91\xc1\xe8\xeaT\x91}\xecD\xb7u\xf2(R!?\xba\x96\xac\x8a\xfe5\xc1\x13t\xc0\xb9\x82\n\xba\t%\x06\x9d\xe9\x02\xd4<\xb3\xe3b\xf2B\xc9\x1aZ'j\xa1J\x8e\xd9\xd3\xce\xec\xe5Wu=\x83v\x92\x1c\xbe\x94\"g\xd8ca\x01k\xf8hn\x9c\xd4v\x9f\x9d0.7\xd9\xd7\x8b\xe0\x7fv\xe4\xe7Yq \xae\\\x153\xcf\x8d_sx0\xa72H\x0e\x11p?\xe3\xffR2~\x10\xe7\xc7>.M\xc9\x92t6PlQ\x8c\xb2",
                                "video_metadata": None,
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
            "provider_id": "google",
            "provider_model_name": "gemini-2.5-flash",
            "model_id": "google/gemini-2.5-flash",
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
                            text='{"author": {"first_name": "Patrick", "last_name": "Rothfuss"}, "title": "THE NAME OF THE WIND", "rating": 7}'
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
                                        "author": {
                                            "first_name": "Patrick",
                                            "last_name": "Rothfuss",
                                        },
                                        "title": "THE NAME OF THE WIND",
                                        "rating": 7,
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
                                "thought_signature": b'\n$\x01\xd1\xed\x8ao\x85J\xc4RH[\xbdj\x9f\xb0\xabS&\xf0\xfb\x7f\xf1\x90Yh;\x1b\xd5\x1e\x18r\x05[\x00\x90X\ny\x01\xd1\xed\x8ao\x97Q\x10\xcb"3\x0cJ\x18j#,6\xac\x08\xb2\x17m\xd1\xff\x17\xd7\x84vD\xbd\xa3%*\xf3\xe0\xf1\xcd\x10Js\xb9~\xd2#\xd9\xf2\x8f\n\xb4\x13B\x91s$\xe37\xbe\xa1\x90Pi\x1f\x1a\x10\xd2\x1e[\x1b\xb9\xa4o\xea\xba\x05\xa3\n\xac;=\x97\xdb\xd5l\xc2\xdc\xe2@d\xf2\xfb\xc9\xf3p\xd2\xa5`\xf1\xdc!\xb0\x8a,\x0eP\xc2\x0f0\xbdnh\xdd\x14x-\x81O\xd7\xa4-\x8b\n\xe8\x01\x01\xd1\xed\x8ao\xa8bmzN\x95\x93\x01\xd8&\xcb,\xd2Q\xdf\xc91UR\x15\xe39\x03i\x00\r\xa8\xd9\x8b\xaa\x9a\xc3\x7f\xe1\xd9j\xb8\xcd\xcb\xad\xe5\xa1>\xe4\x9e+\x06J`;&\xc0\x0f\xf8\xe8\x1e*_\xb2\x11\xf3\xd2@\xd5)\x87&\x0e\x16\xda\xfe[\xb4r\xc0\x1f$\x17\xe3Fg\xb7\xf0,\x1bw\x82\xb1Up!\xe4\xb9J\x8edt\xda\xc4\x02Q\xf4\xe7B\x9c\xc3\x86\x89\xf0\x9f:\xd0UH\x19\x8am\xb6)M\xf2\x02M)\xebKp\x19\x17\x10E\xf7\x89\xdf\xb5-\xb0\xe5\x83\x0f\xef\x13\xf1\x91\x00d\xe6\xa5\x89\x0et9\x8e\xcc\x0f1\x82\x18Y\x91\xdb@\x0c\x10Y\xaa\xdd^\x9bc\x9e\xec9h&\x8e|\xc3\x07>p=ho\xfd\xd1\x9b*\xc2\x11EY\xbds\x8d4\x10\xda\xc9N\x0c{\xd1u\xf5*\xf9*\xa4<\xa5H&\xc3\xf3.\x9a#\x0f\xc7\x8c\x00\t\xef\xcf\xd6/\n\xe0\x01\x01\xd1\xed\x8aoO\x8eu\x99\x86gr_\xc8c\xbd\x16\xef\xb2\xaa~\x88$/s\xff\xcf\xd5V\xa1\x9ew/\xb1\xaf\x14\xaeD\xbeDU\xa9L\x8b\x84\xb9=\xbe\xbcT8y2n\x97\'\xca\xe6\xf0\xab\xa4\x97\nZK:\x7f:\x17}\x12``\x80\x91\xe9\x9fM\xf6\x04\xce\xee@~4T\x1c\x80O\x10\xc2\xc1\xf8N\xb5\xe6C:\xe1t[\x8e`\x1fK\xc2\x82"\x10\xe5\xa8\xdf\x88\xc1\xa8\xd9\x07!?\xf2pQ\xb62Th\xea\xed\xec\xe6\xa8\xed6\xc2\xbd\xeeQ,>L2D\xc2r\x15\\\x8e\xdf\x85s\xd6|\xe0\xdb\x04\x82Lj\xac\t%\x9f\xe0\xe5}\xbb\xb8\xbc\x19\x94.?\x18\xd1\xd9\x96im\xf8]\x16_\xcc6\xac\x8d\xe5>A\xa8v\xa1\x9be\x02B)\x15\xa8\xbc\xbfa\x15M\xee\x1f:\xcaD\xa8\xc9\xe4\xec\x8d\xa4\xbf\xa8\x18\x9d\x83\xa8\xb7PO\n\xe0\x01\x01\xd1\xed\x8ao\xcb\x82&\xef\x89\xfe\x80\xab`4\x1d\xae\x977u/\x93\xd4\x07\x858CL\x8en\xa9\x0f6\xaa\xaf\xbc\xedA\xf5>N>J\x01\xa4S\xf6\xec\x1e`\x8a\xd81\x81\x89$~\x86v}\xd9k\xdb\xc3+l\x96\xa71\x02\xc5\xa5"9\xf1\x1aK\xac\xf69{\xfd\x0fJ$\xf1\x95\xdb\xfd\x93\x11\xd2\xfa\xecU\x87\x17Z\xe0l\xc7z\x86\xca\xbd\xec\x858K\xa1\xb1\xeb\xab\x89/\xa5\xb5e\xd1\xbe78{\x80\xc0\xf5\\>\xaa\x81\xcf\xcbTl\xaa\xb7\xbb\x19z\xef\xd0\xf4\xa8\x9d\xd3\xb1+\xac:[\x04\xbfN\xb6\xcdJ\xeac+JW1\xc1\xdd\xa9\xf8\xe5E{\xfe=b)\x9a8Yo\xcb1\xb4\x18\xdd\x0b3\xcc\xed\x88L\xc1\xd7\x91\xb7\xcf\x02\xae\x18\x05\xff\t\x81\xdch\x15\xaan\x05\xb8\xbb\xa2^\x9c>\xb0\xf4<\xcco7!\xc6\x87\xf1\xc3\x81\nb\x01\xd1\xed\x8aom\xaeQS\xab\xad/#j\xfa\xe85$?\xa4\xc2\xfcd\xf9}\xa0\xf8m\xd0\xe9\x90\xa3>\\O\x8b5\xd2\x82\xda\x98\x15\xe5\xdd\x82B\xa9\x17\xe1\x85C>\xc5\xf0\xeb&&\xe8#\x9e:\xba\xbb3\x15e\xb8\x9aX\xff>B\xafy\x90\xcdy:D\x9bn\xb9H\xa3H\xfe\xf8"\xde\xf6\xb7~\xcc~mR4`',
                                "video_metadata": None,
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
            "usage": {
                "input_tokens": 217,
                "output_tokens": 49,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 189,
                "raw": "None",
                "total_tokens": 266,
            },
            "n_chunks": 3,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "google",
            "provider_model_name": "gemini-2.5-flash",
            "model_id": "google/gemini-2.5-flash",
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
                            text='{"title": "THE NAME OF THE WIND", "rating": 7, "author": {"last_name": "Rothfuss", "first_name": "Patrick"}}'
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
                                        "title": "THE NAME OF THE WIND",
                                        "rating": 7,
                                        "author": {
                                            "last_name": "Rothfuss",
                                            "first_name": "Patrick",
                                        },
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
                                "thought_signature": b"\n$\x01\xd1\xed\x8ao\xc3W\xe5+\x1fT\x8e8u\xe5\r\xe43\x83\x825W\xe1\xc5\xf9[\\M\x90\xd2\xcb\xbd\x19IN\xbe\ny\x01\xd1\xed\x8ao\xe0\xe5\x90\x17\x04?\x12\x87\x07\x0e\xca\xaaB\xbe\x8a\xac3\xeaN\xe5\xb9\xca\xc2!\x8c\xca\x8d\xd3\t\xdaUl\xf6\xbe\xeb7\xb9;\xeb\xd0\x1eG7\xe1\xdb1]\xdf,\x0e\xdbO\xccK\xf9\x189\xba\x1c\x1c\x1d\xed\xfe\x95\x7f\x0bR\xc22\xc2\x19\xf3}J\x05\x0f\xe4\xc2]c|J\x01\xe5\xe4`)\xf14\xba\x97|\xe4\xc6#\x11\xef\x00F\x12\xdb\x9b\nI\xf3~e;z\xfe\xda1\x87T\xbe$\n\xe0\x01\x01\xd1\xed\x8ao;\x19A}\xfb\xe6[\xc3x\x92\xeb\r0\xb9\x87\xd61cP\x12\x07\\U\x16\x01q\xa5w\x13\xd9\x99f\x977\x10\x03\n'\xc4c\x16z\x1d\xd5`\x1b8\xe0Q\x01\xcd\x8e\x05\xdc\r\xb3\x8e($j\n\x14\xd2\x0cNVTe\xfc\x13\x01\xd0\x82\x96\xab4)\x81LW\xff\xebc\xdb\xc6\x88\x8d\xe5\xf4\xb1\x94\x9b\x7f\xce\xa2\x8eS\xe1\x0ck\xdb\xad5\xb3\xf4\xab\xf1\xee\x13S\x84\x1cz \x1d\x7f\x86iG]\t\x8b\xe7`5\xd6\xcf\xd9e]\x03\x89S\x08\xe8[\x98\xdb\xed>\xbd\x98\xa8u\xed{\xfb\xf0>^\t0-i\x1aF\xa4\x10\x90\xe5\xfc\x88\x81\x83\xf3`\x11\xa3\x00\xae\x14\xb0' M\xec\xc8llj~\x9c\xac\x11(\xb7\xd9\xe88v\xca\xdc]\x12\xf9R\xf3\x07\xab&r\xd3'\xb6\t_\x07\x8dpr\xae\x9e\xf72\xee\x97;|\xa7\n\xe5\x01\x01\xd1\xed\x8ao\xc4-\x7f\x915\xa3\xa8\xdc~\x93F\xa4\xf1\xb0\xa4\x10x\x06\x92\x12\xacJ\x83\\Q\x87\x06\xe0\x00Rr\xff\xa0YX3\xe3C\xe42u\x871\x03K\x7f\xdf\xeb\xb0\r8\x87M@,\xef)b\xc3\xaa\xc4\xc0\x17\xb6\xc9\\J!|g\x13\xbc\xaa\xab\x9e\xbe\x08\xbd\x0e\xb6[M\xb4\xb0C1\xe3\xc8b\x85r\xb3\xef9\x92\x95%|\xa3\xd8 ~D\x08\xd2\xa4\x18\xd8\x80\x00\xa9\xe7\xb9J\x8b2\xd48o\xbf\x0c\x9f\xc5\x03R\xe6\x90\xed5\xdc\x9ev\x81l\xa7\xa1\x17=\xde\x11\x9c\\\x92i\\\xe2\r\xc5\x8a\x05\x88\xb8\xd48\xac)\xd3Q\xf2\xb0\x81\xb7#\xe2\x15\xbc\nMJaCP\x91\x11\xd4u\xc8\x99\x97r\x03\x11:\x14\x8bt\xa0/\x7f\x04}r\xfb\xec\xa5f\x08\xe3\x9c\xe5\xfa\xe4&\xaa\xbb\xe9\xeb\x15\x0c\xc2\x91\x1d\x11Z6|\x95g\x83\x96:\xcb\x876\n\xcd\x01\x01\xd1\xed\x8ao\xe3\xbc*\xc0\xce\xad\xcf\xbb\xbc\xaf\xfe\x96\xd5Qy\xee\xb8\xba\x95\x9d\xa6\xcfo~EV`=69\xb8\xe6\xf4\xd3\xa8f\xc9\xb6\xd4!$\xbc\x95\x07*\x83\x11\xe3M\xcc\xb6M\xc8Cx%\xf6\xd3\xe2\x97\xe6\x833\xde\xccZ>\xd2\x98J\xf7\xf5c\xd5\x08x\xf4\x04\xb2\x83:{\x8a\xea\x1e\xbd\x1c\x81\xba\xfd\xacH\tW\xa5r{\xa8C\x88\xd3\xed4\x1e!\xa0=\x99\x05\x81\xfd\xcf\xa7\xea\x99\xb9\xd0\x8a|\xbc\xefW\xd8\x80\xe23\xe1\x0bg\xddQ/\x05\x07\x95\x96\xb6\xd8\xd1\x172\xde\xf29=\xe3\xe1V\xb0 \xaa\xe6\x0fw\xb3\x00\xec\xeb\x07\x01\x9fc\x9f\xcc M\x81\x81H\x15\x07\xe5\xd0~\xb6y\x9f(;\xdbS\xba\x8f\"\xac8\xf4\x96P\xe0f\xfe&\x9f!\x02\x80\xdc\xe6\x1c",
                                "video_metadata": None,
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
            "usage": {
                "input_tokens": 217,
                "output_tokens": 49,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 167,
                "raw": "None",
                "total_tokens": 266,
            },
            "n_chunks": 3,
        }
    }
)
