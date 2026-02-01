from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "response": {
            "provider_id": "anthropic",
            "model_id": "anthropic-beta/claude-sonnet-4-0",
            "provider_model_name": "claude-sonnet-4-0",
            "params": {"thinking": {"level": "medium", "include_thoughts": False}},
            "finish_reason": None,
            "usage": {
                "input_tokens": 67,
                "output_tokens": 1274,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "BetaUsage(cache_creation=BetaCacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=67, output_tokens=1274, server_tool_use=None, service_tier='standard')",
                "total_tokens": 1341,
            },
            "messages": [
                UserMessage(
                    content=[
                        Text(
                            text="How many primes below 400 contain 79 as a substring? Answer ONLY with the number, not sharing which primes they are."
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Looking at numbers below 400 that contain "79" as a substring:
- 79
- 179  \n\
- 279
- 379

Checking which are prime:
- 79: prime
- 179: prime
- 279: divisible by 3 (2+7+9=18), not prime
- 379: prime

3\
"""
                        )
                    ],
                    provider_id="anthropic",
                    model_id="anthropic-beta/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "signature": "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",
                                "thinking": """\
I need to find all prime numbers below 400 that contain "79" as a substring.

Let me think about this systematically. I need to check all numbers below 400 that contain "79" as a substring, and then check if they are prime.

Numbers containing "79" as a substring below 400:
- 79
- 179
- 279
- 379
- 790, 791, 792, 793, 794, 795, 796, 797, 798, 799 (but these are all ≥ 400, so not relevant)

Wait, let me be more careful. The numbers below 400 that contain "79" as a substring are:
- 79 (the number itself)
- 179 (contains 79)
- 279 (contains 79) \n\
- 379 (contains 79)

Are there any others? Let me think...
- Numbers of the form X79 where X is a single digit: 079 = 79, 179, 279, 379, 479, ... but 479 > 400
- Numbers of the form 7X9 where X is a single digit: 709, 719, 729, 739, 749, 759, 769, 779, 789, 799. But wait, these don't contain "79" as a substring, they have a digit between 7 and 9.
- Numbers of the form 79X: 790, 791, 792, 793, 794, 795, 796, 797, 798, 799. But all of these are ≥ 400.

So the candidates are: 79, 179, 279, 379.

Now I need to check which of these are prime.

79: Let me check if 79 is prime.
√79 ≈ 8.9, so I need to check divisibility by primes up to 8: 2, 3, 5, 7


- 79 is odd, so not divisible by 2
- 7+9 = 16, not divisible by 3
- Doesn't end in 0 or 5, so not divisible by 5
- 79 ÷ 7 = 11.28..., so not divisible by 7
So 79 is prime.

179: Let me check if 179 is prime.
√179 ≈ 13.4, so I need to check divisibility by primes up to 13: 2, 3, 5, 7, 11, 13. Since 179 is odd and doesn't end in 0 or 5, I can skip 2 and 5. The digit sum is 1+7+9 = 17, not divisible by 3. Testing 7, 11, and 13 shows none divide evenly into 179, so it's prime.

279: Checking if 279 is prime.
√279 ≈ 16.7, so I need to check primes up to 16. It's odd and doesn't end in 0 or 5. The digit sum is 2+7+9 =

18, which is divisible by 3, so 279 = 3 × 93 and isn't prime.

379: Let me verify if 379 is prime.
√379 ≈ 19.5, so I need to check divisibility by primes up to 19: 2, 3, 5, 7, 11, 13, 17, 19
- 379 is odd, so not divisible by 2
- 3+7+9 = 19, not divisible by 3
- Doesn't end in 0 or 5, so not divisible by 5
- 379 ÷ 7 = 54.14..., so not divisible by 7
- 379 ÷ 11 = 34.45..., so not divisible by 11
- 379 ÷ 13 = 29.15..., so not divisible by 13
- 379 ÷ 17 = 22.29..., so not divisible by 17
- 379 ÷ 19 = 19.95..., so not divisible by 19
So 379 is prime.

I've found all the primes below 400 containing "79": 79, 179, and 379. That gives me 3 primes total.\
""",
                                "type": "thinking",
                            },
                            {
                                "text": """\
Looking at numbers below 400 that contain "79" as a substring:
- 79
- 179  \n\
- 279
- 379

Checking which are prime:
- 79: prime
- 179: prime
- 279: divisible by 3 (2+7+9=18), not prime
- 379: prime

3\
""",
                                "type": "text",
                            },
                        ],
                    },
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
            "provider_id": "anthropic",
            "model_id": "anthropic-beta/claude-sonnet-4-0",
            "provider_model_name": "claude-sonnet-4-0",
            "params": {"thinking": {"level": "medium", "include_thoughts": False}},
            "finish_reason": None,
            "usage": {
                "input_tokens": 67,
                "output_tokens": 977,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "BetaUsage(cache_creation=BetaCacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=67, output_tokens=977, server_tool_use=None, service_tier='standard')",
                "total_tokens": 1044,
            },
            "messages": [
                UserMessage(
                    content=[
                        Text(
                            text="How many primes below 400 contain 79 as a substring? Answer ONLY with the number, not sharing which primes they are."
                        )
                    ]
                ),
                AssistantMessage(
                    content=[Text(text="3")],
                    provider_id="anthropic",
                    model_id="anthropic-beta/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "signature": "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",
                                "thinking": """\
I need to find all prime numbers below 400 that contain "79" as a substring.

First, let me think about what numbers below 400 could contain "79" as a substring:
- Numbers of the form 79X (where X is a digit): 790, 791, 792, 793, 794, 795, 796, 797, 798, 799
- Numbers of the form X79 (where X is a digit): 179, 279, 379
- The number 79 itself

Wait, let me be more systematic. Numbers below 400 that contain "79":
- 79
- 179
- 279
- 379
- 790, 791, 792, 793, 794, 795, 796, 797, 798, 799 (but these are all ≥ 790, so none are below 400)

So the candidates are: 79, 179, 279, 379

Now I need to check which of these are prime:

79: Let me check if 79 is prime.
- Not divisible by 2 (it's odd)
- Not divisible by 3: 7+9=16, not divisible by 3
- Not divisible by 5 (doesn't end in 0 or 5)
- Not divisible by 7: 79 ÷ 7 = 11.28... (not an integer)
- Since √79 ≈ 8.9, I only need to check primes up to 8, so I need to check 2, 3, 5, 7.
- 79 is prime.

179: Let me check if 179 is prime.
- Not divisible by 2 (it's odd)
- Not divisible by 3: 1+7+9=17, not divisible by 3
- Not divisible by 5 (doesn't end in 0 or 5)


- Testing divisibility by 7, 11, and 13 all fail. Since √179 ≈ 13.4, I've checked all necessary primes up to that point.
- 179 is prime.

279: Let me check if 279 is prime.
- It's odd, so not divisible by 2. The digit sum is 18, which is divisible by 3, so 279 is divisible by 3.
- 279 is not prime.

379: Let me check if 379 is prime.
- It's odd and the digit sum (19) isn't divisible by 3, so those are ruled out. It doesn't end in 0 or 5, eliminating 5. Testing 7, 11, and 13 all yield non-integers.
- Checking 17 and 19 also don't divide evenly into 379.
- Since the square root of 379 is approximately 19.5, I've tested all necessary primes up to that point, confirming 379 is prime.

The numbers below 400 containing "79" that are prime are 79, 179, and 379—three primes total.\
""",
                                "type": "thinking",
                            },
                            {"text": "3", "type": "text"},
                        ],
                    },
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
            "provider_id": "anthropic",
            "model_id": "anthropic-beta/claude-sonnet-4-0",
            "provider_model_name": "claude-sonnet-4-0",
            "finish_reason": None,
            "messages": [
                UserMessage(
                    content=[
                        Text(
                            text="How many primes below 400 contain 79 as a substring? Answer ONLY with the number, not sharing which primes they are."
                        )
                    ]
                ),
                AssistantMessage(
                    content=[Text(text="3")],
                    provider_id="anthropic",
                    model_id="anthropic-beta/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "thinking",
                                "thinking": """\
I need to find all prime numbers below 400 that contain "79" as a substring.

First, let me think about what numbers below 400 could contain "79" as a substring:
- Numbers of the form 79X (where X is a digit): 790, 791, 792, 793, 794, 795, 796, 797, 798, 799
- Numbers of the form X79 (where X is a digit): 179, 279, 379
- The number 79 itself

Wait, let me be more systematic. Numbers below 400 that contain "79":
- 79
- 179
- 279
- 379
- All numbers from 790-799 are above 400, so they don't count.

So the candidates are: 79, 179, 279, 379

Now I need to check which of these are prime:

79: Let me check if 79 is prime.
√79 ≈ 8.9, so I need to check divisibility by primes up to 8: 2, 3, 5, 7
- 79 is odd, so not divisible by 2
- 7 + 9 = 16, not divisible by 3
- Doesn't end in 0 or 5, so not divisible by 5
- 79 ÷ 7 = 11.28..., so not divisible by 7
Therefore, 79 is prime.

179: Let me check if 179 is prime.
√179 ≈ 13.4, so I need to check divisibility by primes up to 13: 2, 3, 5, 7, 11, 13
- 179 is odd, so not divisible by 2
- 1 + 7 + 9 = 17, not divisible by 3
- Doesn't end in 0 or 5, so not divisible by 5


- Testing 7, 11, and 13 all yield non-integer results, so 179 is prime.

279: The digit sum is 18, which is divisible by 3, so 279 = 3 × 93 and is composite.

379: Since √379 ≈ 19.5, I need to test primes up to 19. It's odd, so not divisible by 2. The digit sum of 19 rules out 3. It doesn't end in 0 or 5, eliminating 5. Testing 7, 11, and 13 all produce non-integers, and continuing with 17 and 19 also yields no factors, confirming 379 is prime.

The numbers below 400 containing "79" that are prime are 79, 179, and 379—three primes total.\
""",
                                "signature": "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",
                            },
                            {"type": "text", "text": "3"},
                        ],
                    },
                ),
            ],
            "format": None,
            "tools": [],
            "usage": {
                "input_tokens": 67,
                "output_tokens": 935,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "None",
                "total_tokens": 1002,
            },
            "n_chunks": 3,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "anthropic",
            "model_id": "anthropic-beta/claude-sonnet-4-0",
            "provider_model_name": "claude-sonnet-4-0",
            "finish_reason": None,
            "messages": [
                UserMessage(
                    content=[
                        Text(
                            text="How many primes below 400 contain 79 as a substring? Answer ONLY with the number, not sharing which primes they are."
                        )
                    ]
                ),
                AssistantMessage(
                    content=[Text(text="3")],
                    provider_id="anthropic",
                    model_id="anthropic-beta/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "thinking",
                                "thinking": """\
I need to find all primes below 400 that contain "79" as a substring.

First, let me think about what numbers below 400 could contain "79" as a substring:
- Numbers of the form 79X (where X is a digit): 790, 791, 792, 793, 794, 795, 796, 797, 798, 799
- Numbers of the form X79 (where X is a digit): 179, 279, 379
- The number 79 itself

Wait, let me be more systematic. Numbers below 400 that contain "79":
- 79
- 179
- 279
- 379
- Any number starting with 79 would be at least 790, which is above 400, so none of those.

So the candidates are: 79, 179, 279, 379

Now I need to check which of these are prime:

79: Let me check if 79 is prime.
- Is it divisible by 2? No (it's odd)
- Is it divisible by 3? 7+9 = 16, not divisible by 3
- Is it divisible by 5? No (doesn't end in 0 or 5)
- Is it divisible by 7? 79 ÷ 7 = 11.28..., so no
- Is it divisible by 11? 79 ÷ 11 = 7.18..., so no

Since √79 ≈ 8.9, I only need to check divisibility up to 8. I've checked 2, 3, 5, 7, so 79 is prime.

179: Let me check if 179 is prime.
- Is it divisible by 2? No (it's odd)
- Is it divisible by 3? 1+7+9 = 17, not divisible by 3


- Is it divisible by 5? No (doesn't end in 0 or 5)
- Is it divisible by 7? 179 ÷ 7 = 25.57..., so no
- Is it divisible by 11? 179 ÷ 11 = 16.27..., so no
- Is it divisible by 13? 179 ÷ 13 = 13.76..., so no

Since √179 ≈ 13.4, I've checked all primes up to that point, so 179 is prime.

For 279, the digit sum is 2+7+9 = 18, which is divisible by 3, so 279 = 3 × 93 and isn't prime. Now checking 379: it's odd, and 3+7+9 = 19 isn't divisible by 3, it doesn't end in 0 or 5, and I need to continue testing divisibility by 7 and beyond.

Testing 379 against primes up to its square root (about 19.5): 7, 11, 13, 17, and 19 all fail to divide it evenly. Since I've exhausted all primes up to the square root, 379 is prime. The numbers containing "79" that are prime below 400 are 79 and 379.\
""",
                                "signature": "EvoSCkYICxgCKkAOnPSlxBFeekiXeR4m90xrUgq0I4RSeDSNrhDgEcuP19Q6tFSboWp18Sl0qpQB6TfHldF0Rs0UnwDETzG/vDBqEgwekXsbmXLIZnIAeZAaDFmuXHgMZHwwWXbaLSIw97DT5UnDS179VFIc+ngN4lZqBDSeeYyxk6TNxIbKqg2kTl4dW+t2G8LG3imlVanHKuERBr+EgjpkbFXzp6KuZHsGSMVEVfVI/ZmtlqX9piyEQ4Vd1/In0GP/fdHHy/qnsHspTgD5tEZANZCwBPGCABMMZOhpmxAff2PncWBfqbsv3WUYNkpnYAabT7zwkNA4az74nEOZPNY6zDpmt8ch6cJsw4O2zE2qGPlwy1QMRjOjIs0ixEzpybX4JZwv0q0JqpK0I6hWIF6+By/rqqDVzvuECXWscBt9FyTWpu/njOsj6aBwYzJwJ6Rttqyr5bFx1rKgbTWXregvp7imyx4HLro1Wb9K7l2QnaRfZCRhJbvb8tTfxmXhsiWRcIWixqzLfZhFWZXP6wO5VJqCitVUFMJW8zrq+Uqz3WeZnwOZ8szPmvQJNh2nQ7MoUrivfwu/QuXLMxjtitEy+AO4X4Z3UdFCCGoY2hubehIyYdYSCDVxxZ/sTZ/RJW/c5tJc57IPi+hWRPydZI2gziEupJZNcdAMuUVLLod1/DzqljZs9zl4F6nQFxs8iQp7OZiyY2wX3IoL20xn9zLJygiGfnoW2FiVy/H9AjlAE4dlbrtAeQ7NLcaQUhLmMdfMn6W5TAS6iSegN0inC/lbcnHIGnYcRgbmJBmGY62VU+Bpjd5XX27yjdn1oJVC95n/Ja2VxK3ePvQo5zYsm3eSFPse6RKb3GO9G1LvlJBr6KrRhQl7YFpvor7AGBWcdYnTeBFe4urppl575QxhvSUwVdSNtMTcAVEB5rUarHbYvZNCzoPBA7Ma7YeaQoMXk+Ilbq0bZDcgnJPJq3g3w6lQuII+vbAFvl8Jy4z8qGn6GfHh+qV95a9x2owyqXwRyZ2nwFo+fH3SZNwg/eJ8xfaCJkzqYyUkjUMeW6QcCCsKhKuTV6A5Yl931ql0I9PnWyaVwUup6bJP1/lq4NQ1fsQLgKXkFMl5sVaXu/ZK3fY1pr9RYZ0Sa/O8XsIjfPkTxNeMnVDnit/idMCifKD/HXdtVD5xfrJBI2s1AyHoSUJ+7bo1WydzaMt+Wc83dtnShI23sE8PpCIV5bO/IUVB9MwiY2En3WOVRuRTr4k4yndgjgKbuuHj9Rqoy0G9m4dXoSDCZ0GkOxnyUGf3mBBd3o8/pKObSKN+jRXnwAIzaO1wPtrfT/6HAE9vtDCiWpLS2/1fVCfiLqEBmIf0cRO1PG3NMwXSYmnz8Sl7sze56M8gzGMiU4n8nkoLo8/oc0fE42ZJTVEALjMWBUFhtRC1I41xe45R3VoFRD3gjAOvmGuHVFb104irzGkw5QX1CkBbm+/2Ugt+9xLCfYYX9YlSKB4nFhBlRlFrAxYw/UW/l7DdvRr0nZ1G2z2NywGQ1OlZiIhEBTMDFeZl5XU06ePdzKVtXDE7++nt8AGHRoENF8smzUikd8WUumA2/+3121aFXuhuBltLpZVVRZJHZbUc9npjORSNXjbtEXoXotN/Qa64Uxug57au2tSXTxBas3qEpkwNMJb5IV8vV+rj/VgVXMX/zO0lygcT5BmuklhP4RqB+HAzidA8GnH/cb9YqUfWJHPDKhMlm59oxMgDvOm/MYrhGfLohFFik0dzH/3buFb07owOIewazsyOhVEhzaQAY+Py3sQNrYuem+kxVYDe4ZCaCIC+ZJ+k6NjtANwrLhwTn5Kr6V19p321KbQmcIv1qytyHh8sQY+40brcwoUApb49llSCVQKJVfL1K7O7X1ctFk5NTmFhvj8oN7Eidt/w6vLwJEDnZYwSLFJFE4xYacN24MfsNtUiHdrm7walOdh07kFkU3nWN5Gl8DfOkFB8flbGeSvF0Exo0dQxYpT7jVLh7vDdMHHgA3we1zuEqAzkT3WySh/zX8DrJj/mx7dN7EUqi0nMsEU9K+xEFyDM8bW/Z9MEhOK3YIBiqjA08UUcs5dWZI3JBTr9Q9CEVVk85C5OeF2vKxP0lPmqomvael+GMZffdApR2DCTnGl6N6dBlN5o6wYO9UcHvGZJ68PVkx39glQ1W0rWBSmnsreppRh2el5L066J8Z+y7xaHRqgQ/h6aZmZb3qyYbvJ0cj5+i7E8+OqKETrl/x4ASh83kWYZyjQZbGiNdvVGBEW5oFfNuvs1ApDG2tHt93mo1d2YvtwesfEOS/V23ecVGptj5enzyhwYvQKzOn/uzKb5Z5B6V8KIAaLjUz+LFDnXCUxUiJ/rT+W2B6gqb/Uy0Uhlrml3DoRirq8b1IDGThNAJjuN+0RLL1D639Te96euZCOyWlIOL9TJFdECJckV+mATDmevNomiD2gK3KDxN2ADkiS2AMtAs5o5oFUS83UgtqqTzzbE0Ab61wwcUPOSGugZZsXDX7/rPsphKDfgTL4uB/tYxKDFpfFUQjxEgwpbaguKr3/R8cgCfSGOFGXpAVtw63PPHfiR++zNWd/3+P7/84LBx27CSoeqXV32Ni0qmbDzjZ41L3hcvpONO+2/nVv22AH+AhWHF6/xcYIg1JYM9xMTQK5Em68oHW1jfHun90EQ/TyqcvC2d8VRIBGQw4d2mPEKCFAItnVp/NXlFy6GS8p3bzoChSd8uFozotfZ1rIEAvPlcUb+Ecc9vep8zZpeLdCIKZo5IAbxOX3DDeMmOvBTEeEIo9Os/3k08SSNc2owituonOyWcm/z92pebm2EGM+OPdPMKUh77c1WX5BOAoR91RgMPPiO3IdodCspBbcmwmgDkXbl3v/fDBskt/+2EPPSCUuhQN1/5EDrsEbH2NIBZTYc9375tztcJfWtOfKvw/NX6XXX6WUudZOpic/uoHzuAtd11nMh6K/9dg0qCvWIfS0kazkWvXgbLreCnrJq/mvb5QqZCnr1WiPW6ZZWraaBa02jo5EoDRw0dyA+LKnZ3XRzjtBz0caXpsF/j3y4kOvETFYpmFxNHSemdnr1yWeRHgNQ+xGW3YRw1QsRY0PB7goTNsFO0UURtQfk6ppG3VoxbQKhqbNs+nP4nNkCXBC0vDBFgS150V43t0YgHgytCndTtuLgEo2j7E6LNqrcC9HHq1CCO1B8YtcaP9nyTapvB39tbpn0xcO2HRoYAQ==",
                            },
                            {"type": "text", "text": "3"},
                        ],
                    },
                ),
            ],
            "format": None,
            "tools": [],
            "usage": {
                "input_tokens": 67,
                "output_tokens": 1035,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "None",
                "total_tokens": 1102,
            },
            "n_chunks": 3,
        }
    }
)
