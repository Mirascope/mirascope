from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    Thought,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider_id": "google",
            "model_id": "google/gemini-3-pro-preview",
            "provider_model_name": "gemini-3-pro-preview",
            "params": {"thinking": True},
            "finish_reason": None,
            "usage": {
                "input_tokens": 13,
                "output_tokens": 313,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 283,
                "raw": """\
cache_tokens_details=None cached_content_token_count=None candidates_token_count=30 candidates_tokens_details=None prompt_token_count=13 prompt_tokens_details=[ModalityTokenCount(
  modality=<MediaModality.TEXT: 'TEXT'>,
  token_count=13
)] thoughts_token_count=283 tool_use_prompt_token_count=None tool_use_prompt_tokens_details=None total_token_count=326 traffic_type=None\
""",
                "total_tokens": 326,
            },
            "messages": [
                UserMessage(
                    content=[Text(text="Answer this question: What is 2 + 2?")]
                ),
                AssistantMessage(
                    content=[
                        Thought(
                            thought="""\
**Processing a Simple Arithmetic Request**

Okay, so I'm presented with a straightforward request: "What is 2 + 2?"  Simple. I need to return a JSON response, adhering to a defined schema, which, as an expert in this field, I instantly recognize. My thinking process, in brief, goes like this:

First, I quickly review the schema: it specifies an object with `integer_a`, `integer_b`, and `answer` as required integer properties.  I immediately recognize these as the components of the simple addition problem.

Next, the mapping is easy: `integer_a` is 2, `integer_b` is 2, and the `answer` is clearly 4.

I then construct the JSON object: `{"integer_a": 2, "integer_b": 2, "answer": 4}`.

Now, as always, I perform a rapid validation check: Is it valid JSON? Yes. Are strings properly quoted? Not applicable, since all values are integers. Are there any comments or control tokens? No, it's clean. Does the structure comply with the schema? Absolutely.

Finally, I generate the output - the validated JSON string. This is practically second nature at this point.


"""
                        ),
                        Text(
                            text="""\
{
  "integer_a": 2,
  "integer_b": 2,
  "answer": 4
}\
"""
                        ),
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
**Processing a Simple Arithmetic Request**

Okay, so I'm presented with a straightforward request: "What is 2 + 2?"  Simple. I need to return a JSON response, adhering to a defined schema, which, as an expert in this field, I instantly recognize. My thinking process, in brief, goes like this:

First, I quickly review the schema: it specifies an object with `integer_a`, `integer_b`, and `answer` as required integer properties.  I immediately recognize these as the components of the simple addition problem.

Next, the mapping is easy: `integer_a` is 2, `integer_b` is 2, and the `answer` is clearly 4.

I then construct the JSON object: `{"integer_a": 2, "integer_b": 2, "answer": 4}`.

Now, as always, I perform a rapid validation check: Is it valid JSON? Yes. Are strings properly quoted? Not applicable, since all values are integers. Are there any comments or control tokens? No, it's clean. Does the structure comply with the schema? Absolutely.

Finally, I generate the output - the validated JSON string. This is practically second nature at this point.


""",
                                "thought": True,
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
{
  "integer_a": 2,
  "integer_b": 2,
  "answer": 4
}\
""",
                                "thought": None,
                                "thought_signature": b"\x12\x86\x07\n\x83\x07\x01r\xc8\xda|\xae\x16\x07x$\xfb\x8f\x0e\ny\x060\x1f\xef|{\xecz\xfe\r\xe8p\x92\xf6\x89\xc2\xd1\x80\xe5\xf9\x9dk\xfc\xcd\xb0\xf3\xd7\x82\xa3\x82\xfb\xad\x97\xa7,\x04wNf\xc3\xe9S++\x82\xc5sY\xa3\xbb\xb3\xc1W\xd9\x9dHe\xc2\x04\xaa\x86ai\x0f\x13\x07\\\xf8'\x06\x8d\x9bx\x84Z=\x99\xda\xcb\xf1\x17)x\xb3^\x1c\x9a/\x0b\xbb\xc1\xb1J\xf6\xfcb\xad[8\x9c\xc2O\x8f\xbe\x04\xfc\x90\x11Wy\xec\x02\xa8d\x82\x8a\x94\xfc\x0c\x10rSy\xff\xac\n\x81\x9e\xc3\xca2\xcb\x81\x9d\xcd\t\xf73\x13\xb5;\xf84\xa4R\xfc\xb0\x81\xe1\xdf\x191\x0e\x811\xa0[\x81vu\x08\xbd\x15I\xeb,\xaf\xa4\x0f\x89x4\x85h\xd0\xda\xe2\x91,\xd8H`z\xd7ju5F0\x18\xfc8\x15\xcd\xb4\x93\xfc\x11\xdc\xafn\x92\xd8\xcf\x9c\x1es\xb1T\x9c\xfd}N\xda:C\x12wSx\xc6\xad\x90\x8cP\xce\xacn\xafQ\x02\xb6\xf8\xc2[-\x99\xc4\xe3\x83\xb9\x7f\x94\xad\x1f66>\x0c\xef\x9ax\xa3\xe3\xf8\xc3\xb1\xf3\xf2gu>\x98|IF\xa9GMm\xd1\x18.\x96U\xf9\xb4\xf3'c\x01\xd9\x0b\x94\t\xad\x94,\x88\x91B\x88|6Ub\xeb\xae\xe6=tK\xbeE\xacq9\x13\xe4\x86\x1bl\x9f2\xd0\x9fi\xfc\xa1\x06*\xb2\xbeN1\xc0\x1b\x12\xdf\x89\x05\xd86\xd7\xb4%T\xf1\xbe'\x80/\xde\xf1~\x1e\x9a\x001\x83\xdb)\xbc\xf8\x1f\xc6oh\xc3\x16\xedH'\x85\xb1\x96\x04\xcdHaD}\xfbn\xc0\xac8\x946\x8d\xdd\xd8\x06\xeaG\x9a\x83\xb6\xf825>_\x868\xc8\x9bD\xf5\x8c\xbcm\x94\x1e\x1dV\xe6\x83\xb5\xdb\x85\xd0P\xd6\x1e\x02\xab\xf9\x0eo\xe5\xaeh\rd\xc7\xd1\\\x9a\xf2Inpx\xe5\xdb\xa8\xe9\xd5\xedi\xf5\xc3\x98\x13<q\xb9\x1e\x00(\xef\x95\x81V8F\x9d\x96\xa3Or.Z\xf33\xc1\xc8f\xa7\xc6\xa0\x97\xd8b\x955\xb8\xf8d\x0c\xc1\x84\xf8\xd0\x11\xcap\xbbC-\x94T\xee\x0f\x92~D\xb5m\x84\xea\xd3\xce@\xa9>\xf8\x19~4\x8b\xa1\x19l<\x17C\x96\xc6IW.\x12]N\xd3\xf4\x8c\x9d\xcf\xbc,\x0eZ\x1e\x980N\xb5xFly\xc4\x0b\x04\x03\xda\xc1\xe4\x1c\xddp\x92\xbdlc\xd8\x90C/6*9\x82\xf4\x96\xe9\x14t\xd5!\xb8\xb0\x8f\\\xa4\xde\xa2\x8dp\x134`\xde\xaeYU\xbe\xfa\xa4mS\xcc\xec\xd6\xef0\x9a$@\xedNV\xdd&z\xd7\x16\x13\xeap~K\t\xad\xdc\xbf\xed\x8a\xbf\x84\xfc\xdb&\xc8M+\xc8\"\x14\xd84;]\x11\xf4\xafE\x0cy\xd6l\x8fE\xca\xc5\xee(\xa5:\x15\x08!\xa8\xf7<\xc6\x81\x9e\x7f\tp\xc9\x7f\x16L\x89Z,\r\x13\xb4\xcf%\x04\n\xa4\x9af\xce\xcb\x00\xbf\xbb\xc0DF\xf0Jl\xe5#Im\x82\x00\xd6<\xc1\x08\xf6\xca0\xdb\xa3%\xf5\xc6t\x8b|n{\x12#\x14$\xddv\xd4\xd8$\xd5\xb7\xe8\x1d\xff\xcfL\x05\xde\xe0\xb9\x1e\xeb%\xce\x13=\xbb\x9d\xaa\xdc:\x82\x0b\xb5\x18l\xd0d?=\xfd5\x93\x91h\x19/d\t\xb9\xed\xd8\xd3\x12S~\xb4\xc39\x88\x00\xe4K\xb6\x9b\x10\x9fE\xd2\xbb\xd9\x12;\tb\xd1\x9a\xe1\x81Z\xd7\xa5\xb9\xa3E,\x8fR\xb9\"n\x993\x0e\xb8\xd5\xc6VQ<\xean\x94\x02'\xa7\xeb\xc6\xc4\xdd\x80d\x88\x1a\x1eM\xc1\xd0\xa7\xb2\x00\x89\xear\xc5D\xeb\xdc\x9aHgVf\xb7QjzeMu\xa9\xd3\xdc\xca@\xa7(\xbc\x9eP\x1e\x9d6\xd8\xeb:\xe1l\xd4\"|\x1e\x10s\x11\xda\x89\x7f\xa8",
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
            "tools": [],
        }
    }
)
