from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider_id": "mlx",
            "model_id": "mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
            "provider_model_name": "mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 8,
                "output_tokens": 351,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "MLXCassetteResponse(text='', token=151645, prompt_tokens=8, generation_tokens=351, finish_reason='stop')",
                "total_tokens": 359,
            },
            "messages": [
                UserMessage(content=[Text(text="")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
<think>
Okay, the user is asking about the difference between the two main types of the same type. Let me think. The first type is the "main type," and the second is the "sub-type." I need to explain each in simple terms.

For the main type, it's the most general category. For example, if I'm talking about a book, the main type would be "book." The sub-type would be specific, like "fictional books." That makes sense. \n\

I should also mention that sub-types can be more specific and narrower. For instance, if the main type is "books," sub-types could be "novels" or "non-fiction." \n\

Wait, maybe I should check if there's a standard way to categorize these. I think in programming, the main type is the base type, and sub-types are derived from it. So the difference is about the base and derived types. \n\

I need to make sure the explanation is clear and not too technical. Let me structure it step by step: define main type, sub-type, examples, and why they differ. That should cover the user's question.
</think>

The two main types of the same type are:  \n\
1. **Main Type**: This is the general, most basic category. For example, if you're talking about books, the main type is "book."  \n\
2. **Sub-Type**: This is a specific, narrower category derived from the main type. For example, if the main type is "book," a sub-type could be "fictional books."  \n\

Sub-types are more specific and narrower, allowing for more precise categorization. They are often used to distinguish between different forms of a broader category.\
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
        }
    }
)
