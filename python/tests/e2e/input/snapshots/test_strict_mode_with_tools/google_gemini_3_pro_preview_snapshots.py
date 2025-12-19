from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    ToolCall,
    ToolOutput,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider_id": "google",
            "model_id": "google/gemini-3-pro-preview",
            "provider_model_name": "gemini-3-pro-preview",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 258,
                "output_tokens": 32,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": """\
cache_tokens_details=None cached_content_token_count=None candidates_token_count=32 candidates_tokens_details=None prompt_token_count=258 prompt_tokens_details=[ModalityTokenCount(
  modality=<MediaModality.TEXT: 'TEXT'>,
  token_count=258
)] thoughts_token_count=None tool_use_prompt_token_count=None tool_use_prompt_tokens_details=None total_token_count=290 traffic_type=None\
""",
                "total_tokens": 290,
            },
            "messages": [
                UserMessage(
                    content=[
                        Text(
                            text="Answer this question: What is 2 + 3, using the custom addition tool??"
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        ToolCall(
                            id="google_unknown_tool_id",
                            name="customAdditionImplementation",
                            args='{"b": 3, "a": 2}',
                        )
                    ],
                    provider_id="google",
                    model_id="google/gemini-3-pro-preview",
                    provider_model_name="gemini-3-pro-preview",
                    raw_message={
                        "parts": [
                            {
                                "function_call": {
                                    "id": None,
                                    "args": {"b": 3, "a": 2},
                                    "name": "customAdditionImplementation",
                                },
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": None,
                                "thought": None,
                                "thought_signature": b"\x12\x90\x04\n\x8d\x04\x01r\xc8\xda|Z\x7f/\xdf\xe5\xa4\x81\x90]\xc0\x04\x952|\xd3b\xe3N\x81\xe55\xf72\xeb\x991o\xc2\x056\xde\x10\xb5o\xa8\xfe\x10\x8f+\x07\nC\x89\x8a\xfcN\xf3]t\xba\xa3Hx\xccBs\r\xb4\xd5\xc5I\xe3\x0c;\xf9\xaaj\x83\x81\xb4^\xb2\xf0\x96\xb2\xea\xbc\xe8]\xbcH\xd4Ss\xecr\x86\xf9\xb0\xa9\xc0\xad\xa3\x19Fv\xc6\xd3\xca\x96\x9d\xb2\xdf\x05\xc5(\xa3\xaa[\xd3!k\xc2\xa2\xf0\xbc8tw\x93]S\xea\x9b\x02\x9b\x90\xf0\xff\xce\x97\xea\xc8\xe6Q\xcep\"\x95Q\x9an\xbb5\x1eyT\x84/\xc2,\xb8\xdcU4\xf4\xa4\xdft\xc8\xbeX\x9f\xbd\x91j-\xc1\x96w\x18VT\xdf\x85\xca\x81\x16\x998\xa2o\x9ct\xf2\x133\xccUp\x0e;\x1a3\x19x\x94\xf8\xe3ZW\x81`\xdc\xa8dO;\x1f\xae\xef\x81~~\x1fL\x96\xf2o[\xd0``g\xdb\xd2\x7f>R)\xdd\xf3\x99Z\xd0\xf4\x8f\xcb\r\x05\xb2,/\xc4\x81\xb1\xf9\x95\x85\x0b\x0cU\x91\xa7AwY\xe5\x11\xb8\xb4\xcb\x8b\xe1\xe8\xe9\x18'\xb5\x8f\xd5\x08\xe1=\xe0:}2\xcd\xd3\xfc\xd3\xdf\xceG2b\t\x8d\x1e\x9a\x83\x953\x17\xd6\xbf\x19\x02\x9a\xfe\x9a\xae\xd1_\x9f\xe2\xe8\x82\xd3\xdc 6\xfd+\xfd\xa6\xfc\x9et\xc2gp\xcd\xbe\r\xe7:-;56\x83M7Gd\n\x0f(\xc8\xe5\r\xe8\x8dT\xba\xc2}G\x95H\x17j\x9b\x0f\x99\x8c\xa8w~I\xdf\xb1D$\xa3\x91\xce<\x17z\xc9$7.@J\xc2d\x83\xcc_\x94\xff'(\xf3\xec\x02^/\x1d\x00\xe8\x83>#\x1a3F\xb5S_c\xbe$V^@\xd8m\xb9 Z|S\xd4n\xecT7\n\x1ez1\xf0\xac\xba$\x08\xec\x8f:*\x17\xab\x02\xc2,GR\xb0h\xca\x1b]\x87\x1c\xf8\xcf\xacr\xa9\xa6\xbbb%7kX\"\xfa\x11\xd3\xa75Q@y*\xe1%\xb9\xe45\x16k\x85\x80\xf1\xd7>\x14(\xa8\xcf\xa1a\xee\xc4\x9fj\x9c[\xb4r3;\x02[\tO\xdd@\x9a\xf7\x83jt\xcb\xbew\xe0\xb8$\xac\x1f\xfc\xfd",
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
                            name="customAdditionImplementation",
                            value=13,
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
{
  "integer_a": 2,
  "integer_b": 3,
  "answer": 13
} \
"""
                        )
                    ],
                    provider_id="google",
                    model_id="google/gemini-3-pro-preview",
                    provider_model_name="gemini-3-pro-preview",
                    raw_message={
                        "parts": [
                            {
                                "function_call": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": """\
{
  "integer_a": 2,
  "integer_b": 3,
  "answer": 13
} \
""",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            }
                        ],
                        "role": "model",
                    },
                ),
            ],
            "format": {
                "name": "IntegerAdditionResponse",
                "description": "A simple response for testing.",
                "schema": {
                    "description": "A simple response for testing.",
                    "properties": {
                        "integer_a": {"title": "Integer A", "type": "integer"},
                        "integer_b": {"title": "Integer B", "type": "integer"},
                        "answer": {"title": "Answer", "type": "integer"},
                    },
                    "required": ["integer_a", "integer_b", "answer"],
                    "title": "IntegerAdditionResponse",
                    "type": "object",
                },
                "mode": "strict",
                "formatting_instructions": None,
            },
            "tools": [
                {
                    "name": "customAdditionImplementation",
                    "description": "Perform computation on integers.",
                    "parameters": """\
{
  "properties": {
    "a": {
      "title": "A",
      "type": "integer"
    },
    "b": {
      "title": "B",
      "type": "integer"
    }
  },
  "required": [
    "a",
    "b"
  ],
  "additionalProperties": false,
  "defs": null
}\
""",
                    "strict": False,
                }
            ],
        }
    }
)
