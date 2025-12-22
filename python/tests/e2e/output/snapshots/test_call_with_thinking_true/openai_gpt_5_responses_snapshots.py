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
            "provider_id": "openai",
            "model_id": "openai/gpt-5:responses",
            "provider_model_name": "gpt-5:responses",
            "params": {"thinking": False},
            "finish_reason": None,
            "usage": {
                "input_tokens": 62,
                "output_tokens": 10,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "ResponseUsage(input_tokens=62, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=10, output_tokens_details=OutputTokensDetails(reasoning_tokens=0), total_tokens=72)",
                "total_tokens": 72,
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
                        Thought(
                            thought="""\
**Counting prime numbers with 79**

I need to find prime numbers below 400 that contain "79" as a substring. This means I’m looking for numbers with "79" as contiguous digits. So, they would be 79, 179, 279, and 379. The range from 790-799 is not applicable since we're under 400. I need to verify numbers like 791, 793, and 797 as three-digit primes that might fit but since they have to be below 400, I focus on the valid ones.\
"""
                        ),
                        Thought(
                            thought="""\
**Identifying primes containing 79**

I realized I made a mistake by limiting the scope to just numbers that end with "79." Both forms matter: "79x" and "x79." However, numbers like 790-799 aren't below 400, so I can't consider those. Given my constraints, the only valid numbers are 79, 179, 279, and 379. Now, I need to confirm which of these are prime. I know 79 is prime, and I also confirm that 179 is a prime number.\
"""
                        ),
                        Thought(
                            thought="""\
**Testing primality of candidates**

I found that 279 is not prime because it’s divisible by 3 — the sum of its digits, 18, is divisible by 3. That means 279 equals 3 multiplied by 93. Now, for 379, I'll check if it's prime by testing divisibility with primes up to its square root, which is about 19.467. After testing, I confirm that 379 is prime. \n\

As for 179, it's also prime after testing divisibility. So, the valid primes in my candidate list are 79, 179, and 379. That gives me a total of three primes.\
"""
                        ),
                        Thought(
                            thought="""\
**Finalizing the count of primes**

I want to double-check if there are any other primes under 400 that contain "79." 279 is composite, while 79, 179, and 379 are confirmed primes. Checking if "79" can be formed with a digit between them doesn't apply since it has to be contiguous. I also considered if numbers like 197 contain "79," but they don’t. Thus, I’m confident that the total count of qualifying primes is 3. The user requested just the number, so my answer is simply "3."\
"""
                        ),
                        Text(text="3"),
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-5:responses",
                    provider_model_name="gpt-5:responses",
                    raw_message=[
                        {
                            "id": "rs_06c3415857cabd720069494d6b87e0819393b5cd71d7d3ff8d",
                            "summary": [
                                {
                                    "text": """\
**Counting prime numbers with 79**

I need to find prime numbers below 400 that contain "79" as a substring. This means I’m looking for numbers with "79" as contiguous digits. So, they would be 79, 179, 279, and 379. The range from 790-799 is not applicable since we're under 400. I need to verify numbers like 791, 793, and 797 as three-digit primes that might fit but since they have to be below 400, I focus on the valid ones.\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Identifying primes containing 79**

I realized I made a mistake by limiting the scope to just numbers that end with "79." Both forms matter: "79x" and "x79." However, numbers like 790-799 aren't below 400, so I can't consider those. Given my constraints, the only valid numbers are 79, 179, 279, and 379. Now, I need to confirm which of these are prime. I know 79 is prime, and I also confirm that 179 is a prime number.\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Testing primality of candidates**

I found that 279 is not prime because it’s divisible by 3 — the sum of its digits, 18, is divisible by 3. That means 279 equals 3 multiplied by 93. Now, for 379, I'll check if it's prime by testing divisibility with primes up to its square root, which is about 19.467. After testing, I confirm that 379 is prime. \n\

As for 179, it's also prime after testing divisibility. So, the valid primes in my candidate list are 79, 179, and 379. That gives me a total of three primes.\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Finalizing the count of primes**

I want to double-check if there are any other primes under 400 that contain "79." 279 is composite, while 79, 179, and 379 are confirmed primes. Checking if "79" can be formed with a digit between them doesn't apply since it has to be contiguous. I also considered if numbers like 197 contain "79," but they don’t. Thus, I’m confident that the total count of qualifying primes is 3. The user requested just the number, so my answer is simply "3."\
""",
                                    "type": "summary_text",
                                },
                            ],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_06c3415857cabd720069494d8d9db0819399e41a0b11b72bdf",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": "3",
                                    "type": "output_text",
                                    "logprobs": [],
                                }
                            ],
                            "role": "assistant",
                            "status": "completed",
                            "type": "message",
                        },
                    ],
                ),
                UserMessage(
                    content=[
                        Text(
                            text="If you remember what the primes were, then share them, or say 'I don't remember.'"
                        )
                    ]
                ),
                AssistantMessage(
                    content=[Text(text="I don't remember.")],
                    provider_id="openai",
                    model_id="openai/gpt-5:responses",
                    provider_model_name="gpt-5:responses",
                    raw_message=[
                        {
                            "id": "rs_06c3415857cabd720069494d8ebe648193a2abd3a8a2fda89a",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_06c3415857cabd720069494d8f07148193b144c31df0dcb19c",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": "I don't remember.",
                                    "type": "output_text",
                                    "logprobs": [],
                                }
                            ],
                            "role": "assistant",
                            "status": "completed",
                            "type": "message",
                        },
                    ],
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
            "provider_id": "openai",
            "model_id": "openai/gpt-5:responses",
            "provider_model_name": "gpt-5:responses",
            "params": {"thinking": False},
            "finish_reason": None,
            "usage": {
                "input_tokens": 62,
                "output_tokens": 10,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "ResponseUsage(input_tokens=62, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=10, output_tokens_details=OutputTokensDetails(reasoning_tokens=0), total_tokens=72)",
                "total_tokens": 72,
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
                        Thought(
                            thought="""\
**Counting prime numbers with "79"**

I need to find prime numbers below 400 that have "79" as a substring. The candidates are 79, 179, 279, and 379. I can see that 79 is prime. However, numbers from 790 to 799 don't count since they exceed 400. I notice that "97" contains 79 reversed, but reversed doesn't count. \n\

So, the only relevant primes under 400 are 79, 179, 279, and 379. I’m confirming their primality as I check!\
"""
                        ),
                        Thought(
                            thought="""\
**Checking candidate primes**

I need to check which candidates below 400 are prime. The candidates are 79, 179, 279, and 379. I know 79 is prime. For 179, it's also prime, confirmed by checking it against smaller primes, and it's not divisible by any of them. \n\

However, 279 is not prime since it’s divisible by 3. As for 379, after checking divisibility with primes up to its square root, I find that 379 is indeed prime too. It's nice to confirm these!\
"""
                        ),
                        Thought(
                            thought="""\
**Confirming prime count**

So, I’ve identified the primes below 400 that contain "79": those are 79, 179, and 379, giving me a count of 3. I want to double-check for other candidates, like 197 or 297, but neither of those contains "79" properly. \n\

397 and 97 don't qualify either. Then I confirm that we’re only considering positive primes below 400—negative numbers don’t count. I’ve checked all the necessary details, and it’s all looking solid. The final count is 3!\
"""
                        ),
                        Thought(
                            thought="""\
**Finalizing the answer**

I need to ensure I'm clear: 97 doesn't contain "79" as a substring, even across boundary in base 10. So we definitely don’t count it. While 1979 includes "79," it exceeds 400, so it also doesn't count. \n\

After careful consideration, I can confidently say the count of primes below 400 containing the substring "79" is 3. I'll return just the number: 3. That should satisfy the user’s request perfectly!\
"""
                        ),
                        Text(text="3"),
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-5:responses",
                    provider_model_name="gpt-5:responses",
                    raw_message=[
                        {
                            "id": "rs_033ee4bc00eb555d0069494da830a08196bea87483b2b1ba36",
                            "summary": [
                                {
                                    "text": """\
**Counting prime numbers with "79"**

I need to find prime numbers below 400 that have "79" as a substring. The candidates are 79, 179, 279, and 379. I can see that 79 is prime. However, numbers from 790 to 799 don't count since they exceed 400. I notice that "97" contains 79 reversed, but reversed doesn't count. \n\

So, the only relevant primes under 400 are 79, 179, 279, and 379. I’m confirming their primality as I check!\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Checking candidate primes**

I need to check which candidates below 400 are prime. The candidates are 79, 179, 279, and 379. I know 79 is prime. For 179, it's also prime, confirmed by checking it against smaller primes, and it's not divisible by any of them. \n\

However, 279 is not prime since it’s divisible by 3. As for 379, after checking divisibility with primes up to its square root, I find that 379 is indeed prime too. It's nice to confirm these!\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Confirming prime count**

So, I’ve identified the primes below 400 that contain "79": those are 79, 179, and 379, giving me a count of 3. I want to double-check for other candidates, like 197 or 297, but neither of those contains "79" properly. \n\

397 and 97 don't qualify either. Then I confirm that we’re only considering positive primes below 400—negative numbers don’t count. I’ve checked all the necessary details, and it’s all looking solid. The final count is 3!\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Finalizing the answer**

I need to ensure I'm clear: 97 doesn't contain "79" as a substring, even across boundary in base 10. So we definitely don’t count it. While 1979 includes "79," it exceeds 400, so it also doesn't count. \n\

After careful consideration, I can confidently say the count of primes below 400 containing the substring "79" is 3. I'll return just the number: 3. That should satisfy the user’s request perfectly!\
""",
                                    "type": "summary_text",
                                },
                            ],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_033ee4bc00eb555d0069494dbe3ff0819697e28937cfddde94",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": "3",
                                    "type": "output_text",
                                    "logprobs": [],
                                }
                            ],
                            "role": "assistant",
                            "status": "completed",
                            "type": "message",
                        },
                    ],
                ),
                UserMessage(
                    content=[
                        Text(
                            text="If you remember what the primes were, then share them, or say 'I don't remember.'"
                        )
                    ]
                ),
                AssistantMessage(
                    content=[Text(text="I don't remember.")],
                    provider_id="openai",
                    model_id="openai/gpt-5:responses",
                    provider_model_name="gpt-5:responses",
                    raw_message=[
                        {
                            "id": "rs_033ee4bc00eb555d0069494dbf2c988196bb7c28811e2b9953",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_033ee4bc00eb555d0069494dbf8ae08196b9574e68f98417a2",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": "I don't remember.",
                                    "type": "output_text",
                                    "logprobs": [],
                                }
                            ],
                            "role": "assistant",
                            "status": "completed",
                            "type": "message",
                        },
                    ],
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
            "provider_id": "openai",
            "model_id": "openai/gpt-5:responses",
            "provider_model_name": "gpt-5:responses",
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
**Counting prime numbers with "79"**

