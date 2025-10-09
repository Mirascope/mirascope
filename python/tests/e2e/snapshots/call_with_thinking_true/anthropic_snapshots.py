from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    Thought,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "response": {
            "provider": "anthropic",
            "model_id": "claude-sonnet-4-0",
            "params": {"thinking": False},
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
                    content=[
                        Thought(
                            thought="""\
I need to find all prime numbers below 400 that contain "79" as a substring.

First, let me think about what numbers below 400 could contain "79" as a substring:
- Numbers of the form 79X (where X is a digit): 790, 791, 792, 793, 794, 795, 796, 797, 798, 799
- Numbers of the form X79 (where X is a digit): 079 (which is just 79), 179, 279, 379
- Numbers of the form X79Y (where X and Y are digits): None below 400 since the smallest would be 1790

Wait, let me be more systematic. I need numbers below 400 that contain "79" as a substring.

The possible forms are:
1. 79 itself
2. 179, 279, 379 (three-digit numbers ending in 79)
3. Numbers starting with 79: but 790 and above are ≥ 790 > 400, so none of these work

So the candidates are: 79, 179, 279, 379

Now I need to check which of these are prime:

79: Let me check if 79 is prime.
79 = ? I need to check divisibility by primes up to √79 ≈ 8.9
Check 2: 79 is odd, so not divisible by 2
Check 3: 7+9 = 16, not divisible by 3
Check 5: doesn't end in 0 or 5
Check 7: 79 ÷ 7 = 11.28..., so 7 × 11 = 77, 79 - 77 = 2, so not divisible by 7
So 79 is prime.

179: Let me check if 179 is prime.
√179 ≈ 13.4, so I need to check primes up to 13


I systematically test divisibility, finding no factors that divide 179 evenly. The number passes multiple divisibility checks, including 2, 3, 5, 7, and 11. This suggests 179 is indeed a prime number.

I'll now investigate 279's primality. By quickly checking divisibility by 3, I discover 279 can be factored into 3 × 93, confirming it is not prime.

For 379, I recognize I'll need to check primes up to its square root. Initial divisibility tests for 2, 3, and 5 look promising, with no immediate factors detected.

Continuing systematic checks, I find no divisors up to 19. Precise calculations reveal no prime between 2 and 19 divides 379 evenly. This confirms 379's prime status.

Scanning the range below 400, I identify three primes containing "79": 79, 179, and 379.\
"""
                        ),
                        Text(
                            text="""\
Looking for primes below 400 that contain "79" as a substring.

The candidates are: 79, 179, 279, 379

Checking each for primality:
- 79: prime
- 179: prime  \n\
- 279: divisible by 3 (2+7+9=18), not prime
- 379: prime

3\
"""
                        ),
                    ],
                    provider="anthropic",
                    model_id="claude-sonnet-4-0",
                    raw_content=[],
                ),
                UserMessage(
                    content=[
                        Text(
                            text="If you remember what the primes were, then share them, or say 'I don't remember.'"
                        )
                    ]
                ),
                AssistantMessage(
                    content=[Text(text="The primes were 79, 179, and 379.")],
                    provider="anthropic",
                    model_id="claude-sonnet-4-0",
                    raw_content=[],
                ),
            ],
            "format": None,
            "tools": [],
        },
        "logging": [],
    }
)
async_snapshot = snapshot(
    {
        "response": {
            "provider": "anthropic",
            "model_id": "claude-sonnet-4-0",
            "params": {"thinking": False},
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
                    content=[
                        Thought(
                            thought="""\
I need to find all prime numbers below 400 that contain "79" as a substring.

First, let me think about what numbers below 400 could contain "79" as a substring:
- Numbers starting with 79: 79, 790, 791, 792, ..., 799 (but only 79 is below 400)
- Numbers with 79 in the middle: This would need to be at least 3 digits, so 179, 279, 379 are possibilities
- Numbers ending with 79: 79, 179, 279, 379

So the candidates are: 79, 179, 279, 379

Now I need to check which of these are prime:

79: Let me check if 79 is prime
- Is 79 divisible by 2? No (it's odd)
- Is 79 divisible by 3? 7+9 = 16, not divisible by 3
- Is 79 divisible by 5? No (doesn't end in 0 or 5)
- Is 79 divisible by 7? 79 ÷ 7 = 11.28..., not divisible
- Is 79 divisible by 11? 79 ÷ 11 = 7.18..., not divisible
- Since √79 ≈ 8.9, I only need to check up to 8
- Is 79 divisible by 8? No (79 is odd)

So 79 is prime.

179: Let me check if 179 is prime
- Is 179 divisible by 2? No (it's odd)
- Is 179 divisible by 3? 1+7+9 = 17, not divisible by 3
- Is 179 divisible by 5? No (doesn't end in 0 or 5)
- Is 179 divisible by 7? 179 ÷ 7 = 25.57..., not divisible


- Is 179 divisible by 11? 179 ÷ 11 = 16.27..., not divisible
- Is 179 divisible by 13? 179 ÷ 13 = 13.77..., not divisible
- Since √179 ≈ 13.4, I need to check up to 13
- Already checked up to 13

So 179 is prime.

279: I'll investigate its primality by checking divisibility
- The number is odd
- Sum of digits (2+7+9 = 18) suggests divisibility by 3
- Indeed, 279 ÷ 3 = 93, so 279 is not prime

379: Methodically testing divisibility
- Odd number
- Digit sum (3+7+9 = 19) not divisible by 3
- Not divisible by 5
- Checked divisibility up to 19
- No factors found within √379

So 379 is prime.

Primes with "79" below 400 are: 79, 179, and 379.

Total: 3 primes.\
"""
                        ),
                        Text(text="3"),
                    ],
                    provider="anthropic",
                    model_id="claude-sonnet-4-0",
                    raw_content=[],
                ),
                UserMessage(
                    content=[
                        Text(
                            text="If you remember what the primes were, then share them, or say 'I don't remember.'"
                        )
                    ]
                ),
                AssistantMessage(
                    content=[Text(text="I remember them: 79, 179, and 379.")],
                    provider="anthropic",
                    model_id="claude-sonnet-4-0",
                    raw_content=[],
                ),
            ],
            "format": None,
            "tools": [],
        },
        "logging": [],
    }
)
stream_snapshot = snapshot(
    {
        "response": {
            "provider": "anthropic",
            "model_id": "claude-sonnet-4-0",
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
                    content=[
                        Thought(
                            thought="""\
I need to find all prime numbers below 400 that contain "79" as a substring.

First, let me think about what numbers below 400 could contain "79" as a substring:
- Numbers that start with 79: 79, 790, 791, 792, ..., 799 (but we only go up to 400, so just 79)
- Numbers that have 79 in the middle: 179, 279, 379
- Numbers that end with 79: 179, 279, 379 (these are the same as the middle ones for 3-digit numbers)

Wait, let me be more systematic. The numbers below 400 that contain "79" as a substring are:
- 79
- 179  \n\
- 279
- 379

Now I need to check which of these are prime:

79: Let me check if 79 is prime
- Not divisible by 2 (it's odd)
- Not divisible by 3 (7+9=16, not divisible by 3)
- Not divisible by 5 (doesn't end in 0 or 5)
- Not divisible by 7 (79 ÷ 7 = 11.28...)
- Since √79 < 9, I only need to check primes up to 8, so I need to check 7
- 79 ÷ 7 = 11 remainder 2, so not divisible by 7
- So 79 is prime

179: Let me check if 179 is prime
- Not divisible by 2 (it's odd)
- Not divisible by 3 (1+7+9=17, not divisible by 3)
- Not divisible by 5 (doesn't end in 0 or 5)
- Not divisible by 7 (179 ÷ 7 = 25.57...)


- Not divisible by 11 (179 ÷ 11 = 16.27...)
- Not divisible by 13 (179 ÷ 13 = 13.77...)
- Since √179 ≈ 13.38, I need to check primes up to 13
- So 179 is prime

279: Let me check if 279 is prime
- Not divisible by 2 (it's odd)
- Let me check divisibility by 3: 2+7+9=18, which is divisible by 3
- So 279 is not prime, as it's divisible by 3

I'll continue checking the remaining number, 379, to see if it's prime.
- Odd number, so not divisible by 2
- Sum of digits not divisible by 3
- Doesn't end in 0 or 5, so not divisible by 5
- Checked divisibility by small primes
- Square root suggests checking primes up to 19
- Confirmed 379 is indeed prime

I've found three primes with "79" as a substring: 79, 179, and 379.

The total count is 3 primes.\
"""
                        ),
                        Text(
                            text="""\
Looking for primes below 400 that contain "79" as a substring:

The candidates are: 79, 179, 279, 379

Checking primality:
- 79: prime
- 179: prime  \n\
- 279: divisible by 3 (2+7+9=18), so not prime
- 379: prime

3\
"""
                        ),
                    ],
                    provider="anthropic",
                    model_id="claude-sonnet-4-0",
                    raw_content=[],
                ),
                UserMessage(
                    content=[
                        Text(
                            text="If you remember what the primes were, then share them, or say 'I don't remember.'"
                        )
                    ]
                ),
                AssistantMessage(
                    content=[Text(text="I remember them: 79, 179, and 379.")],
                    provider="anthropic",
                    model_id="claude-sonnet-4-0",
                    raw_content=[],
                ),
            ],
            "format": None,
            "tools": [],
            "n_chunks": 7,
        },
        "logging": [],
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider": "anthropic",
            "model_id": "claude-sonnet-4-0",
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
                    content=[
                        Thought(
                            thought="""\
I need to find all prime numbers below 400 that contain "79" as a substring.

First, let me think about what numbers below 400 could contain "79" as a substring:
- Numbers starting with 79: 79, 790, 791, 792, 793, 794, 795, 796, 797, 798, 799 (but we only go up to 399, so 790-399)
- Numbers with 79 in the middle: like 179, 279, 379
- Numbers ending with 79: like 179, 279, 379

Let me be more systematic. The numbers below 400 that contain "79" as a substring are:
- 79
- 179
- 279
- 379
- 790, 791, 792, 793, 794, 795, 796, 797, 798, 799 (but these are ≥ 400, so not relevant)

Wait, I need to be more careful. We're looking at numbers below 400, so the possible numbers are:
- 79
- 179  \n\
- 279
- 379

Now I need to check which of these are prime:

79: Let me check if 79 is prime.
79 = ? Let me check divisibility:
√79 ≈ 8.9, so I need to check divisibility by primes up to 8: 2, 3, 5, 7
- 79 is odd, so not divisible by 2
- 7+9 = 16, not divisible by 3
- Doesn't end in 0 or 5, so not divisible by 5  \n\
- 79 ÷ 7 = 11.28..., so not divisible by 7
So 79 is prime.

179: Let me check if 179 is prime.
√179 ≈ 13.4, so I need to check divisibility by primes up to 13: 2, 3, 5, 7, 11, 13


I systematically test divisibility, finding no factors that divide evenly. The number passes each divisibility test, confirming its primality.

I verify the division by 3 carefully, breaking down 279 into component parts to confirm it's composite. The calculation shows 279 = 3 × 93, definitively proving it's not prime.

For 379, I methodically check divisibility by primes up to its square root. After testing 2, 3, 5, 7, 11, 13, 17, and 19, no factors emerge. This confirms 379's prime status.

I meticulously validate each division, showing no prime less than √379 divides the number evenly. Each calculation confirms 379 remains prime.

The primes featuring "79" are 79, 179, and 379 - a concise set of three unique numbers.\
"""
                        ),
                        Text(
                            text="""\
Looking at numbers below 400 that contain "79" as a substring:

79, 179, 279, 379

Checking which are prime:
- 79: prime
- 179: prime  \n\
- 279: divisible by 3 (2+7+9=18), so not prime
- 379: prime

3\
"""
                        ),
                    ],
                    provider="anthropic",
                    model_id="claude-sonnet-4-0",
                    raw_content=[],
                ),
                UserMessage(
                    content=[
                        Text(
                            text="If you remember what the primes were, then share them, or say 'I don't remember.'"
                        )
                    ]
                ),
                AssistantMessage(
                    content=[Text(text="I remember them: 79, 179, and 379.")],
                    provider="anthropic",
                    model_id="claude-sonnet-4-0",
                    raw_content=[],
                ),
            ],
            "format": None,
            "tools": [],
            "n_chunks": 6,
        },
        "logging": [],
    }
)
without_raw_content_snapshot = snapshot(
    {
        "response": {
            "provider": "anthropic",
            "model_id": "claude-sonnet-4-0",
            "params": {"thinking": False},
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
                    content=[
                        Thought(
                            thought="""\
I need to find all prime numbers below 400 that contain "79" as a substring.

First, let me think about what numbers below 400 could contain "79" as a substring:
- Numbers of the form 79X (where X is a digit): 790, 791, 792, 793, 794, 795, 796, 797, 798, 799
- Numbers of the form X79 (where X is a digit): 179, 279, 379
- Numbers of the form X79Y (where X and Y are digits): This would give us numbers with at least 4 digits, so starting from 1000, which is above 400.

Wait, let me be more systematic. Numbers below 400 that contain "79":
- 79 itself
- 179
- 279
- 379
- Numbers starting with 79: but 79X where X ≠ 0 would be at least 791, which is above 400.

So the candidates are: 79, 179, 279, 379

Now I need to check which of these are prime:

79: Let me check if 79 is prime.
79 = ? \n\
√79 ≈ 8.9, so I need to check divisibility by primes up to 8: 2, 3, 5, 7
79 is odd, so not divisible by 2
79 = 7 + 9 = 16, 1 + 6 = 7, not divisible by 3
79 doesn't end in 0 or 5, so not divisible by 5
79 ÷ 7 = 11.28..., so not divisible by 7
79 is prime.

179: Let me check if 179 is prime.
√179 ≈ 13.4, so I need to check divisibility by primes up to 13: 2, 3, 5, 7, 11, 13


After systematically testing divisibility, I confirm 179 passes all prime number checks and is indeed prime.

279 fails the primality test. Its digital root is divisible by 3, and direct division shows 279 equals 3 × 93.

For 379, I'll methodically verify primality by checking divisors up to its square root. Initial tests show promise for potential primality, with no immediate divisibility by small primes.

After systematically testing divisors 2 through 19, I confirm 379 is indeed prime. Scanning primes below 400, I find three primes containing "79": 79, 179, and 379.\
"""
                        ),
                        Text(text="3"),
                    ],
                    provider="anthropic",
                    model_id="claude-sonnet-4-0",
                    raw_content=[],
                ),
                UserMessage(
                    content=[
                        Text(
                            text="If you remember what the primes were, then share them, or say 'I don't remember.'"
                        )
                    ]
                ),
                AssistantMessage(
                    content=[Text(text="I remember them: 79, 179, and 379.")],
                    provider="anthropic",
                    model_id="claude-sonnet-4-0",
                    raw_content=[],
                ),
            ],
            "format": None,
            "tools": [],
        },
        "logging": [],
    }
)
