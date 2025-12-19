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
            "provider_model_name": "gemini-3-pro-preview",
            "model_id": "google/gemini-3-pro-preview",
            "finish_reason": None,
            "messages": [
                UserMessage(
                    content=[
                        Text(
                            text="Answer this question: What is 2 + 3, using the custom addition tool?"
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        ToolCall(
                            id="google_unknown_tool_id",
                            name="customAdditionImplementation",
                            args='{"a": 2, "b": 3}',
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
                                    "args": {"a": 2, "b": 3},
                                    "name": "customAdditionImplementation",
                                },
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": None,
                                "thought": None,
                                "thought_signature": b"\x12\xde\x05\n\xdb\x05\x01r\xc8\xda|\x03\xd3T\xb2>\x03i\xc2\xbd\xb2\x14%O\xc3!]\xa9\xc8\xd0\xaec0\xa4\xd5j\xee7t\xbb\xa2\xca\xe9p\xa5Q\x81\x8cC\x12\xcd\xab\xbb,\x11\x8es%\x10\r\xe4Mq\x1a\x00\xd0\xd6\x8fQ!c\xac\x99\x0b\xab\xd0r\xa6\x00\x91\x8f\xab\xe3q&\x8fd\xae\xe0\xc2B/)/\xaf6;\xd8fZ\xc2\x95\x03\x0c\xd6\x06\xba\xbc\x83\xe6h\xfccN\x96w\x9e\xc1\xe3\xa5\xf2\xe6\xe3\x8f\xc3\xc8J9\x7f,\x16\xcd*\xc6c\xa2\xe1u\x80t\xbf\xcbX\x127 \xf2JW6\xef\x7f.\xb5~\xf7F\xaf\xdd\xbd\xc2?\x85\xf3s\x96\x04\xcc\xa1\xae\xea\x83v\xa9a\xec\xbb\x85_H\xff[_\xa9\x8aE\x8dC\x0b\x9ag\xe0\xf8\x8b\x11\xaaK]\xbc\xc0\xdb{\xf5\xef3N\xf2\x82\x07G \xc6\x92+\x1b\xd9+\xe2\xd9\xaf\x14w\x03\xde\x0b\xbc\xf9\x81\xfcc\xcc\xbd\x1d\xcc\xdc?\x18bT-\x96\x9d\x8fp\x8e\x86d\x8d\x1b\x9e\xc92\xed\xebx\te\x7f\x1d\x1cg\x93\n\xb1\xb5\x1eY\x17\xaaf9\\}\xa2\x8e7\xad\xbf&\x13\xac\xab\x0ey\xfa\xb3\xbe\xfaG\x05~\xe1^:h\xdc'\xec\xc7$\xcdC\xca[A|A{\x86\x02]\x7f\xee\x91c\xb5\xb1\xec\xdfym\xcb:\xe7\xde\xf3\x9e\x16\x1d\xb5bU\x10g\x15\x9e\x895\xb7\x1b\xbd\x8e\"\xe0\xf6\x06\xedS-D\x12\x96\x05\xe9\x1d\x8ayr\x9dL\xbf\xa1\x9f\x9f\x9a}\xcb\x94\xb0\xc1\x86\xfa\xb9\xce\xb2\xdbK*\xd6|D \x82\x82\x88\xe5\xb6*\xf2f\xb9\x9d(r\xc4\xe2\xdf\t\xf3\x0b\xeaLyq\xa9L\"\x05\xecZ2\x0b\x11\x9a\xb0\x9d\xc6\xe7\x9dL\x9a\x8b_X8ac'\xd9\x1d0\x8e\xd1J^\xa4q\xe8\xfc\x04\xe8\x04\xcc{\xa1\xa3\x03\x8c\xe3d@\xa7\xa1n\xe3+\xa45\t\x16\x8c\x9ed@\xe5\xae(U]\xb5a\x19\xf8/\x02\xddb\x8f\xe5\xde\xa8 \x05\x9c\x1b\xcc\xcd\xea\x82\x9e)I\xfalEO\x8e\xeb3\xce\xc4\x0b\xcc\xd9]\xcd.\xc4\xd8\xb9\x1c\xcd\xba\xd8#\xb0\x98\x16\x92@54\xa4\xe7d\nNApS\xe9\xec'.\xfa\xad&]\x11\t8FG\xbf\xb7j\xe8 2\xc4\xa9\x8f\x16L\xc0|\x0b\xa4a\x87\xf5Y\x9b\x8b\xc9\x8e\xc0\x10\xaak\x10)f\xbe\x87\xa15\xa2b\xe6B\x18\xd2M,P\x9bi\x10\x8a\xee\x1f@[\xb6H\x9fP\xb0\xcf\x87}\x0f:7c-q#\xbb6\xa3\xf0\x07\xfa\xdc3\xad(\xed\x92\xa5\x90\xde\xf2Kv\xcb\x13G\xf8\x91\x98\xee9\xee\xf2\xf6\x8d\xffr\x16\x9f]\xf7vP\xdb\x9f\xb3\x9e\x1e\xe4O=>\xc9\x90\x14\x1d\xe7\x0f\xba\xf5\xe0\xa830#`7\x91\xd7]r\x8e\xee~&H\xd0\xe4\x13'\x96\x1aA\x8a\xdc\xa0\xcdQ\xf2|kv\xf3\xb7b\xb5\x02\xe5\x13\x14\xb0zre\xc38\xc4\xe0\xa1:o\xceAP}\x9f\xb0\xf5\x9cz!~|a\xb0\xb6#l\xf5\xe6D\x1c,",
                                "video_metadata": None,
                            },
                            {
                                "function_call": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": "",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
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
                                "text": "{",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                            {
                                "function_call": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": """\

  "integer_a": 2,
  "integer_b\
""",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                            {
                                "function_call": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": """\
": 3,
  "answer": 13
} \
""",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                            {
                                "function_call": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": "",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
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
            "usage": {
                "input_tokens": 271,
                "output_tokens": 32,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 303,
            },
            "n_chunks": 5,
        }
    }
)