I need to find the prime numbers less than 400 that contain the substring "79." Let's start by listing those primes. The two-digit prime is 79, and then the three-digit primes include 179, 279, and 379. Primes above 400 are not relevant here.

The numbers in the range of 790-799 include "79," but they’re all above 400, so they're also irrelevant. Ultimately, I find that the only primes containing "79" under 400 are 79, 179, 279, and 379.\
"""
                        ),
                        Thought(
                            thought="""\
**Evaluating primes containing "79"**

I'm considering the three-digit numbers under 400 that might contain "79." The sequence can only appear in certain ways: as the last two digits (like 179, 279, 379) or the first two, which isn't allowed here since that would make it 79x, exceeding 400. \n\

So, my candidates are 79, 179, 279, and 379. Now, checking which of these are prime: 79 and 179 both check out as prime numbers, while 279 is composite since it's divisible by 3. Lastly, it looks like 379 is prime!\
"""
                        ),
                        Thought(
                            thought="""\
**Confirming prime count with "79"**

I’m checking to confirm that 379 is prime by testing all primes up to its square root, which is approximately 19.467. I find that it isn't divisible by primes like 5, 7, 11, 13, 17, or 19, so 379 is indeed prime.

Next, I check if other numbers like 97 or 197 contain "79," but they do not. The only primes under 400 that contain the substring "79" are 79, 179, and 379. Therefore, the total count of primes below 400 containing "79" is 3.\
"""
                        ),
                        Thought(
                            thought="""\
**Finalizing count of primes with "79"**

I've confirmed that 79, 179, and 379 are all prime numbers that contain the substring "79." I've also checked for other candidates under 400, and 279 is composite. After verifying that 179 is prime through various divisibility tests, it holds up. \n\

I've double-checked primes up to the square root of 379 for completeness, and everything checks out. So, it looks like I can confidently say the final answer is 3.\
"""
                        ),
                        Text(text="3"),
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-5:responses",
                    provider_model_name="gpt-5:responses",
                    raw_message=[
                        {
                            "id": "rs_0267eb1da113a32e0069494d907fb4819696883f87f4271ee6",
                            "summary": [
                                {
                                    "text": """\
**Counting prime numbers with "79"**

I need to find the prime numbers less than 400 that contain the substring "79." Let's start by listing those primes. The two-digit prime is 79, and then the three-digit primes include 179, 279, and 379. Primes above 400 are not relevant here.

The numbers in the range of 790-799 include "79," but they’re all above 400, so they're also irrelevant. Ultimately, I find that the only primes containing "79" under 400 are 79, 179, 279, and 379.\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Evaluating primes containing "79"**

I'm considering the three-digit numbers under 400 that might contain "79." The sequence can only appear in certain ways: as the last two digits (like 179, 279, 379) or the first two, which isn't allowed here since that would make it 79x, exceeding 400. \n\

So, my candidates are 79, 179, 279, and 379. Now, checking which of these are prime: 79 and 179 both check out as prime numbers, while 279 is composite since it's divisible by 3. Lastly, it looks like 379 is prime!\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Confirming prime count with "79"**

I’m checking to confirm that 379 is prime by testing all primes up to its square root, which is approximately 19.467. I find that it isn't divisible by primes like 5, 7, 11, 13, 17, or 19, so 379 is indeed prime.

Next, I check if other numbers like 97 or 197 contain "79," but they do not. The only primes under 400 that contain the substring "79" are 79, 179, and 379. Therefore, the total count of primes below 400 containing "79" is 3.\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Finalizing count of primes with "79"**

I've confirmed that 79, 179, and 379 are all prime numbers that contain the substring "79." I've also checked for other candidates under 400, and 279 is composite. After verifying that 179 is prime through various divisibility tests, it holds up. \n\

I've double-checked primes up to the square root of 379 for completeness, and everything checks out. So, it looks like I can confidently say the final answer is 3.\
""",
                                    "type": "summary_text",
                                },
                            ],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_0267eb1da113a32e0069494da5723081968396edb35944b5c3",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": "3",
                                    "type": "output_text",
                                    "logprobs": [],
                                }
                            ],
                            "role": "assistant",
                            "status": "completed",
                            "type": "message",
                        },
                    ],
                ),
                UserMessage(
                    content=[
                        Text(
                            text="If you remember what the primes were, then share them, or say 'I don't remember.'"
                        )
                    ]
                ),
                AssistantMessage(
                    content=[Text(text="I don't remember.")],
                    provider_id="openai",
                    model_id="openai/gpt-5:responses",
                    provider_model_name="gpt-5:responses",
                    raw_message=[
                        {
                            "id": "rs_0267eb1da113a32e0069494da6ada481969bc01d0080fc1853",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_0267eb1da113a32e0069494da700d88196883c80b7f6eaf077",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": "I don't remember.",
                                    "type": "output_text",
                                    "logprobs": [],
                                }
                            ],
                            "role": "assistant",
                            "status": "completed",
                            "type": "message",
                        },
                    ],
                ),
            ],
            "format": None,
            "tools": [],
            "usage": {
                "input_tokens": 62,
                "output_tokens": 10,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 72,
            },
            "n_chunks": 6,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "openai",
            "model_id": "openai/gpt-5:responses",
            "provider_model_name": "gpt-5:responses",
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
**Counting primes with "79"**

