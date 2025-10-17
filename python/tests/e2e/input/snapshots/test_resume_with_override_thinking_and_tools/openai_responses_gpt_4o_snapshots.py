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
        "provider": "openai:responses",
        "model_id": "gpt-4o",
        "params": {"thinking": False},
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="What is the 100th fibonacci number?")]),
            AssistantMessage(
                content=[
                    Thought(
                        thought='The user is asking for the 100th Fibonacci number. I have access to a function called "compute_fib" that can compute the nth Fibonacci number (1-indexed). The user has provided the specific value n=100, so I have all the required parameters to make this function call.'
                    ),
                    ToolCall(
                        id="toolu_01Mjec5pPiK2o6jGwzNFA9wS",
                        name="compute_fib",
                        args='{"n": 100}',
                    ),
                ],
                provider="anthropic",
                model_id="claude-sonnet-4-0",
                raw_content=[
                    {
                        "signature": "ErUDCkYICBgCKkBu3sY/7ZuUOcbiLFXGUIPtQ96joTBhtL6mSUbAAiXw+fGhn5Inf6ahCEc4YPLvNE/oEG94XNHLzQLE5Wb3r1AsEgyuA/2S/2rRT3EWUfsaDOWE/d+50T7CsY8tBiIwT4yQ2SIuulksatbv/zKFauBwemVeyh8jpzEXCuzfwUdpx/sHztErkPJD7r13WrExKpwC+VnoZjXGG9TzjOVVdagBwdp5omjt3DGvLa0icKZ7IbOWmyqwubFV6bpsPSp5a5Yyse4Sazc1DkSdPw29H2gJUMjowV9IWsi+A1Mhq8Lgpy0xgcBfqy26z1jbBi7m4cisjdwGzAcy9tin4taiyEY3WTwsNjtzts2ENGV+c0nap4G95GbU0N9NfSfra4Bbx+Ln3jaNFDXewdD04WG1fETWOHPMCA2O4QhU1LDnFbgm6qEZdb79090Q1RPjc3IYdCz458ug+/KYLxtDmeoXBUyYVY29gC9V5fDmgXRB1ln9hZZSrdr/zGbhlZxHJTuG4eIbEUopi5838KS1sSEpSbrG4L0X8wSThafdvIjti2uRfn3R9SKyw0CyxlzYDwoYAQ==",
                        "thinking": 'The user is asking for the 100th Fibonacci number. I have access to a function called "compute_fib" that can compute the nth Fibonacci number (1-indexed). The user has provided the specific value n=100, so I have all the required parameters to make this function call.',
                        "type": "thinking",
                    },
                    {
                        "id": "toolu_01Mjec5pPiK2o6jGwzNFA9wS",
                        "input": {"n": 100},
                        "name": "compute_fib",
                        "type": "tool_use",
                    },
                ],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="toolu_01Mjec5pPiK2o6jGwzNFA9wS",
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
                raw_content=[
                    {
                        "id": "msg_00d582e3fce6d7ce0068f29b871b3481949d7c68ddf48043f3",
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
)
