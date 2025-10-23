from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    Thought,
    ToolCall,
    ToolOutput,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider": "anthropic-bedrock",
            "model_id": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
            "params": {"thinking": False},
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="What is the 100th fibonacci number?")]),
                AssistantMessage(
                    content=[
                        Thought(
                            thought="The user is asking for the 100th Fibonacci number. I have a function called `compute_fib` that can compute the nth Fibonacci number (1-indexed). The user has provided the specific value n=100, so I have all the required parameters to make this function call."
                        ),
                        Text(text="I'll compute the 100th Fibonacci number for you."),
                        ToolCall(
                            id="toolu_015gzCmZHkowWCdiXYiocCNb",
                            name="compute_fib",
                            args='{"n": 100}',
                        ),
                    ],
                    provider="anthropic",
                    model_id="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "signature": "EqsDCkYICBgCKkDos1duYpOOoqSDWciv4pxxGTvAw4fOmR1KfvS8FNDS6GurRcDcxfSjsVPXODaO2GTmPC/dmW6NxsDuTnZihLPdEgx+aEgKqy6dqPGkSP0aDG5+ILoN4Xzrrv9dxiIwyqwSveT6sG6BZIo8jYdXCSLC0ScjWY9/DU7PkN58OCOW10bvgRRAK41/qyNuoLW1KpIClGyRL+lyVfKzXBu0aSiit84EKxl87iLlwoMUmM9haZAI5NnyOwszLRZ5Mua3qNffrq8wy4QWWe1fjW0dLsL+BHlcql76egfgLX6NVTRSBvfIi/ug+F0fCbq58ix/AcRQjS7kr/TlDJ3sHp3G05s0IbIh/0bnWjO+V//r/N4eMvTp0sun9/qlXZm9ncPScUHovthx+IVSzJ6voNLwwd7NkDHp3+YDV1EVuke1GJFqQjJeEUljsZuJ7hdfpVxfNjeyEUzWJGdA1Zqiy00tArVCpR09ssyZ9EJkKtlOqAPMosEhvOBwFOQSnIFxlCDTptEn/NfZt+B0Pam/HrtiZg/wbl2fOBQuJxqRJjz/5s9eziZ5ZxgB",
                                "thinking": "The user is asking for the 100th Fibonacci number. I have a function called `compute_fib` that can compute the nth Fibonacci number (1-indexed). The user has provided the specific value n=100, so I have all the required parameters to make this function call.",
                                "type": "thinking",
                            },
                            {
                                "citations": None,
                                "text": "I'll compute the 100th Fibonacci number for you.",
                                "type": "text",
                            },
                            {
                                "id": "toolu_015gzCmZHkowWCdiXYiocCNb",
                                "input": {"n": 100},
                                "name": "compute_fib",
                                "type": "tool_use",
                            },
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="toolu_015gzCmZHkowWCdiXYiocCNb",
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

This is a very large number! The Fibonacci sequence grows exponentially, so by the 100th term, we get numbers with 21 digits.\
"""
                        )
                    ],
                    provider="anthropic",
                    model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "citations": None,
                                "text": """\
The 100th Fibonacci number is **218,922,995,834,555,169,026**.

This is a very large number! The Fibonacci sequence grows exponentially, so by the 100th term, we get numbers with 21 digits.\
""",
                                "type": "text",
                            }
                        ],
                    },
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
    }
)
