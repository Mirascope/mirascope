from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    SystemMessage,
    Text,
    ToolCall,
    ToolOutput,
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
                "input_tokens": 268,
                "output_tokens": 267,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 218,
                "provider_tool_usage": None,
                "raw": """\
cache_tokens_details=None cached_content_token_count=None candidates_token_count=49 candidates_tokens_details=None prompt_token_count=268 prompt_tokens_details=[ModalityTokenCount(
  modality=<MediaModality.TEXT: 'TEXT'>,
  token_count=268
)] thoughts_token_count=218 tool_use_prompt_token_count=None tool_use_prompt_tokens_details=None total_token_count=535 traffic_type=None\
""",
                "total_tokens": 535,
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
                            text="Please look up the book with ISBN 0-7653-1178-X and provide detailed info and a recommendation score"
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        ToolCall(
                            id="google_unknown_tool_id",
                            name="get_book_info",
                            args='{"isbn": "0-7653-1178-X"}',
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
                                    "args": {"isbn": "0-7653-1178-X"},
                                    "name": "get_book_info",
                                    "partial_args": None,
                                    "will_continue": None,
                                },
                                "function_response": None,
                                "inline_data": None,
                                "text": None,
                                "thought": None,
                                "thought_signature": b"\n\xbd\x05\x01r\xc8\xda|\x1dk\xacN\xde;\xd0\xeb\x9a&,\xa6\x8f\xda\x9dzTjf\x18\xfb\x14#\xf4\xa8\xb8\xaf\xec\xadN\xc2d\xe6_\x91w\xdfH\x03\x1f\xb7\xed\xe4a(M\xd3\x04\r\x18P\x9f8\xaae\x83\xeek\x8b\t\xa5\x10\xe8J\xd0\x15\"I\xb5\xd8\xf9\x89-\xe4\xfd(\xd4wT\xc1\x00\xfa\x12}\xa3\xfcz{\x9fp\xe0\x1b!\xdfu@\xe1\xbd%}<x\x1b\xd0~\x01\x15\x11\xb3C\xd9\xb1V+n\x9e\xdbN\xf4\x98\xcd`\xb6\xc5\x07\xee(\x14\xd2m\xa9\r\x1cK\x16\xfd=\xc4GVb\xf6\xd2\xb9\xc7\xc4\xd3\xb7\x10\xa8\x0f\x80\x8a\x18\xa0\xb5\xde)y\xc6\xa4!\xed\xaan;\xddX\x02\xd3\xf7\xdaX\xa5\xf4\xbfya>K\xa2\xec\xdeQ\xf7\xdco5F\xc9\x95\xdaE\xfaW\xc9k]\x98\xb3!\xa0\xdc\xb23\x00e\xbc+\xcf\x8ah\x80\x8d<\xc2Re\xb2m\xd6*\xbe\r\xa5a'\\Q\x7f\xa7m\xe0\xea\x19\xa9\x0c\xee\x86\xb3\xa1.\x1f\xfc\xb3\x04\x80E\xce\x92\xf9\xfe\xbf\xd97\xaf\xa0\xf5\xdc\xa7\xc4\xb56S\xb1\xa3-\xa4\x94M\xb8/*,!\x04`\x83\xf6]\xae\x10\x98\xb98xy\xact\x89D\xb8J)\xfb\xfc\x06\xfb\xde\x81(r\xbe9\x05\x03\xa9\xe2v%{\x81\xc9\x8c\x9e\x82\xafe@\x00\x98\xe6\xe5n\x1f!\xb4\xd3\xacW\x8b\x05\xe4TD\xd2\x86\x0e\xad\xd4%\xfd\x13\x8f\xa97g^\xf9\x10c\x82S\x1b\xa7Gp\x7f\x1b\xd6\xb4\xb4\xc3Q\xcbib\xcc&\x96b\xfd\xb8\x0b]\x87\xd1a\x81C\xef\xb2\xe5*\xe7\xf8,1x\xacF\xcc\x8e\x83\xe1c\x94Lu\xd6U\x87\xca\x85\xf9\xfd\xe7\xd1g\xbeez\x8f\x89\xfa\xab@;^\xac\xde|\x93\xb2^Z\xc1\xd8<\xf1h\x10[}j$0\xba\x13\xcf\xe0I5\x89\xd6h9\xa5\x99f\x1aJt\xe9t\xb8\xc4>\x1e\x08\xf5a\xf9\xc7\x08Hj\xd8\x01\xff\xf2;c\x0b:\tf\xcfl\xe1 '\x07z\x87\xcf\x81\x93\xd9/\xa5\x87\n\x8e\xe6\x9e\xf4T\x85\xc7\x9e\xe9r`,w\xbbUu\xf0\x0b\xc6\xbc\xf3\xfbS\xb69\xb7\xaf\xbf\x14a{5\x0e\x8b\x113\x0fQ\xb1D\x05\x9f{ \xee\xd3\x10\x148D\x03\x00\xd3\xbb%)\xb6s\x08\xb78\x85\xbfT\x19\x0b\xd5\x01\x9eJX\x1b\x85\x1b\\[U\x8d\xd96hr\x91L\xa5\xc0\xd8\xdcc\x1e\xfe\xaf\xb8\x17BC\xe4\xee\x87\x88\xb6\x166\x12&\x98\xaa\xd3h\xf1\xf3\xa0\x89\x85\xd5b\xb3\xbe\xe5\x9d\x91f\x1c\x15Vt\r=\x17GW\xf2\xa7R\x0b\xec\xdf\xddNu\xae+\xceQ\t\xb9\x06\xd6!mx\xdd\xaa\xd0h\x88\xdd\xdc\xa7$ryF\xd9&\xf8\xd2N\x80b\x01\xd0\xf3\x1f\xdf\xff!y\x81~\x94\xefu\x0b\x14\xa6`\x88\x0c|\xf7Q\x9eS\x0f\x92\xe5\xd4\xf2B\xb8\xc7\xf2",
                                "video_metadata": None,
                            }
                        ],
                        "role": "model",
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="google_unknown_tool_id",
                            name="get_book_info",
                            result="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text='{"title": "Mistborn: The Final Empire", "pages": 544, "publication_year": 2006, "author": "Brandon Sanderson"}'
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
                                        "title": "Mistborn: The Final Empire",
                                        "pages": 544,
                                        "publication_year": 2006,
                                        "author": "Brandon Sanderson",
                                    },
                                    "name": "__mirascope_formatted_output_tool__",
                                    "partial_args": None,
                                    "will_continue": None,
                                },
                                "function_response": None,
                                "inline_data": None,
                                "text": None,
                                "thought": None,
                                "thought_signature": b"\n\xa8\x06\x01r\xc8\xda|@\xa1\xb1\xaaz\xcd\xc5\x17q\xc7\x90\xfb\xe9\x19-\xef^q\x0c\x83\xadP\x9b \x1c\xb0\xd5\x1d'<\xda`a\x08\x9f\xa7\xf8\xa2\xef|\xaf\xee0\xb1_\xb4\x95u\xfc\x1a'\xe6\x0f\x0e\xa0\x1b\x02\xbd\x0br/\x80cC\xb1rv\xf0\xbd\xb8\xa6`\xeb1\xb0\xa5\xa8\x81lV\xfaV\x9bc\xdc\xea\xd2\x17\xea\xdc\x0c\xe3\xee#\xfa\xee\xab'\x9a,I\xd6\xd5\xae\xa7\x9at\xa4\xd9\xa1|\xca\xc2\xa8\xe9;\"J\xb8j\r\x1a<T\xa4\xe3\xf9\x87I\x17'\xbea\xbaz\x87\xf9\xb7\xe7\x7f`\x1e-v\x0b[\xe4?l\x0f\xbb\tx\xde6O\xc1d\x96\x1b\xd0\xec\xab\xc6NZ\xd4[\xc3\x97\xdb>\x11\xc5\xfc=\x86+XW\x87\xbfG`2X\xfa\xd2\xcd:*}\xdbn6\x0c64\xa9\xb9\xc5\xddk\"o\x83!'D\xbb\x18\xf4\xe3\xc0\xac0\x92.8)\x14=\xe2\xb5&L\xe2kv\xef$A\xcc\xbf\x91`\xfbJ\x815\xd42=\xe4\xf1\x04(u\x92\xf1yL\x80\x80\xaf\x0b\x00o\xbd|L\xf4:I\xf3\x9e\xfd\x96\x82\xc7\xe5\xfc\xfc}\xc7\x15N\x12H^\xd5|\xc9\x13\xaf\xc3\x18\xe2\x1el\xa6\xc9\x13\xbdJ\xb0\x15\x05#\xdc}\x93\x1c\xf8k\x84\xbd\xfd\x08\x8c*\xf1{n?~\xad\xf3-\xe9\x7f\xa4\xd3\t\x10\xc9\xbd`\xa3\xcdk\xe5\x07_V\x1e\x15\xadO=\n\x8e[\xbf\xc7\xc3\xfdO\xac\r\x95\xd7\xd6\xde\xd3\xe9d\xc0\x11hh}u`\xc1N\x95#\x0e\x04\x8dsj\x98\xf1\xc9\xd8\x86\xbf\xa9\x14AK\x10\r\r+0\xdc\"s\xed\x80\x90\xe1a\x0f\xc4e\xdc}\x939\xb3\xf7\x07nUZ\x87\xd8\xd6v\x94\x9f\xc5\x8c\xba\x15\x19\xad\x95T\xa1\xb5\x11_\xcf\x90\x0c\x0c\x0e\x07\x81\xf9S\x9dK\xb5\xf5q\xe6\xb3M5K\x10\x9a\x8cJ4\xfb\x87\x0cC\xce\xc4\xf1\x84\"l\x05\x91\xc5yrQ\xa91R\xcdSPW\xb3\x0c@\xbc\x19\xde\x04t\xc2\xe8\xc39D\xf5\xe5\x051t\x05_\xc1_\xb5\x05\x97\xd9x\xf5\xf8\x02\xacP\xad[v{R\xa3Jc\xce\x9fT4\xf2oZ$\xc8vB\xc0\x85\xe0\x0e\x83\r\xd6.\xba\x968\xcd\x9f\x920\xd1Y\xc3\x1e\xf7\xf8\xe3\xce\x87(\xa2\nXI\xdf\xac\xde\xbd\xe68\x84g\x06\x9dkH+\x9a\xc9\x85C\xab\xf1t\xa7\x8f\xd6_\xdd\x9fN\x1a\xb3\xa8\xb0l8?\x05REA\x16\x83\xdd<QU\xf1\x87\x99\x9aMk\xf3\x9f\x84a9\xa8\x81\x14\x94\x81E\xbeQ\xe2\x16\xa3\x16\xfa\x06\xfb\xa7J\x9e\x8c\xc0\xb9\xba\x06x\xbc\xa7\xa5\x1e2\xe4\xe7\xa8\x91N\xd8!}\n\xf7+\xf7\xde\x1c\xef}\xfd\xb5\xa1l.,\xcc\x94\xb9\xa5\x9e\xf6\xf0\xaf\x98\xe5\x0e(\xa8\xf7\xaa\xf8\x1d\xbc4\xf0\xab\x01(\xbe\xe1Ym\x0bs\xeckztK\xf1;\x8d&\xd9O\xa6\xb7\xd7\xfe\xf6\xc9#\x8b`\x92\xfa\xbb#\x92b\x83H\xfc <\xf6\xd1\x95\xf7K|\x86_z\x9f\x1f\xde_W\x90c\x9f\xadP7\xa4\x1d\x84\xe3e\x89\x19\\\xe7\xe86\x91\xf6\xc2\xd8\x80\x07i\xbei\xd7\xdfm\x1f\xc6-L\xeb/\xc7\xe7\xbf\xafD\x12\xc1\x1e\xe0\xea\x7f7m\xed\x88\xfb\xd0J\xd7&8\x9f\xe7\xfd\x10\xf1\xac]\xc3\x1a\xab\x9aF\x06",
                                "video_metadata": None,
                            }
                        ],
                        "role": "model",
                    },
                ),
            ],
            "format": {
                "name": "BookSummary",
                "description": None,
                "schema": {
                    "properties": {
                        "title": {"title": "Title", "type": "string"},
                        "author": {"title": "Author", "type": "string"},
                        "pages": {"title": "Pages", "type": "integer"},
                        "publication_year": {
                            "title": "Publication Year",
                            "type": "integer",
                        },
                    },
                    "required": ["title", "author", "pages", "publication_year"],
                    "title": "BookSummary",
                    "type": "object",
                },
                "mode": "tool",
                "formatting_instructions": "Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output.",
            },
            "tools": [
                {
                    "name": "get_book_info",
                    "description": "Look up book information by ISBN.",
                    "parameters": """\
{
  "properties": {
    "isbn": {
      "title": "Isbn",
      "type": "string"
    }
  },
  "required": [
    "isbn"
  ],
  "additionalProperties": false,
  "defs": null
}\
""",
                    "strict": None,
                }
            ],
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
                "input_tokens": 268,
                "output_tokens": 273,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 224,
                "provider_tool_usage": None,
                "raw": """\
cache_tokens_details=None cached_content_token_count=None candidates_token_count=49 candidates_tokens_details=None prompt_token_count=268 prompt_tokens_details=[ModalityTokenCount(
  modality=<MediaModality.TEXT: 'TEXT'>,
  token_count=268
)] thoughts_token_count=224 tool_use_prompt_token_count=None tool_use_prompt_tokens_details=None total_token_count=541 traffic_type=None\
""",
                "total_tokens": 541,
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
                            text="Please look up the book with ISBN 0-7653-1178-X and provide detailed info and a recommendation score"
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        ToolCall(
                            id="google_unknown_tool_id",
                            name="get_book_info",
                            args='{"isbn": "0-7653-1178-X"}',
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
                                    "args": {"isbn": "0-7653-1178-X"},
                                    "name": "get_book_info",
                                    "partial_args": None,
                                    "will_continue": None,
                                },
                                "function_response": None,
                                "inline_data": None,
                                "text": None,
                                "thought": None,
                                "thought_signature": b'\n\x95\x06\x01r\xc8\xda|\x0e\xed\xe2\x87\x16\xaa*OwB\x1f\xa7\xee5_J\x92F\xabSl\xcdwI\x8c\xc4\x9bX7\x0f-l\x01\xc5\x80\xa0\xf9"t\xacO\x8eN\x8b\x8f\xc3\xe0/\xefT\xb0\t\xf0\x1e|\xf8\x9ax\x91\x17\xb8\xee\x8bn)Z\x14s\x18[\xae\xcbbG\xc1\xa3L\\\xc5\xb9@\x11\xad\xe9s\xfbz\x07\x02\x7f\x08\xa3\xb3\x96\xbb\x97T\xa4\x87Y\xa8td\xa4`K\xe7\xea\xa9\x96\x1f\xc8\x85\xdc9\x152\x82\x00Od\xaepR\x16\xf3\xce\x04\x88\xcf(q \xe1\xb9\xe8\x1b:\xfe\xa2&\xcb\xe94\x9c\xb0+\x03\xee\xdc\xa0l\x91\xf4[\xd0\x0c"}E\xaf\xcf\x17\xcb\xd5\xech\x0392\xd8\xdf\x05-\xa5/Np\xbb\xcd\xde\x19\x1d\xfe\x94\x0fW%\x9d\x08\xf1\xa5\x91\x13h\xd8:\xc7\xec\x0c\xab\xa6i\t\xda6\x02\xf7O\xd3\xc3G\xf8\x12\x94\xcd\xc2\xad\xd8w\xf4\xec\'\xdd\xcb\xa6j\x19\xcf\x19\x85{\xf3k4Kg^\x86\xf5\x9f;E\x0c\xdfKXsM*\x82\xb7\x0eL\xb6\xe6o\xcf\x1b7\xd2\x870\xa7\xe0\x8e\x99\xeb\xdf\x0f\xdcF\x95\xe8\'ts^\xd2\x84\x93M\xb7\x8bc\xd6B{\xcf\xa4\x7f\xdc22B\xe5zm\xea\xd5X#O\xa0n?X\xbd\xe7*\xb3b\x0f;|\xad\xe5\x08-:\xa0\x02\x19\x12\x97W\x14\x8f>\xa0\xcb\xec\xc6\x1f\x87\xa1\x1f\xc6\xedS\xc1\x16\x13\x1d\x03Q\xae<\xdf+\xb6\xf6\x16\xaaM\x80\x8a\x91\r:\x13\xb3\x8d{\xed\x15g\x08\xeb\xf0\x1f\x14,\x83Hs0N\xa2\xe9\xc9\xcd\xa8\x12\x949v\xfa\xcb\xd9c\xf0#\xday\xdb\x0el\xe3.\x99YW\xa7\xc6\xd0\xb2{\x9b\xb9\xe8\xda\x18\xd3\xeb\x1e3\x96<\xd3\xbb\xc8U@\xd8[,7\xf8\x86[\xa8\x18\xcdR\xda\x13/\x0c\x1f\xda$\x0b\xff\x94\xb3)\'w\xa8}\xd1\xc9\x07o9[\xb9\xa0\x08\xb9\xff\x8ce\x92E\xe05(\x91\xb3|\xb0-\xb5;\xb4}\x9dX\x92\x93\xf7\xcch\xd3\xb3^\xfa\x88\x99\x93\x8a\xf0/%u\xcb\x0b\xf6\xa4\xaa@\xefu\x1c\xd4d\x82D\x84r\xac\x0b\x04\xd3\x82\x95$\xcdg\xdd\xa7H\xb5\xe6\xc0He\xcbh\xc0\xa1b\x96(\x85(TJo\x83\xe7fZ\x83\xac\xcbv\x82\x81\x01\x9f\xe3[\xa1\xd8\xc4H\xfe\xec\\\x7f\xa1\x90\xafj\xcbWk\xe1\xb6\xb5\xa0\x8b\xc3\x1cDf\x80=\xe5d\xe5O\x9dk\x86\x94\x9c\xf2\xf9\x83\x80\xb6{;\x82\xd9p-nw\xb5\xf1\x1c\xbfb\x06\x1b22\xf7\x1b\xab\xfa\xbf\xbe\xc26d3\xb6\xf9G\x11\xbf|\xc5\xacj(\x1b\x04:\x13\xd2\x8e\xbb\xc1\x040F\x9b\xaaS3@\x90Zc?\x8e\xdf\x15VK.\x17\xe8.O\x1f\xef\x80\x0e\x93\xde\xee\x85j\xafO8\xb3V\x81\x16q\x19\xa0\x81\xa1Hg\xf9\xa98\xca\xb4(\x03\xcc\xee\xe0\xaa]\xbf\xe1\x94Y\xb6\xbcQ\xee]\x83\xd7\r\xd7\x93J\x86[\xa5\xfe"\xfc\xb3\x91\xc7\xc5\x96\xd6qyH\x07\x0e\xc3\xdeY\x82\x96\xd9\xeax\x11\x83\x85\x9d`v\x9a\x85{h\xed\xfe>\xa4B\xadg\x15+Q\x7f\xe0\xe9\xa0\xd6q\xf2\x8d"\xf31\xce\xa7\xc8\xa0\x8e:r\xe8\xaa\x1f\xeb\xc9\x83$TV',
                                "video_metadata": None,
                            }
                        ],
                        "role": "model",
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="google_unknown_tool_id",
                            name="get_book_info",
                            result="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text='{"title": "Mistborn: The Final Empire", "author": "Brandon Sanderson", "publication_year": 2006, "pages": 544}'
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
                                        "title": "Mistborn: The Final Empire",
                                        "author": "Brandon Sanderson",
                                        "publication_year": 2006,
                                        "pages": 544,
                                    },
                                    "name": "__mirascope_formatted_output_tool__",
                                    "partial_args": None,
                                    "will_continue": None,
                                },
                                "function_response": None,
                                "inline_data": None,
                                "text": None,
                                "thought": None,
                                "thought_signature": b"\n\xbd\x06\x01r\xc8\xda|\xedA\x15I\xbe|\xf2\xa5\xa7\xfd\xa9L0;.\xf3\xb3Oy\x9ct\xf4H\r\xfb*\x11\xbe\xbe\x8f0\x8bw_<[\x85Q=\x03*\xc3\xc0\xc48\xf7q\x10\xe0TGH\xf8\x8f^\xd3\xbaR\xeaL\xb0\xf6\x9a\xb0\x83\x93\x98Ex\xca\xf5~x\x12M\x91\x9b\xa7\x05\xd2\xe4\x96hR\xe0{\xfd\x96S\n\xa6\x16\xa0d\xe9\xae\xc8\x03\x03\xb3p\xb4E\x93\xd99>\x15\xac\xb8\xcfv\x9cp\xc5n\xe9\x1aV\xf6\xbbQ\xa89V\xee\x96B\xeb\xa6\xe1\xb1'\xb6\x9er\xe5\x9d\xbd\xf5Mv\xd9\xe9\xcfV\xc3Y\t[E\x0f\"\x02\xdd\x9b\x16 C/\x12\r\x05\x85(\x18)`\x8c\xd9\xe7\xe1\xd6\xc3#\x1e\x87\x1c\xef\xa5\xf4\x9eu\xb5\x85gV\xa7\xddn\x16\xf4\xab\xfd\xeb.i\xb9':\xf4}\xfdf\xee\x14\xf5=\xd0,\xe0Hxs\xe7c\xba\x1c\x92\x07\xf4\xe1o6\xedr\xed\x05'p\xbbL\x07`\xff#\xb1\x14{s\x1c\xd0\xff\xc7\x02\xa2( c%B\xbe\xc0_QXe1`\xf5^\x05\xeb\x87)\x8e\xcd]\xafD\xbdGA\xe6n5\xa75~\x15\xe0g\xeeg\xde1\x03Yh\x0b\x1a\x08\xce\xa2\x02\xe8L\x01\x0e5g\xb84\xb6{6\x98P:\x883\xe6\x11=\xea%\x8bh\x94k\x8d\x97\xd6\x82#K\xfcF\x03Z\xf7_-\xa5\x86\xa6\x88\"\xc3j\x1cN!y\xc5K\x05|\xaex\xb6\xe4\x93\xfd\x8d\xe3\x8e\x07\xb4\xa1\xe8f]\xca~\xe7\xa6YOWn\x0b\xef\xe1\xff\xdf\xaf\xe9p\xe8+n\x98)\xc6\x9b\x1e\xf8M\x90dD$\\\x04\xfb\xc4\x90\xd1b\xc2\x8f\xff\x1f\x8er\x8f\x89\xd8\xb5\xeb\xb4\xb4\x87\xd6\xa6\x87\x8e\xd81\x07\xb4\xba\x98\x1b\xb8\xdc\xa2\xe7\xbcu\x1aCh9\xca\x81\x04\xd6\x90\x89Uqy\xac\xa9)\x9f\x00\x99\xcfT\xfe\x9a\x8a-i\xf6n\xecw\x11K\x89\x89tz\x1b\xa0\xbdI-\xd5\x0c\xd7\xd6\xdd\xb9\x9c\xe4\x08\x92\xe1\x16)9K*\xd9\x96\xac\xb5 1\xa93\x113\xf1\x93\x1d\xe1k\xd5\\\x18\x95\x05{\x11\xf8\xa6@\xa1\xe5%\x9d\xaf\xa8\xa8\xe7\xb2\xe81\xff\x91\xa1\x08\x05\xbe'\xe8\xae\xe3(Y\xc8\xa6\xd5\xda\xc2X\xd9\x01\"\xe3#\xdc\r\xb7\xac\xc2P\xf7\xf2\xab`\xa07\x82\xfd\xa8\xb9\x10,\xa9\xe6]\xde\xe0O\xb4+_a\x95 \x13qJ\xd8\x04V\x96X\xa9\x97p\x9e6\xa8;\xde\x9f\x87\xe1\xaf\xee\xb0\x80\x96\xe7)h,L\x9d)\xed \xd6\x93\xa9\xd3\x14e\xf5\x12\xa7\xa4\x8c,\xfa\xe6-\\\xd7p}G'm\xc6\xc9\xb5j\xf5\xbb\x1e\x94\xab\xb5\x16A-\x06+Nj\x8a>S\x00\xe3Wb0V\xfc\xa8\xa09\xd8C\xc8\xc5\x82/\xb7q\xd7\xba\x12\xa7\xb1V\xa4\xa22\xb6C,\xadM\x04\x97@\x91:\xbb)P\x92\xc7R\xbc\x9f4e\x83(\xe6:\x17\xd2\xecM)\xf4\xf1\x92`u\xaf\xd6\x18\xe33\xca\xb4\xd6\x1f\xa8\xd9=\x7f] e\x1c\x0bc\xa6\xacopV\xdb\xd0o5\xa4yz;\xf4\xd0A:5\x16\x05b\xf6\x9bZ\xbc,\x96Q\x1c\r\xd3+\xa6\xad\xd2\xec\xbd\x9f\x84\xb8\x85:\x93d\xbc\x03#\x9e#\xe94\xc2[;\xfd3F\xe5\xaf_\xe5\xea\x9a\x98fj\x865lH\x98\xc0\x89\x06:OY\xe6@ai\xb5\xad\x8c\xa6z\xe4SWvI\xaf",
                                "video_metadata": None,
                            }
                        ],
                        "role": "model",
                    },
                ),
            ],
            "format": {
                "name": "BookSummary",
                "description": None,
                "schema": {
                    "properties": {
                        "title": {"title": "Title", "type": "string"},
                        "author": {"title": "Author", "type": "string"},
                        "pages": {"title": "Pages", "type": "integer"},
                        "publication_year": {
                            "title": "Publication Year",
                            "type": "integer",
                        },
                    },
                    "required": ["title", "author", "pages", "publication_year"],
                    "title": "BookSummary",
                    "type": "object",
                },
                "mode": "tool",
                "formatting_instructions": "Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output.",
            },
            "tools": [
                {
                    "name": "get_book_info",
                    "description": "Look up book information by ISBN.",
                    "parameters": """\
{
  "properties": {
    "isbn": {
      "title": "Isbn",
      "type": "string"
    }
  },
  "required": [
    "isbn"
  ],
  "additionalProperties": false,
  "defs": null
}\
""",
                    "strict": None,
                }
            ],
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
                            text="Please look up the book with ISBN 0-7653-1178-X and provide detailed info and a recommendation score"
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        ToolCall(
                            id="google_unknown_tool_id",
                            name="get_book_info",
                            args='{"isbn": "0-7653-1178-X"}',
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
                                    "args": {"isbn": "0-7653-1178-X"},
                                    "name": "get_book_info",
                                    "partial_args": None,
                                    "will_continue": None,
                                },
                                "function_response": None,
                                "inline_data": None,
                                "text": None,
                                "thought": None,
                                "thought_signature": b"\n$\x01r\xc8\xda|\xd8\x9b\xa8\xeb\xd0\x0b\xcb\x9d?\xcb\x9a\xaf\x8a\xcc\x0e\xf6\xb3\xcc1fY\xd5SSe\xbc\x10S\xa1z{\n|\x01r\xc8\xda|\xa9!\x84\xc2\xfe[~\xa5\x06\xc2\xf01\x0c,\xf6\xf3\xf2\xf6\xd8\xac\x95U?\t\x08\x95\xafAO\xd5\xfd\x9e\xf5]\x86\xderUm\xef;q\x06\x01\xe4\xb6\xb3\x0c\xd1\x89\xd3oheW~!\xa9i}\r\x86\x9b\x0e\xcd\x180\xba\x1c\x0c\x14\xd7\xb6\xcb\x1f\x90\xd7\xd2\x84oV_}z(\x11\xc2E\xb5/\xba%\x11\xb3\x99[$H\xef\xf4\xd2\xc1\xdc>?P\x95T9\xa7D\x9e\xa5}\x1c\x05\xd9\xf9\x1a\n\xf3\x01\x01r\xc8\xda|\xda\x87\x8d\x82\x90\xb8\n+\x106\xddA\xbd\x82D\xc19\xb3\x0fkF\xb9\xb7e\xa6M\x05>\x18\x01F\xca\x8d\xd2\xa6\x94w\x88\xf2\x97@2\xc4F\x19\\a8\x1d9\xcc\xd8\x99\x07\xea\xa6\xd3\xf59H\xdc\xebDt:\xde'\xde\xe8\xcb\x92{\x86\xdb\xce\x90\x18\x8b\xe3\xedEi\t\x1a\xb5\xe8\xee\xb8\x7f\x17'\xca`\xf8M\xa1k%\x93jq\x1dy\t\xa51\xdd\xa1\xe2\xf8\xbd\x04\xa8y%\xab/)\xa2w\xb4\x173\xbb\xa8\x85\x9af\xaf\xdc\x9a\x9ej\xf8\xaa\x13\x8c\x08\xea\x1e\xbf\x0e$?\xee\xd3\xf4_xW\xeb\x19\xd7Pl`dN\xa2U\xbf\xf5!\x90\x99)\xe5\x16\t\xf1\x0eL*\xb6\x04\xba\x81;\xd7\x83\xea\xde\x9f\xcdI2%\xab\x7f\x94\x8c4\x17O\x91\x92\x88/n\xb8\x03\xc9\xfe)\x0b\n\xfd\xf2,\xe7J1\x03\xab\xc0\xa7\t\xe7;\xdd\x0eA\xd8\xd5\xaa\x87\x97\x93Y\xbe!\x16\xd0z\x12\x8fLX\n\xef\x01\x01r\xc8\xda|t\xe2zD\x0f\xfa\xb4NA\x92\xe2\x9dg8\xd9K\xc2\xc9\xd0Gw6\xe2\xdf\xce]\xcb\x8et#\xb1B\x1e<4\x00?\xbf\xaa\xddk\x17\x8cd\xe9]/\x8e\x8fw\x12\x171\xab5\n\xa3\x05\x15S\xdeT;\xe0T\x1c\x0c\xac\\\xe4##\x07&\xf0\x1f\xef\x9c\xd5U\x8f@\xd6\xf3>\x1b^\xf1\x0e\x1f\x87l)\xfeV\xdc\xe2\x08\xe4|\xf6\xf8\xd4\x17 \xb7kO\x8e,H\x9d@\xc9\xba\r&fj@\xa6P\xb6\xa7\x02\x01\xb6\xf8\x17\xe3\xa9A\x9dS\x96\xf7}}\xf1z\x83\"\xa8:\t\xb9\xc1B\xa2Me+\xad\xe6=\x0b\xbc\x12H\xb7\xc3L\xbc\xb8\xf3 2'\xa2v/\x15b\xc5`\xb9\x01?\x81\xba\xbfF\x08\x90h\x81\xf8\x9b\x8cg`\xa4\xedMN8z\xf8\xe4y\xddE\xa4\x038+\x80\xab\x127\xa7W\x05\x04:\x1cT5\x08G,\x15\x17\xa6bR\xd0\xbaJP\xcb^\x83\x19\n\xbf\x01\x01r\xc8\xda|0\xeb4\xa1\xe9f\xa3\xc3\x04\"4{\x90\xe6\xe9\x0840\xa41'm\x16\xa7\xfbiy:\xdf\x9a\x04j\xb5/\xe9\xdb)\xeb\"\xfcSd\xe2'tgYLU\x9b\xe0Xr\xc2\xeaB\xff';\x82\xca\xef\xb1\xbd\xf3\xd3\xc2\x1fA\xbc]\x899\xa2\xe9\xa8\xaeU\xbb\x02\n\x7f\x9b/\xff\xe0\xeed\xb1\xc5A\xcda,\x16V\xfd\xde+\x0fa\xc73\x0fAzTG\x81\xcaM\xa9R\xf8\xba\xdf\xe6\xa1\xa4g\xebn\xb6\xe531\xe8\x93)_t\x12\\\xb2 \xfaf\xd3z\xdf.\x0fd\x9b\x8e\xb2\xe6;\x08\x90Sp(\x87\x86R0\xae\x97m\xa8\xc7l:\x16\x19S1\x9e\"\x03\xef\xcc\xb66\xf6\xfb\x95t\"\xbf\x0f\xec\xbf2J",
                                "video_metadata": None,
                            }
                        ],
                        "role": "model",
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="google_unknown_tool_id",
                            name="get_book_info",
                            result="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text='{"publication_year": 2006, "pages": 544, "title": "Mistborn: The Final Empire", "author": "Brandon Sanderson"}'
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
                                        "publication_year": 2006,
                                        "pages": 544,
                                        "title": "Mistborn: The Final Empire",
                                        "author": "Brandon Sanderson",
                                    },
                                    "name": "__mirascope_formatted_output_tool__",
                                    "partial_args": None,
                                    "will_continue": None,
                                },
                                "function_response": None,
                                "inline_data": None,
                                "text": None,
                                "thought": None,
                                "thought_signature": b"\n$\x01r\xc8\xda|z\xb7lk\xc2\x9c\x97\x7f\xc9\x96\xbc\x96_F2\xear\xa5M\xbaY\x00r \xf7>\xe4o\x8a\xb9`\n\x81\x01\x01r\xc8\xda|\xe2\xac\xf5\xde(\xe8\\w\xe5\xedM\x08\xa41\xef\xa3\xba\xa4F\xcdc\x1b\x95b,fT\x89P\x1d\xeb\x08{\x9a\xb1\xb3\xa3\xa2s'\xd3t\x99\xdd,tY\x1a\x1d\x1fN\x8d\x0b\xa3\x81\xd8\\\x9d\xa5=\x89\xa5\xa1\xbe\xad\x1d\xeb\xad\xee\x0bGi\xa5\xc0\xd89\xc5\x00\x0c\x95\x07\x8b\xe8\xffV\xf6\xb9P.2\xa6\x83\xebh\xc8\x9b\xd9E\t\x98\xa2\x8b\xab\xdd\x7f\xe2R\x0e<\xaf\x893,\xf0Y4\x0e\x85\xcd\x81\xd82>\x80\n\xbc\x01\x01r\xc8\xda|\x87\xea\x004\r\x8e\xa2\xd4\xfd3/\x19T/$?\xf5\xec\xc3}j\xf0\x89\x84g~\xea\xad\x9d\xd2\x0f6\t\xff+V\x1f \x85\x95\xf9\xa3\x8e\xaa\x0f\xc7\xee\x9f{qXO*\xbbY\xf8=\x13a\xf0\x04.\x04\xfb\xdc\xe5\xcc\x99\xd74\xb5*\xa6w\xe5\xa7>L\x81\x1c\xb2\xa7\xfe\x94\xe7\xc1\x17\x82\xbb\xa1\t\x96\x1f\xb0\n\x17\xb8?\xd3\x94g\xb8!\x7f\xb3\xe4\xd0\xda/\xd7\x9e\x07_\x8a0\xf2\xecM+1V\xa4h\xd4\xe1\x912L\xb1\x92\xa3\x83U\xc1u\x17\xb3\xb4\x1dW\x91\x8f\x99\xdcs\x99|\x80\xfb\xf1\xf1\xd1\x04\x99\x9b\xd3!\xd1h2+D\xd1m\xce6V\xb2\xd9\xb9\x07\x92\xd4\xb4\x13?v\xd0l3\xa4\xe7\xa2\n\xc5\x01\x01r\xc8\xda|\xf9Cr\x98\xbb\xb5\x91\xdb\x94$\xff^Ep~]]\xf6c\x13$\x14\xc84\x84\x187\x01\x1c\xd6\x88\xa7\x14\xf6)\xb2I\xc8\xd5\xdd\x0b\x18~=v\xa4\xb2\xe5\\d\xe1\xe5\xefM,\xa1\xcdJ\x94\x1d.Y\x07\xf7\x01\xfc\xed\xdc\xbb\x8d(\xc2\x00\xfd\x14\xf8\xaeHY\x08t\xaa\xe1g\xb6J~*\xac$\x90\xdaw\xa8Y\x91\xeeiC\xc4k;>&\xe0\x8a\xf2H\x19\xa5\xc5\xd0\xa1-7\xcb\xdbdpM\xd8\x9chS|\xc4N\x08o\xd6\xcaI\xd2\xb1\xa0\xc48O\x16\xb9_\xe9\xcdG7\xfdV~Xix\x16_\xc3\xac?V\x18\xb5\x87Am\xf6\x14t\x1bl\x86\xd6\xc2\xe6\x15\x8b\xce\x85\xecc\xb8\xd6\xe4[i;\x83\xe7\xce\x88,\xb1\xf9\xa4\x04\n\xb5\x01\x01r\xc8\xda|IC\x1a\x9e\x82\xf1xI\x15C%\xfc?\xe5\xe4\x01\xaf[{\xdd\xe40\x90\xb3q1\xb0\xecjK\x0c\xe1{\x1dA.\x14\x19\xac0k\x1eJ[\xc4_\xc8t\xd9\xf7L\xa8\xe6\x10;\xcbJ\x95?\x15\xaa\xaa\xfe\x03\x05\x8c\xb0\x17\xa8\xc3\xb6\x03\xdc3\x80\xa0\xcf\xba\x98\x8e8\x8c\xf8\x8d`\xb3\x06\x17\xc0\xe7\x11%\x98\xed\x92Y\xbf5G\xed\x87\xee\x92\xaa|\x8f\xfa%\x02\xa8\xd3\xc3\xabMi\x0f\xc9\x8d_\xe6\x02=\xe9\xe0S\xc4\xe8\xa1\x15\xbc\x07\x8a\xb3\x16\xf4H\x08T#jp\x04\xb4\x0c\xfa\xa3\xdb@\xc0\x97\xf0\xef:\x18\xa8\x13\xb9\xf8\xd8\x1c\xb6\xe7\xe1\x08\xb94o?g\xf4\x06o\x92\x9c\xbd\x0f\n\xcc\x01\x01r\xc8\xda|-\xb6\x1f=\xc8H\x19\x04j<E\xdb\xd6\xc0\xb9\xc1!g\x94;\x913RTMMj4\x1b)U\x80\x8a#\xad\x83\x19\xa6\xbbJ\xc4\xa7`-2\x18\xbb?\x18\"\rq<\x1d=\xff\x86k\x87\x86\x86\\oo\xc0\xae\xf5LN-\xb5W\x92\xe1*#\xbc(#\xf8\xc4@\x80\r\x15\x04\x05d*k\xfa\xc9\xe3\xb6^c\xf6\xdce\xfd\xfai\x17*aF\x97Az\x82rV\xf28\x81J\x8e+\x16\xd2\x95)\xf0\xbf\xa6\xb2\xc9\\h\xe8Y\x14Q\x91\x8f\xa9\x10\xe6*\xea\x14\xfd{,rh\x01\x81eC_6\xb0\x89\xe9e\xc6\xf35M\xcf8\xd7\x7f^F\xbbda0#\x1c\xb5\xc6\x0cu\x15|b\xa7\x83\xdb\xbc\x8aj\xbf\x9clF\x1b\xfd\xbb\xe6\xa8\xd3ly\xab-\n\x7f\x01r\xc8\xda|\xae\xba\xc5 a:k\x8d4)V\x84\x03]\xe3\xa8\xa9B\x08\xf9\x88\xc7!\xc0^=\x85\x0b\xfc\x11\x16\r\xbf\xa7\xd7\xac'\x9eE\xec>\xa4s\x80\x8dhH\x02S\x9a\xf5\x05Zb#\x8eq4\xf5\xd1\xad$\xe5\xa4\xcf\xeaz\xb0~\xe2\xd1\x0f\x17\xb3vc=j%\xadI\x0c\xc0i\x11\x8d\xdc\xcf\x88\xe3YL*\xa02.\x92?\x7f\x81Q#\xd9\x050T\"\\\xc1\x93\xe5\xaa\xdfK0\xfb]+Ci\xd1X",
                                "video_metadata": None,
                            }
                        ],
                        "role": "model",
                    },
                ),
            ],
            "format": {
                "name": "BookSummary",
                "description": None,
                "schema": {
                    "properties": {
                        "title": {"title": "Title", "type": "string"},
                        "author": {"title": "Author", "type": "string"},
                        "pages": {"title": "Pages", "type": "integer"},
                        "publication_year": {
                            "title": "Publication Year",
                            "type": "integer",
                        },
                    },
                    "required": ["title", "author", "pages", "publication_year"],
                    "title": "BookSummary",
                    "type": "object",
                },
                "mode": "tool",
                "formatting_instructions": "Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output.",
            },
            "tools": [
                {
                    "name": "get_book_info",
                    "description": "Look up book information by ISBN.",
                    "parameters": """\
{
  "properties": {
    "isbn": {
      "title": "Isbn",
      "type": "string"
    }
  },
  "required": [
    "isbn"
  ],
  "additionalProperties": false,
  "defs": null
}\
""",
                    "strict": None,
                }
            ],
            "usage": {
                "input_tokens": 434,
                "output_tokens": 49,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 241,
                "provider_tool_usage": None,
                "raw": "None",
                "total_tokens": 483,
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
                            text="Please look up the book with ISBN 0-7653-1178-X and provide detailed info and a recommendation score"
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        ToolCall(
                            id="google_unknown_tool_id",
                            name="get_book_info",
                            args='{"isbn": "0-7653-1178-X"}',
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
                                    "args": {"isbn": "0-7653-1178-X"},
                                    "name": "get_book_info",
                                    "partial_args": None,
                                    "will_continue": None,
                                },
                                "function_response": None,
                                "inline_data": None,
                                "text": None,
                                "thought": None,
                                "thought_signature": b'\n$\x01r\xc8\xda|\x9c\x13\x16w\xe9\x17\x1es\x0e\x9d\xb2CM\xa1\xed\xbe\xd3q\x0b^\xfb5l\x1c\x8d\x13\x90.\r\x86&\n|\x01r\xc8\xda|1\x92\xad\x0b\xa4\xe2PC\x8eI\x80}z\xb9\xaf\xab\x16\xa4\xba\xe7`7\xcb\x83\xc5\xe2Z\\\xf6V\xb0\xf8I\xfe\xfa\x0f\x91\xf05\x06\x89\xda\xcd\x93\x81h\xdby/\xaa\xd4"\x15\\)\x9f\xf4}@\x80\xa5$\x02\xecPI\x98\x0c\xa7c\x9f\xe1\xd5\xe4\x7fH\t\xcd\x19\x9fd\xc3\xe5\x13;YjUY\xae\xdf\xc2{?\xb6\x19\n\xb9H\xcc5\x90K\x04\xbe\xd3\xa1\xea\xe1\xd1\xb6\xb6F\x18\xcf\x80w\x9e,\n\xd2\x01\x01r\xc8\xda|\x81\xb2\\(\xdb\x8a\x9bigH\xc6\xcc\x0b\x04\x8dw7\xcf@\xdb3\x08\xfe\xe7K\xaa\xfd\x10-n\xbc\xd6\xbe\xbe\xbd\x1f&6=/\xa4W\x83\x03.V\xfc\xe5Q[\x94\r)"\xf3\x10\xb0\x08\xd4\xa6w\xa7\x83%\x15\xc9v\xcc\xef\x062\xc9\xe3\xb2J\xdfl\xbar\xb1o\xc0\x89\x01\xdd\x9b\xf9kP\xa7\xd3b\x95\x96\x9bq;n\x19-i&\xf5/gG\x8f\xc4\xb7\xf3U\xd0nae[\x0e\xf6\n\xfe\xc1\x9c+T\x12}6\x08\x94\xd5\xa5\x0bNy\xac$\xe4\xc6+\x93>)\x0f\x97\xfe~\xb7\xf7\xaf\xa1\xb0\x86"\xd5(\xce\x85\x84\x7f\xa1\n\\\xd7\xd56\x1d\xa8\xff\xe2\x11\x01\xc9wLP\xe3\xf1C\r\x8dz\x97w\xfa(m\xa7\x8b\rF\x7f\xa1g\x12\x8d Y\xc3\xa3w\xc3\xc5\x1b\xef\xce\n\x86\x02\x01r\xc8\xda|NZIi\xf3\xc3\x0cZ\xda2\x86\x85\xb78\xb4\xd7}\xf86(\x99f\x9c\x1a|-[\x9a-\x12\xc5W\x7f\xb5\x8b\xd57\xffs\x8e\xf3\no\x8cB\xea)0k\x8bD\xae\xd0\x96\xe6\t\x89\xc0\xa6\xfc\x92cT\xa4N\x1c\x86\x8e\x90Xl4xgy\x19t5PuW\xd9K)q\\\x19\x97\xa9;\xb3\r7[\xf8&\xe1\xad\xb0\x1b\x8e;\xb9~\x88\xb5\xd2\xe8Mgb\xe4\x16q\x08\xd1\xdayb\x85\xe3\xea\x04R\xe6k\xfcR\xafK\xf9\xa6\xf2\x17\x93EZ\xf9\xa6]n\x90-M`C\x81\x90$\rM\xa36{\xe7\x9c!h\x12\x1b\xa4\x0f\x80M\xe9\xf6\xb3\x93:\xf9\x1e\xc5\x90n\xa1\xd0\xa8K,\x0e\x8e\xe9\x15\xe7\xd5\x0c\xd6=\xc3Q\xf8\x92\x9c@\xf5*\xa4\xc6\xb3\x8a6\x89\x87\x1d\xba;\n\xb1\xa0\xfa\x1e\x05\xce\x98\xe2\xd7H-\xd0\x08\xbb\xff\xc0\xcd\xdd\x08\x98[\xc8\x89\x03\xad\x1a]\xe5\x15\xfc\x17@\xab\'o>A\t\xb4\x81\xf5K\x9b\xcf\x7f\x1c\x94\xb6\xf7$\n\x83\x02\x01r\xc8\xda|A\xd7\xff\xe9\x97\t\rc\xae=N\xad\xc5\x80R\xc7\xe1\xa7\xbd\x96\nz\x9c\re\xe8<\x0c"R\x15\x18\xd0 \t]\x112\x03\x0b\xf47#\xa5Q\xe1\x11\xb8K\xe7\xf2A\x04\x17](\x90A\x85\xc3&\x98\xe5R\xc8\xf57F\xf9\xe4 2|\xdb\xcb\xa7\xbfD~H\xbb\x84\x80\xf7\x8e\xd0DK\xb1L\xad\xd1\xfa\xa8\x99E\xfc\xcf\x0f\xf4\xa0O\xe2\x92\x8b\xcd\x8fP9\xb8\x9d\xfbq\xef/j\xb8@\x18r\x1bq\x1bB+\xb0\x14\x88]\xbc\xfaK\xdd\xa8>\xf2W";\xa5\x1a\x93X\xa3bz\xd0\xeaXS\xf0Y\xabR{\xe7\x82\x84\xc5,t%\xc6@\xaa\xb8%\xba\x03\xdc\xa3\x16\xf5\xfd\'|W\x04doaus\x8b\x1d\x08h\xbd$\x0c\xb2kj\xday\xaf\x01\x9e\x96=\xee\xd1\xb14w\x8b`\x94%:\xc0\xa0\x8c\xfb\xdc\x9dak\x8fq\xc9\xb97\x02\xe8\r\x96\xf0\xd1)\x8bC\xfa1\x04\xfa\xfe\xc8;U\x87fu1\xa0\x97\x7f0\xb7s\x96\xb3\x8b\r\n/\x01r\xc8\xda|\x88\xd5\xe0\x9f[\x89\xaf8\xa7\xfa\x8e\xb7M \xe8\x13\x13\x10\x82\xf1\xdc\xeb\xc9\x97\x9a\xff\xe1\xbb]\xb1\xcc\xe0a\x80#[\xa2+\x9bW\x0b\xef',
                                "video_metadata": None,
                            }
                        ],
                        "role": "model",
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="google_unknown_tool_id",
                            name="get_book_info",
                            result="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text='{"title": "Mistborn: The Final Empire", "publication_year": 2006, "author": "Brandon Sanderson", "pages": 544}'
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
                                        "title": "Mistborn: The Final Empire",
                                        "publication_year": 2006,
                                        "author": "Brandon Sanderson",
                                        "pages": 544,
                                    },
                                    "name": "__mirascope_formatted_output_tool__",
                                    "partial_args": None,
                                    "will_continue": None,
                                },
                                "function_response": None,
                                "inline_data": None,
                                "text": None,
                                "thought": None,
                                "thought_signature": b"\n$\x01r\xc8\xda|\xe9\x18\x13a;2s\xe4\xee[\xd0\x84\xe3@p:a\x8f\xb48d\xb0\x88\xb2\x85$\xab\x90ld\xf3\nu\x01r\xc8\xda|\xa0\x9f\xcc\xb8\xb9\x93\xab\xd7\xd0\xdb\x89Pw\x1b\x96\xf5\x84t\xb1\xde\x9b\x07(\xd9\xd3\xb4\xa5\x9c\x92\xf5@\x96\x9d\xe2\x10\x12\x13\xd3u\xfd\xef\xd98\x05=i\x13\xcep\xd6\xd7\x85,\xfa\xd6\x13q\xf3\xfdf\x0241\xee\x9d\xe6\x9d\x1ct\x05t\x1e\xbd!\xae\xfdP\x9ePGNh`\xb8\xb8=\"\x19X\xb0\xec\xbe\xee\x7f\xbb\xf5\xb9C7\xdc\xe4\x8d\xef\xae\xa7h\xafgV\xb8\xcft\n\xc7\x01\x01r\xc8\xda|\xc9'\x8a\x93M\xff?\xff\r\xc8A\x87>\xbe\xac\x9a&;\xfc)\x8f \xd5\xc2\x96\x08\xdb\xad\x8fn\xa6\xd7t\x84M\x8aq\xdb$\x94o\xc0\xaa\xb4\xc5\xab\xb9\x14\xa1fH!{%\xd5\x7f\xb0PT\xf6U\xdfj\x02\xdbId(G\xdbP\xb7@\xdd\x8e\xc2&\x96\x9b\x17H\x84\xec\x99\x95N\xc7\xbeX\xed\x82,\xa1\x90u\xd5[\x90]\x12P\xfa\xaa\x9cr\xcd^\xb4\x95\x8e\x9e\x13%q{])\xc3[R\xf5\xeao\xaa\x17\xbe\xbd\x9f\xb1\xea\xa1\xe9|D\x19\x15\x94f\xae4\xf5CKO'\x9bP\xe7E\x80\xdb\xc8\x018\xe9\xa9YR\xcf\xcd\x0c\xbah\xa8/\xb6\xaf\xe7\xb90$\x97\xa3\xe0\xb1A\xa3\xa2\x04\x90<Q\x1c\xb8\xb4\x9a\x181\xeb\xb2\xf6\x93\xce\xa6\n\xf8\x01\x01r\xc8\xda|W\x12\x19bJ\xa7\xd7\xec8\x1d\xc3\xfa\xcf\x17_\x13'\xc2JC\t\x03\x0c\xda\x19\xdc\x0e\xd4V\xf3\xa9\xaf\x7f\xa9\xa3\x88\xdaH\xban\xed$i\x1dm\xfc\x98\x94$v\xc5*`\xec\xafAN\x01\xfc\xa6\x83\xbc\xe6\xf8\x7fi\x9cVm\xf7\xc9\xe34z\xf9M\x1a\xc0)L\"\x98.\x8c\xec\xf3\x8fW\x97#\xb5\xc6\x15\x80t\xa3\xcd\xa8\xa2\x065\xb6{YZ\xd5\x01\xb7\x1d9\xd9\x99\xcc\xb4^E\xf9\xca+\xf2\xbf\xec\xf8 \xae\x8d\xf7R\x9d\xceN\xa2&;\x9e\xfd\x0b!\xd1\xee\xa2\x85\xd3\xa6\x8d\xf6\x99\xc9\x83]\x9c\x03~\xa1.\xa3\xd1\xab\xba\x98\x8c\xec\xf9\xbc\x80][\xadA\xe1\xab\\F\x9a\xbd\xd0\xc3\xf83\xceS\r8\x865\x0bsI\xd3}\x8b}\xc4\xed\x04\x19\x84\x13\x84#'\xddS/\xdb\xa6\x98\x94\xf2\xd1\x9d@\xe7\x82}h\x8b_}`\xa7n\xf3R\xe3\xed\x82\xd0=xaO@$\xa2p8k\xa9rw\xd6#\n\xd9\x01\x01r\xc8\xda|>\xb4\x04\nM\x19\x9f\xbd\x12\x9f\xb6\xcd\xc9E\x80*X\x1e\xb0Q?{\xa7\x19\xbd\x9d\\Dl\xd3\x04u\xbe\x86\xad2D\x8fd\xe8\xf2NU\xb7eb+\xbb\x15\x1dk8m\x19\xc3\x88Z\x96\x07U\x99\xa3\x89\"\xec\xa36Q}\x08L\"6\xd2\xa2Z\x8f\x86\xd2\xfff#P\xa3}\xe7RV\xeb\xa2\x18\x07A\xd5\xc6y\x0e\xa6\xd5\xee<\xf2!6^\xc8QA\xc7-\xa4\xad\xf5\xb4\xcd\xb0m\n\xb2H\xb2\xc2\x0b\xce\xd4\xdb\x8bF2\xcfd^d\xe5a\x9b\xee\xe6\x01\xe0\x03\x8f3\t\xae\xe8`\x19\xd2c\x15AFe\xc4\xe6\x15\xa1\x9f\x97@j\x14\x9b#\xdc\\\xc4{F\xe3\xd7\x10Ic\x7f\x9a\xf8e\x97U\xc9\xf6{nH=\xb0\xa5\x1d\xc3\x18.\xbam2\xe6\x89PD\xd3\xf5+\xb3\xc69i\xc8\x0c\xf1\xb2\xdb\n\xb4\x01\x01r\xc8\xda|U\x91\xec\xb9\xd4\xc0\x95((\x9e'\x16\xa1r\x9c\x04i\x06E\x9c\xca\xd5\x8b\xe7\xb6\xaa\xcd8\x1f/\x19|\xc5\xb1y.l2\xf1\x8b5\xc5[\x1a1\xfa\xf8u\xe5sv\xfa\xf3\x99\x07H\x94,:\xb5c\xfa\xc9P\x92\xa3\xe0\xd4\x93\x12!Th\x8c~;\xe2\x84\x8d.\x83C:6\xe0\x98\x98Y1\x7f\xa3\xb0e=\xfe=\x027/w\xcd\xab\x95\x85\xf3\xcb3\xa7\x85LI\xc7\xd13l{Q\t\x8c\x8e-/\x8c:Iy\x8aCv\x03\x9b\x1f/\xdc1\xba=\xc2\x0c\xbf\xcaH\xc0\xef\xaf\xc15\x908\xff\xea'\x82l1\xee\xd3\xc0\x03\x86\x00+o\xeb\xee\x05\xfc\x961\xf7\xb6Kf\x04\xe5\n\xad\x01\x01r\xc8\xda|\xa1w\xfd\x06\xa0yF\x07\xb1\x0f\xdfp\xd5\x8c\x1c+4\x90\xba\x1e/I\xfei]\xa7~o\xf1\x83C(e\xe6:\xaf\xc0\xa0-\xdfK\xcfhO\xac\x83\xf7\xf6?'y\x98\xfa\xde\xb0*g,%?H\xacj\xb2a\x0b\xfc\x0f\xc7\xde\xb5\xe6!\xe7F)\xfc\x81\x98\xdbn>\xd4]\xaf\x83\x8f\xf79\x83\xbdN{\xd3w`\xe7\xdf`\xbb\xd5>\x15\x17R\xfbK\x0bg\xd4\xa7\xa79\x05,\xa0 \x10\xb3LO(\xc3\x95\x9b\xc6*\xc1\x9f\xf0+\xba\x90\xdez\x85Twl=&\x8e(\x9a\"\x91\xe0\xc1\xa0z\x06\xe3|pbT~[\x19<)Ujm\xab\xb3\xcfr\n\xb2\x01\x01r\xc8\xda|\x97\xbc\xe8<\xad\x07\x96\x07\xbdk\xce\xcb\xd3\xbce@N\xc0'\x98\xfb'\x13\xc5\x89L\x13\x12\x92\xe8]\x04\xfaNd\x150\x80\xb4\xe6\x02\xdam@&\x10\x08\xeb\x08\xe5i,A\xc9\x7fe\x11<G\xdc\x9c\x82\xba\xee\xdaF\xf6\xd9F<v\x8a\xf0\x13G\x0c\xb7wE\xda)\xe5\xb7\x03\xd1\xbc6\t\xd2\x8c\x06\x87\xfe\xe2\x9e5\x9by*L\x01\xb9kn\xc0\x98\xa1AT\xe1\xfd+\x97\x19\x0f\xd7\x0fI\xcc\x0e\x0b\x1d\xbevx-R\n\xa3\x86i\xda]\xf21QW\x0cA^\x94\xee\x1c6\xef\x15\xc3(2\xd6X>\xab\xa8\xfeh\x08r\x8dT;\x85\x10\xd3\xc1\x1b\xeb\xfam\xea\xc8CX",
                                "video_metadata": None,
                            }
                        ],
                        "role": "model",
                    },
                ),
            ],
            "format": {
                "name": "BookSummary",
                "description": None,
                "schema": {
                    "properties": {
                        "title": {"title": "Title", "type": "string"},
                        "author": {"title": "Author", "type": "string"},
                        "pages": {"title": "Pages", "type": "integer"},
                        "publication_year": {
                            "title": "Publication Year",
                            "type": "integer",
                        },
                    },
                    "required": ["title", "author", "pages", "publication_year"],
                    "title": "BookSummary",
                    "type": "object",
                },
                "mode": "tool",
                "formatting_instructions": "Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output.",
            },
            "tools": [
                {
                    "name": "get_book_info",
                    "description": "Look up book information by ISBN.",
                    "parameters": """\
{
  "properties": {
    "isbn": {
      "title": "Isbn",
      "type": "string"
    }
  },
  "required": [
    "isbn"
  ],
  "additionalProperties": false,
  "defs": null
}\
""",
                    "strict": None,
                }
            ],
            "usage": {
                "input_tokens": 451,
                "output_tokens": 49,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 300,
                "provider_tool_usage": None,
                "raw": "None",
                "total_tokens": 500,
            },
            "n_chunks": 3,
        }
    }
)
