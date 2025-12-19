from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    FinishReason,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": (
            {
                "provider_id": "mlx",
                "model_id": "mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
                "provider_model_name": "mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
                "params": {
                    "temperature": 0.7,
                    "max_tokens": 500,
                    "top_p": 0.3,
                    "top_k": 50,
                    "seed": 42,
                    "stop_sequences": ["4242"],
                    "thinking": False,
                    "encode_thoughts_as_text": False,
                },
                "finish_reason": FinishReason.MAX_TOKENS,
                "usage": {
                    "input_tokens": 20,
                    "output_tokens": 500,
                    "cache_read_tokens": 0,
                    "cache_write_tokens": 0,
                    "reasoning_tokens": 0,
                    "raw": "MLXCassetteResponse(text=' is', token=374, prompt_tokens=20, generation_tokens=500, finish_reason='length')",
                    "total_tokens": 520,
                },
                "messages": [
                    UserMessage(content=[Text(text="What is 4200 + 42?")]),
                    AssistantMessage(
                        content=[
                            Text(
                                text="""\
<think>
Okay, let's see. I need to add 4200 and 42. Hmm, how do I do that? Well, maybe I can think of it as 4200 plus 42. Let me break it down. \n\

First, 4200 is like 4000 plus 200. And 42 is 40 plus 2. So if I add 4000 + 40 and 200 + 2, that should give me the same result. Let me check that. \n\

4000 + 40 is 4040, and 200 + 2 is 202. Adding those together: 4040 + 202. Let me do that addition. 4040 plus 200 is 4240, and then adding 2 more makes it 4242. So the total is 4242?

Wait, but maybe there's another way to do it. Let me try adding the numbers digit by digit. 4200 + 42. Starting from the rightmost digit: 0 + 2 = 2. Then 0 + 4 = 4. Then 4 + 2 = 6. Then 2 + 4 = 6. Wait, that gives me 426? But that can't be right because 4200 + 42 is 4242. There must be a mistake here. \n\

Oh, right! When adding, you have to align the digits properly. So 4200 is 4 2 0 0, and 42 is 4 2. So adding them:

First digit: 0 + 2 = 2
Second digit: 0 + 4 = 4
Third digit: 2 + 2 = 4
Fourth digit: 4 + 4 = 8

So the result is 4242. That matches my previous calculation. So maybe I confused the digits when I thought of it as 4000 + 40 + 200 + 2. Let me check again. 4000 + 40 is 4040, plus 200 is\
"""
                            )
                        ],
                        provider_id="mlx",
                        model_id="mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
                        provider_model_name=None,
                        raw_message=None,
                    ),
                ],
                "format": None,
                "tools": [],
            },
        ),
        "logs": [
            "Skipping unsupported parameter: stop_sequences=['4242'] (provider: mlx)",
            "Skipping unsupported parameter: thinking=False (provider: mlx)",
            "Skipping unsupported parameter: encode_thoughts_as_text=False (provider: mlx)",
        ],
    }
)