I'm checking for prime numbers less than 400 that include "79" as a substring. The valid candidates are 79, 179, 279, and 379. Numbers like 790-799 are excluded since they exceed 400. \n\

Now, I need to verify which of these are prime. I know 79 is prime. Next, I’ll check 179 for divisibility — its square root is about 13.38, so I need to check against the primes up to 13. This will help narrow down the list.\
"""
                        ),
                        Thought(
                            thought="""\
**Checking primality of candidates**

I found some interesting details while checking the primes with "79." For 79, the sum of the digits is 17, which isn’t a multiple of 3, and it’s not divisible by 7, 11, or 13, confirming it's prime. \n\

Next, for 279, the sum of the digits is 18, making it divisible by 3, so it's not prime. \n\

Moving on to 379, with a square root around 19.4, I checked through primes and confirmed it's also prime. This gives me three primes: 79, 179, and 379. I wonder about any three-digit numbers containing "79"? They'd be in the range of 790-799, but I need to exclude those since they’re too high.\
"""
                        ),
                        Thought(
                            thought="""\
**Finalizing the count of primes**

I carefully considered the placements of "79" in various combinations. We confirmed that the candidates are 179, 279, and 379, totaling three valid entries. \n\

Next, I made sure that 279 is composite, as it's divisible by 3. However, I also confirmed that 97 reversed doesn't count, even when looking at other variations like 297, 397, and 197. \n\

