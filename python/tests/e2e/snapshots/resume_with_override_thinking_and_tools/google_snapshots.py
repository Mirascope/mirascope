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
        "provider": "google",
        "model_id": "gemini-2.5-flash",
        "params": {"thinking": False},
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="What is the 100th fibonacci number?")]),
            AssistantMessage(
                content=[
                    Thought(
                        thought='The user is asking for the 100th Fibonacci number. I have a function called "compute_fib" that can compute the nth Fibonacci number (1-indexed). The user has provided the specific value n=100, so I have all the required parameters to make this function call.'
                    ),
                    ToolCall(
                        id="toolu_01QKtDsUz6YB2zKb1TqWYqkH",
                        name="compute_fib",
                        args='{"n": 100}',
                    ),
                ],
                provider="anthropic",
                model_id="claude-sonnet-4-0",
                raw_content=[
                    {
                        "signature": "EqsDCkYICBgCKkBKiK2f736b6lfckFJzbd/q7SYJmdU2qhn5hvcg4o7ITfIn3EI5eI6rD1VZ41U04M1Sy2QvF+3zw+8YcdKNyefBEgzCU32HaM2EO/dRB9waDG6JBr4KkgsbtPG/TyIw8OO5M3WW/BaykEl/RuQ4zdW17/bXp1vFDz/h436H6aN0iH1IZorgr0Jz40+EEB51KpICJhW/D0vBXrM3yNau9DiuB5G7CMqCdQlMvEFq4QhnzBly5XDI1wM08pzRkKwhUc7tmto8URW+1jm+dhpPs3Slr3dwCLKCfY4RrZSwEqBTXZWIPvZjfNk6Vl8NiHaFwlFcdoXKHtIBF9I3t3I3eWCvAfZvdck+21x6i9ORj7JKEabrmb+b7zkVq+8vGN7QLd6P5K1TqrM8GUyhe4bYcQptS7hHkhV+Ix/g/Z6Xctx0x483CEmFCoorfQQvkrTolGw4hxWAymbX6pHFYMYdidGmjMPYzk30YlNMkYPp0iQKqPqobwalZcLsb/etn67EurLT6cbxtJ3qM8GTlke1d2gi84Ch7HZ77VI0GPgswUnS8cZi1hgB",
                        "thinking": 'The user is asking for the 100th Fibonacci number. I have a function called "compute_fib" that can compute the nth Fibonacci number (1-indexed). The user has provided the specific value n=100, so I have all the required parameters to make this function call.',
                        "type": "thinking",
                    },
                    {
                        "id": "toolu_01QKtDsUz6YB2zKb1TqWYqkH",
                        "input": {"n": 100},
                        "name": "compute_fib",
                        "type": "tool_use",
                    },
                ],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="toolu_01QKtDsUz6YB2zKb1TqWYqkH",
                        name="compute_fib",
                        value="218922995834555169026",
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(text="The 100th fibonacci number is 218922995834555169026.")
                ],
                provider="google",
                model_id="gemini-2.5-flash",
                raw_content=[
                    {
                        "video_metadata": None,
                        "thought": None,
                        "inline_data": None,
                        "file_data": None,
                        "thought_signature": None,
                        "code_execution_result": None,
                        "executable_code": None,
                        "function_call": None,
                        "function_response": None,
                        "text": "The 100th fibonacci number is 218922995834555169026.",
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
        "provider": "google",
        "model_id": "gemini-2.5-flash",
        "params": {"thinking": False},
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="What is the 100th fibonacci number?")]),
            AssistantMessage(
                content=[
                    Thought(
                        thought="""\
The user is asking for the 100th Fibonacci number. I have access to a function called `compute_fib` that can compute the nth Fibonacci number (1-indexed). The function requires one parameter: `n` which should be an integer.

The user has provided the value 100 for n, so I have all the required parameters to make the function call.\
"""
                    ),
                    Text(text="I'll compute the 100th Fibonacci number for you."),
                    ToolCall(
                        id="toolu_012dQkNDrTEsr5exoLQmfWDR",
                        name="compute_fib",
                        args='{"n": 100}',
                    ),
                ],
                provider="anthropic",
                model_id="claude-sonnet-4-0",
                raw_content=[
                    {
                        "signature": "EvUDCkYICBgCKkCBZxhFgNp30I6NhpYniKZIP1v+8TJ7TlF1ECD95gu8AD2D67dsxOswIv/cJdj6PN/92Oemm521NiJ95M8/tr7BEgynB1hBqfwTbKZspZEaDKDTc9M4bHSIh8oFMiIwx0LZEIdCQ+6u/gxDddTS9AfdHE9v4Z0L9/a1tcxEK0AZpc8hs7ZNcl58EjbPHRlUKtwC2wqoB/n1gO6FcIY3I826ShPMS5QG62/VYp+oi921Ix7hOydJ70CtU97tYj0cxMiN/j6GYgnh0VzOgR8RFGtqGw+Ij6gwFX37dE0QgLUvosNWz3pzWaZqCP/tZkj/L8dgr9TTK0rgmy1LK4e3Bb4mEETw1ceUNiQomXAwDZSY4PY04g1IxUCsGKK1IjwPuB5irI/JPXPzkcP47CPDXZdqMFQbgq8ViKZCo/QE+3WtX6HVuaS3hPf/luiwNRPBXhWAifOBHC5yedOQi675usZ1VTd69OmW0C8szr75Tu9+WqlZtKfLYv48Pxx5h7JnqpxCcbLj3p3jUDrbvcrT8Mpzos3PD89fSFWTAbCtth1AbP2Hy82HwmymE1j/A+3RgAqnbCJhbK1UM8GLpAbC6j6N9HHvsHOUa7cmqiJeGZvvvOzMgJjIQ45JQE5t7pgRBe4z0dJ5EPQsUkssZblrGAE=",
                        "thinking": """\
The user is asking for the 100th Fibonacci number. I have access to a function called `compute_fib` that can compute the nth Fibonacci number (1-indexed). The function requires one parameter: `n` which should be an integer.

The user has provided the value 100 for n, so I have all the required parameters to make the function call.\
""",
                        "type": "thinking",
                    },
                    {
                        "citations": None,
                        "text": "I'll compute the 100th Fibonacci number for you.",
                        "type": "text",
                    },
                    {
                        "id": "toolu_012dQkNDrTEsr5exoLQmfWDR",
                        "input": {"n": 100},
                        "name": "compute_fib",
                        "type": "tool_use",
                    },
                ],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="toolu_012dQkNDrTEsr5exoLQmfWDR",
                        name="compute_fib",
                        value="218922995834555169026",
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(text="The 100th Fibonacci number is 218922995834555169026.\n")
                ],
                provider="google",
                model_id="gemini-2.5-flash",
                raw_content=[
                    {
                        "video_metadata": None,
                        "thought": None,
                        "inline_data": None,
                        "file_data": None,
                        "thought_signature": None,
                        "code_execution_result": None,
                        "executable_code": None,
                        "function_call": None,
                        "function_response": None,
                        "text": "The 100th Fibonacci number is 218922995834555169026.\n",
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
        "provider": "google",
        "model_id": "gemini-2.5-flash",
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="What is the 100th fibonacci number?")]),
            AssistantMessage(
                content=[
                    Thought(
                        thought="""\
The user is asking for the 100th Fibonacci number. I have access to a function called `compute_fib` that can compute the nth Fibonacci number (1-indexed). The user has provided all the required parameters - they want the 100th number, so n=100.

Let me call the function with n=100.\
"""
                    ),
                    ToolCall(
                        id="toolu_01S12S7ibmewEgYRGTXPycAc",
                        name="compute_fib",
                        args='{"n": 100}',
                    ),
                ],
                provider="anthropic",
                model_id="claude-sonnet-4-0",
                raw_content=[
                    {
                        "type": "thinking",
                        "thinking": """\
The user is asking for the 100th Fibonacci number. I have access to a function called `compute_fib` that can compute the nth Fibonacci number (1-indexed). The user has provided all the required parameters - they want the 100th number, so n=100.

Let me call the function with n=100.\
""",
                        "signature": "EsQDCkYICBgCKkBasrLs9AGgNE8DpsyJkUarBc47qsuV2vuK5pWOkUp+5n+VrfOAgYxEe/kY/R7jDdrsn0XlflReLvI5we9jtUTYEgx92RF51igHzURrklMaDCCe8nMcphhphDaGiiIw9pi4jeE2uungo5PGuxcyl8mlS+P5LADAFBSGODvQ+MA7GvQmEz+wbqzkRD1TTkMGKqsCmDe+S81RmBmXWtsfBmnj19Xega+6wnfzlQJnQLH38RY8Y9crWwGvwKnsFtB6RtvN0L41094D0BJXnNeoyhHM+l2lrkemTdv35+qquxmKyp42ycp+4MnNMf1V+H/jpS08f/qQYaz0CJrai41d7l/HtP4gmO9C/rCPAFWccbq+27oMp+gq1Q/wAsgEdOm/dR9s4IBTfa0RQOpICv82/a9+E38ZQS2iiWWrDUy2pgrx6+68x6sPVHb5989qtBM+pKv4uJYzVGfK/FeM+mW2Jpe65zD3caCoRChmPp3P0zIksPqtb5Poq1XBDAvfE/lli3tpLoaxYF2vDLnsTviMRJEmyvlNZM2YeINjF/n/3LwuRoVqZGNbrPtPZfx/R9xINYB1XZbVh/aY3/AwregYAQ==",
                    },
                    {
                        "type": "tool_use",
                        "id": "toolu_01S12S7ibmewEgYRGTXPycAc",
                        "name": "compute_fib",
                        "input": {"n": 100},
                    },
                ],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="toolu_01S12S7ibmewEgYRGTXPycAc",
                        name="compute_fib",
                        value="218922995834555169026",
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(text="The 100th fibonacci number is 218922995834555169026.")
                ],
                provider="google",
                model_id="gemini-2.5-flash",
                raw_content=[
                    {
                        "video_metadata": None,
                        "thought": None,
                        "inline_data": None,
                        "file_data": None,
                        "thought_signature": None,
                        "code_execution_result": None,
                        "executable_code": None,
                        "function_call": None,
                        "function_response": None,
                        "text": "The 10",
                    },
                    {
                        "video_metadata": None,
                        "thought": None,
                        "inline_data": None,
                        "file_data": None,
                        "thought_signature": None,
                        "code_execution_result": None,
                        "executable_code": None,
                        "function_call": None,
                        "function_response": None,
                        "text": "0th fibonacci number is 218922995834",
                    },
                    {
                        "video_metadata": None,
                        "thought": None,
                        "inline_data": None,
                        "file_data": None,
                        "thought_signature": None,
                        "code_execution_result": None,
                        "executable_code": None,
                        "function_call": None,
                        "function_response": None,
                        "text": "555169026.",
                    },
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
        "n_chunks": 5,
    }
)
async_stream_snapshot = snapshot(
    {
        "provider": "google",
        "model_id": "gemini-2.5-flash",
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="What is the 100th fibonacci number?")]),
            AssistantMessage(
                content=[
                    Thought(
                        thought='The user is asking for the 100th Fibonacci number. I have a function called "compute_fib" that can compute the nth Fibonacci number (1-indexed). The user wants n=100, so I should call this function with n=100.'
                    ),
                    Text(text="I'll compute the 100th Fibonacci number for you."),
                    ToolCall(
                        id="toolu_01J7hSXkaj2gutTd4eGhfSLs",
                        name="compute_fib",
                        args='{"n": 100}',
                    ),
                ],
                provider="anthropic",
                model_id="claude-sonnet-4-0",
                raw_content=[
                    {
                        "type": "thinking",
                        "thinking": 'The user is asking for the 100th Fibonacci number. I have a function called "compute_fib" that can compute the nth Fibonacci number (1-indexed). The user wants n=100, so I should call this function with n=100.',
                        "signature": "EvsCCkYICBgCKkCrF3A23iWsI9CbuXWKSIczp22RwhvKHeSWO49SB3ya+f3ETvP4hEbr1nf+e4W80I0slNZ+lH6KzQSXmn2XloLuEgwX3AcDDfH0zJvglHMaDLtUwVKUt2wBjH2gZyIwii+BKEgqVIfpMS1wLotcxzV2MeHkkIP3DrYvGenP0aWeoGO6yUcfTi0PlyMDjLDNKuIBkAIP0l/anV3UpvaV4hl0Swuhah9FliaD9cyQ7LCSp2OVPBvbIxTVCCQgSXSYU9wmHBU3tWl93fLRs3kZRQIO1iqz8Qi+SV95ppY2KZcIS+gO2PzWbFX4V6oRqvleXeyBnuk9DiKJePIVF7zkm27/1OKThFQzkL+2IZXihi0sm4K9DBzuRH9Uyfzh03ksHWTtM2eA0V72sspgDycy5444k1q9dm/ivDyRi4z81453NkiXlMRQQjycsoBg7XIdxuP+P0y85BuZ/cEnLWx6qASAB8lTJXePJXT3EMkR6pq5onzPORgB",
                    },
                    {
                        "type": "text",
                        "text": "I'll compute the 100th Fibonacci number for you.",
                    },
                    {
                        "type": "tool_use",
                        "id": "toolu_01J7hSXkaj2gutTd4eGhfSLs",
                        "name": "compute_fib",
                        "input": {"n": 100},
                    },
                ],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="toolu_01J7hSXkaj2gutTd4eGhfSLs",
                        name="compute_fib",
                        value="218922995834555169026",
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(text="The 100th Fibonacci number is 218922995834555169026.\n")
                ],
                provider="google",
                model_id="gemini-2.5-flash",
                raw_content=[
                    {
                        "video_metadata": None,
                        "thought": None,
                        "inline_data": None,
                        "file_data": None,
                        "thought_signature": None,
                        "code_execution_result": None,
                        "executable_code": None,
                        "function_call": None,
                        "function_response": None,
                        "text": "The 10",
                    },
                    {
                        "video_metadata": None,
                        "thought": None,
                        "inline_data": None,
                        "file_data": None,
                        "thought_signature": None,
                        "code_execution_result": None,
                        "executable_code": None,
                        "function_call": None,
                        "function_response": None,
                        "text": "0th Fibonacci number is 2189229958",
                    },
                    {
                        "video_metadata": None,
                        "thought": None,
                        "inline_data": None,
                        "file_data": None,
                        "thought_signature": None,
                        "code_execution_result": None,
                        "executable_code": None,
                        "function_call": None,
                        "function_response": None,
                        "text": "34555169026.\n",
                    },
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
        "n_chunks": 5,
    }
)
