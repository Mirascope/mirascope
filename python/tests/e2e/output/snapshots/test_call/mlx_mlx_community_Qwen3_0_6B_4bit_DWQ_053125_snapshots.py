from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "response": {
            "provider": "mlx",
            "model_id": "mlx/mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
            "params": {},
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
<think>
Okay, let's see. I need to add 4200 and 42. Hmm, how do I do that? Well, maybe I can think of it as 4200 plus 42. Let me break it down. 4200 is like 4000 plus 200, right? And 42 is 40 plus 2. So if I add 4000 + 40 and 200 + 2, that should give me the same result. Let me check that. 4000 + 40 is 4040, and 200 + 2 is 202. Adding those together, 4040 + 202. Let me do that addition. 4040 + 200 is 4240, and then adding 2 more makes it 4242. So the total is 4242. Wait, but maybe there's another way to do it. Let me try another approach. 4200 plus 42. Let's add the units first. 00 + 2 is 2, and then 4000 + 40 is 4040. So 4040 + 2 is 4042? Wait, no, that's conflicting. Wait, no, when adding 4200 and 42, the units are 00 and 2, so 00 + 2 is 2, and then 4000 + 40 is 4040. So total is 4042? But earlier, when I broke it down into 4000 + 40 and 200 + 2, I got 4242. Wait, that's a problem. Which one is correct?

Wait, maybe I made a mistake in the second approach. Let me check again. 4200 + 42. Let's write them vertically:

  4200
+  42
------
  4242

Yes, that's right. So 4200 + 42 is 4242. So why did I get confused earlier? Because when I broke it down into 4000 + 40 and 200 + 2, I thought 4000 + 40 is 4040 and 200 + 2 is 202, adding them gives 4242. But that's correct. So the answer is 4242. Let me verify once more. 4200 + 42. 4200 + 40 is 4240, plus 2 is 4242. Yep, that's right. So the final answer is 4242.
</think>

To solve $ 4200 + 42 $, we can break it down as follows:

- $ 4200 + 40 = 4240 $
- $ 4240 + 2 = 4242 $

Thus, the final answer is:

$$
\\boxed{4242}
$$\
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
async_snapshot = snapshot(
    {
        "response": {
            "provider": "mlx",
            "model_id": "mlx/mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
            "params": {},
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
<think>
Okay, let's see. I need to add 4200 and 42. Hmm, how do I do that? Well, maybe I can think of it as 4200 plus 42. Let me break it down. 4200 is like 4000 plus 200, right? And 42 is 40 plus 2. So if I add 4000 + 40 and 200 + 2, that should give me the same result. Let me check that. 4000 + 40 is 4040, and 200 + 2 is 202. Adding those together, 4040 + 202. Let me do that addition. 4040 + 200 is 4240, and then adding 2 more makes it 4242. So the total is 4242. Wait, but maybe there's another way to do it. Let me try another approach. 4200 plus 42. Let's add the units first. 00 + 2 is 2, and then 4000 + 40 is 4040. So 4040 + 2 is 4042? Wait, no, that's conflicting. Wait, no, when adding 4200 and 42, the units are 00 and 2, so 00 + 2 is 2, and then 4000 + 40 is 4040. So total is 4042? But earlier, when I broke it down into 4000 + 40 and 200 + 2, I got 4242. Wait, that's a problem. Which one is correct?

Wait, maybe I made a mistake in the second approach. Let me check again. 4200 + 42. Let's write them vertically:

  4200
+  42
------
  4242

Yes, that's right. So 4200 + 42 is 4242. So why did I get confused earlier? Because when I broke it down into 4000 + 40 and 200 + 2, I thought 4000 + 40 is 4040 and 200 + 2 is 202, adding them gives 4242. But that's correct. So the answer is 4242. Let me verify once more. 4200 + 42. 4200 + 40 is 4240, plus 2 is 4242. Yep, that's right. So the final answer is 4242.
</think>

To solve $ 4200 + 42 $, we can break it down as follows:

- $ 4200 + 40 = 4240 $
- $ 4240 + 2 = 4242 $

Thus, the final answer is:

$$
\\boxed{4242}
$$\
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
stream_snapshot = snapshot(
    {
        "response": {
            "provider": "mlx",
            "model_id": "mlx/mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
<think>
Okay, let's see. I need to add 4200 and 42. Hmm, how do I do that? Well, maybe I can think of it as 4200 plus 42. Let me break it down. 4200 is like 4000 plus 200, right? And 42 is 40 plus 2. So if I add 4000 + 40 and 200 + 2, that should give me the same result. Let me check that. 4000 + 40 is 4040, and 200 + 2 is 202. Adding those together, 4040 + 202. Let me do that addition. 4040 + 200 is 4240, and then adding 2 more makes it 4242. So the total is 4242. Wait, but maybe there's another way to do it. Let me try another approach. 4200 plus 42. Let's add the units first. 00 + 2 is 2, and then 4000 + 40 is 4040. So 4040 + 2 is 4042? Wait, no, that's conflicting. Wait, no, when adding 4200 and 42, the units are 00 and 2, so 00 + 2 is 2, and then 4000 + 40 is 4040. So total is 4042? But earlier, when I broke it down into 4000 + 40 and 200 + 2, I got 4242. Wait, that's a problem. Which one is correct?

Wait, maybe I made a mistake in the second approach. Let me check again. 4200 + 42. Let's write them vertically:

  4200
+  42
------
  4242

Yes, that's right. So 4200 + 42 is 4242. So why did I get confused earlier? Because when I broke it down into 4000 + 40 and 200 + 2, I thought 4000 + 40 is 4040 and 200 + 2 is 202, adding them gives 4242. But that's correct. So the answer is 4242. Let me verify once more. 4200 + 42. 4200 + 40 is 4240, plus 2 is 4242. Yep, that's right. So the final answer is 4242.
</think>

To solve $ 4200 + 42 $, we can break it down as follows:

- $ 4200 + 40 = 4240 $
- $ 4240 + 2 = 4242 $

Thus, the final answer is:

$$
\\boxed{4242}
$$\
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
            "n_chunks": 716,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider": "mlx",
            "model_id": "mlx/mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
<think>
Okay, let's see. I need to add 4200 and 42. Hmm, how do I do that? Well, maybe I can think of it as 4200 plus 42. Let me break it down. 4200 is like 4000 plus 200, right? And 42 is 40 plus 2. So if I add 4000 + 40 and 200 + 2, that should give me the same result. Let me check that. 4000 + 40 is 4040, and 200 + 2 is 202. Adding those together, 4040 + 202. Let me do that addition. 4040 + 200 is 4240, and then adding 2 more makes it 4242. So the total is 4242. Wait, but maybe there's another way to do it. Let me try another approach. 4200 plus 42. Let's add the units first. 00 + 2 is 2, and then 4000 + 40 is 4040. So 4040 + 2 is 4042? Wait, no, that's conflicting. Wait, no, when adding 4200 and 42, the units are 00 and 2, so 00 + 2 is 2, and then 4000 + 40 is 4040. So total is 4042? But earlier, when I broke it down into 4000 + 40 and 200 + 2, I got 4242. Wait, that's a problem. Which one is correct?

Wait, maybe I made a mistake in the second approach. Let me check again. 4200 + 42. Let's write them vertically:

  4200
+  42
------
  4242

Yes, that's right. So 4200 + 42 is 4242. So why did I get confused earlier? Because when I broke it down into 4000 + 40 and 200 + 2, I thought 4000 + 40 is 4040 and 200 + 2 is 202, adding them gives 4242. But that's correct. So the answer is 4242. Let me verify once more. 4200 + 42. 4200 + 40 is 4240, plus 2 is 4242. Yep, that's right. So the final answer is 4242.
</think>

To solve $ 4200 + 42 $, we can break it down as follows:

- $ 4200 + 40 = 4240 $
- $ 4240 + 2 = 4242 $

Thus, the final answer is:

$$
\\boxed{4242}
$$\
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
            "n_chunks": 716,
        }
    }
)
