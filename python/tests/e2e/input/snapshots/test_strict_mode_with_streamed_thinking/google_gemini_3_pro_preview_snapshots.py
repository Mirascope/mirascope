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
            "provider_model_name": "gemini-3-pro-preview",
            "model_id": "google/gemini-3-pro-preview",
            "finish_reason": None,
            "messages": [
                UserMessage(
                    content=[Text(text="Answer this question: What is 2 + 2?")]
                ),
                AssistantMessage(
                    content=[
                        Thought(
                            thought="""\
**Assessing the Schema**

I'm currently focused on the schema provided. I understand the user requires an object with an "integer_result" property. I've grasped the need to structure my response to precisely match the user's defined output format. I'm contemplating how to generate the correct JSON format.


**Finalizing the Output**

I've moved through the steps: mapping the request, constructing the JSON, and verifying its integrity. It seems I'm prepared to generate the final, valid JSON string, ready for output. The process of constructing and validating the JSON confirms that it aligns with the requested schema. All checks have passed.


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
**Assessing the Schema**

I'm currently focused on the schema provided. I understand the user requires an object with an "integer_result" property. I've grasped the need to structure my response to precisely match the user's defined output format. I'm contemplating how to generate the correct JSON format.


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
**Finalizing the Output**

I've moved through the steps: mapping the request, constructing the JSON, and verifying its integrity. It seems I'm prepared to generate the final, valid JSON string, ready for output. The process of constructing and validating the JSON confirms that it aligns with the requested schema. All checks have passed.


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
                                "thought_signature": b"\x12\xae\x08\n\xab\x08\x01r\xc8\xda|\xb2\xe4\xf7e\xddqp-\xe4R\xab?\x89\x8c\x9e|\xbaNs\x10r3\xdc\xdd\x92\xcfb}\xcf\x9f*\x86\x0b`FhdXS\x9fD:n\xa8d\x1b\xd9\xf2\xf3\xb6Y@I\x8e\x85\xddd\x1d\x10\xcb\xc9e\xe1v\xc7\xef\xc6\xc7\xf8\xac\xf8W\xe5a\xe4\xec]_:\x19\x1f\xad\xcfB\xc7f\xef\xdd\xb1\xc2\xf4u\xb6\xa2\xcc\xcc\xa7\xe7\xc6\xdf_\xbbyC`j\xb5N\xab\xfd\xc8\x11\x02L&X\x87\x1bw\xeeB\x98Z\x0eW\xffb\xd5\xe0\xe3CPd\\w\x01\xa4\xc5G\xb6K\xb1/\xd6N4\x1e\xd5u7C\xb3\x13\x15S5z\xd3\xd4\xa2-7?\x9e|\x87\xf3q\xc5\xe8\x03\x97\xb7\xe1\xa3\xd2\x0b\xd1.\x9e\x87c*\x19\xf2\xe1q^/\x83\xab_DB\x85\xaf^]\x97\x1f\xe5_\xe5\xb9+'\xd1\xad\x01d0\xdc<\x1a\xd6\x16e\xbb\x9f\xafa\xb4w,:?\xf3\xbex\xf26Q1\xa1\r\xb3\x9c\xba\xe8\xcai)m\x91(Aj\xfa\xbb\xd8\x879W0z\x87\xd7n\xb1w\x14P<\xe0\xa4\xbe\xee\xdf\xe1]\xd3\x8d,W\x8b\x91\x1d\xbdg\xa4C\xed*\x98\xb6r\x9b7\x1a\xa4I\xd4\xf39\x9e$:\xe7\x0c{\xea\x112U\xc3=1\xa1\xf4\xdb\xc2r\xd4f]\xcbKY\xce\xda\x1d>\xa6\x04\x89R\x96?\x17Y\xf4\xb6\xd1\xe6?\xbao\xaf\xfcb\x0b\xb5\x11\x92\x84\xcaw\x01\xce\x9a\x161\xd5\t$q\xaf\x9a\xd0Y\xe1,\xf1\xd6\xf3\x95w\x02r\x1c\xe7\xe5[\x17\x81\x96R\xa1\xc0\xd7\x90H\xe6\x10\x03\xa2\xca\xaf/rF\xbe\x83H\xb9\r\xa5y\xa4\xde\xf6\x9b\xd3\x05\x83\xb9-\x17\xc51\xe9\xde\xdc?qL2\xaf\xfaqf`\xc6\x8b\xb4\xa0|\x9f\xc9&r\xbb\xc4[\xcf\xa7\xf1\xe4:\x1eo\x82\xb5\x99x\x12\x1e\xa2#~Qzm\x88o\x90\xe6\xe8x\xb7\xca\x15\xff\x8e\xf2\x87\xdf\xa3!\x13\xfe>,x\xb7\x13\xf3\x93\x16\xc6{<\xbd\xdf\xd0\x81$\xd6\xbc\xf0\xb1\xday\xe2\xa4\xf4\xd3U|h\xc2W\r\xc5p\xbf\xd6sM~h\xc5y\xe8\x13\x88y\xc0\x85\x063z\x8d\x97\x84\n\x0c\xbcA\xe5pOn\xe1x\x93\xce6\x10\x12V\xf4Z//\x17\xe9EO\xd3\xb1\xc9o;\xe6xy\xba\xbe6`\xcad\xf6\xb9F~l_\xe4\xa8\xc4\xd1\xa6P\x89\xc3\x06\xc1\xa8<\x96r\x9a\xb0\xbe\xd2<\x00e\xe3\xf5\x89h.\xccA\xd2iU\xff}\xf6LTC\xd4P\xeb\xc3\x9f\xc4y\xbc\x92\xfc\x95l\x86\x0b9\x8c6k\xc1\xa5\xe3\x13\xfei^\xda2`Xl\xa9\x17\x9a\xd7v\x95a\x8fl\xd7\x94B\x9c\xc2y\x96\xa7\xff\x12Ni\xcc\xad\xb8\xdb\x0f8\xb3-\xe5\x18\xc3H\xaa\xe8\xc2;i\x8e~\x9a\xed\x07-\x8e\xca\x87\x93\x08\x83\xdf\xceQ\x00Q\xfd\x90\xd9\x8e}d\xaej\x87&\xfe'\x0f\x82\xd4\xfd\xe3\x11\xe4\xba\x99j-\xf4L|>\x94\x9f\td\x1d\n\xef\x02;(d\xcb\xb7\xa6d$l\xe0:\xc4C'\xe7\nG\xa4|2\xc0\xb84\xa9\xc34\xc2\xe8qO\tE!\x11\xae\x00{y\xce\x82\xcao\x98}\xf1=x\x11\xb8\x99\x16\xfbK\tz\x06%\xa4\xac\xec\x91\xcc\xf2\x949\xda\xa2\x0f\xba\xf4\xcf\xfdR\xfc\xe4\xca\xd7\x03\x82\x8b;u\xf6!g\xcbL\xa9\x85\xec-q%4\xa1v)a\x11\xf7\x9b\xda\x9b\xce\x85\x17\x96 \xe5\x08\x99J\x85h\xbd0_\x83N-\t\x93\xeb\xc6\xb9\xa8\xebn\xfa\x8c-\x1ap\x08\xd3W\xaa\xe0Z\xc0e\xcb\xbd\x94\x9c\x9d\x13\x11\xacz\xbcjI\x07\xf5j\xab^\x811%s\x15N\xc5\xa1\xcfM\x89\xf0\x94\xdeo\xd1>/,{8\xb2\xf3\xb1\xb2\xe9\xf3\xfe\xd4\xb4\xb4\xa4B\xcd\x0e\t\xe8\xf7\xa7\x81\x8a\x9c\x87\xb25E|+\"\x1a\x94\xee]{N\xc5\xd7\t\xc5H/\x87\x11s.b\xaeE\xc5H\xad%\xe4\x8bx\xaak\xcc\x08\xbf\"\x8cjYP'p_\x99\xd5A)'\xdc\xd3=\t\x8d\x11\xfd\t\xcbH\xec;\xd7n%\xf3'\xfa$\xe6jp\x98\xe9%\xba7\xbc\xd2b\xd6\xcao\xfa\x12\x9f\x9e\xae\xf25Lw\xdc\x9e\x0cD\x14\x9c!9\xbeY'\xfc\xc2\xe5T\xb8C+\xd8m\xbc.\x04;\xee.A\x8d}\x81\x10\xdf\xcd\xe1D\"\xe5x\xbb\xc3U\xebl",
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
                "reasoning_tokens": 273,
                "raw": "None",
                "total_tokens": 43,
            },
            "n_chunks": 7,
        }
    }
)
