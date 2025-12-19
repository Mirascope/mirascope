from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "response": {
            "provider_id": "mlx",
            "model_id": "mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
            "provider_model_name": "mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 20,
                "output_tokens": 711,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "MLXCassetteResponse(text='', token=151645, prompt_tokens=20, generation_tokens=711, finish_reason='stop')",
                "total_tokens": 731,
            },
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
<think>
Okay, so I need to add 4200 and 42. Let me think. First, maybe I should write them down to visualize better. \n\

4200 is like 4 thousands and 200. And 42 is 4 tens and 2. Adding them together... Let me add the thousands first. 4200 plus 400 would be 4600, right? Then add the remaining 2 to get 4602. Wait, but 4200 plus 42... Let me check again. 4200 plus 42. 4200 + 40 is 4240, plus 2 more is 4242. Hmm, so maybe my first approach was correct. \n\

Alternatively, maybe I can break it down. 4200 + 42. Let's think of 4200 as 4000 + 200, and 42 as 40 + 2. So adding 4000 + 40 gives 4040, and adding 200 + 2 gives 202. So total is 4040 + 202. Let me add those. 4040 + 200 is 4240, plus 2 is 4242. Same result. \n\

Alternatively, maybe I can add them digit by digit. 4200 is 4, 2, 0, 0. 42 is 4, 2. So adding the units first: 0 + 2 = 2. Then tens: 0 + 2 = 2. Then hundreds: 2 + 4 = 6. Thousands: 4 + 0 = 4. So 4, 2, 6, 2. Wait, that would be 4262? Wait, no. Wait, 4200 is 4 thousands, 2 hundreds, 0 tens, 0 units. 42 is 4 tens, 2 units. So adding units: 0 + 2 = 2. Tens: 0 + 4 = 4. Hundreds: 2 + 0 = 2. Thousands: 4 + 0 = 4. So 4 thousands, 2 hundreds, 4 tens, 2 units. Which is 4200 + 42 = 4242. Yes, same as before. \n\

So all methods lead to 4242. I think that's the correct answer. Let me just verify once more. 4200 + 42. 4200 + 40 = 4240, plus 2 is 4242. Yep, that's right. I don't see any mistakes here.
</think>

To solve $ 4200 + 42 $, we can break it down as follows:

- $ 4200 + 40 = 4240 $
- Adding the remaining 2: $ 4240 + 2 = 4242 $

Thus, the final answer is:

