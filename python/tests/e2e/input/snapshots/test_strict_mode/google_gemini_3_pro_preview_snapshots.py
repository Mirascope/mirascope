from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
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
                "input_tokens": 13,
                "output_tokens": 218,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 188,
                "raw": """\
cache_tokens_details=None cached_content_token_count=None candidates_token_count=30 candidates_tokens_details=None prompt_token_count=13 prompt_tokens_details=[ModalityTokenCount(
  modality=<MediaModality.TEXT: 'TEXT'>,
  token_count=13
)] thoughts_token_count=188 tool_use_prompt_token_count=None tool_use_prompt_tokens_details=None total_token_count=231 traffic_type=None\
""",
                "total_tokens": 231,
            },
            "messages": [
                UserMessage(
                    content=[Text(text="Answer this question: What is 2 + 2?")]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
{
  "integer_a": 2,
  "integer_b": 2,
  "answer": 4
}\
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
  "integer_b": 2,
  "answer": 4
}\
""",
                                "thought": None,
                                "thought_signature": b"\x12\xbf\x04\n\xbc\x04\x01r\xc8\xda|\xc0}\xc4\xfe\xe1ED\xcf<K)J\xc3\xc9vu\r\xd1\x1eSAG[\xe5\xc4\xa51_\xb8\xed\x86\xb3\x83`\x0eB\x84]\xb0.\x02`\x14[\xb8\xef\xa9\x8e\x9aUq\x8e\xc9h(}\x96,\xd7\xc66]\x8d;\x84\x1a\xd8\xbd\xbb}\xd4\x0b$^\x14\xa4\x1c\x1a\xecr\x85H\x11\xefn\x81\xf1\xdcf\xc4x\xf3\x18J\x89\x82\xc11|\x83\x1d\x94\x84M\xae@\xd8\xf7\xf2\x06\xd1\xf4\xf5\xc5@\xe9\x88X\x02 \\\x96\xd5\xda\xd6\x7fr\xaa{\xf6N\xcd0\xc5\x15V\x12\xb5\xb319Yr\x95l`\x7f\xe2\xc4\x05\xeb\xffn-\x14-oBA\xcc\x1a\xc55j\xcbR\x9cN\x13[\xb2\x93\x16\xea\xd0\xba\xb4\x08B\xbe\xc0\xf3\xe03\x9bU+\x95\x8b\xe7C\xd5\xb9\x87\x15\xb4R\x18@/\x86\xeb;\x08W\xa3\xd1\xce\xc6:a\xea\x8d8\x17\xf0\x94\\l3\x97\x85\xc0JNB\x12O#{\xa8Yj\x1b\xa9\x02\xb7'\x9e\xd2\xf2\xef\x89\x94\xc4\x87\x023\x8c\x87]\xa5\xcaM\xd6M\xb1P\xf8\x8aT\xfbo\xb8\xe9\xb8u\x86/\x99\xed!\x10\xd6\xdf2\xc3\x8c\xc3\x90\xdac\x12\x8b[;\xa7&\x16\x97\xb5zV\x8f'&\x97e\xa4\xe1\x80\xaelr2\x95\x94\xc2\x11A\xb4\xf6\xf7m\x12\x1a\x9c\xba\xe0\x08\x15~\x15\xe1\x04\x15l\xb2\xf1\xd1\xa3\xc0\x1fT\xa7*K\x06\xf2\xe3\xdaIN,\t\xcf\x91\xb3\xd4*\xef\x93]#\xc3\xf7\x1d\xc5\xb1\x96-=V]\x9b\xce\xbb\x9b\xe7\x13\xcdi)\xcf\xc6\xda\x022Bn\x83\xf9\xd5w\x04X0\xccR\xed\xf4o\x91,Q\xb3\xfe\xadxtL.#\xa3D\xae\xa9\x00\x87\xc3\xba\x11\xee@\x86i\xf7^L\xf7\xf8\xb8\x1c\xa3w\xe8\xc6n\xffh\xbe)\x9e\x0f\xd1\xd3\x93\x89W\ry\x81\x9bh h\xaf\xc3\x9e9\xd8\xcd:\x01@\x8a\xc5\xa0\xfe\xd4\xbf\x851I\x9b\x99\xff\xca\x19\x92;^B\xea\x1b-:\x1d\xfdu}@\xd3\xe8\x93>\x11\xfc@\xcb\x06{\xec\xc6\xee\xf8\xfc\x83\xc3u&\xc0\x17\xcd\xa2\xdf\xd7\xe5\xc3\x08\xdd\xaam\x81\xe3\x15\xa1z\xb4\xec5\x1b\xecV\\\xfec\x8f\xd9!:W\x85(\xe0\xd4\xc9\x05\xcb\x93mZkd\x8a\x98\x82\xc95\x8c\x99s\xe4\xd8\x85\x81\xdc \xf4\xd4+,\xf8\x9f\x919\\",
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
            "tools": [],
        }
    }
)
