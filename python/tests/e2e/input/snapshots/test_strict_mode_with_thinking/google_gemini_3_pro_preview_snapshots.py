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
            "params": {"thinking": {"level": "medium"}},
            "finish_reason": None,
            "usage": {
                "input_tokens": 13,
                "output_tokens": 307,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 280,
                "provider_tool_usage": None,
                "raw": """\
cache_tokens_details=None cached_content_token_count=None candidates_token_count=27 candidates_tokens_details=None prompt_token_count=13 prompt_tokens_details=[ModalityTokenCount(
  modality=<MediaModality.TEXT: 'TEXT'>,
  token_count=13
)] thoughts_token_count=280 tool_use_prompt_token_count=None tool_use_prompt_tokens_details=None total_token_count=320 traffic_type=None\
""",
                "total_tokens": 320,
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
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
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
                                "thought_signature": b"\x12\xc4\x07\n\xc1\x07\x01r\xc8\xda|C\x98W\x0c\xe2\xc3| kO\xc6\x8b\x95\xf0\xe9\x06\xca\xdaG\xad\xfe\xe0v\xe9\x83\x13\xbb\xc4\xf1RC\xd3w\xe2\xd9\xecx*;\xcd\x06\x93\x87\x1cK\x0b\x0bF\xa9\xa3\xcaz^N\"G\x81I\x8bO\xec\xf4\xca\\\x87\x96\xd5m\xc7}?\x95l\x13w\xcb)c<\x87K\xcc\xe5\x95\xce\x19\xa7.\xd6\xc1\x05\xb2#\xb7R\xfe\xfb\xc1\x869\xb7\x9f\xcf\x05\x1cv\xc6\xf6\x8d\xf6\xec\x06w\xc5\x17\xe0,\xa7\x88'\xc5\xca\xcb\xc9\xa6\x10.\x9f\x7f\xcc\xb3\x91\x11 \x9d\xce\xee\xe7[\x82\x1d\xe5\x83\xe7D!\xdb\x1f\xb4+\x1e\xd4\x98gt=RC\xde\x00\xdfc\xcc\xdeG}\xa7L\xd3\x87jB\xe2u\r\x94\xe3\x14\x08\xfe@\x13\xda\xcb\xaa\x18\x0e\xcd\xcf-\r\x87\xb1\xe6)\xf5\xf2\x9a\xc1E\xbd\x9f\xcdIN\xee\xdd\xff)\x81\xb91\x96K@\xe4\xe8\\\xf5\x86\xbc\x0f\x16\xf5\xc2\xfe\xf1\x11\x9d\x05o\xa26C\x81\xf4\xe8BEk\x1b\xd8\xa5mg\xf6\xbb\x1e)R\x92\xa4\xbe\xc3\x02\xd9p\xd9\xb3ijBQs\n\x03\xb6\x0c\xed\xd8?\xe26\xeb\xc4N\x1cQ\x85\xedd\xfbO\x18\xd8\xae+\xaab\x0fd\"\xff\xc48D\xd1\xfa\xda6\x9d\x91\xec\x16z\x8b\xef_iD\xfbQ\xe0~\x15\xac\x87\x82\xbe\xbaa\xd9\xc0\xe0\x83}a\xb9\xb5\xa7w\xc5\xb0\x01d\xfe\xd0HO\x7f\x0c\xf9-\x1b\xa1g%\x10\x90\xe7\x04\xd3\"\n\xe1\xdc\xb87[\xde\xce\xcd\x90e\xa9\x89\x91I)\xe4\x8e\xc6>\x1bb\xf8\x8e\xcc2\xfd\xe8\x85\x02\xbe\xeas\xa1\xd5\x0c\xb8Ok,\xdb,n\x8eR3&-\xe6\xfb\x9d\xbf\xaa\xf5w\xf8\xa27O\x0b_\xf2\xec\xedd\x01\xf7,O\xe1\x8a\x12Xn\xd5\x84\x07\xc92k\x81\x9ez\xb8H<\x94u*uLlb\xfar\xe7\x18:\xc3,\xe5J\x0f\xe7\xa0\xda\x06x\x10d\xdb\xab\x8e\xbb\xe5#\xae/\xf0\xd5\x16%T\x84\x04W\x89L\xed5\xe8\xda\xd2\xdf<\x0ek\xd7\xee\xa7\xd1\xef\x02\xdaA\xdc\x8d\xad\xf1\x1d'@\x1c\x16v\xa9\xeeo\xd8\x03\xe0\xd0\x89\xc5\xff\x1b\xb2\xa7\x16\x06\xa0\xb7\x00\xf6{\xe1o\x97\x02\xe4U7sw\xe6\xb2\"\xd5/\x9d\xbf\xc8\x05uE\xfap\x9d_\xd2L\x8a\xda\x8a\xf6]\xf6\x81\xed&\x03\xfc\x83\xde\x83\x9dM;\x03\x01\xa7=\x04\x19P\n\n\xda\xf5f\x95\xe4\x8b>\xba3\xa3\xd4\x0f\x12\rJ)\x11 \xe8\xce\x98J\x1a\x1e\xbf\x9f+\xe9\x95\xd1\xd6u\x94\xda\x0f\x00\xe3\x11\x9e\xebUjBoz\xe9\xbc\x81a\xae\x03\xab\xa13ab*'\xaf\x99\x8b\x96O\xa7\xdc\xca\xd7\xb0\xd0b<\xd51\xf2\xe1[R\xc7#\x11^/.\xf8\xff\xacHxEZeE\xe3\xa6\xa1?\xb8|C\xdf7'\x9c\xa5\xd2\xd7\x06>J\xd4\x80\xcax\x0bDxp\xf8\xfcTyH\x82\xf0U\x11_\xe6H\x87\n\xb6e\xd4\x9aN\x1b\xd5\xb5Mh\xe2Ai\xb0\x86\x17\x8f\xe02\x9b\x83\xff#\xd1/8k\xf8\xf3&I\xa23\xcd\xe0\xedwc\x17\xbd\xbcK\x9bTN-%\xf3!\xa0\xf5>\xb1\x03\xcf\x8eN\x7f!\x15\xa6\xaaa\x91S\xff\xde\xd1\xb6 \x03Q\xb0\xbd\xf95\xd5\x946\xb772\x1b\xbd\xad0\x12\xb9\xa9Z\xff\x18\x07\x17\xd7\xa1\xbb\xc3\x03w\x84\xee\x9f\x8aQ\x04\\5\x0fq-!\x9e\xeb\x1c\xa93\x9d\x0f\xc6\x14\xc8T\x82k\xef\xe81^T\x1c\x8a\xa8\x87t\xd7.a\x9b\x1a\x11\x1f\x8a\xb2\xf6\x0c\x07\x1a\xf0\xa4p\x8b\xa3\xd6\x97\\\x13\xb8\x03\x9b,\xc1\xf7\xe3\x90,\xaa\xe0\x06=\x0b\x059\x1d\x81\xd2\xf4\xe4~p\xec9y\xd3`x\xda\xf4\x87\xab\xd5\r\xf4c\x93\xb0\xaa\xa2\xda\xb7\xb4\xe6\x1c*\xd0\x1f\xe6\xd2\xdc\xc5\x04i\xe7\xb3y\xb00\x17\x979\x9fM\x8d\xb9\xdbYW\x12+\x06\x12\t\xca\xf7x\xcf\xb9\xbd\xd4\x18\n\x05\xc1\xdb\xbc",
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
