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
        "provider": "google",
        "model_id": "gemini-2.5-flash",
        "params": {"thinking": False},
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="What is the 100th fibonacci number?")]),
            AssistantMessage(
                content=[
                    Thought(
                        thought="The user is asking for the 100th Fibonacci number. I have a function called `compute_fib` that can compute the nth Fibonacci number (1-indexed). The user has provided the specific value n=100, so I have all the required parameters to make the function call."
                    ),
                    Text(text="I'll compute the 100th Fibonacci number for you."),
                    ToolCall(
                        id="toolu_01AK1C1BcDm5xcrrvo4MHdDZ",
                        name="compute_fib",
                        args='{"n": 100}',
                    ),
                ],
                provider="anthropic",
                model_id="claude-sonnet-4-0",
                raw_content=[
                    {
                        "signature": "EqoDCkYICBgCKkCIlwIs2f+gS7ppP4lUwmwBwhdOe9t8oE9CHo+7ZDCxjT1QVnU7MY+urmA3L9K08WMzZoAr4i4e4A/Npy5dTwwqEgyDXcTDvqkmr9inEVAaDKobl+DyN94GMn1oPyIw+tR/HvIDSe41FEEXMI+q2Zk/7StOOPPhOcAm8OyLLg1W7xyAwgKbVlaI1R7v+kizKpEClvJy3qIDPf4NVWetPezDoi3PnHMjQ1wb2InJKnkkJAFtN0TG8lYXz6bSniyFklFX0FUb/O85AvLsowHv4Gk+jGUMXgcaig4CIZcQ21by5rruYuEoNP3MqnyW9r7HJwRN7AmCjndhCGE03QzyPABy6XTQPE3+VLOn8P4z8aU4OLEyTDuqRNUCsGtGC4NYZJ1cHqzSlBIASVRT01PVt7vyDIbQ6B7DG0i+b4tY0gSi70lKd+K4UZIhwsHi042hBknl7ldaRuGcwX8/ybDRBYUcrk8nR/+aWg74ddqoBdwPpS0z9tQy6aJDu8tbyqHm93fjf2VKFmYjMXA1VKfY715MaVIRnnx+VaLHcEeuE+xtttsXGAE=",
                        "thinking": "The user is asking for the 100th Fibonacci number. I have a function called `compute_fib` that can compute the nth Fibonacci number (1-indexed). The user has provided the specific value n=100, so I have all the required parameters to make the function call.",
                        "type": "thinking",
                    },
                    {
                        "citations": None,
                        "text": "I'll compute the 100th Fibonacci number for you.",
                        "type": "text",
                    },
                    {
                        "id": "toolu_01AK1C1BcDm5xcrrvo4MHdDZ",
                        "input": {"n": 100},
                        "name": "compute_fib",
                        "type": "tool_use",
                    },
                ],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="toolu_01AK1C1BcDm5xcrrvo4MHdDZ",
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