$$
\\boxed{4242}
$$\
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
async_snapshot = snapshot(
    {
        "response": {
            "provider_id": "mlx",
            "model_id": "mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
            "provider_model_name": "mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 20,
                "output_tokens": 711,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "MLXCassetteResponse(text='', token=151645, prompt_tokens=20, generation_tokens=711, finish_reason='stop')",
                "total_tokens": 731,
            },
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
<think>
Okay, so I need to add 4200 and 42. Let me think. First, maybe I should write them down to visualize better. \n\

4200 is like 4 thousands and 200. And 42 is 4 tens and 2. Adding them together... Let me add the thousands first. 4200 plus 400 would be 4600, right? Then add the remaining 2 to get 4602. Wait, but 4200 plus 42... Let me check again. 4200 plus 42. 4200 + 40 is 4240, plus 2 more is 4242. Hmm, so maybe my first approach was correct. \n\

Alternatively, maybe I can break it down. 4200 + 42. Let's think of 4200 as 4000 + 200, and 42 as 40 + 2. So adding 4000 + 40 gives 4040, and adding 200 + 2 gives 202. So total is 4040 + 202. Let me add those. 4040 + 200 is 4240, plus 2 is 4242. Same result. \n\

Alternatively, maybe I can add them digit by digit. 4200 is 4, 2, 0, 0. 42 is 4, 2. So adding the units first: 0 + 2 = 2. Then tens: 0 + 2 = 2. Then hundreds: 2 + 4 = 6. Thousands: 4 + 0 = 4. So 4, 2, 6, 2. Wait, that would be 4262? Wait, no. Wait, 4200 is 4 thousands, 2 hundreds, 0 tens, 0 units. 42 is 4 tens, 2 units. So adding units: 0 + 2 = 2. Tens: 0 + 4 = 4. Hundreds: 2 + 0 = 2. Thousands: 4 + 0 = 4. So 4 thousands, 2 hundreds, 4 tens, 2 units. Which is 4200 + 42 = 4242. Yes, same as before. \n\

So all methods lead to 4242. I think that's the correct answer. Let me just verify once more. 4200 + 42. 4200 + 40 = 4240, plus 2 is 4242. Yep, that's right. I don't see any mistakes here.
</think>

To solve $ 4200 + 42 $, we can break it down as follows:

- $ 4200 + 40 = 4240 $
- Adding the remaining 2: $ 4240 + 2 = 4242 $

Thus, the final answer is:

$$
\\boxed{4242}
$$\
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
stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "mlx",
            "provider_model_name": "mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
            "model_id": "mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
<think>
Okay, so I need to add 4200 and 42. Let me think. First, maybe I should write them down to visualize better. \n\

4200 is like 4 thousands and 200. And 42 is 4 tens and 2. Adding them together... Let me add the thousands first. 4200 plus 400 would be 4600, right? Then add the remaining 2 to get 4602. Wait, but 4200 plus 42... Let me check again. 4200 plus 42. 4200 + 40 is 4240, plus 2 more is 4242. Hmm, so maybe my first approach was correct. \n\

Alternatively, maybe I can break it down. 4200 + 42. Let's think of 4200 as 4000 + 200, and 42 as 40 + 2. So adding 4000 + 40 gives 4040, and adding 200 + 2 gives 202. So total is 4040 + 202. Let me add those. 4040 + 200 is 4240, plus 2 is 4242. Same result. \n\

Alternatively, maybe I can add them digit by digit. 4200 is 4, 2, 0, 0. 42 is 4, 2. So adding the units first: 0 + 2 = 2. Then tens: 0 + 2 = 2. Then hundreds: 2 + 4 = 6. Thousands: 4 + 0 = 4. So 4, 2, 6, 2. Wait, that would be 4262? Wait, no. Wait, 4200 is 4 thousands, 2 hundreds, 0 tens, 0 units. 42 is 4 tens, 2 units. So adding units: 0 + 2 = 2. Tens: 0 + 4 = 4. Hundreds: 2 + 0 = 2. Thousands: 4 + 0 = 4. So 4 thousands, 2 hundreds, 4 tens, 2 units. Which is 4200 + 42 = 4242. Yes, same as before. \n\

So all methods lead to 4242. I think that's the correct answer. Let me just verify once more. 4200 + 42. 4200 + 40 = 4240, plus 2 is 4242. Yep, that's right. I don't see any mistakes here.
</think>

To solve $ 4200 + 42 $, we can break it down as follows:

- $ 4200 + 40 = 4240 $
- Adding the remaining 2: $ 4240 + 2 = 4242 $

Thus, the final answer is:

$$
\\boxed{4242}
$$\
"""
                        )
                    ],
                    provider_id="mlx",
                    model_id="mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
                    provider_model_name="mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
                    raw_message=None,
                ),
            ],
            "format": None,
            "tools": [],
            "usage": {
                "input_tokens": 20,
                "output_tokens": 711,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 731,
            },
            "n_chunks": 713,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "mlx",
            "provider_model_name": "mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
            "model_id": "mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
<think>
Okay, so I need to add 4200 and 42. Let me think. First, maybe I should write them down to visualize better. \n\

4200 is like 4 thousands and 200. And 42 is 4 tens and 2. Adding them together... Let me add the thousands first. 4200 plus 400 would be 4600, right? Then add the remaining 2 to get 4602. Wait, but 4200 plus 42... Let me check again. 4200 plus 42. 4200 + 40 is 4240, plus 2 more is 4242. Hmm, so maybe my first approach was correct. \n\

Alternatively, maybe I can break it down. 4200 + 42. Let's think of 4200 as 4000 + 200, and 42 as 40 + 2. So adding 4000 + 40 gives 4040, and adding 200 + 2 gives 202. So total is 4040 + 202. Let me add those. 4040 + 200 is 4240, plus 2 is 4242. Same result. \n\

Alternatively, maybe I can add them digit by digit. 4200 is 4, 2, 0, 0. 42 is 4, 2. So adding the units first: 0 + 2 = 2. Then tens: 0 + 2 = 2. Then hundreds: 2 + 4 = 6. Thousands: 4 + 0 = 4. So 4, 2, 6, 2. Wait, that would be 4262? Wait, no. Wait, 4200 is 4 thousands, 2 hundreds, 0 tens, 0 units. 42 is 4 tens, 2 units. So adding units: 0 + 2 = 2. Tens: 0 + 4 = 4. Hundreds: 2 + 0 = 2. Thousands: 4 + 0 = 4. So 4 thousands, 2 hundreds, 4 tens, 2 units. Which is 4200 + 42 = 4242. Yes, same as before. \n\

So all methods lead to 4242. I think that's the correct answer. Let me just verify once more. 4200 + 42. 4200 + 40 = 4240, plus 2 is 4242. Yep, that's right. I don't see any mistakes here.
</think>

To solve $ 4200 + 42 $, we can break it down as follows:

- $ 4200 + 40 = 4240 $
- Adding the remaining 2: $ 4240 + 2 = 4242 $

Thus, the final answer is:

$$
\\boxed{4242}
$$\
"""
                        )
                    ],
                    provider_id="mlx",
                    model_id="mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
                    provider_model_name="mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
                    raw_message=None,
                ),
            ],
            "format": None,
            "tools": [],
            "usage": {
                "input_tokens": 20,
                "output_tokens": 711,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 731,
            },
            "n_chunks": 713,
        }
    }
)
