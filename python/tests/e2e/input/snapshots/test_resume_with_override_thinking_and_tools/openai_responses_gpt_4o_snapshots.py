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
            "provider": "openai:responses",
            "model_id": "gpt-4o",
            "params": {"thinking": False},
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="What is the 100th fibonacci number?")]),
                AssistantMessage(
                    content=[
                        Thought(
                            thought='The user is asking for the 100th Fibonacci number. I have a function available called "compute_fib" that can compute the nth Fibonacci number (1-indexed). The user has provided the specific value n=100, so I have all the required parameters to make the function call.'
                        ),
                        ToolCall(
                            id="toolu_01CL5eUDHsg9AGHyBotNfisY",
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
                                "signature": "ErQDCkYICBgCKkCsItOUHNinar+NABlYn+UTCEV462H15XiUdax8L7lhYMAvN2X2YxzcMd8Obghv+2Menhq/JUHTvDvU3gt3TiOQEgwbJS5D9xNGwcTpovgaDIWaDuk5agJhVcc67CIwQTu7O3W/HWUsl4CWXns5CbrWEKEDFpBaC/jIojdf37xLxSaKF/CYBpzGNemQ5kT4KpsCOFrS1f/TnnRDLRSGmrRE0n1JXup6FGelkDA3Lgrj9e25KzwINfQWLJ+kFa1ujPNLGwhMqs9qykmuE9pL+3zScityn9s05T3NBxcNi5HcmH/7PGTGWYy5R2MBwKSruk8ClRVBUeBo9KXOVEIfolaIVu+CUrCH13yU98qFDvdJdVu+KWPAIZHTr7q4qOpjkzYtjruSZfrz0fzMir8ajLzkCDAOgNOzKobqtrDvjuyoku2A3ni7jzpoOA0S7c4VzwEt/JjzPKeBfnbQwr6n0FKSjzl2HdhrKFl0R0fLcpgrdYG2O3yQoO87xgXYQ902VratKLhNz8aCGUU702+8CwzdF7bgYL4X2kFnPMi/SrtXp0f8K46BqP1bAsR1vBgB",
                                "thinking": 'The user is asking for the 100th Fibonacci number. I have a function available called "compute_fib" that can compute the nth Fibonacci number (1-indexed). The user has provided the specific value n=100, so I have all the required parameters to make the function call.',
                                "type": "thinking",
                            },
                            {
                                "id": "toolu_01CL5eUDHsg9AGHyBotNfisY",
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
                            id="toolu_01CL5eUDHsg9AGHyBotNfisY",
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
                    provider="openai:responses",
                    model_id="gpt-4o",
                    raw_message=[
                        {
                            "id": "msg_0c39e9e96939d63c0068f8032a699c819598a4227b3bfaf979",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": "The 100th Fibonacci number is 218,922,995,834,555,169,026.",
                                    "type": "output_text",
                                    "logprobs": [],
                                }
                            ],
                            "role": "assistant",
                            "status": "completed",
                            "type": "message",
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
    }
)
