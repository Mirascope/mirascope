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
                raw_content=[],
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
                raw_content=[],
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
