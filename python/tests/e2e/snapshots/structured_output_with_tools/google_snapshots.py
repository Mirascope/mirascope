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
                        id="<unknown>",
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
                        "thought_signature": b'\n\x91\x07\x01\xd1\xed\x8aoH\xc7\xbf\xae\x04 \xa0\x9eV\x9b\xbc\xda\x90Q\x91\x08\xda\x87(f\x95\x04\xa3K\x86\xf5\x15\x1a^\xf3\xab\xb8\xf5\xa2\xacO\x11c\x96\x98\xf0\xdb\xfe\'\xeeB9"F\xa5\x9c\x86<\x94\xc5;\xc7\x1a\xdbj\xdeI\xe6\xb9kG\xd5\xb6\xebp\xca\xdf\x9co\xde\xac%w\x80\xc2\xfc\x01\xd2\xe9\xaa&\xa2f\xfc\x1d_\x14G\xd2\xeb<\xb37bu\xacA\xf9\xb0%\xd9\x15m\xdbM\x83V\xa5\xe2\x80\x9al\xbes\x0c_D\x9b\x95\x90F\xaa\xc1\x92\x99 \xc9`\x9f\xdb\x01\x89\x9c4\xff\x9ck\xef\xe50\xcfZ\xd6`\xfa\xc459\xfd\x0bO\xa6\xf7\xd3\xf7\x9a\xb7\xf8\xe1\x97o}5\x9b\xfb\x81\xf4\x1cw\xe1$\x9a\xa7n1\x05\xfe\xf4\xb4\xc0\x1e*\x97\x8e\xe1\x15\x14\x9917\xba\x01_\x8d\x06;\x90\xb4\x99\xfd;4\x87\xd5V\x8a\xbc\x1dl\xf0\x90OA\xd0\xdamI\xd3\xe2\xaa\xe5\xd8V\xaa\xf6\xae\x08N\x93\x02\x0e5]\xa7t\xcc\x0f\xfc\xb5a\xd3j\xcd\xd8!\xfer\xc4lv\xab%+Tg>\xcc\xca\xf3t\xd9\xbf\x93\xd2\xa9\xd3\xea\xf7w\x82\xa5h\xe8\x10\xbcy\x8f\x8d\x0fi\xe0ydx\x9d\xa2\x86\xae?y\x95<W?@):\x90^M\xe2o\xbb\x1c\x81I\xb6\x84\x7fg\xe2\xa5v\xf9\xb2\x10\xd0\xc8x\x10X\xb2\xc9`*=k\x16@\x9e\x80\xeeC{\xaf\x82\t\xb41\xdf\xdfM\xe8\x0fb)\xe8\xd8\x8b1G\xcar\xdf\x03\x90K\xaa\n\xcbv\xb5)\x19\x06\xd6\xa70\xb8\xfcC\xbf\x9c\x9dr\xe2\xccP\x0eTe\x15L\x8d",7\x074\xab\xe7\xa7:\xb9\x13\x8d\x9c\x92\x07\xb7\xc1\xe3\x01\x97\xcdh\x13\x1b\xe5\x14h]\xa0\x86\xcb\x9e\x93\x8b_\t\r\xb1|Q\xf48\x9az\x94\xdf\xfc\xa2\x9c\xf0\xc8\xd97%\x13\xfc|x\x99V\x1b\xd7 Xs\xf1\x8e{\x94\xe6\xd3\x12\x88D\xf7\xea\xabwN\xcd\xce\xc9%U\x01\xcb\xdbS\xac\x8e\x80\x93\xaew\x0f\t\xfb\xb5\xf3\t\x11\xad;)u\x15x\xe6V\xcb\x88?\x95\x85\xbb\x7f\xffOp\x06\x91uo\x16Z.?\xdf\x86\xf4\xbc\x8b\xaf\x8f\xd7\xff\xaffX\xc0\xa5Sq\xc9\xc8L\x9d\xc9v\xd4e\x14\xfc\x86r\xf2>\xccc\xa7P\x08\x0f\xf4\xe2\x93QF\xdd<P\x18\xe0\xc8\x01\xd0x\xf8Yd\x08\xa8\xf6\x89\r\xa6\xd9V\x88;\xbf\xcdG\xb5\x81\xc9\x92\x91\xcd\xdfL$@]\x12\x14\xa3\xd2\xa5\xe8\x91RRB\x04\x8d\xa7\xdd!\xf7\xe6\x94z\x1dcr$\xa3\xb5\x96f\xff\xd57Uej\xe2i\x14Rx\xe3G\xda\xad\xfa\xc98$l\xc2\xc6\x88s|\xbf\xdfz\x1d\x9e\xbf5\x14\xfa\xde\xa9\x95\xe6\x8c!1\xe6\xfa\xfb\x9e*\xe6vU$U\xc3\xdb\xeaw\xaamr\x91\xb0g(O\xe4\xa0\xad\x8c\xd1\xfb\xb6\xe3\xf8\x10\x9fV\x8e\t\x91\xab\xb4\x17*|\xb3\xbf\xe02n7\xae\x9a\xc9aM\xde\xd7m\xa6p\xe2r\x0b!@\xfe\xeb\xc1\xf3\xdb\x9f+\xf1#Ih\x8c"\xce\xb2\x98\x9b"\x96\xf9\xb9+\xaf\x8d`m&\xf4\xf0\xdf\xa3\xfdl\xef\xf6\x85\xbe_h\x03&\xa4\xfa\x9aY\xd8`\xa2\xdb\xacq\xf9\xffA\x1b\x99\x92~\xd9j\x0fX\xdc8\xa0\x07G\xa3\xb1v\x8f~\xfbd\\\x0e\xecsZ\xea$\x9a\xa7h\xfc\xa7<\x03?\x98R\x1b\x1f\x84\x8b=\x00\xa5t;v\xeb-\xbf}\x93T\xff\x9a\xce\xc0\xf2\xff\x8b\xa6\xc6"\x05l=\x81?\xb5\x18\xf9\xd5\x8di\xa2\xf9\xb3\x9b\x80q\xf2HJ\xd5WUE\x8au6\x0f\xe8Vm8Ci=\x04\xd4\xd5\xdd\x8a\xbf\x94\xab{\x8erJ\x8e\xaf\x05\x92\xd6:\xf9\xbe\xa3)\xfdk\x05\tyC\xd1}\x88\x80',
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
                        id="<unknown>",
                        name="get_book_info",
                        value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text='{"author": "Brandon Sanderson", "title": "Mistborn: The Final Empire", "pages": 544, "publication_year": 2006}'
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
                        "thought_signature": b'\n\xd0\x05\x01\xd1\xed\x8ao\xfa\xea\xae\x0b\x7f\xe6\x90\xc7E\x0f\xc6}\x0ei1+\xc3\x13\xc9(\x033\xc8;\xad\xe3-g5\x97\xce\xce)\xea\xcao&\xfb\x81-\x90t7\xc8\x90\xf1\xf81\x82\xbd\xe3\x9f\x1a\xda\x9eA\xe3a\xcfH\xa0\xfag\x04\x96\xc7\xfd\xc8\x81\xf9\xff\xad\xa0z\x0c\xad\xcaY\xf3.\x8a\x80yL"\xa8A\xba\xd9+^\t\x1a\x7f\x03\xaa{\xe6P\x87\x08-\x7fE\xc2.\x94D\xa1!\xfc\t\x8bD\xaa\x03\xbd%\x02\xb2\xd4\x8d\x92\x18?F2K7D\xaf\xd6\xa4\xd8}\xd3\xf6C(\xa0i\xfb\xef\xd0\x8c\x9a\xb9>\xeaN\nn\x8dQ\xb5\xec,\r\xbf\x84\xe1_!c\x93Q5\x0e\xd6m\xba\xba\xca\rP\x91H\xfdS\xbf\x87w\x01\xa4w\x96\xf8\xb4\x94<{t\xa9m\x8e\x95\xf5\xeb\xee\xb6Bq\xdd\xe1t!\xfe\t\xcf\xd6\xfb-\x16aq\xad\xbc\xeaK\x03>\xd8\xfb\x16\xaa\x1c\x9bG\x11\xccc\xa0(\xd2\x9fd\xbal_\xc87K\x8a\xd8B\x17\xff\xd1Q2bU\xa3`\x86%\xc2\xd2\xc2\xb7\xc0\x84*J\x07\xc3>4\xe0N\x8a[\xa4\x03_\xa5\x99\xfb\xcf}0\xd9\xf1\xdd\x91w\x81\xcb\xab\x92&\x82\xee\xe3KG\xf5\x1eP\x020\xc3=\x93\xf4\x9d!j\xef+\xd2\x07\x14\xb8\x02\x19\r\xdb\x12\x1e\xc67\x1cK\xbd"-C\x10\x95\r\xeb\xdf\xaf\xa3(\xcbd)\xa2\x97DY\xb6[\xa3\x14\x9e\xf0\x92\x8d\xcd\x08\xb9\x8f\x16\xb5\xe3C\xe8\xb5\xe2\xbeM\xdafM\xc4^P^s\xcb\xa4\x02\xce\x03\xa9,$X\xb9\x0e\xb4\xe1\xae\x03\xb3\x14&\x0c:\xdb\xf9\x0c\x81\xcd\xbd\xffB\xa0\ra\xa3+wm\xd3\xbcv\xc6\xe1\xae\x02\x14tR\x12\x10\xe9\xb8\xff\x99\xf1\x81\xa0\xae\xda\xcfQVE\xbd\x81\x8dEzh\x97\n\\L\x99\xc9\x80=\x879\xdb\x02\x83zC\xc4\x81~\x91\xa5\xad:\xad\xd2T\x90\xee\xc9\xcfl`\xf6,\xc7\xe5\xb9\xd30\x18\xbcqX\xa9\x1c[\xc0u\x80\x9a\nS\xcb\xb1\x83\xc8=\x11\xd4-\x95\x15\x08\x16\xaa\xf51\xf1[\xc0\x9d\x01o\x157\xa0\xb3\x03\x0f\x18j1C\x0b\rl\\\x17K\xb3\xbfwx\xdc\x91p\xaer\xf6\x1d9\xfa\xa9\xb1{\xfa\xe7Z\xcc\xbf1M\x7f\xc9\x7f\x99\xbe\xe2\xba\xc2\x9b\xd8}_q:3\xf9-~ \xbe\x9eF4${nU\x0e\x92\xd8\x13`\xfa\x9er|\x9fR\xed`_\xbc9&2\x00An\x1f9\xe5\xec\xf7\xc7\xcd\xad\xb2d\xe7m[\x9a\xd5\xf0Dam_\xe7\x8b\xbf]r\xde\x87\xda\x85&\xaa\x00\xbcG\xa2`X\x1e3\x08\xb6\xa9\xfe\r<9\x91\xb0\x801\xa7\x11\x9a\xb2\x17\x1a\xca\xc3b\xe9c\xe6\xb1\x0cB^}H\xda|\xda\xab\xd5\xcd\xb3R^\xc0m7"g\xd6\xf6^6\xfe8\x84.lE\xf2$|c\xafH\xfa*\x0c:\xcc ##B7\x12H\x96z\xa9/\xa0\xfd\xd6\xdf',
                        "code_execution_result": None,
                        "executable_code": None,
                        "function_call": {
                            "id": None,
                            "args": {
                                "author": "Brandon Sanderson",
                                "title": "Mistborn: The Final Empire",
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
                        id="<unknown>",
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
                        "thought_signature": b"\n\x85\t\x01\xd1\xed\x8ao\xcc\x00\xbe=\x9c\xfbw c\x95\xdbu\x07\xde\x1e\rA\xba\x13\xd1\xa5+\xb6\xec\xf5\x06\xf2\xc3\xc7\x93\xd5\x15c\x11\xf8\xf8\xa1\x97\x81>\\\xfc\xe75\xf8\xb9s\x1d\x8b\x81b\x82\xa0<\xff\x80O\xa0fVmZ\x16\x04\xa9w\x16i\xed\x9d\xef\xaf\x00\xd9\n\x1f\xb6\xc6-6\x07\x14\xdb\x88\x88\xddX+)k\xc9\x03b\x02Q\xb3\xd5\x03?\xc5\x83\xf8}\xf5\xd0e\x1dhU\xe9\xb7\xdd\x0e\x1e\xb9\xb5o\x7ff@\xabq(;\x8f\xe4\xd3\xfa\xce\xf2GA~\xc9\xa0\xdb\xe7\xe7\xdb\xeb\xb5\xbe\xf8\xd4\xa6\x9f>\xd5a\xe0\xed\x81R\x88\xad\x91\xc3_i\x04\xa4E\xdd\xd3G\xfaS\x11\xefo\x0f\x86\x07{\x03\x14\x17=\x0f\xecq2\xa2m\xad\x1eX\x95\x84\x0f\xa6wv\xe3\xf1\xfe\xbf*:\x94\x95n\x03\xc6:\t\xbf\xcd|\xcaM\x83\x1e\xb6'\x94g\xc5\x97\x82,$b?\x87Ll\xbd?\x14:\xf6\xd0\x926\"\x0c\x10+g/7(\x95\x14\x15E\xf5\x80\xb1y\xb0\x80\x14\x0b\xf4\xda\xcb\xe2\x18D\xe0\xdf\xb7I\xd7\xa2V\xb5\x84M\xfa\x86*\x01\x88\xf2A\xce>\xdaE\xb7\xf5\xa1\xd4O\xa2\x9f\x94\xad\x15PM>\x87\xa6\x0f'\xf38\xdc1\x9d\x80<\x8dA\xb1\xb6GUdYc\xd6\xb4\xf8qq\xf9\xc0|p \xd8\x19\x13<\xcc\xf5=\xcf\xf9d\xdf\xf8^\x1d\xd4XZB\x91wo\xce\xb1\xfe\x836\x15\xb0\x0eu\xcd\xa28\x01\xfb\x12\xf5\n;\xd7\xf5\x15\xba\x0e\x9ek\x00{\"/;\xc8\xd5<\x80\xfdW\x90&\x1c\x19\x8f\xbf\xe3!{\xd1hc\"L!6 \x9as\xce,\xe7}\x8c\xe0\x05\xab\x97\xbb1\x14\x88\xcf\xf2\xae#\xc7\xe1LZG\xd4\x9d\x15n\xae\xb2\x1f`\xba?\xb1|1\x9e\x95b\xd4 }\x9e\xcc\x90A\xa2U\xd1\xea\xf6p\x0e\x80\xdb1z^\x9c\xcf\xa6\xd1\xc5\xb2\x16d\xcf\xd3\xad3C\x90\xacA\x8c\xedU\xc6\xcaZ.}R\xc3\x97\x80*\xcd(u\x18\xa7\xfd\xb4\xdb\xd5\xd30\x84C\xc4\x00y\xc1I\x81\xac\x87\xe6s\xec?\xf5\xafo\xcd\xd3\x8c\xf8A\xe4\xd2\xd7\x84n\x9f\xa9~\x8e\xa2\xeb\xac\xec\xfd\xbb\xb2~\xfa`\xec\x81s9\x98?\x99\xd8~\xe4\xb22SO\xce\xbb4\x1a\xf8\xf5\xd0\xa5 \x97\xd8\xab\xaa\xe8\xc3x\tGb\xa6}\xb9\x80\xe6\xfa\xed\x8f66\xe5\x8f\xd6\xee\xb2\xee\xa4q;[\xc54\xca0\\\xe0\xcc\xe1\xfd\x8e\x05F\xf7f\xb2yiy\xb0\xaa\xb5e\xb3\xa0\xbb\xa1\xeb0ha \x85D\xa3I_'\xeaq\t\xe8VX\x0c\x0b\x01\xeb\x00\xff\xaa\r\xb0\xf0\x84\x10\xda\xaa=\x9f\x8f\xf2j\x92\xb3\xa6\xa8\x13\xf5\xfc\xae\x8cuo\xaae\xdb&\xd5\x84\x19\xe0h\xd8qC\\\x13\xcc@\xc2\x85\xf0\x93\x9f\x87h\xde\xeacg\xc2\xe0<c\xe8Uq3\xf0'\xa4\xa9\xc5\xd0{;\xf6\x06\x83\xed]\xe4)<\t\xc4\xbf\x058K\xc1h\xabr \xe8\x08\xfab\x9b\xf2\xc9\x88\x8d\xd3\xdd\xc4C\x02\x0b\x8a\xd6*\xfd\xd9\x10(v\xe9\xed\xca\xbaQ\xb4\xb26\nj;\xb61\x80\xc8\x03\xca\x8bF\x85\x93kA\x85\x96I\x93\x83n)\x15\x1f\xcb\xcc\\\xa3:\x17\x0f\xbd\x97\xea\x12[DW*\xd5\xe2\xfe\xb8\xab\x95\x87\xd4\x9c\x1a^b\xc2\xf7\xb1k\x96\x88\xfe\xaeY\xa6\xdc\xd3st\xca\x9b:sqf\xeae\x90>\x97\xf2y\xda\xcb\xc9)X\x84\xf9A\xa4[\xf9\x94\x84\xe6\xd5ME\xb3\xf5C\xbf\xd1\x82\xa50l\x1c\xbaXJ\xe8\xb5(\x90\x92\xffr\x16t\xc0)\xd3\x04e\xa3\xa2u>\xd5y\x82\t=\xa0i2\xf94h\xba\x93e^\\\xf1t\x0exW#\xa8h\xa7\x99\xb2a\x11\x8c\xb5\xc8\x8b.\xeb*\x9e\x0f.\x1bZl\x00.Q[\x01\xfdI\x95V+\xad\x1d\x87m\xd5\x98K\x82;\x12\x18_\x06\x08X&\x8c\xeeE\xd8\xe92\x84\xd6I\xdc,\xda\xbb\x01\xcaJ\xe39\xae\xb4\x8c\x16\xea\xd7-\xc1\xae\x812#Zs\xfaN[\xf5W\x181\xfc\x92\x04\xad\xb8\x7fGX\x87PX*\xb5\x90\xb8\x82\xb1\xdc~\xa5\x8dGr\x02\xdc\xe9\x82\xc0>\x7f\x92^\xf6\xef\x962b\xc0\xa16\xff\x16X9\xb1\xde }\x89\x81\xe2DA\xd6fU\xff\x02\xad\x18\xc8)d\xf3\x14-W/\xd7\xa7\x06\xeb\xda\xec\xef\xc1\x05\n\xdegNf\xaeE\xc3\xea\x01M\n\xc3/\xc2\xf4\x0b\xb1E\xde\x0c\xa5:7~J\xd1\x18c\xf1\xc9H\x80\x9c{\x96\x1a)\xc9p\xca\\\xe2\x00\x84\xdc\xd6\x9a\xb3(N\xc9WZx\x9b\xcfiM&d\xf4\x94\xf7\x99*\xf6g\xb0\x92j\x16\x08\xf2\xaf\xc0\x8a.\xc1@D\xc6\x9f@",
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
                        id="<unknown>",
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
                raw_content=[
                    {
                        "video_metadata": None,
                        "thought": None,
                        "inline_data": None,
                        "file_data": None,
                        "thought_signature": b"\n\xd9\x03\x01\xd1\xed\x8aoG\x12\xa6\x9aL*\xb0\xaa(\x9d\xf8\xf7;1\xf4\xe0\x85T)n\xfe\x10\x08U\xd23\n\xa6\x0c.t3\x1f\xab~\x88\x99\xd4<\x87\xa19\xa6B\xbf\xfc\x18\xef\x94H\x13\x9b\xdb-$\xcbz\xcd\x8fS\xe3\t\x12\x7f\xab\xca\x90\x15\x89\xc9E\xe4\xae\xa9?o\x85,\xb4h\xe6\x07\xf3.<\x89\r\xf5\x86f\xef\x84\xf70\x02J4\x84\xb7Sb\xa2\xd1\x03\xb4\xce\xd6\xdb\xfbp\x03\xa4\xb1\xc5\xb1\xb5\xc4\xce\xa6\xa4\x0e\xf6'\x9c\xf7\xac\xaf\x11\x8a\xbaul\x8d\xa1\x98\x9b\xdf\x97\xee\n\x96E\xf3S5\xba\xdf6\xf0\x90\x14X@\x15\x88y\x01'[\xb9'\x97\x99\xed\\B\xa8\xc4\xb2f\x15\xac\xb4\x86\xa9{\x80\xea\xac\xceyZ\xbe^g}\xe3\x1ch[E7\xe7\xbb\x8d\xd9\xcd\xc8\x19\xe1\xb3\xfa\xf3\x91]\xf4E\xc3\x9c\xd2\x8d\x00\x9d\xc3m\x1e\x17\x06v'\x8dq\xbd\xf4\xba\xae\x1e\xed-k\xdc\x18\xa3Y\xcc8O\xab\x876t\xabB5\x1b\"\x19Q\"\x08\x8co?+\xe4`]\xd39\xdf\xe0D\x8f\x7f\xd6\t\xeeS\xe9e\x94\x91\xd4\x17\xc0\xc8n\xcdN\xf6\xdaXvw\xf6#\\\xd0\x07\x95r\xac\xfc\xce+\x9bRP5\xe6k\xcbc\xf2e\xab\x91\x0e\xb7\xe9V\xa8\xb4Ux\x88\x16p\x8b=\xd0[\xe9l\xecl\xee\xdd#yS\x02\xf3]FUK\x8a\xc8|s\xd9%\xe7\xef\xb0\x8b\xa4\xa3<,\xd4\xef\xea\x16\xf38\xcf\xdd\x1b&&\x8e\x18\x00\xc8\xcbl\xe6<\xbe\xe6\x05\xa5\x11\xb8\x10\\Q\xfb$3\xdd=p\xfb\x11\xbaH\x05\xdaVrqb\xa4V{(\xa9,\x95<2U\x9f\xe5\xf3e\xd3O*\xe8gy\x120a\xe4\x81\xdel\xef;\xb1{~\xf9\x87\x10\x86\xce1\xb0\xef\xa2\xf1\x07\x9a\x96z\xe3\xe9\xcc\x85\xb7\xb6\xbd\xaf\xaa}P\xb5z\x99t\xa1X\x81\xb4n\x9a\xb2}\xfe\xa8\xe0L",
                        "code_execution_result": None,
                        "executable_code": None,
                        "function_call": {
                            "id": None,
                            "args": {
                                "pages": 544,
                                "publication_year": 2006,
                                "title": "Mistborn: The Final Empire",
                                "author": "Brandon Sanderson",
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
                        id="<unknown>",
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
                        id="<unknown>",
                        name="get_book_info",
                        value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text='{"publication_year": 2006, "author": "Brandon Sanderson", "title": "Mistborn: The Final Empire", "pages": 544}'
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
                        id="<unknown>",
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
                        id="<unknown>",
                        name="get_book_info",
                        value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text='{"pages": 544, "author": "Brandon Sanderson", "title": "Mistborn: The Final Empire", "publication_year": 2006}'
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
