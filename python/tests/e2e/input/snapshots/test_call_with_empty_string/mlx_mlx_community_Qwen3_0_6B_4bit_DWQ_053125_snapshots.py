from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider": "mlx",
            "model_id": "mlx/mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
            "params": {},
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
<think>
Okay, the user is asking about the difference between the two main types of data in programming. Let me start by recalling what I know about data types in programming. There are two primary types: integers and floats. Integers are whole numbers, like 10 or 23, and they can be positive or negative. Floats are decimal numbers, like 3.14, which can be either positive or negative. \n\

Wait, but maybe the user is thinking of other types? For example, in some languages, there are other data types like strings, booleans, and arrays. But the question specifically mentions the two main types, so I should focus on integers and floats. \n\

I should also consider if the user is referring to different programming languages. For example, in Python, integers and floats are the same as in other languages. But maybe the user is confused between different languages. However, the question doesn't specify a particular language, so I'll stick to the general case.

Another point to mention is that integers can be of different sizes, like 32-bit or 64-bit, which affects their storage. But the main difference is between the two types. \n\

I should also check if there are any other data types that might be relevant. For example, in some contexts, arrays are another type, but that's more about data structures. So, the answer should focus on integers and floats. \n\

Let me make sure I'm not missing anything. The user might be trying to understand the distinction between these two types, so providing a clear explanation with examples would be helpful. Also, maybe mention that integers are used for whole numbers, while floats are used for decimal numbers. \n\

I think that's all. Now, I can structure the answer to explain the two main types, their characteristics, and examples.
</think>

In programming, the two main types of data are **integers** and **floats**. Here's the key difference:

- **Integers**:  \n\
  - Represent whole numbers (positive, negative, or zero).  \n\
  - Example: `10`, `23`, `0`.  \n\
  - Integers are precise and used for counting or basic arithmetic operations.  \n\

- **Floats**:  \n\
  - Represent decimal numbers (positive or negative).  \n\
  - Example: `3.14`, `2.5`.  \n\
  - Floats are used for more precise calculations and are commonly used in scientific and engineering contexts.  \n\

Both types are fundamental to programming, with integers typically used for whole numbers and floats for decimal values.\
"""
                        )
                    ],
                    provider="mlx",
                    model_id="mlx/mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
                    raw_message=None,
                ),
            ],
            "format": None,
            "tools": [],
        }
    }
)
