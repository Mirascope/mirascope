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
            "finish_reason": None,
            "messages": [
                UserMessage(
                    content=[Text(text="Answer this question: What is 2 + 2?")]
                ),
                AssistantMessage(
                    content=[
                        Thought(
                            thought="""\
**Processing the Input**

I'm currently focused on the initial request. I've dissected the prompt and the accompanying JSON schema. I'm prioritizing understanding the expected output format, specifically the required object structure with its `integer_a` property. This groundwork is crucial for a correct response. I'm ready to move into actually calculating now.


**Calculating the Response**

I've completed mapping the request to the schema. I've determined that the first operand, `integer_a`, is 2, and the second operand, `integer_b`, is also 2. The anticipated `answer` is 4. I've constructed a JSON object using these values and validated it against the provided constraints. Now, the final JSON string is ready for output.


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
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": """\
**Processing the Input**

I'm currently focused on the initial request. I've dissected the prompt and the accompanying JSON schema. I'm prioritizing understanding the expected output format, specifically the required object structure with its `integer_a` property. This groundwork is crucial for a correct response. I'm ready to move into actually calculating now.


""",
                                "thought": True,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": """\
**Calculating the Response**

I've completed mapping the request to the schema. I've determined that the first operand, `integer_a`, is 2, and the second operand, `integer_b`, is also 2. The anticipated `answer` is 4. I've constructed a JSON object using these values and validated it against the provided constraints. Now, the final JSON string is ready for output.


""",
                                "thought": True,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
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
  \
""",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": """\
"answer": 4
}\
""",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": "",
                                "thought": None,
                                "thought_signature": b'\x12\xd4\t\n\xd1\t\x01r\xc8\xda|\xc7\xf6\xda\xc2\xb7\x9bh\xd5\xcb\xe2>\xefI\x05\x15\x01@\xc10s-\xda\xdb\x00>\x8c\x85\x9e*^d\x07\x1a\xc9\xfb\x8aZ\x10L1\x88\x7f\xb9\xde\xba\xe1\xa2\x89oa\xff1?< \xea\xa3\x95<O\x85l\xa5\x1fC\x0c\xc2\x87\x00\xf0\xb1\xcd\x80\xf0M\xbf\xea\x8bP5\x18\xac\xcc\xbb\x10\xc5F\xc1#\xf8`\xe6\xb2\xba\x8da\x18{\xde6$\xf0\xac\x9e4\xe6)\x9d\\[\xf7D\xdco\xd5\x08\\\x99\x1f\x14W\xcf\x86\xff\x94\x06n\xa7\xc42\x03\x183\x049\xc4\xa8!%\xf5\x01?\x07\xa0\xe7\xdb\xaa#\xee\xe3\x98\x7fM\xba\x85o\r\x01\x95\xf6\xed\x81\xbc`\x1a\xcc\x0e\xe8\x00\x8b\xdc\xb1\xccgSY\x11\xa9\x9eD.rV\x10\n1\xa7\xecL^#9\x8cK\x02\x8d{\xea\xc0\'he*\xf8L%7\xd9~\x10LcV\xd5\xc6\xce`d\x9f\xb1`6k\xb8\xe2Q\xba\xe4\xea\xd6\\M\xcd\xd7\x1a\xc5\xcb\x10\x01\xf2\xad\xec\x01V\xf4\x1a\xd0\xf4\xee\xba\xd11;\xb3\xda\x8cD\xcb1g\xbcg\xd0\xd8W\x07\x86\xedB_s\xe8\xc6!\x81\x8a\\x7\x13\xe6o\x89Ij?\x11F\xb7\xd4\xe1\x96e\xd2\xec\xd2LZ1\x94\xd1v2ytp\x9b.\xc3\xe5\x83\xd9\xb7\x13p\x97"\x9b>\x83\x9b\'\xc8Z\xae\xa7\x9di\xcb\xe9K?\x19\xdd\xa1\xe9!\xc3\xb3\xb9\x83Sw!\xfcO\xdd\xf9\xe0)\xcf\x03\xff\xdd\xc1?\xd3\x89G\xb8\xa8\xd7>\xa1\xd3\xadD7*\x82\x1bn\xbaD\xe8q\xd5\xd1+)d\xe3\xf4D"I\xb6N\'\xa9.&z\xf7\xc0DS\x08\xefA\xfeo\x01\xb1\x17U\x93@\xbb\x13\xd6\xe4M\xc6\xae\x1b\x9a\xa9\x9fm\xba1\xd0e\xf4\xc0\x16\x16\x98\xc2\x02\xe2S\x86\xfa]h\x95\xd7\x1e\x9b\xf7\xf1U\xe1o\xdb\xbe\x18\n\xe3\xf8\xad\x88&P\xdc"Z1\x19\xda\xe6v\x1d\x10\x9cO\xa8q%\xf80\x1e5A\x88\xbf\x85\t\x08\xfb\xbb\x0e\xb3\xe6\xa4\x9d\xcb\x1b\x97\x1f\xac#k\xb8\x92VA\xe8\x95\x99\xd8\n\xde\xceE\xee\x04\nw.;\x07K\xd5\x8aoL\xf4\xe7\x19+\xf7U}\x902\xe6w\xca\xafYcT\xd2\x8e)\x92\xca-\x90\xd1\xd7\xea4Vt\xf5&\xb7S5,m\xf8\xc0\xc0pK\x8f\xee\xe1\xfbXDL\xdc`\x15\x87T\xc4\\\x0b\x03=\xa7%T\x03e\x94\xae\x9ej\x12\xd0z\xd1\x11/\xd0\xe5\xa5\xd8D\x15\xaa%\xabV\x92\xc3\x07+!\xa9\xd3\xac\xdb\xca\x9a@/q\xa6l)\x01t\xd4\x18\x1cL/\xb1Aa\x00\x87\x96tU\xf8eB\xc4\xb5\x06\x1b\x9f#\x14W\xd8\x80\xfd\xc3\x97\xf9(\xb4M\xe4Z9\x9b\x87\xe3C\xf9\xe3\xd6s\xb7\x10@\xc1^\xfbYw\xfc^/6&E\xe6\xe1@\xaa\xa1\\\xbe*:\x05\x12\x82\xb4\xf5\xc1\xaa\xa1\xab\xd4o\x14K$\xa2\xb5\xe3\xa4\xba\x02a\x89\x0e\xcb\xc0\xfdd#:$\x14\x8e\xb9\xa5\x1b\xc1\x0b]YS\x94\xa2$\x7f\x14_\xb8\xbd$\x9e\x8e\xd3\x0b\xdb}\xc0s\x7f\xee\xc5\xc4\xed\x91\xf3\xe4\x82pH\x9f\xb58BS<\xd2\xf3\xc7\x10\xdd-\xae\xfb\xd8T\xad\xbdc\x0cHB8\x02\x97O(\xac\x02\xc6\xf2\xb7\xc6\xd5\x06\xfatZIDE\xc5]\x8e_\xc4%@\x06\xde7\x92IR\x03\xb0\xc6\xa2c\xb9~X0\xb5\xbaZ\xe3\n\x9d\x8fC^-\x9b\xdc\x1a\xa1\xccP/l\x8f%\x91x\x0c(\x18/#z\xe3\x04W\x8d\x8fq\xd6L\x1f<&v\xbc\x83!]\xf80\x81\x97\xe96/|\xa8\x8b\xb6\xd9\x10\x06\x06\xd6\xd3"\x95\xfc\xa66(c\xd7t\x17h\r\xce\xd5\x0e\xc4\x03\xb8\xc4 \xf7U\xd8,]Z0\xf2+@\xb6\xd2\xab\x80\x8c\xb3\xf2\xf6\xbe\xf4h4\xfc\x8b\xdfI\x88\xcb\x82\xed\xdf*\xf3\xa5\x1e\xe4\x17\xc8\xa5$\x1f\x00\xa1\xfa4\xd8X\xd4\xdb\x89\x9c/,\xc3\x01kF\x15\xf9=\xf9\xbc=@\\"\xdb\x13\x0f\xc5\xac8\x0e\xde\rUb\x14:\xfc\xd8\x9f4\n\r\xd9\x06\r\x1c\xb1\x87\xa1>P\x87\xaf\xcc\x8cP\x91\x1f\xc88\x95\x04\x12>\xa2\x96\xe9\x8d/\x85\xa5\x9eI\xcee\xafN\xb3M\x825n\x16.\x9d\xdf\x16q)V\x00\xeaZ\xfb\x95\x96\xfb\xe8\xd9$\xdfsy\x85+Q\x12\xb10\xc0!:\x8b\x11\x06\xe0\x13!\x18?\x92r\x01\xf5\x8a\x7fw\x80\xad\xc3\n\x13\xffw\xaf\xcfT\x1ccN\xc3\xb72\xb3\x12\xf4\xd1\\t\xe6\xec`KV\x80\xe2\x99S$i*\x94\xa7?G\x1bkJ\xc8\xca(\xbd\xf3\xdc\xf4\x08\nP\x11\x88t$E\xcefs\xdd#\xa2A\xf3\x10&9\xe2A\xe3$k\xbd\xf5r\x8fT\xae=G\xaa\xe6\x1c\x9e-\xcc\xe9\xa1hP\xa7\xb8\xe6\x9d!\x19d\x10\x9b\xc9\x87Ln|\x00\xf9e\xd2\x99\x9f+c\xf6U\n\xc3,ngu\x1f\xd7\xa76\xc7\xe4\xfd\x1d\xe5\x8e\x9a\xe6\x1b#\x83z\xaa\x0b\x81\xf8\xc0\xbd\xa9:t\x03r\xcf\x0f\xad\x8bvI\x97\xbc\xbdW\x9d',
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
            "usage": {
                "input_tokens": 13,
                "output_tokens": 30,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 308,
                "raw": "None",
                "total_tokens": 43,
            },
            "n_chunks": 8,
        }
    }
)
