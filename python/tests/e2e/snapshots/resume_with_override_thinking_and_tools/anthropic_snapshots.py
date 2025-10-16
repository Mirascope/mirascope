from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    Thought,
    ToolCall,
    ToolOutput,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-0",
        "params": {"thinking": False},
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="What is the 100th fibonacci number?")]),
            AssistantMessage(
                content=[
                    Thought(
                        thought="""\
**Okay, let's get this done. My thinking is clear here.**

The user wants the 100th Fibonacci number.  The documentation points directly to `default_api.compute_fib`.  That's the function I need to use.  The input argument, `n`, is clearly defined as the desired Fibonacci sequence position.  So, I just need to call `default_api.compute_fib` with `n=100`.  Simple.
"""
                    ),
                    ToolCall(
                        id="google_unknown_tool_id",
                        name="compute_fib",
                        args='{"n": 100}',
                    ),
                ],
                provider="google",
                model_id="gemini-2.5-flash",
                raw_content=[
                    {
                        "video_metadata": None,
                        "thought": True,
                        "inline_data": None,
                        "file_data": None,
                        "thought_signature": None,
                        "code_execution_result": None,
                        "executable_code": None,
                        "function_call": None,
                        "function_response": None,
                        "text": """\
**Okay, let's get this done. My thinking is clear here.**

The user wants the 100th Fibonacci number.  The documentation points directly to `default_api.compute_fib`.  That's the function I need to use.  The input argument, `n`, is clearly defined as the desired Fibonacci sequence position.  So, I just need to call `default_api.compute_fib` with `n=100`.  Simple.
""",
                    },
                    {
                        "video_metadata": None,
                        "thought": None,
                        "inline_data": None,
                        "file_data": None,
                        "thought_signature": b'\n\xe2\x01\x01\xd1\xed\x8ao\xf9\x96e\xc6\x95\x81 \xf2H\xf3%\x0f\xbct\x84\xae!\xc2\xd6\xc1\xa1\xa1F\xa6\xa7\xc8\xe3\xe8\xd5n}\xc4j@\xf2\xa0\xd4\xd2\xae\xadO\x0eE\xeb]\xa6\xaa`\xce\xa6X\x8c\x04\xe9\x92\x9d\x90\x97\xc7\x81l\x84\xed\xd0\xc9\x93\xe0\xf6W\x08_0\r\xb3&^\xdf\xe0\r\xec<Jh\x05\xd9\xed\x0f\x8b\xd7u,\x98\xb3=\x19g\xa5\xe7\xb1\xbc\x88R\xac"<T/;\x89\x02\xf0\xc8\xfe[p\n\x8f\xdd\xc7\xff1\xf9\xad\xf3`\x1a\x05\x03\xd2\x97\x81\x88:*\x87\x8cqrC\xa49\xfe\x0c;g\x15\x17\xb1\xec\x00\xfa0\xb7\xb0\x04]\x94\xcf5\x94tA\x14\x87y\x18a\xa9}\x11\xde]\xdd\xf0q\xe8\xdbR2I\xfb&\x1c\x83\x8ba\xbb-\xbf\x13a\xd6\t\xac\xa2\x80- \xfd\x8fq\xd3;T\x10\xcc[v@\xf3d\xea5W\xe3\xa7\xc4\x0b)\x9ac',
                        "code_execution_result": None,
                        "executable_code": None,
                        "function_call": {
                            "id": None,
                            "args": {"n": 100},
                            "name": "compute_fib",
                        },
                        "function_response": None,
                        "text": None,
                    },
                ],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="google_unknown_tool_id",
                        name="compute_fib",
                        value="218922995834555169026",
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="The 100th Fibonacci number is 218,922,995,834,555,169,026."
                    )
                ],
                provider="anthropic",
                model_id="claude-sonnet-4-0",
                raw_content=[
                    {
                        "citations": None,
                        "text": "The 100th Fibonacci number is 218,922,995,834,555,169,026.",
                        "type": "text",
                    }
                ],
            ),
        ],
        "format": None,
        "tools": [
            {
                "name": "compute_fib",
                "description": "Compute the nth Fibonacci number (1-indexed).",
                "parameters": """\
{
  "properties": {
    "n": {
      "title": "N",
      "type": "integer"
    }
  },
  "required": [
    "n"
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
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-0",
        "params": {"thinking": False},
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="What is the 100th fibonacci number?")]),
            AssistantMessage(
                content=[
                    Thought(
                        thought="""\
**Solving for the Hundredth Fibonacci Number**

Okay, so I see the user wants the 100th Fibonacci number.  That's straightforward.  I remember that we have the `default_api.compute_fib` function available for just this kind of task.  The name itself is pretty self-explanatory.  All I need to do is call that function, setting the input parameter 'n' to 100. Should be quick and easy.
"""
                    ),
                    ToolCall(
                        id="google_unknown_tool_id",
                        name="compute_fib",
                        args='{"n": 100}',
                    ),
                ],
                provider="google",
                model_id="gemini-2.5-flash",
                raw_content=[
                    {
                        "video_metadata": None,
                        "thought": True,
                        "inline_data": None,
                        "file_data": None,
                        "thought_signature": None,
                        "code_execution_result": None,
                        "executable_code": None,
                        "function_call": None,
                        "function_response": None,
                        "text": """\
**Solving for the Hundredth Fibonacci Number**

Okay, so I see the user wants the 100th Fibonacci number.  That's straightforward.  I remember that we have the `default_api.compute_fib` function available for just this kind of task.  The name itself is pretty self-explanatory.  All I need to do is call that function, setting the input parameter 'n' to 100. Should be quick and easy.
""",
                    },
                    {
                        "video_metadata": None,
                        "thought": None,
                        "inline_data": None,
                        "file_data": None,
                        "thought_signature": b'\n\xe2\x01\x01\xd1\xed\x8aoeCI\xe0\xae8\xefo\xea\x9e;\x82+a\x9b@\xd0\x8d\xae\x02\xe1:\xc6x%\x9eR\xf0[\xfew\xe9\xb7\xe8"9\xfd\x96\xd9\xbb\xf2\xff\xa2\x06i-\x0c\x0c\x91\xca\x8b\xa7\xdb\x18\x8a\xf5N^3\xc2\xe6\x02\xb8\x8d\x16\xda\xf1Ex\x05\xd8\xfd\xb55A5\xf9jdoTr\x7f\x0e>T\xd3\xa0\xa7>g\xb3!\x08\xfcM\x8c|w\x89i\xaf\xc4@uc\xcb\xb5\x97 \x9d\xb7QYJ!\xf6T.\x91s\x90\xf9ax\xd2\xdbu\xbdl!\xe6\x97\x1b\x8b\xd3wo\xa6\x8a\rv\x1fd>0s\xc8\x03\x01f\xec\xff\xb7\x9c\xc3\x1aD\xe4\xc6\xa7\x1c\xec\xd0\x8bg2\xf7\xf1\x8dp\x1c\xe7pn\x14\xd8\xf9\xf6q\x17\xb9b\xf3x\xef\x01j\x0fuk(Z\x98+w\xa4 \xefW\xca\xab\xbb\xb8v\xae4e\x06s\x18\xe7#5v`8\x07X\xedV',
                        "code_execution_result": None,
                        "executable_code": None,
                        "function_call": {
                            "id": None,
                            "args": {"n": 100},
                            "name": "compute_fib",
                        },
                        "function_response": None,
                        "text": None,
                    },
                ],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="google_unknown_tool_id",
                        name="compute_fib",
                        value="218922995834555169026",
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
The 100th Fibonacci number is **218,922,995,834,555,169,026**.

This is quite a large number! The Fibonacci sequence grows exponentially, so by the time we reach the 100th term, we're dealing with a 21-digit number.\
"""
                    )
                ],
                provider="anthropic",
                model_id="claude-sonnet-4-0",
                raw_content=[
                    {
                        "citations": None,
                        "text": """\
The 100th Fibonacci number is **218,922,995,834,555,169,026**.

This is quite a large number! The Fibonacci sequence grows exponentially, so by the time we reach the 100th term, we're dealing with a 21-digit number.\
""",
                        "type": "text",
                    }
                ],
            ),
        ],
        "format": None,
        "tools": [
            {
                "name": "compute_fib",
                "description": "Compute the nth Fibonacci number (1-indexed).",
                "parameters": """\
{
  "properties": {
    "n": {
      "title": "N",
      "type": "integer"
    }
  },
  "required": [
    "n"
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
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-0",
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="What is the 100th fibonacci number?")]),
            AssistantMessage(
                content=[
                    Thought(
                        thought="""\
**Calculate the Fibonacci Number**

I've determined that the 100th Fibonacci number can be obtained by calling `_api.compute_fib` with `n=100`. This seems straightforward, and I'm ready to proceed with the calculation using this approach.


"""
                    ),
                    ToolCall(
                        id="google_unknown_tool_id",
                        name="compute_fib",
                        args='{"n": 100}',
                    ),
                ],
                provider="google",
                model_id="gemini-2.5-flash",
                raw_content=[
                    {
                        "video_metadata": None,
                        "thought": True,
                        "inline_data": None,
                        "file_data": None,
                        "thought_signature": None,
                        "code_execution_result": None,
                        "executable_code": None,
                        "function_call": None,
                        "function_response": None,
                        "text": """\
**Calculate the Fibonacci Number**

I've determined that the 100th Fibonacci number can be obtained by calling `_api.compute_fib` with `n=100`. This seems straightforward, and I'm ready to proceed with the calculation using this approach.


""",
                    },
                    {
                        "video_metadata": None,
                        "thought": None,
                        "inline_data": None,
                        "file_data": None,
                        "thought_signature": b"\n$\x01\xd1\xed\x8ao\x8f\x17\x8d\xc7vp-dj\xac0\xf3\xf8\xa7\x15h \xb6\x99\xff\xed\x02U\x85\xa20\xedNJ`\x9f\n]\x01\xd1\xed\x8aoU\xae\x83z\xf7\xf8cF\x06nN\x19\x94Z'\xe4\xab\xa6\xba\xd9\xbe\xfd9=\xc0\x9d\xcb\x89czZ\x91\xf9\x1d\xbe\x9e\xdc\r\x08>\xd7=\xa4\x93\x084\xdd7\x10\x87L\x12?\x9c\xc1\x84G\xb4\xa3\x92\xe2\x0b\x0b\x10\x18\xcb\x11\xd8\xe7\x19',k\x98\xdbt\x1c\xd6}\xb9\x0e\x00\xdbb\x8f\x86\x9f\x8b\n\xa3\x01\x01\xd1\xed\x8ao3\xd0\xc0S\x8a\xaa\xbeH\x0e7\xa6]Bz\x1c\xf1}\x1d)\xcb\x86\xec,\xa1\x83\x1a\xa2\xc8\x16\xcb|d\xd3\x03#\x9e\x8d\xec\xb5n\x11?\x16\xdb~\x88\xbb\xceg5q\xe8\xc2\xcb\xc7\xa7\xcb;\x1b\x84=\xc9\xee\x97]\x8f[\x84\xdbeXkU\xda\xf7{>\xcc\xeay\x92\xb2RJ\x9e\xfb\\\xe5U\xfd\x1c\xe8w\xe4x\x19\xda\xcc\x15\xaah\xdd\xb5\xa5\x95\xec\x16\xb8\xd9?\x8b\xec\xcd\xc6B\xfd\x1f\x12\xcd];\xcd5\xe6\xe0\xe3uk\x02\xfdM\x9a'\xdcQ\x94\x9cdr\xb1\xef\xd9\x91\xe5\rT\x95#\xbf#\x7f:MwO\xc1\xb7j",
                        "code_execution_result": None,
                        "executable_code": None,
                        "function_call": {
                            "id": None,
                            "args": {"n": 100},
                            "name": "compute_fib",
                        },
                        "function_response": None,
                        "text": None,
                    },
                ],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="google_unknown_tool_id",
                        name="compute_fib",
                        value="218922995834555169026",
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="The 100th Fibonacci number is 218,922,995,834,555,169,026."
                    )
                ],
                provider="anthropic",
                model_id="claude-sonnet-4-0",
                raw_content=[],
            ),
        ],
        "format": None,
        "tools": [
            {
                "name": "compute_fib",
                "description": "Compute the nth Fibonacci number (1-indexed).",
                "parameters": """\
{
  "properties": {
    "n": {
      "title": "N",
      "type": "integer"
    }
  },
  "required": [
    "n"
  ],
  "additionalProperties": false,
  "defs": null
}\
""",
                "strict": False,
            }
        ],
        "n_chunks": 5,
    }
)
async_stream_snapshot = snapshot(
    {
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-0",
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="What is the 100th fibonacci number?")]),
            AssistantMessage(
                content=[
                    Thought(
                        thought="""\
**Computing the 100th Fibonacci**

I'm now focused on calculating the 100th Fibonacci number.  The initial plan is straightforward: I intend to directly use the existing `_api.compute_fib` function, passing in `n=100`. This should give me the desired result efficiently.


"""
                    ),
                    ToolCall(
                        id="google_unknown_tool_id",
                        name="compute_fib",
                        args='{"n": 100}',
                    ),
                ],
                provider="google",
                model_id="gemini-2.5-flash",
                raw_content=[
                    {
                        "video_metadata": None,
                        "thought": True,
                        "inline_data": None,
                        "file_data": None,
                        "thought_signature": None,
                        "code_execution_result": None,
                        "executable_code": None,
                        "function_call": None,
                        "function_response": None,
                        "text": """\
**Computing the 100th Fibonacci**

I'm now focused on calculating the 100th Fibonacci number.  The initial plan is straightforward: I intend to directly use the existing `_api.compute_fib` function, passing in `n=100`. This should give me the desired result efficiently.


""",
                    },
                    {
                        "video_metadata": None,
                        "thought": None,
                        "inline_data": None,
                        "file_data": None,
                        "thought_signature": b'\n$\x01\xd1\xed\x8ao\xebl\xd7\xa6}|6\xbc!A\xc0\x8e\xaa\xf8\xc19BS j~\xd8%\xdcB\xf1\x8d\x18\x1c\xc4\xc4\n]\x01\xd1\xed\x8ao\xf3\xf83\xcd:\xe7%\x8f\xdc\xa8\x97)\xe9b\xb6\xc8\x96\xc9\xe1\xcb\xc7\x0b\x8a\xde\xc9L\x8b\xba$\xa5\xccIX$\x16\x95)?3\x9b=J\xfc\xeaq\x8eDs\x87%D"\xedN\xd1_\xa2\xed\xa2\x85\xf1\xbaF\x90\xadK\xfas*,0X\x1bK\x04\x9b\xe4\xdaP\xecqBH\x87\tLC\xcb\n\xa3\x01\x01\xd1\xed\x8ao66SW\xcf\xa4\x06\xd6\xc6\x1f\x92m6\x0c1\x8b\xec! \x95\x12a\xbbS\x92\x8a/"z*\xbd\x81 9c\x01\xa6\xf1\xd81H\xe6\x88\xb6\xf7\xc8E\xb4w\x0f\x14+\x84V\x00%\xea\'\xb6:\xfad$\x18D\x05\x07;\x7f\xc5\xcd\x03`*{\xaa\xd6\x19a"\xdd\xf3jW\x03\xe4\r\xf6\xba\x8a\x14\x85\xc4a4MT\x92\xf7e\x98\xc1\xaaT\xf2\x1e/\xc0I\t\x94\x96ifXc:\xed3\x81\xf3\x80\\\x0e`o\xdc_\xd2a\xf9@\xa2\xb6\x10x>.\xb6\x9eL\x1b=\xa2_\xd1_\xcc\xc1\x92?$\x8fa\xfe\xc6\xe3\xc8',
                        "code_execution_result": None,
                        "executable_code": None,
                        "function_call": {
                            "id": None,
                            "args": {"n": 100},
                            "name": "compute_fib",
                        },
                        "function_response": None,
                        "text": None,
                    },
                ],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="google_unknown_tool_id",
                        name="compute_fib",
                        value="218922995834555169026",
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="The 100th Fibonacci number is 218,922,995,834,555,169,026."
                    )
                ],
                provider="anthropic",
                model_id="claude-sonnet-4-0",
                raw_content=[],
            ),
        ],
        "format": None,
        "tools": [
            {
                "name": "compute_fib",
                "description": "Compute the nth Fibonacci number (1-indexed).",
                "parameters": """\
{
  "properties": {
    "n": {
      "title": "N",
      "type": "integer"
    }
  },
  "required": [
    "n"
  ],
  "additionalProperties": false,
  "defs": null
}\
""",
                "strict": False,
            }
        ],
        "n_chunks": 5,
    }
)
