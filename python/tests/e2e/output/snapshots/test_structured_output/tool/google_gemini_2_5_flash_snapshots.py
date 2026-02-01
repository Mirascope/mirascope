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
                "output_tokens": 267,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 218,
                "provider_tool_usage": None,
                "raw": """\
cache_tokens_details=None cached_content_token_count=None candidates_token_count=49 candidates_tokens_details=None prompt_token_count=217 prompt_tokens_details=[ModalityTokenCount(
  modality=<MediaModality.TEXT: 'TEXT'>,
  token_count=217
)] thoughts_token_count=218 tool_use_prompt_token_count=None tool_use_prompt_tokens_details=None total_token_count=484 traffic_type=None\
""",
                "total_tokens": 484,
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
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
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
                                    "partial_args": None,
                                    "will_continue": None,
                                },
                                "function_response": None,
                                "inline_data": None,
                                "text": None,
                                "thought": None,
                                "thought_signature": b'\n\xaf\x06\x01r\xc8\xda|\xe6\xffnc\x18$`\xbd\n5o\xec\xf1\xff\xd4\xcep\x82\xd7Hf\xc4an\xbf\xb8\xa6\xc0\x1aa\x81\x1a\xb0\x98%\x07\\\xb0dC0\x81\xf20\xf4$\xda\x16X\xfc\xe3\x88}\x088fK&FmQ\xe5\xc8\x12\xf7{/\x1d\xaa\x94\xe2\xd2\x03\x1eDy\x10\x83YA4\xe6\xd4\x85h\x05wk\x1f\xa0\x9a\xce\rp\x98v\xf8\x87\xa7T"\xc5\x07\xdd\nM\xf5m-5Ft\x1e\x02;A\xd0\xa3q\x18\xcd\x7fh\xa9=\xa5|\\t\xcd.3y\xfc!\x88\xb0`X4\'A\xd3\x92\xac\x18\x0e\x9a@`*a\x1c\xa8\xee\x8fk\x1c\x8ad\xad\x8313\x94\xaf\x96\x1f\xc1,O #\x91\xa6\xf9\xd3\xd2r\xd3\x80\xec\xfdI.\x83\x00\x0b\x87\xf9w\xb9l\x9c\xa2\x84\xee\xef\x08\x9b\x84al\xe7\r\xab?\xcc\xee\x9bH\x87\x85\xcd<\x9eT\x16<\xf1\xdcp!f\xa4\x07m\xf75\xfb\xf9d\x8b\xa8n5\x80\xab\xe8|\xf0\xde/\xa0\x15\xf7\xc4\xa9\x0e*\xce\xf6\x17\x95\xb6\xab\r\x14\xc0H\xc6\xffF~a\x98\xe6l\'\x1ef3\xcc\xbdY\x8dF\x18|\x9d\xfb\xeb\x0c\xcb\x18\x86u 7\x9d\x879b\xc1\x88@\x17\xa3\x82\xdf\xc3)\x10\x9ftl\x01\xfcY\xd1\xad\xd6\xce\xd7U\xe9E\t\xb0\xc7\x80\xc8\x0c\x82O[B\x88\xda\x18\x19\xe0N\xe6Y\x8a\t[I\xa2\xca\x03F\xe0\xc6\xc6l\r\xe0\xc7\x899\xb6\xa8\x10Hj?^\x9d\n\x86\x07\xae\xab\xc6\\\xb4\xf0z\x98\x88\xe9\x14\xdfb}O|\xc8\xb3\xb8\x87P\xc1\x18k\x9bl\xda\x97\xa4\x1fmeY\xf3L\xdc\x82\xa1\x83\xafyfo\n\xd37\x9b\x0b\x19\xd2\x11\xd2&5G\t\x13\xdd-b\x88\x13Q\xac\xccL\x17\xf6\xc0Xt\x04~D\xa0\xb9C\xe0\xbfx+\xa41\xce\xb3\x0c\xd3\xd5B\xd5\x04\x9f\xe0\xca\xd0\x9a]\xb4>\xd4w\x8f\xfb\xd5\xaf\x7f\x157\xc9\xa2\x1e!\xe1>\xbc\xd6t\xaa\xc6$\xe4\xea\x16\xebZ1\xb9\xad\xf0n\x0et|\x9c%bt*\xf8\xe8\\5n\t\xef\xdc\\^T\xf5\x9b\xcf\xe8R[>y\xa0\xba\xd5C\xeb\x8b}\xc8+\xee\xb6\x96y\x94IsBHq\x8a\xc6V\x81\x92\x80~\x1d\xdd\xbf\xf2*\xaaT\xd2\x80P\xfc\xc02\x016LV\x95\xe6z\x1fc\x0cW\xe2\xe7\x9a"\x97\x19\x99\xde@\x9a\xa6\xf2\xd8\xfd\xf8\\\xb1\xe4\\Z\x05\xb3~\xa6]\xa4\xad\xd6\x13h3\xf0\xcb\xf4\xd1U9\x88>\x96W`[\xdbB\'\xed\x83\xe8\xa1\x97$\xbe%\xd4\x05\xcd!\x84g\x93\xe6\xbez\xcf\x8b\xf8DJ\xba\x03\xdb\x0c\xe2\xb2\xe1\x89\xd6\xd7%O\xa9\xa3\x16\xc5m\x89\x8b\xd5\xc1X\xa0\x8d\x07\xb7\xbd\xcd\xd4jK!\xf9\x7fP\xbaE|\x9a\x8c\x8c\xbc\xc3\xc1|\xe1\xe1\xe9\xa5\xd2\x02.\xe6\xf6\x7f\xaf\x0f\x04\xa9\xd6\xf8\xd7`\xde\xb2B\x1c\xd3\x19KX\x9f\xd7:\xbf\xd5F\x87\x9bo\x9af\xb5+p\xa3h\xa6#8\xd0\xd2\xcb\xe0\xc6\xed\x91=\xcf\x8b\xf5=\xd3\x1dNF\t5\xd8\xc2k\\\x90\xfa\xb1|zf\xd3gOm;u\x040.\x06\xdb\xe7\x8dp\xf5\x8bP\xf2\\\x8f\xbd\x9b\x97\x9a\x90YC\x87Y\x11_pL$\xc3\t\x04"\xeb|b\xea`0W#\xdd\x12-dD\t>\n"\x01r\xc8\xda|j$\x82\x99\x8b\x03\x145)\xc5\xe5\xe5\xe0IZ\xcb\xd5g\xf0\x07\xf3sY\xaf\x01\x96\xb5q\xeb',
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
                "output_tokens": 406,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 357,
                "provider_tool_usage": None,
                "raw": """\
cache_tokens_details=None cached_content_token_count=None candidates_token_count=49 candidates_tokens_details=None prompt_token_count=217 prompt_tokens_details=[ModalityTokenCount(
  modality=<MediaModality.TEXT: 'TEXT'>,
  token_count=217
)] thoughts_token_count=357 tool_use_prompt_token_count=None tool_use_prompt_tokens_details=None total_token_count=623 traffic_type=None\
""",
                "total_tokens": 623,
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
                            text='{"title": "THE NAME OF THE WIND", "rating": 7, "author": {"first_name": "Patrick", "last_name": "Rothfuss"}}'
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
                                        "title": "THE NAME OF THE WIND",
                                        "rating": 7,
                                        "author": {
                                            "first_name": "Patrick",
                                            "last_name": "Rothfuss",
                                        },
                                    },
                                    "name": "__mirascope_formatted_output_tool__",
                                    "partial_args": None,
                                    "will_continue": None,
                                },
                                "function_response": None,
                                "inline_data": None,
                                "text": None,
                                "thought": None,
                                "thought_signature": b'\n\xe9\n\x01r\xc8\xda|Eh\xa5\x9e\xb6\xa4`\x95\xb7\x9b\x90\xec\xb9o\xdbOo\xce\xf4\xb7^\x94\xcf*aB\xe0.\x17\x9f[@!n\xb2\x07\x12\xde`\x8a\x1c\xcc\xe9\x90]/\xad\xa6\x8c\x02w|\xc7Fz\xea\r)\xab\x0c^\xd4\x1d`\xb5;\xb4ZTe,\xa6\xd0\x0c\x04\xcbL\xf7\x1d$;:!c\xb8w~\xcb\x1b\xcc#IH\x81\x14x\x1e\xdb\x02E\x04\xa5\x87\xa1\xfd&\xc5\x96\xd4\x8d2"\xdb]+\x18\xb9O/\x94\x10\xab/<1A\x98O\x9e\xcaH\xed\xc2\x9e28trn\xaf\xde\xeb\xfc\xf1*\x1a\xbf>)q\xd4\x915f\x18\x15h\x1au\xf4\xc2>\xca_5\x92`\xb5z\xa5/\xe5\x9b\xf6\x19\xb4C\xa5\xec:\xdb$\x9a\xe2}\xd4\x03\x80\x04%\xaa\t\xf8\x1d4\x01\x91\x1f\xda\x98\x1e\x19%[1\xaf\x9e\xc0^\xdf(\xa6\x13\xc5\xdd\xd6AR\xad\x02\xed\xf1\x1dl\xc6C\xe9m,[\xda@\xc9\xda\xa8\xfdW?\xba\x9e\xd1\xa1@\xd1\x07\xa4\xc8uO\xa6\xca\x86\x99\r\xfa\xaa\xc52\xa06\x99\xe3\xd8|\x9c\x991\x077e\xc4|\x14\xbav\x08\xee\x04/\x8b\xca\x9aex;`<\x1b\xd1\xf0S/07\xbc\xec\xf9\xb1e\xe9\xb9\xf5"69M\xc4l&n\x8aX\x06\xa5K\xd0\xd9\x16\xeb\x83(}44\xd0\xc3\x8e\x82\xd6\x96\xd5u\xf5l\xcbj\xfa\x95\xda\xbe@\x04r}\xc2\xb6[\xeb\xa3k\xe4A\xc5\xbd\xa9H\xd2Kn\x8e\x1b\x8c\xbd\x946K\xc7\xff\xcf\xac\xa0\x89-,S\xbc\x9d\x13+\x15\xac\x12*4\xe7v\xc1\xb9\xe5\x9aV=p\xa6\xc2Z9t\xff\xbe8\x12\xc6\xee\xde\xdfi\xd8\xd5?\xd8R\xbfk\xd8\xd4sO\x85\xf1\x97\xf3`\x0f\x91\xed\xbf%\x1a\xa2\x81\xdd\xbe\xb5D\xd5\xe6m\x1e`\xa0Mh2)\x95\tqX\xf9\xbf\xd3\x90\xed\x9eW\x0e!<\x86\x9f\x19\xff\xb1w+cV\x8d\xc9LcM#\x1d\xfb\x19\x07\xbf\xb4\xcbZ|e\xa8tw\xc4\xdb\xf0\xa7\xb9i\x8e\xd0I\xfa\x07d\x06H\xcf\xea^\xd4hv\x18\x1a|PI\xbcf\xd9&\x08\x91D\x94\x1f\xc2\xcf\xb4+\x7f\xd0\xb8\x89#\xc0V\xbd-3\xa0X_\x95\xdeV2`*\xcd\xb2\x16S\x0b+\xec\x94`\x88\xf4\x1b\xc7\xf4\xde\x80\xde\xc2\xa6\xcf\xd8\x958Q\n\xe7#\xb9\xe0\x80\xb9D\x811\xc0\xeb\xdd\x91\x00l\x86G\xa1m\xfcB[\x1e\x7fE:\x06HO\x9d\xc7\x86\xedZ\xb1\xb9e\x94\x80Jm\xcc#\xc2Z\xbcY5\xa0\x02\':\xc1j\x07\x0e\xfe\x80\xcaX\xaa\xc5\xed\t\x12\xa9\xdd\xab\xf7\xed\xab\x00G_\n\xbf?o\x964\xb7\x01\xae\xcc-"\xbf y\xfb\x0b\xf3\xc6\x14\x143(\x11\x1b;\xf0\xe3T\xc1\x1b\xfc\x0c^i/\xa9\x1c\xda\xfb\x91\xea\xfdW<Gs[\xaa\x0e@\x8d3(v\xf6\xdflH\xd1\xa2\xcf\x0b\xdd\x10\x1f\xd7\xe9)U\xa5&}\xe6\xf6/\xdeB\xef`,\x8d\x93\xa5\xc3\xe2\x95\xe1\xf7\x17\x90\x16\xefC\xb1\xc7\x08\xeb\x9a"\x00\xd6+k\xe7\xf0\xe9\xce\x07\xac\xe1\xf1\xb8&r\x02\xc2\x16(\xbe\x951\xc0{\xf0\xa6\xd9\xb5I\xfd\x15\x80\x93\xc2\xe7e\t\xf8\xaa\xbd\xef0\x0e#nRZ\xcbs\xad(\xeb\xc6\xd1\x03}\x90\xaa\xf79\xe6p_\x7f\xe2\x00~?\xacRj\xd3\xa1\xfd\xe4\x10~\x1fr\xe1p\x87\xc8\x02`\xadb\x16\xe3\xeb\x15\xb4\xfa\x0bO\xbat\xd0\x88\x8c\x12\xe7/\xdey[Ob\x0b\x07\x95\xcc\x96\xabbj\xfd\xb4b2h\xb2&\xc3\xee\x17Y\t\xac\x0f\xc2\xd3\xc2\xb3\xdc\xf2#\xad\xe9\x8c\xcb\xc6{?\x8e\x03\xf5\xba\xd6\xdc\x90\x13S\x8f\xdf\xe8!\xfd\xca\x8a\xc5\x81Ad\xbc#\x83A\x95T\xd0\x84\xc0w$"M*bB B\xe5*p\x88\xc9\xcd\xba\x92\xe5S!N@\xc5\x16i\x0f.\x01\xb9\xc7\x15b\xcf\x0bG\x1d\xa6\xa5\xbb\x9e\xceP\x88\xb2\xcd\x8fl\x0f*\x91\xf94\x1d\xb5\x97r\x94\xfc\xb7\xd3\xbdW\xc8$\xac>\xb4\xa7\xe9\xbf\xb1\x98\xd4\x84U\xfe\x177]\xc9x\x08\x8b\xeekn\xa1\xdaJr\xa0\xa0dg\x1ay\xa9\xec\xea\xe8\xc1\xc4\xcf\x01\x85\xda\xc5>\xc7#\xec\xff\xc1\xd4\xdd\xef\xbf6\xd1\\\x97\xa5\x17\xbc\xdan\x84!P\x16w2\xff\xfe\xbf\xb1\xdeA7T\xd7\x8a\xae^f ZH\xf67+s\xb9\xae\x93Y\xf2d\xc6\xe72\xdc\r\x8a\xf5\x07#e9f7O\xff/\x15\xfc\xed\x06\xcd\xfc@\x91\xfcp\xc9\xf1\x98\xbd>mH\x9f\xe0\x1en\x10bG\x00\x1ay\xc8\xff\x1d\x11\xe7\n.@\x9f\tfw\xc8O\x0bT\x1f\x00\xb6\x13|^\xcd\xbc\x89r\x05\xe0W\xf0\xaeS\xef-\xc4\x15i\x10\xc9\x07&ZN\x04N\xdbK\n\xdf\xce\xfc,\xef\\\xb3\xe6>q{\xbb\xedV\xcc\x17\xa0I\xf3{S\x96N\xa4\xdd;\xd3\x1b\xe1\xd3\x13ic\xa5\xfc\x7f\x9b\t\xb2*\x8b\xbe\xe9C\x86\xe1\x02\x1c\xbeCyn\x88)2o\xdf\x89o\xa1\x81\xa3\xa7ZYm\xd0A\x82\x12\n\x0f\xb6F\xee\xe9\xff\x814\x8aB\xa1\xe8\xba\x11P(^H\x88x\xde\x9a]+\xd6\x19Z}^\xee1\xd7jbo\xecKI\x02\xc8\xd2`\x08\xe5\xf4e"k\xe4\xccW\xe2B]\x93\xe4\xab\x08*\xb8\xf4\x97\x14a\xc9\x88T\x9b]\xb0^\x1f\n^o\x82\x03\xfbz\xcfv\x86\x9b<>\xe5\xf7zY\xa7\xac\xbe_\xd68\x87\xa8\xfb*\xd1\xaf{\xa1\xa0\'Myb\x18\xc7\xa3`<\xe3c^fnL_"\xdd\x0fU\x07D\xe4%\xd6;\xa0\xc3\x93\xe9\x1a\xf1!;\x183O\xe7\x9c\xfc',
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
            "model_id": "google/gemini-2.5-flash",
            "provider_model_name": "gemini-2.5-flash",
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
                            text='{"title": "THE NAME OF THE WIND", "author": {"first_name": "Patrick", "last_name": "Rothfuss"}, "rating": 7}'
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
                                        "title": "THE NAME OF THE WIND",
                                        "author": {
                                            "first_name": "Patrick",
                                            "last_name": "Rothfuss",
                                        },
                                        "rating": 7,
                                    },
                                    "name": "__mirascope_formatted_output_tool__",
                                    "partial_args": None,
                                    "will_continue": None,
                                },
                                "function_response": None,
                                "inline_data": None,
                                "text": None,
                                "thought": None,
                                "thought_signature": b"\n$\x01r\xc8\xda|\xdb\xd0\xee\x17uk\xb6V\x92t\x91(8\x94%nH\xb7\x0c\xe1\xa5\x1e\x14n\x95G\xa6\x9dJ\x8b\xd3\ns\x01r\xc8\xda|\xbf\x0f\xac\x0b1o0\"=\x8c\xb7\x84\xcd\x17\xa5\xa6E\x9fmq\xc5\x04e\xcf\xde6d\xb0\xaa\x98\x97\x0c\xee\xbd\xf1+\x00\xa5\x7f[\xfc\xe1Q\xe0\xc3\xb3F\xb0\x7f\tT\xcd\xec\x1am\x15\xf6)\xd8t1REM\xfba\x99_\xe4s\x0fH\xc6Nx\xd3\x8d>\xa5r^\x83Lf\xe9-\xe4H\xa7B\xa3\x14\x94#F\xa4EoP\x18o\xdc\xaa\xf3\xc1B\x1d\xb2\x05~\n\xdc\x01\x01r\xc8\xda|\x82M\x16\xd9\xd1\x01\x16%\xadC;0r\x1f\xf0{\xe3\x8a\xda\xd8Mn+\xea\x17\xf4`L\xa5\xa3\x88\\\x17q\xb0\naB\x87\x13\xe5\xe8\xedV\x00\xedx\xda\xec.\xe6\x1b\"|\x11.\xb6Z\xb9\xc1c\x18\xc3\xa1\xbf%\x08ww\x05T\x00\x98x'UE\xdf\xca.R\xd2\x91\xccY\xa7\xb7\xcb\xc6^\x96\xd3v\x94/\xc8\xfdL\xa7\xbck\xd2\x0cxG\xeb=U\rZY\xb5%\xf9\xc8\xbbL\x97D\xc7\xa0^\xbc\x7fF[\x8aZ\x18 \x15\xbc\xb2\x86\x9b\x07\xb7\x18Uv\xd3\x98\xd5\xfc9\xcf\x8d\xf5\xd5\xd8W\xca@\xf8\xcf\x8d\xbft\xf7\x82\xfa\xc9A\x9c\x04\xcb\x95\xc7\x01K\x1c '\x11\xc9\xe2\x99\xdf\x9d\x1c\x88\x9a\xcb\xd8Y|\x8f\xf6db \r'4ZL\xb51\xe6k\xd7#\x9eL3\xe2\xb8\x12\xc6\xde,8M\x1e\xf7\n\xce\x01\x01r\xc8\xda|\x02\xfc,\x9d\xcb8\xf6\xf5\xabi\xfe|\x84\x11F\xb1p@\tBC\x0bBS\xb8E}\xf1\xdc\x8d-\xd2@\xca\xa4\xd1\x98\x13\nC3\x08\xb27+,\x13\xd2\x14N\x84cJ\xf2\xffz\xb3\xa7oX\xf1\x17\x80Y4!\xf9\x1c\xb6R\x8a\xc0.R^\x02a8(\xa7\x15\xa8\xdf\x98\x8b\x97\x19\xac\xea\x0b\n\x90\xe05\x8e\x11\xc9\x9fh\x07\xd1$,\xbdl4V\x18Y\xb1D\t|*\x16\xd9\xafG\x80\xf2\x87\x88*\xdd<{\x11\xdbV\xffB?Z\xad\xe9\x1f\x0f\xf3\xd5q\xa3\xb7\xf3\x9c\xfe\xea\x18\x8ay-!R?T\xcc\n\xd6\x8a\xe6\x0b\xf1\x8f\xacwAD\x00\xd7\xa7\x1f'{3\\\x85\x96\xc0\xe2\xae\xdd>\x17\x86\xc6\xeb\xcc\xfc\x86\x81\x99)Cl\xad=\xdbj/A\xf6\x98\n\xca\x01\x01r\xc8\xda|\xde\xfb\x96\xa7~\x05l~\xf0\xd6\xe9\xd8l9\x80\x9aQ\x89d?\xb3|tS\xbd\x9bS\x9fh\x13\x87\x9065\xedS\xf0\xf4\xd1g\x1bEbC7\x13\x97?\r\xabP\x95#Dmk\x98[]\x9bh\x896/2\x8d%\x03\xe7r\xc2q\xea\xfc}\xa8f\x89x\xab\x857|t\xe7\xd6\x8c$\xfd\xf7\x7f\xf5B\xab\x8e\x00@J\xe7\x1c\xf5Q\x0f\xb4\xb0Oo,\xc4\xf9\xce\x80-[\xf2\"\xa9O,6\xda\n\x99\xe7\xb7\xeeq\x1a\xda\x95+\xf5\n\xceM\x99T7E\x0c\xa4\xdb}\xe1H\xaf}\x88\x1a/\x81\xce&F\xf6\xfcom\xe7&}q\x9d*4\xd4}\x90\x8cw\tm\xa3\xaf\x1a\xaa\x84\x90\xdf\xd1\xab\xa7\x0bw\xba\xcfw\xdb\xfc\x87\x8bE\xd2_\xba8\x01\n\x9e\x01\x01r\xc8\xda|\xa5\xdb\xd4n\xc0\x87\xe8+\xa9\xb2K:\xaah{\xce^k]\xf4V2\x86\xaf\xa6\xc1>\x88\xb0p\xeb\xdev\xdf\xb2n(\xe4\xc5\x94\t\xd3\xbd[\xd9\x97\xb1\xb6u\x1f;y\xf9N+,\xdd\xc5\x9c\x1bCK\xc8v\x7f\xb9\x05\xd6:x\xdeIt\xc2.4}\xd5\x8am\xc6]\xaa}Vt\xc2\x08S\x0boT\x82\xe1\xb8\xd99O\xf7\xa9\x1d4\x04\xf2m\xdbX\xe8\xbc\xd8\xd5K\xce\xc3u\x9d\x13}\x03\x12\xce\xbd\xf9l\xd1-\xbc\xcb\x08\xe0\\\xddc\x87\xaas\x9c\xf5\x1biMm\xc5\x00\xccR!\xe0\xb6\x7f\xd1\xa8j",
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
                "reasoning_tokens": 204,
                "provider_tool_usage": None,
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
            "model_id": "google/gemini-2.5-flash",
            "provider_model_name": "gemini-2.5-flash",
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
                            text='{"title": "THE NAME OF THE WIND", "author": {"last_name": "Rothfuss", "first_name": "Patrick"}, "rating": 7}'
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
                                        "title": "THE NAME OF THE WIND",
                                        "author": {
                                            "last_name": "Rothfuss",
                                            "first_name": "Patrick",
                                        },
                                        "rating": 7,
                                    },
                                    "name": "__mirascope_formatted_output_tool__",
                                    "partial_args": None,
                                    "will_continue": None,
                                },
                                "function_response": None,
                                "inline_data": None,
                                "text": None,
                                "thought": None,
                                "thought_signature": b'\n$\x01r\xc8\xda|\x8dj\x92V{N\xe2\xb6p\xa7!9\xdc\x89\xdb\x13\xd9j\x07\xffE\xebj/\xf8d(\xe2a\xd4,\nr\x01r\xc8\xda|j\xc2\x9cE\xfe\xb6v\xbf\xd0sz\x11\xa4\xf6\x83!$\xae\xd6oz\xed\xd6\xe5\xd7\xd7.L0\x8b \xa5 \x91$\x147\xb9\x84!\x9c]\xb0\x1c@l\xc5\x197#\xaf\xec\x0b9\xc8\xe5\xc0\xdegE\xbe\xb5V?\t\xd7\x98\xeeLE110F\xed\xbf\xb1\x88-\xd6\xc5\x01\xfa\x86\xe0\x84Myx\x10\xbb\xd6\xe02\xf4\x00\xb9\xbe\xf4\x03Zo\xd1\x1d\x8c#\xd1M\xb1\n\xec\x01\x01r\xc8\xda|4Z\xc3\xb1\xa3s\x91\x12\xb4\xa0\x91S\x1f\xb8Y\xf2D\xb1M\x03y\x15L\x80 \xda<\x1e\x95x]\xec-\xa7<\xfd\xe8~\x00\x9e\xa0\x85^\xf5\x82\x8a@\xd8\xb3\xd2\xbe\xe5\xdb+\x90\x87l\xcbM\xff\xb9\xe1\xfb\x17\xc7\x8d\x82\x7fvnm&\xe8\x97\x84\x83&\xcd\xb2i\xd1\xde\x18\x95\xbb\x97\xeb\x8d~"/\x97\r\xa1Tw\xb6P\x07+Yjp\x86\xe2\xaf\xabH\xd0V\x94\xa6u\x9a\xa8\xf4\xa1\xe4\xcct9\x05\x80\xb7\xf1\x854\xca\xf5\xdaY+\xb3\x10ZA\xdfQl\xaf\xe2\xc0$\x1e?p;t\x0bl\tc\x861\xad\x0b?\xe8\xf1\xca\xacW\x84/\xa3=\xac\n\xe5\xba\x84\xd3}\x96\x18\r\x0f\x17\xde\x87\xd1\r}.\x92\x84n\x9cR[>i\x03z\xd7\xb3\xfd"\x1769\xd2\xb6\x88\xe5\xff\x84\x12\xe6[I\xdf\x04t\xec\x81\x96\xa6\xf3i\x1dd\x04\xd9\xf4\xaf\xc2\xe7\xe6\xe9\xae\n\xc0\x01\x01r\xc8\xda|\xc0\x11\x95\r{\x020o\x15\xc6\x7f\xeb\xec\xe30\xb0\x1b\x91\xc9\xe5\x9d3\xf3\xa4\xbb\xc8\x8d\xce\x15&\xaa\xbe\xe7\x87\x17\x0e\xcazra\x1f\x17\x86\x17\x8e\x9e\x87\xb1,c\x14\xc6*\xd5\xbe\xf06W\x00\xf2\x12\x92;\x95\xdd\n\xda:\xf9\r\x1e\xee\x83\xe0%\xa4`7\x98\x00\xf1\xf9\x1b\xd4\xf1\x92F\xd1\xb7~$L\x9bJ\x83x\x9dZ\xdc\rT\x01\x16\xa0Cf\xb3f\xb70e\x8e\xc3_\x89\xb3\x1a\x86\t\xfe\x95vb\x15\xd6\x1f\xa5\xccFW8*ZR1\xa2fz\x08\x187\x08\x88`z\x17\xb1j\xc7\x98\xe0\x9e\xe9\x87\xda\x10\rP~Z\x9a\xdd~\nN\x0e2\x1b\xd7\x9d\x15\xfe\r\x81\xad\xc9G\xbeo\xdc\'\xc5)\x12F\x11\x87\n\xf5\x01\x01r\xc8\xda|c\xfaDT\xcb\x92\xa5\xf28\xb6%\x06f=K\xd7\xa18\xc0e\x08\xa8\x13-Q\xd3\xae\xb1\xa6C\x17Bp\xf7>p}c\x81(\xca\x14h\x03\xae\x9d\xc7\xc1\xc4\x86\x8d,\x8b\x8a(\x13\x92\xa2u&\xd2\xc1\xd9\xbd[\x7f\xf8\xda7D\x8c\x10e\x90\xff\xf0|\x98\xb0\xdd\x86+\xe5\x89S\xb3\x1bt\t0\x00\xb5\xbc\xcd9FJ-\x18[\x00C\x86h\x16\xad\xabfHBWp\x8a1s\xc0\xa1O\xa8\x929\x0e\xc0\x0fQN\x0b\xdb\xaf\xe87\x9b\xfb\xc3s\xfd[9"53W"\xd5\x0fo\x0e\xe8\xa2\xbd\xa9\xd0N\xc3<v\x80Z\xff\x1a\x80#C\x83\xfc@\'\x85\x9fW\xc7d\x94\xa5\x02|\x89b\xae\t\xebSo\x82,\x8f1A\x0f)\x8e@\x17\x8f@(\x18\xc4\x17\xc4X\xf38\n\xe3\x01\x81y\n\x00\x9c\xd5\\\xe5\x95\x95\x1aC\xb5\xc4\xe1]\x852\x88\x17F\xc9\xfa\xb6\xec1\x9e\x18\xa9\x94\x88\xc6-\x9b\n\xb7\x01\x01r\xc8\xda|>oI\n=\xff\xc8U\xac\x1f\xa6R\xe4y\x8e\xe7\xd9\xe6\x1c\x94f\x8b\xbdz\x9f\xfa\xed\xc4gF\x14\x1b\xa6qwv\xee\xa8\x81\x92W\xab\xfa\x16\x17\x928\x86\x0b\xa7\xect\x8d+\xd2\xa0G\\\xba_\x8e\xd2\xc4 \xac\xbc\x8e\x82\xcfu-\xa5\x89\xe72G+\x0f\x19\xea\xffl\x08\x08\xce_\xf0\xf6\xa6\x8f\xea?i7\xfe\x08\x87\xe7\xda{\x8f\xa6\x8f\xe85B\x922\xc9\x83!?\xa1 ;p\'>\xe6\xb8\xaa\x082\xb5\xa9Z\xb9\xb8Z\xf4\x0e]\xbb\xb4\xaf\x1b\r\xfca\xd6D\xeb\x10\xf1\xee\xe6D\xe6:+5d[{\x00\xdam\xe8.\xa9\x98\x9a\x86\x13\xec\xfd\xbd<\xee\xe4\xbc\xe7\x08w*}S\xad\nJ\x01r\xc8\xda|\xe8j1\xb7D\xe3\xa2\x01\x98&a\x12\xdd\xd7C\x0c\xe3\xeb\x86Qu\x1f\xbfp\x8a/L\x18`\xad\x8e\xda\xafL\x81E\xdd\x80f\xde\x15\xa2\xf3\xd1\xfb#\x03\xd8\x17\x13\xc5\xca\x14\xae\xed\x97\xff\xe0\x08\xd3\x80"\xc1/\xc1\xf107\xf1',
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
                "reasoning_tokens": 231,
                "provider_tool_usage": None,
                "raw": "None",
                "total_tokens": 266,
            },
            "n_chunks": 3,
        }
    }
)
