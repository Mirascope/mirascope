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
                provider="google",
                model_id="gemini-2.5-flash",
                raw_content=[
                    {
                        "video_metadata": None,
                        "thought": None,
                        "inline_data": None,
                        "file_data": None,
                        "thought_signature": b"\n\xb9\x08\x01\xd1\xed\x8ao!t\x01>\xfa\xc2\xa5\xd6\xd7\x07\xe6\xe3F\x1b\xa3\xca;\xa7\xdbR\xa1\xde\x11*\xa49\xb9\x12zo%\x1dc\xeen\x86\xf5\xf1`\xe7\x1d\x02)\\\x03|\x01\x88\xe8\xe6\xfc \x15%#\xd6\x7fJ\xcagy\xd9\x07\xc3\x83\xe2r\\\xf7\xbe\x9b\xe7OT\xcc \xb7\xfd\xfeBY\x15\xa0\x98\xc5\xff\xcd\xc5:\xfcM\x8e3\x9c\xa5\xd1B\x05\x97\xc6#<|@E\xfc\xe50\xd6\x01\x95!\xb87T\xffv\xa8\xc7\xc2\xe5Z\xed\x1d~3\xa9\x8f\xcb\xb4\x9a-\xa1\xe5\xec:\xbfa'\xcf/4\xb23s\x17\xe7\xef\xa1\x7f\xda1\xb7\xf0\r6\x1alJ\xe4\x9a\x8a`55\x07\xcf@\x85^P\xa7q)m\xe4\xc4\x96\"G\xe0\xac3\x97*\xda\x95\r\x0e\xdb1Ey\x14\x1cH\x8c\x12v\x96\xcfcuL.s\xcc1\xfd=\xe6\x0eh\xbdk\xf7\xa7\xf9r\x0c\xfe\x1bBXh\xf7\"e4\xbfc\x7f\xebVQ\x17p\xfaOV1Nw\xc9\x86\xe3\xccG\xcb\xa3k\x01\x9cJ\x8f\x8a@\xf1\x0bV\xebZ\xa6\xe7\rB\xfc\xa8|E\xef3\xe7\xfc\xd1\xac\xb1\xecHp\xd8B\xc0.7\xddJB\n\xb1\x81\x88W\xea\xc8\x8b\xf1'\x82\x08\xbc>\x8b\xb1\xfc\xd3d\x1b\x13>\xf3\xf7\xff\x10,\x88\xd6\\(\x1c\xc4\x88\xf7|XS\xa91\xe3\x0e\xcb\xdcJp\x13%\xf3\xbe3\xb1K1>\x85\xad\xf0\x93\xc9k\x7f|\xcb\xcc\xd1\xb7\x943\xcd\xf9\x13\xb9\xd0_\x85u\xda\x1d\xc1\x1f\x1dGv\xa1\x0et\xb3\x84q#\xc7\x81\xcdY\xa4ml\x10`6\x0es\x1b\xec\xd0\xc9\x82\xe4\xc9\"\r0\xdd.^{\x82\xb3\x03p4%\xffL-\"\xbe\xb2\x089` \xb8\xb9?\xc1\xa4aR\xb7\xe7o\x92\\zB\xfd\x02\xd5\xea\x16\x7f\x8d\x1e\xe8\xedJ\xa3Jr\x8c4\xa2/6`\x06\xafc\xe6\xc7\xaa\xec\xf11\xf2\xfe\xbazix3\xe3tk\x0e/\x181]\xdcV\xa5\xa5\xdf\xd7\n\x14\xbbt9\x11\x16\x1b<\xe5X\x1f]\xb1\xd7\xe5\xe69\xa0\xc9\x92\x10'\xa6\x0e1\xe3?\xaf\x96\x856\xa4e\xf8\x1d\xb3\xa9\xdb.0\xbb\xbe\xdcmH\xa9\x99\xe3\xcbN\x1a\x1b\x07\xc9U\x93f\x16^v\x92\xee\xed\t\x9f\x9d_\x0e\r\x1f'\xb0\xf1Y;c\xc7p\xe0<\xbb\x01\xea\x0b\xa1\n\xadAk\x10\xa7/A\xff\x86\xb1#<\xc5\xdbz,q\xe1\x86\xf2f\x0b#U\xe7\xaf\xce\xefS\xcd\x85g\x97\xbehd~\xf4\xda\xe9\xf0XvK\x07\x9b\x8f\x98i\x9d\xfc\xff\\\xb1\x8b\xbex\tZ\xc3\xa0\x07\xa4E\xae}\xd8\xcea\xb9?Z\xf5N\x9a'd/\xf1\x0c\xf9\xca\x8b\x02\xa4\xaai\xe9\x9cP\x0eJ\xecZ,l\xc6\xf6\x0b\x96\xd5K\x92u\xb1\xdf\xa7(\xe7\x1du\\H\xaa\x8e\x11\x8a\xfb\xa1\xa6\x8fP\x87?\xd6\xf4\x86\xb63\xd1\xfccHu\x89v\xfd\xed\xc8,\xad<M\r\xee\xc6.N\xf8\xd8uH\xe2\xb4h\xa0\xd7F};^\x1fcUm\xc9~\x1f\x8d\x1b\xea\xd6C\x05\xc7WK\x12\x8c_\xb2\xae\xf3$)dP\x91\x08K\x85W\xf5\x9a\x16c-\x08\xecG\x13o\xd3A\x1a\xe9\xec\xb8\x9c/\xc3.v~\x92w\xae\xba\x0e- \x05\xb3\xeeh#\xceW\xef$\x05\xb3\x9fx\xc7\xd9\xd9\xda\xe7E\xe7,6\x1b\xe3\x8e\xca\xd3C]4\xcd\xc0\x98\xd5\xbe\\\xa2,\xb5\x1e<\xaa\xd6\xb4\xd8\xf5\xaet7\rqO&2\xac\xa3\xbd.&m\x94j\x7f*i\xf7\xb5\x17J\x88tp\xec\xdb$680;\xa4}\xed\xf9\xd9\xbc\xdbXi\x07\x88\x8b_\xc8=\xecXW\xb0\xc7\xc0\xa0\x0c\x85\xcbX%jq.\x13\t\x7f\x1f\xfd\xc4\xf2\xf3\xf7Y;\x0b\xd59\xf8\xf3DEY\x9d\xfc\x93I^\r\xe5\x80\x94\xa5P\xcc\x97y\x86\xbdG\xb8\x9c\xb9\xbeR\x18\x03\x06X\x8d\x0f\xfd\xbd\x9b\x05M\xf4\xcb\xc0%`\xc0\xba\x7f\xd0\x99\x88^\x89\xc5r\x82\x0c\xf7\xf5\xbb\x91\xf8\xd9N\x1dE+\x838 \xc8\x0f|\xbd+\xfd\xeb\x0c`\x9b\x869\xd1d\x02)\xfb\x80H\xde\xc0qZ]\xe1\x82\xea\x80\xed\xce\xda\x02`\xe6~\xf3\x0f\xb6\xa2\xf6`2\xf7\x10v#9\x15\x03\x8dK\x7f\x9d\x8a-nG\x0f?\xac\xcf\xe14\xcc\x0bP[\x0f</ :\x1c\xaepM\xe9\xa2x\xb3\x13T\x10,\xbd\xd4\x86\x97Y\xfcI9",
                        "code_execution_result": None,
                        "executable_code": None,
                        "function_call": {
                            "id": None,
                            "args": {"isbn": "0-7653-1178-X"},
                            "name": "get_book_info",
                        },
                        "function_response": None,
                        "text": None,
                    }
                ],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="google_unknown_tool_id",
                        name="get_book_info",
                        value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text='{"title": "Mistborn: The Final Empire", "author": "Brandon Sanderson", "pages": 544, "publication_year": 2006}'
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
                        "thought_signature": b"\n\xde\x06\x01\xd1\xed\x8aoh\xb5\x88\\\xaeW\xd7m\x0e\xba\xf1\xac\xbc\xc7\n\xd6[iza9\xb4\x1f\xeb\r\x9e\xc6c@k\xa8\xc4\x9a+H\xe6\x96\xd6^^\x93\x02h\xb9O\x9f\xd4;f\x92\x8e=\xe5\xed'\x071\xf1\xa2\\\x96\xd4\x9e\xd8\xe6\x8e\x83\xf2%&\xcb:H\x0e\xc4\xafr\xdc\x04p[\xfd\x08wMv\xc1\x02\xb7\xc0\xfcC+\x9e\x85\xc8\xc3\x1ep\xaf\x8b|\xfb\r\xf7\xf3\xda\xa1\rl#z{T\xd0R\xf9\x01e\x88y\\e\x8f\xa3\xcd\xe5\xe1\x82\xe8F\x99\xa7rd: q\xfb\x07\xa8\x19w\xdf\x95\xef\x82\xf2\x86\xb6`\x18\xde\x99\x8a;\x86\xda\xbb\x93)\x82\xb25d\xb11sSJ-\x0e\xa2lJ\x12\xa02\x05`\x9azA\xd85\xbcO qoz\xb7\x8a)\n9\xae\x9b\xefZsp\xd4n\xf7\x8d\x85(7Dn\x7f\xfe\x81\xdb<\xcd7\xca\x8d\xeay\x91\x92M\xde\x01\xed[l\xd0\x9c\x1er^.A\x1e\x97\xc5\xb2d\x8d\xfe^V\xa0\x8d\x97\x12\x1bZc\xa6\x026N&\xf6\x91,\x9cw\x08\x83T\xc3\x90\x8d\x13\x92\x01\x02\xbf\xc1\xdb\xf7sX4m\xcf\xf3:\xc8\xf2\x92\xd6,\xc0\x0c\x89\xef\xb2C\x9f\xaf\xbf\xe7@\xab^\x17\xee@\xea;\xfb\x0b&\xab\x9b9\x14\xae\x97\x84L\xdc&\xf3\xb9\xa2)8\xd5\"`\xbc\x02l\x88\xd3\xe3\xd5\xea4\xd3\x93\xba\x0cui\x14\x87\xac\xcb\xcbc\"+\x9e@\xf9yG\xb7\x0f\xda\r\x1d#\x0c\x10r\xf5AS\x94x\xc8\x98,\xde\xf4\xfd\x8a\x02&;\xd5\xbf\x96\xc6\x9e,\x94\t\xbc\xce\xb0_\xc5\x8a\xc3\xe6\xa3;{#\x8etc\x01\x8f\x1f\x02\xcac\x1aZ\xfc-GG'\x0f\x7f\x05\x1f\xa1\xbfv\x8b\x9a\x96{\xcf\xd2\x1ar\xed/\x16/c\x85P\xa1\xeb\xfc\x1c\xfaq\x9e\xd8\xa1\x87\xbaL\xaf\x9b\xeb\xcb\xb8\xe5\x82\xbeC\xcb\xfc(\x01\xc2,\x8d\xb6\xb4jh\xbf\xbf\xcf\x8fW\xfb\xb2\xa3\x83\xa3\x15\xe1E\xf0\x17o\x1d\xc8\xc9\xa3\x06\xd4\xe4\xdbv\x93\xd9\x81,\xcd\xb6c=\x96\xd3\xd6>V\xa7\xb0e:\x96\xb5\x87\xcfr\xd0\x0c\xfb\xe7\x9cn1I@\xc4\x9d[\xd1\x1dX\x80\xf6\x17/\xbb\x9b\xa8f\t\xbb\xd5\x15\xb2\x18\xe6Rv\xb0\xbc\x7f\xf4\xb1\xaf\xfd\xf9p3SM\x10\xdd_\xa2\x7f,+<K\x83Di\x87v\x17'H\x894\xa7'\x90>r\x96\xe5\x1c\xc5\x92\xdab\xca\x9d\xf3\x1d\xb2\n\xd1\xa7k\xda$\xbd,\xcb\xb2N\x19\xa8h\x7ftp?\x15i\x9bZ\x94\x82OO\x004\xc3O\xe1,\xfb8\xf7\xa5\x9d#\x87\xadm\xf4\x9d3\xc2\n?\xc8\xe3\xd0I\xe2lb\x1f\x9b\xd5#<\x8d\xc8\xad\xee\r\xec\xe4\xf1ZX\xfc\xd5n\xcf\x89r\xa0W\xe3\xcc\xed\x8d\xf7d\xf1\xe2\xe9_\xfe\x80`\xf8&\xc2\x1e%\x9f\x18l\x92\xf9\x94\x8dX`\xdb\x14\n\x8f\x82P\xdf\x99\xe1\x13y\x1c\xd2\xe1\x98|k|8\xb4\xaa\xbd\xea\xc3\x91#D\xda\xee\xa2*\"\xab\xf2aQ\x95\x92\xc1@\"\xb3ki\xfb\xa0\xbdr(s\x918\xf8^\xd3\x1aBak\xd1\xac>\xfd\xa9\x8a\xed\xb5\xd7\xd73?\xb2\x1aD+\x07\x8b\xc0\x83`\xa5\x86\x80\xcb\x17W\xd9\x04-\xd5/\x1a\x9c\xec\xf8m\x96\xa6\x9f\xb0\xf0\xf9@Zn\xa8Vb|D\t\xd1\xc0\x14uA+\x15\xee\x85fs\r\xcc\xff\xe9\x88\xbe\x9e\xd3\xf5~\x01'\x0c\xdfU\x0c\x1c@\x00\xee9\x0e\xdf\x9d\x19(Q?x\xca\xfc\x00\xd6\xac",
                        "code_execution_result": None,
                        "executable_code": None,
                        "function_call": {
                            "id": None,
                            "args": {
                                "title": "Mistborn: The Final Empire",
                                "author": "Brandon Sanderson",
                                "pages": 544,
                                "publication_year": 2006,
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
                "strict": False,
            }
        ],
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
                provider="google",
                model_id="gemini-2.5-flash",
                raw_content=[
                    {
                        "video_metadata": None,
                        "thought": None,
                        "inline_data": None,
                        "file_data": None,
                        "thought_signature": b"\n\x8b\t\x01\xd1\xed\x8aof\xfc)+\x9d\x90=\xf9\xc29\x00\xd5]\x1c\x9a\xe6\xf00>\xb7\xe4\x90;\x8f\xd5P\xc0A\x96\x89]x\xf3+W\xfan\xa1\xe7\x1f\xf2j\x0ehYc\xa1\xac\xc7b\xb0\xc1\xa9ak.\xb9m\x99\\\xe8\x9fe\xd8\xd7\xd0\x8aA\xb8\xfe3\x03\xbb^\xe6\xb7$\xa8\x0e\x01\x1a\xf5Y,\x8c\xcd\t\x06\xe8Sy\x16\xcdEG\xbdV\t\x97\xba\xc9Bj\x19\xf5\x95\x1bu\x1f\xca\x85\xb6\xa7O-=\xd80\xb2T\xe9\xe2\xbb\x87\x89\xa5\xc2\x90AG\x93\x05\xc5\xfb\xc6X\xddy\xa3\xb5\x9f\x8d\xd9}\x1e?\xf0(j\xa5\xf3\x8b\xc7\nW\xe2\x02T\x8e\x82\xe4\xad\xb0\xc7\xaf\x95\x1f\xdd\xa4\xbem-X\xb2\x8f\xfe2:\xe301\x06\xd8\x97\xd2*\x8d\x90r\x08\xf0\x17\xf1\xba\xfdo\xd8\x07A\xcc3v\x00\x88\xfcGq;/\x03\x07#\x1e\xf7F\xdc\x9a\x9b\\'$\"6\xd9`\x0bQ\xa8\r\x94\xd7\xa3\x94\xa0\x061f48v'\xa5Qa\xe9\x92'<\xbf\x89s\x18ke\x8ah\xed\xb4\x14\xce\xeck\x98\xd0\x98\x86+\xdb\xa6\xfa(!\xcc1\x96\xd4EZ\x08bK\x9e~\x8b\x15m/a\xca\xd0\xfb\xe0\xbf\x82\xfe\x0bKJ\xa4\xde\x1fz\xcc\xa9\x7f\xab+w\xb1C^1u\x8e\x04_\x9f\xfb\xf4#\xa4IWJ\x7ft\x92\x01*\x946)\x1bb\xf2k\x9c\xf61\xf9\x1d\xec\xe3QK5\n\xb5\x19G3\xdc\xdfT{C\xf1\xf6&\xd7\x1fN\xaf\xf55\xb6OV|G \x7f\xfe^\x00\xf9\xff*\xc3\xbf\xe0\xa3I\x14\x0e\xa8\xee\xfc\xe0\x02KV\xa3\xdf\x14J\xdb C\xa0\xef#\xae\x8fy\xfa\t|\xcdE\n`02\xab\xa8|\xd0\x99\xae\x99\x82\x1e\xcdT,;\x82\x93\xf8\xfd*\xf4\xe3\xba\x1e\xea9\x1f\xe4\xc0\xbd\xb9\x87\xf0K\xda\xc0\xc5\x1bNM\xad\x7f\x87\x9d\xa9J\x85\x19\x9d|B\xc9$\x97!q}\xeb\x1d\xcb\x93!\xfb\xc3\xa1_7\x8f\xe3\x93\xfd\xa2Ff\xde\x94Z\xec\x92%\xf8J\nS\xf0C\xdd\xe4\x0fP\xf9v\xcb\xb2\x9cW\xc2\x9dh,\x94\xfej<\xfdp\x1d\x1b\xb4=\x8e\xa1`V\\.\xd5\x0bq\x14KVs\xc74\xccRG-\x9e\xc7T\x8f\x95*\xd7H\x0c\xe8W\x98F\xcbL\xe7t?\xf8\x07\rW\t>\x83\xebe\x17~+r\xb8\x96]\xce2\x93\xbcoF~\x91I\xf8\xb2b\x18$w$4\xa2\xe0\xf6r%\xb3\xe6q\xd2Q1\xefiUV\xb3Xm\xc0_\rmS\x08)\xf1\xd3q\xbf\x1c\xb7\xfd\x0f6\xfa\xe8\xdb>}_\x8d\xd1#X\x9b\xee\xbb\xe9\"V\x7f\x0b\x02\xc3\xf2\xdcqkf\xb9\x1eN\xf1fw9\x10\x14*\x07\x1b\x0c\xd6\x0cq\x16|\x95\xd7\x911\xab\xff\xed\xdb\xeaa\x98\x05j\x8a{\x89\xfda\xd2\xff\xe4\xbe>\xfc\xc9%\xb2\x10\xbb\x90\xee(\xad\x9f-\xaa\x00\xf6\x92\xea\x8bY\xa4\xd5\xb5\xfd~\x84F\xde3\xb7\xe6\xff\xdcq\x0f\xbeL\xa99\x94\xd4\x83\x0b\xce\xd5\xac\xffK7\xbeW\x04l\x13;\xc2\x8bm\xd5\x16\x16G\x0b` L\xde/\x99\x10\xaf\x95\xf8TE%\xcf\xdd\xb1uf\xb2$\x0eA\xa1.\xb6\xb3\x00\xbeX\x8ag~\x14^\xb8\xdc\xec2\xc7[\x1c\xe6\xd7\x8c\x93MN \xacn\xa2\x18aic\x99okB\x1e\x0c\xb8\x11\x8d\xd6%\xbeq\x10\x15\xcc\x8e\x1bS\x0e\xbb\xa7NES\x12M\xad\xadzI\xd0\xc0\xbe\xa4\xf8G\"\\\xb2\xbe\x81j\xed\xf0\xbf\xcb\n`\xc8\xfb5m\xb8|\xee\xc3G\xca\x8c\xce\xee\x16#\xceo\x8e\x019\xf9\x88[\x15|\xfev\xe2\xbd1\xe0\x1a\x02\x90P\xb8\xc3r^U\x1c\xc3i\xe4V^\xc2\xca\x04~\xca\xf1\xff\x0b\t|\x0cO\xc8\xf4\x8d\xb7\xb5\x84\xcc\x85H\xb6\x9e\x19\xa0\x89\x15\x12[\x05d\xa4\xce\xf3o\x03\x19G[M%\xb0i\xec\xffw\xcb\xffN\xc5\x07\xb00\x1db\x0f5\xfaHz$\xf5e\x8d\xc0O\x80i\xf3\xb0\xa9/\x1d\x9b\xcc\xb2t\xa9\xa0\xe0We\x8a\xa1\xfb\xad~\x8dA\xf4\x1c\x89i\x9d\x8c~\xe3\xc0\x987x\xe6\x05\xaa\xb1+\x01z\xfa\x8e\x15(\xbb\xe8Lw\xf5\xf6\xb9\xb1\xdf\x050\x93>i\x1e\xa6X\xa5O\xff\xa1\xddK\xa8\xb3\xa1\xb5D\x89+5\x08\x8e\x89\xbd\x99\xb3G\xb8 U\x1d|\xe5xT\xf3I\x14\x04\x91\xb0\xef*\xc5\xb7\x07\xa0>\xd2\xa1R&\x9d\xd6V\xe5\x1f\xdb\xe7v2\xdf\xce\x16]\xba89\xba\x15\xbb\x8f\xb5T\x1c\xb8\x02\x89\xf5Nc\x0f\xe3_\xd7l\r\xb4\xfe\x12nA?\x8f:\xda\xd1\xc1\xa3g\xc2\xed\xac\x96\xc7<\x01\x00\x19\x08\xb7\xdbZU\x98\xd2\x85\x0e\xcd\xec\xa0\xc1\xbd~\xe5k\xcf\xdej\xe8\xc5",
                        "code_execution_result": None,
                        "executable_code": None,
                        "function_call": {
                            "id": None,
                            "args": {"isbn": "0-7653-1178-X"},
                            "name": "get_book_info",
                        },
                        "function_response": None,
                        "text": None,
                    }
                ],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="google_unknown_tool_id",
                        name="get_book_info",
                        value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text='{"title": "Mistborn: The Final Empire", "pages": 544, "author": "Brandon Sanderson", "publication_year": 2006}'
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
                        "thought_signature": b"\n\xd7\x06\x01\xd1\xed\x8ao\xcf\xbbE7\xb9H7\x14BJ\xf6!9q\xa4\x99F%\xff\xcd\r\x06\xee\x80dj\x1fM3q>\xa3\xaci\x08i\x00\xeb\x03\xc5\xdf'\xe5;\x86\xbd\xb9VL\xa2\x83`\x07\xd0\x84\xbcu\xd4n\x15\x13;\xc4\xbdV\x17\xb8\xf0\x9a\xdak\xca\xfbPp\x02:\x8c\xda\x0e@\x0eDtL\x88\xc5\xe4\xc8\xb1E\x86?v\xf6\xbb\x92#\x8a\x84\xf7m7\xe4\x8d\xa0\rd\xb9H\xd5\xb6\xc3Q\xe6\xe0\xa7\x9b\x8a`\x1e\xc9e\x08\xca\xc0n\xc8\xe7+\xa4\x9951Y\xef\xce\xa5\x9c\x8dN\xbcy\x85\xc2\xe0\xe8?\xc2\xbb\x8c\xc9\xc4\x1by\xe3\xfb\x00\xd8\xd5\xb1\xaaIj\xda4\xaa\x9b\xddeSl>\x0b\xa2]\xcb5\xd5D\xaf\xf0)\x03\x0f\x94E\xa5tR\xb6r\x10\xea\xbd\xd5B\x01\x15Id?\xf7\xcc\xfb\xcdPs\xa2_\x1f<\x9f\x04\xc4\x0c\xf5\xe6L\xe9\xc9\xde\xb8\xf4'z\x15\xc5Y\x7f\r,\xd4a\\\x9d\xeb\xcc\xc6\xb5\xfe\x156\x1d\x9e\x9c\xd1w\xf2\xf1cTX\x8b\xc4\xe3*uo\x88:]\xf6\x89\x93\xe8\xee\x95\x86\rr\xf13\xfe\"\x1a\xfd7y\xab5\xd9\xd3\xf6\x89\xe1\xe2)\x93\x15C\xa7\xfa\xa0d\xf9i|\x981\x8c\xba;\x7f\xc3z\x14\xb5e\xcf\xe4&\x809\x1b\x8f\xb7\xe8\xeaI@\x9e\xa9\xcayw6G;P\xabv\xb3G\x0c\xef\xeb<\xfb,7\x99a`&94aW\xb6\xa7\x14MJ\x80\xc6\x9f\xe6K(\xa9<6\xdf}\x98F\x96N{\x02QK\x9eu\x8b\xc0\xa3{\x00\xaa\xd0Jb\xf2.^\x84\\@m\\Q\xdb&\xbcr\x01\xcbHO\"\x07\xcf\x9e\xee\x9d\x8e\xf9\xa7\xa5\xd90#\x07hv\xf4zJ\xab\xa8\xfe\xa0\xe6\xdc\xcd\xba\x9aK\x9a&r\x93{$\xfe_\x1a\xb3Ru\xd7H\x98W\xaaO\xf8\xfb\xbe\x99X_+K\x87X\xc0\xfd\x9d\xc7\xac\xb2\xbf\x12\xbc\xa0\xf5\x9e\x9b\xcb\xce9\xb1\x075E.\x1a\xf7\xc4\x84\xee\xbdp\x82\xa72u\xbe\xcc\x8e\xf6\x86\x08\xb9}\x06:$\xd5\xa7M\"d\xf6\x02~\xc8\x89\xfd\xbe\xbd2_\xa7Y\xd0\xa9\xfd\xe0`\x18[\xb87r\xfdG\xddz\x93\xb5\xc7b\x8c\x8fE\x93L\xb0\x1a\xba\x85s\xdd:\xe5L\xdc}7\xba4\xa2\t\xd1\xaf`JU\x11.R.'i\xe6>{\xb0.\xae\xcfV\xd7@zf\xc1m\xbf\xd4<\xc9\x0f \xa4+\xdbe\xe4\xe2\x9e\xd5n:\xdc3\x01K\x91<\xe6\x19\xdd\xfd/\x85\xces\x85\x06O\xc8\xa8l\xa3\x1d\xb6\x00\xd03p)\xc9\xeb\xb2 \xd1\xa8\x0c\x138h\xf8s\xc1\xf6\xd0\x97\xf3\xb0\xef\xbdG\xb9\xf9-\xdd^\x01s\xb5$\xa8\x15,\xd8:'\xcb\x8d}\xbc\x7f'\x86no^g\x82\x00C\xcd\xe8\xe9\xef\xc0|\xd6\xf7wv\xef\xfd\x9d\xda\x0fk`Bg\xd6\xb3\xfb>\x93f\xe3Ceez\x983r<@\x15\x9b<\xbd\xcd\xbeN\x8e\\\xb2\x0507\xe7\xfd\xe8Bo\xbd\x1c\xa9\xc6\xd9LF\xb8@*\x9d\xaa\x9fh\x8a@\xc8\xca\xf6\xa9\xfa\x89\xa9\xc2V\xff1Rc\xc9m\xa9\x0b*?\x9a\x0f\x9ah\xbc|\xb0\xe6\xe8\x0b\x0ec\x84wg\xbb3;\x89\xcd\x10\x89X\x86\x94p\x92#\x7fwF\xe7\x870\x0c\xcd\xc5X\xdeN\xc8\xf4\x0f,\xd7\xd5\xc6\xe0\x0c\xc9 G\xb32\x85\xa8\xe4\x84\x1eJdP\xd1\x9f\xca`\x88\x9a\x9c\xc3\xc5r\xf69\x00\x9b\x15\xab\x8a\xcfs\x1cZ\x97Br",
                        "code_execution_result": None,
                        "executable_code": None,
                        "function_call": {
                            "id": None,
                            "args": {
                                "title": "Mistborn: The Final Empire",
                                "pages": 544,
                                "author": "Brandon Sanderson",
                                "publication_year": 2006,
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
                "strict": False,
            }
        ],
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
                provider="google",
                model_id="gemini-2.5-flash",
                raw_content=[],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="google_unknown_tool_id",
                        name="get_book_info",
                        value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text='{"pages": 544, "publication_year": 2006, "title": "Mistborn: The Final Empire", "author": "Brandon Sanderson"}'
                    )
                ],
                provider="google",
                model_id="gemini-2.5-flash",
                raw_content=[],
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
                "strict": False,
            }
        ],
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
                provider="google",
                model_id="gemini-2.5-flash",
                raw_content=[],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="google_unknown_tool_id",
                        name="get_book_info",
                        value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text='{"title": "Mistborn: The Final Empire", "publication_year": 2006, "author": "Brandon Sanderson", "pages": 544}'
                    )
                ],
                provider="google",
                model_id="gemini-2.5-flash",
                raw_content=[],
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
                "strict": False,
            }
        ],
        "n_chunks": 3,
    }
)
