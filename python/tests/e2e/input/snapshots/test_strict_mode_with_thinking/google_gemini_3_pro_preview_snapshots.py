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
            "params": {"thinking": {"level": "medium"}},
            "finish_reason": None,
            "usage": {
                "input_tokens": 13,
                "output_tokens": 339,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 309,
                "raw": """\
cache_tokens_details=None cached_content_token_count=None candidates_token_count=30 candidates_tokens_details=None prompt_token_count=13 prompt_tokens_details=[ModalityTokenCount(
  modality=<MediaModality.TEXT: 'TEXT'>,
  token_count=13
)] thoughts_token_count=309 tool_use_prompt_token_count=None tool_use_prompt_tokens_details=None total_token_count=352 traffic_type=None\
""",
                "total_tokens": 352,
            },
            "messages": [
                UserMessage(
                    content=[Text(text="Answer this question: What is 2 + 2?")]
                ),
                AssistantMessage(
                    content=[
                        Thought(
                            thought="""\
**My Thought Process: Generating a JSON Response for a Simple Addition**

Okay, the user wants "2 + 2" as a JSON response. My first step, as always, is to thoroughly analyze the request and, importantly, the provided JSON schema. I need to make sure I deliver precisely what's expected.

First, I see the core task is a simple addition. Then, I drill down into the schema: "object", with specific properties: `integer_a`, `integer_b`, and `answer`, all integers. These are *required*, so I can't omit any.

Next, I need to map the question to the schema. "2 + 2" means `integer_a` is 2, `integer_b` is also 2, and the `answer` is, of course, 4.

With those mappings done, it's straightforward to construct the JSON:

```json
{
  "integer_a": 2,
  "integer_b": 2,
  "answer": 4
}
```

Now, the final stage is validating the JSON, ensuring it’s correct. It needs to be valid JSON, which is a fundamental requirement. I need to make sure all strings, although not applicable in this case, are double-quoted, there are no comments or control tokens, and there is only a single JSON object. It is, in fact, valid JSON. I'm now ready to generate the final output.


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
**My Thought Process: Generating a JSON Response for a Simple Addition**

Okay, the user wants "2 + 2" as a JSON response. My first step, as always, is to thoroughly analyze the request and, importantly, the provided JSON schema. I need to make sure I deliver precisely what's expected.

First, I see the core task is a simple addition. Then, I drill down into the schema: "object", with specific properties: `integer_a`, `integer_b`, and `answer`, all integers. These are *required*, so I can't omit any.

Next, I need to map the question to the schema. "2 + 2" means `integer_a` is 2, `integer_b` is also 2, and the `answer` is, of course, 4.

With those mappings done, it's straightforward to construct the JSON:

```json
{
  "integer_a": 2,
  "integer_b": 2,
  "answer": 4
}
```

Now, the final stage is validating the JSON, ensuring it’s correct. It needs to be valid JSON, which is a fundamental requirement. I need to make sure all strings, although not applicable in this case, are double-quoted, there are no comments or control tokens, and there is only a single JSON object. It is, in fact, valid JSON. I'm now ready to generate the final output.


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
                                "thought_signature": b"\x12\xe2\x07\n\xdf\x07\x01r\xc8\xda|\xe0\x03\x0f\x1b$\x9aV\xd0\xce\xc3Y\xde0]D<j\xf5]\x04#\xd2\xc5?\xf8\xeb\xd6\xddC\xf8\x9dAs5\"\xd2\x8aK_\x84Y\xec\xe1\xd1\xed\xa1\xf0\x9d&\xd5\x07~\x01\x19\x13\xd1\xfa\x02&O4\xe4&\x8fH\xec4~\xce\x94R(\xaa\xf7\x1e\x08\xb8\xd3`\x0c^~[f\xde0\xb3\xa5Y\xfeS\xa9u\xf0\xe2qS4\xab9\xaf\x11\x98\x1a\x8b\x13\xa9\x9e\x88\xf2\xcf\x1b\xa1$d\x18\xe1\x9a\x115r\xc7\xdfW\xb3\xeb88\xff\xd6\x86\x05\xe6\x17\xdd\xcd\xed\xdc\xd7^\x19S\xa5\x8f\xbdP\x998pC\xd4\xf8\x94\x11\xc89 \x90\xf0\xc7,%Q\x9d\x8d\xfe\xc8\xb8\x1a\xd2g\xbdN\x17,H\x0f\x9c\xe9\xb9j\xb5)\x92\x81\n\x8by\x95\x19\xc5<\x88[\x1a0l\xb1\x92\xc2*\xd3P09\xa8\xe1\x91\x02\xb0Za\xff\xd2_\xfa\xe1\xfe5P\x89\xab\xdaM\x15\x8f\x97\x9c=\x9a[)\x1fe\x92$$\xaf3\xa6\x7f\x8c*\x04q\xcc\xeb\xfb\xd4\xb1k A\xf3\xe05\xfc\x13fBb\xad\x19c^\xccE%\xa6\xfe\xd8Z\xb6\x9bC\x9c\x15\x0c\xa9s\x90&\x9f$\x97\x0e\xfe\xb31<\x0f\xce\xac\xe7\xea\xf8\xd2B\x9d\ng\xef\xdb\x9e\x1aqwo\xad\x9b\xa7E\x9e\xa24\xc3\x84\xb7y\xa62\xfe\x10\xaeh\xd8\xba\xdbF,\x83\xbb\xb7\x84\x00\xab\x96\xd2R\xb0w84\x15\xeb9Q\x1e\x89\x7f*XFi\x9e9?\xf2\x1a\xd6\xf51\xf6\xdb/\xaa\xa1fWv\xfc\x0e\xbesJ\xcdb\x03\x1a\xb6\xf6n\xa7\xe2Y\x7fD)\xc8\xbb\x8bW0\xbd\x8f\x9b\xad4)\xae\xf5\xdaA\x88\x96z\xdeSu\xe0\xcd}\x01\xf0\xcdBU\x92\xde\x8b\xd4\xb1\xbfJ:\xcd\xa1\xbf\xd4\xc2\x08\xe3X\x0b[\x12v\x99\x01\xc4#t\xb5\xabq\x1b\xf8\xc6\x81\x1c\x01\xdf\nF\xabP\xe5\x8c\x7f#'\xcc\x13`\xa8\xce\xcd\x91K\xd2c\xe3~\xfc>\xb9\x18p\xac;\xe8[\xe9*\xa5\xe0\xd6HT\xd2\x8fk\xf1\xff\x99\xf7yq^'\x92\xe6\xb3?\xcc\x84\x95^z\xcb\x16\xbe\x10\xfb\xa9\x95\x08p\x01V\x0f;6\xa3!mR6\x02\xa7E\x9f\x1d{g\xde\x03G\x8b\x16\x91[\x15\xdf\x84\xa7\x88}k<+c(h{\xb1\xeb6>\x81\xd70E\x9b1\xe8)\x83\x90\x94\x1b&\x7f=\xeb\x84\xfe\xd3';T'\xfc\x120\xa0\x1a\x171\x1ezg\xcc\x8c\x17\xa3!e'\x94\xcbb\xe8`\xcawgh\"\x00\x02\xcf\xa8\xca\x1b\x80|MN\xfa\x02=v\x14\x83\xc4\x9a\x0b\x19jpE\xfc\r\xdc\xafGJ\x0f\xd1=;\xf9|\xbc\xea\x06]\x8b9Y\x99\x91\xb8\x85\x86*\x11z\xc5\xf1E\xc4@\x8a<}\x90\xb3\xb3\xde\xeb\xf7gTcO\xab\xca6\xa6\x04\xa5a#\xd8q\xcf\xe4\x94\xd6\x8bA\xb96\"!\xb8|\xb0j\x92\xfd\x9b1\xbb\xf1\x9f\xf0\x1ee\x87V\xd3/b\x07\x01\xf3\xbf\xe0[\xea\"\x8d&c\x99\x9d\x00s\xf6\xfc.:4\xe8A\xb9\x97\xd0[\xff\xbd\xc8\\\xe16gM\xfa\x1e\xb0\xcdt\xed\xe3\xd3\xbc\x1f\xc6\xfb\xf3^\xe2\xdda\xdd\x9e\xb1\xc6\xde\x1fww\x80{ix\xcb\xa4g\xb4\x98\x10<\xae\x11\xe9k8{t\xa8\xf4\x83\x0bcy\xe8\xb5\xdc\xa6=\xd5\x8b\xed\x0c\x9d\xe3\xc5\xd2\xa3\x94w(b%\xe7\r^\xc2[\x88P_`\xf5\x1e\xe0\xd1$\xba+\x9f\x7f\xa4+\xf8-,\xbb\xa2\xd7\x15Z\x82\xc3\xf18\xcf|n\xf8u\xbc\x81\xef\x1e\xefsA\x9bu\x1a\xd2\xf4\xf4\xde\x1dq1O\xf2\xba\xf21\x1b\xdcQ\x05vyk:\xeb6\xceU\xb2m\xe0}\xbb\x89t~(\xef\xfc\xf2\x16\xb9\x86H#\\04Ds\xc6M\xb5\x89A\xbf\xd9\x98I7\xad__\xac\xab\x94\x9c\xa8'\xf5N\xc2\xf8\x8d\x87#\xb1\xd4\x14s\xe7\xb5\\\xd6\xb6\x8d\xb8\x9a\x1d\xfc\xac\xff\x05b\xaf\xc3\xfe\xa6\xa5\x05\xf3\x04\xb6%\r\xdco\xbe\xea\x83\xe7t\\\xc0\x13D\xcd\x1f\x10h\x1a\x14_\xda\x08",
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