So just to be clear, the final answer should indeed be "3," including 79, which is also under 400. I'm finalizing this now!\
"""
                        ),
                        Text(text="3"),
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-5:responses",
                    provider_model_name="gpt-5:responses",
                    raw_message=[
                        {
                            "id": "rs_0534fb6e1ebc05960069494dc10a608195b0beba4e369189d6",
                            "summary": [
                                {
                                    "text": """\
**Counting primes with "79"**

I'm checking for prime numbers less than 400 that include "79" as a substring. The valid candidates are 79, 179, 279, and 379. Numbers like 790-799 are excluded since they exceed 400. \n\

Now, I need to verify which of these are prime. I know 79 is prime. Next, I’ll check 179 for divisibility — its square root is about 13.38, so I need to check against the primes up to 13. This will help narrow down the list.\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Checking primality of candidates**

I found some interesting details while checking the primes with "79." For 79, the sum of the digits is 17, which isn’t a multiple of 3, and it’s not divisible by 7, 11, or 13, confirming it's prime. \n\

Next, for 279, the sum of the digits is 18, making it divisible by 3, so it's not prime. \n\

Moving on to 379, with a square root around 19.4, I checked through primes and confirmed it's also prime. This gives me three primes: 79, 179, and 379. I wonder about any three-digit numbers containing "79"? They'd be in the range of 790-799, but I need to exclude those since they’re too high.\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Finalizing the count of primes**

I carefully considered the placements of "79" in various combinations. We confirmed that the candidates are 179, 279, and 379, totaling three valid entries. \n\

Next, I made sure that 279 is composite, as it's divisible by 3. However, I also confirmed that 97 reversed doesn't count, even when looking at other variations like 297, 397, and 197. \n\

So just to be clear, the final answer should indeed be "3," including 79, which is also under 400. I'm finalizing this now!\
""",
                                    "type": "summary_text",
                                },
                            ],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_0534fb6e1ebc05960069494dd538248195b3ae4cd0135501e4",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": "3",
                                    "type": "output_text",
                                    "logprobs": [],
                                }
                            ],
                            "role": "assistant",
                            "status": "completed",
                            "type": "message",
                        },
                    ],
                ),
                UserMessage(
                    content=[
                        Text(
                            text="If you remember what the primes were, then share them, or say 'I don't remember.'"
                        )
                    ]
                ),
                AssistantMessage(
                    content=[Text(text="I don't remember.")],
                    provider_id="openai",
                    model_id="openai/gpt-5:responses",
                    provider_model_name="gpt-5:responses",
                    raw_message=[
                        {
                            "id": "rs_0534fb6e1ebc05960069494dd6576881959070c54ea9d208a2",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_0534fb6e1ebc05960069494dd69b848195b9236f18dd7d0b3c",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": "I don't remember.",
                                    "type": "output_text",
                                    "logprobs": [],
                                }
                            ],
                            "role": "assistant",
                            "status": "completed",
                            "type": "message",
                        },
                    ],
                ),
            ],
            "format": None,
            "tools": [],
            "usage": {
                "input_tokens": 62,
                "output_tokens": 10,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 72,
            },
            "n_chunks": 6,
        }
    }
)
