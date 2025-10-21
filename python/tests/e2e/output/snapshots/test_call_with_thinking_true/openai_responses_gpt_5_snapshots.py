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
            "provider": "openai:responses",
            "model_id": "gpt-5",
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
**Counting primes with substring**

I need to figure out which prime numbers under 400 contain the substring "79" in their decimal representation. That means I should look for numbers like 79 itself and those including it as a consecutive pair of digits. The potential candidates are 79, 179, 279, and 379—I'll be focusing on that range to find the relevant primes. It seems I have a clear path to check for those specific patterns in decimal numbers.\
"""
                        ),
                        Thought(
                            thought="""\
**Determining prime candidates**

So, I'm refining my list of numbers under 400 that contain "79." The only valid candidates are 79, 179, 279, and 379. I need to check which of these are prime. \n\

I know 79 is prime. Now, for 179, I'll check primality by testing divisibility against primes up to the square root, which is about 13.38. It turns out 179 isn't divisible by any of those primes, confirming it's also prime! But 279 is definitely not prime, as it divides by 3. So I've narrowed it down effectively!\
"""
                        ),
                        Thought(
                            thought="""\
**Verifying primality of candidates**

I need to check if 379 is prime. The square root is about 19.46, so I’ll test it against primes up to that point. It turns out 379 is indeed prime because it’s not divisible by any of those smaller primes.

So, the primes under 400 that contain the substring “79” are 79, 179, and 379—making a total of three. I confirmed that post separation, digits won't count as "79", ensuring only those with consecutive digits qualify!\
"""
                        ),
                        Thought(
                            thought="""\
**Confirming final count of primes**

The count of primes containing the substring "79" remains at 3. I’ve double-checked for other combinations under 400, confirming that valid three-digit forms are limited to [1-3]79, and there aren't any valid two-digit candidates aside from 79 itself.

I also re-checked the primality of both 179 and 379, confirming they are indeed prime. So, I can confidently provide the answer as “3” without any additional details.\
"""
                        ),
                        Text(text="3"),
                    ],
                    provider="openai:responses",
                    model_id="gpt-5",
                    raw_message=[
                        {
                            "id": "rs_0082116a5a2628830068f2975e0e08819087ca8472035130bd",
                            "summary": [
                                {
                                    "text": """\
**Counting primes with substring**

I need to figure out which prime numbers under 400 contain the substring "79" in their decimal representation. That means I should look for numbers like 79 itself and those including it as a consecutive pair of digits. The potential candidates are 79, 179, 279, and 379—I'll be focusing on that range to find the relevant primes. It seems I have a clear path to check for those specific patterns in decimal numbers.\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Determining prime candidates**

So, I'm refining my list of numbers under 400 that contain "79." The only valid candidates are 79, 179, 279, and 379. I need to check which of these are prime. \n\

I know 79 is prime. Now, for 179, I'll check primality by testing divisibility against primes up to the square root, which is about 13.38. It turns out 179 isn't divisible by any of those primes, confirming it's also prime! But 279 is definitely not prime, as it divides by 3. So I've narrowed it down effectively!\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Verifying primality of candidates**

I need to check if 379 is prime. The square root is about 19.46, so I’ll test it against primes up to that point. It turns out 379 is indeed prime because it’s not divisible by any of those smaller primes.

So, the primes under 400 that contain the substring “79” are 79, 179, and 379—making a total of three. I confirmed that post separation, digits won't count as "79", ensuring only those with consecutive digits qualify!\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Confirming final count of primes**

The count of primes containing the substring "79" remains at 3. I’ve double-checked for other combinations under 400, confirming that valid three-digit forms are limited to [1-3]79, and there aren't any valid two-digit candidates aside from 79 itself.

I also re-checked the primality of both 179 and 379, confirming they are indeed prime. So, I can confidently provide the answer as “3” without any additional details.\
""",
                                    "type": "summary_text",
                                },
                            ],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_0082116a5a2628830068f29776713c81908d61359ae89236b5",
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
                    provider="openai:responses",
                    model_id="gpt-5",
                    raw_message=[
                        {
                            "id": "rs_0082116a5a2628830068f29777f1cc8190b6645119f231c826",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_0082116a5a2628830068f29778213c819093fe79c7e69b1024",
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
            "provider": "openai:responses",
            "model_id": "gpt-5",
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
**Counting primes with substring "79"**

I need to find the count of prime numbers below 400 that have the substring "79" in their decimal representation. The substring can appear in 2- or 3-digit numbers. The 2-digit number is just 79. For 3-digit numbers, valid forms are 179, 279, and 379 since they include "79" but must be less than 400. The 790-799 range is excluded as they exceed 400. So, I think we only have four numbers to consider.\
"""
                        ),
                        Thought(
                            thought="""\
**Checking primes with “79” substring**

I’m considering candidates with the substring "79" below 400. So far, these are 79, 179, 279, and 379. I noted that "79" can't appear crossing digit boundaries, and the range 790-799 exceeds 400, so those won’t work. Now, I need to determine which of these are prime numbers. \n\

79 is known to be prime. After testing 179, it’s also prime since it’s not divisible by any primes up to its square root. However, 279 is divisible by 3, so it’s not prime. Next, I’ll check 379.\
"""
                        ),
                        Thought(
                            thought="""\
**Finalizing prime count**

I’m testing whether 379 is prime by checking divisibility with primes up to 19. It’s not even, the sum of its digits (19) isn’t a multiple of 3, and it’s not divisible by 5, 7, 11, 13, 17, or 19. So, it’s confirmed as prime. \n\

From my candidates, I find that 79, 179, and 379 are all prime, totaling three primes. I also double-checked for any other numbers containing "79" but none match. So, the answer remains three!\
"""
                        ),
                        Thought(
                            thought="""\
**Confirming final count**

I checked the number 397, which doesn't contain the substring "79." The only candidates below 400 with "79" are 79, 179, and 379. While 279 is included, it's not prime. Just to ensure accuracy, I also looked at numbers like 197 that don't contain "79" and confirmed 279 and 297 aren't prime. Since 379 is prime and 790-799 are out of range, my final count of primes is indeed three. I’ll conclude with just the number: 3.\
"""
                        ),
                        Text(text="3"),
                    ],
                    provider="openai:responses",
                    model_id="gpt-5",
                    raw_message=[
                        {
                            "id": "rs_0cce3b068d5493670068f297e2d0d481969c0a486c14f78ad6",
                            "summary": [
                                {
                                    "text": """\
**Counting primes with substring "79"**

I need to find the count of prime numbers below 400 that have the substring "79" in their decimal representation. The substring can appear in 2- or 3-digit numbers. The 2-digit number is just 79. For 3-digit numbers, valid forms are 179, 279, and 379 since they include "79" but must be less than 400. The 790-799 range is excluded as they exceed 400. So, I think we only have four numbers to consider.\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Checking primes with “79” substring**

I’m considering candidates with the substring "79" below 400. So far, these are 79, 179, 279, and 379. I noted that "79" can't appear crossing digit boundaries, and the range 790-799 exceeds 400, so those won’t work. Now, I need to determine which of these are prime numbers. \n\

79 is known to be prime. After testing 179, it’s also prime since it’s not divisible by any primes up to its square root. However, 279 is divisible by 3, so it’s not prime. Next, I’ll check 379.\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Finalizing prime count**

I’m testing whether 379 is prime by checking divisibility with primes up to 19. It’s not even, the sum of its digits (19) isn’t a multiple of 3, and it’s not divisible by 5, 7, 11, 13, 17, or 19. So, it’s confirmed as prime. \n\

From my candidates, I find that 79, 179, and 379 are all prime, totaling three primes. I also double-checked for any other numbers containing "79" but none match. So, the answer remains three!\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Confirming final count**

I checked the number 397, which doesn't contain the substring "79." The only candidates below 400 with "79" are 79, 179, and 379. While 279 is included, it's not prime. Just to ensure accuracy, I also looked at numbers like 197 that don't contain "79" and confirmed 279 and 297 aren't prime. Since 379 is prime and 790-799 are out of range, my final count of primes is indeed three. I’ll conclude with just the number: 3.\
""",
                                    "type": "summary_text",
                                },
                            ],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_0cce3b068d5493670068f297f4a230819685891308a6bd86b0",
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
                    provider="openai:responses",
                    model_id="gpt-5",
                    raw_message=[
                        {
                            "id": "rs_0cce3b068d5493670068f297f637a08196a1deefce5fbb267b",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_0cce3b068d5493670068f297f670f48196bf265dc9b289138d",
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
            "provider": "openai:responses",
            "model_id": "gpt-5",
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
**Finding primes with substring "79"**

I’m looking for prime numbers under 400 that contain the substring "79." First, the only 2-digit prime is 79 itself, giving me one candidate. \n\

For 3-digit primes, I considered numbers of the form 79x, but those fall outside the 400 limit, so there are none. \n\

Then I checked numbers like x79, where x can be 1-3. This gives me candidates: 179, 279, and 379, which I need to verify for primality. \n\

Finally, I realized that "79" must be adjacent, ruling out non-adjacent digits.\
"""
                        ),
                        Thought(
                            thought="""\
**Testing candidates for primality**

I’ve established that only adjacent digits matter for the "79" substring. There’s also a possibility of having "79" in the middle of a 3-digit number, but those options are limited. My candidates are 79, 179, 279, and 379, and I need to test the primality of 179, 279, and 379.

Starting with 179, after checking divisibility against primes up to around 13, I find it’s prime. For 279, since the sum of digits equals 18, it’s divisible by 3, so it’s not prime. \n\

Finally, I check 379, and it doesn’t seem divisible by the primes I tested either.\
"""
                        ),
                        Thought(
                            thought="""\
**Counting primes with "79"**

After testing, I confirmed that 379 is also prime. So far, I have 79, 179, and 379 as primes, making a count of three. \n\

I wondered if there are any other numbers under 400 with the substring "79." Well, I already included 79, and I considered 297, but it contains "97," not "79." \n\

I realized my criteria for 3-digit numbers can only lead to x79 or 79x, but those like 79x (790 or higher) exceed 400. My total remains three primes: I’ll double-check to ensure there are no others under 400. \n\

After confirming, I finalize the answer as "3."\
"""
                        ),
                        Thought(
                            thought="""\
**Finalizing the count**

I'm checking the user’s request for numbers "below 400." Typically, that means less than 400, so 79 is definitely included in my count. I want to be accurate here. \n\

Since I found three prime numbers containing the substring "79" (79, 179, and 379), I can confidently say the answer is exactly "3." I'll make sure to keep it clear, just providing that number, with no additional text.\
"""
                        ),
                        Text(text="3"),
                    ],
                    provider="openai:responses",
                    model_id="gpt-5",
                    raw_message=[
                        {
                            "id": "rs_00c8480f43d079250068f297ab91608195931c432c34fd7b8e",
                            "summary": [
                                {
                                    "text": """\
**Finding primes with substring "79"**

I’m looking for prime numbers under 400 that contain the substring "79." First, the only 2-digit prime is 79 itself, giving me one candidate. \n\

For 3-digit primes, I considered numbers of the form 79x, but those fall outside the 400 limit, so there are none. \n\

Then I checked numbers like x79, where x can be 1-3. This gives me candidates: 179, 279, and 379, which I need to verify for primality. \n\

Finally, I realized that "79" must be adjacent, ruling out non-adjacent digits.\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Testing candidates for primality**

I’ve established that only adjacent digits matter for the "79" substring. There’s also a possibility of having "79" in the middle of a 3-digit number, but those options are limited. My candidates are 79, 179, 279, and 379, and I need to test the primality of 179, 279, and 379.

Starting with 179, after checking divisibility against primes up to around 13, I find it’s prime. For 279, since the sum of digits equals 18, it’s divisible by 3, so it’s not prime. \n\

Finally, I check 379, and it doesn’t seem divisible by the primes I tested either.\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Counting primes with "79"**

After testing, I confirmed that 379 is also prime. So far, I have 79, 179, and 379 as primes, making a count of three. \n\

I wondered if there are any other numbers under 400 with the substring "79." Well, I already included 79, and I considered 297, but it contains "97," not "79." \n\

I realized my criteria for 3-digit numbers can only lead to x79 or 79x, but those like 79x (790 or higher) exceed 400. My total remains three primes: I’ll double-check to ensure there are no others under 400. \n\

After confirming, I finalize the answer as "3."\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Finalizing the count**

I'm checking the user’s request for numbers "below 400." Typically, that means less than 400, so 79 is definitely included in my count. I want to be accurate here. \n\

Since I found three prime numbers containing the substring "79" (79, 179, and 379), I can confidently say the answer is exactly "3." I'll make sure to keep it clear, just providing that number, with no additional text.\
""",
                                    "type": "summary_text",
                                },
                            ],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_00c8480f43d079250068f297bd2e7881959d4a40334d943244",
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
                    provider="openai:responses",
                    model_id="gpt-5",
                    raw_message=[
                        {
                            "id": "rs_00c8480f43d079250068f297be563c819585de932de447cba0",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_00c8480f43d079250068f297be8238819593d2dbf1908f29a8",
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
            "n_chunks": 6,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider": "openai:responses",
            "model_id": "gpt-5",
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

I need to find primes under 400 that contain the substring "79". First, I think of 79 itself, then 179, and check if 197 doesn’t count since it has "97". I realize 279 isn't prime, and 379 seems to be prime. However, 479 and any number in the 790s are greater than 400. Therefore, the only prime under 100 containing "79" is just 79. It's quite a specific search!\
"""
                        ),
                        Thought(
                            thought="""\
**Finding primes with "79"**

I’m examining the numbers between 100 and 199 to see which contain "79," and I find that only 179 fits because it's the only one with "79" in the last digits. I'll confirm that 179 is prime — and it is!

Next, looking in the range of 200 to 299, I see that 279 is composite, as it’s divisible by 3. In this range, there are no additional candidates. Lastly, for 300 to 399, I found 379 and confirmed it’s prime too. So, 179 and 379 are our primes!\
"""
                        ),
                        Thought(
                            thought="""\
**Confirming prime counts with "79"**

I’m considering numbers like 790, which is over 400. I check other primes like 97, 197, 297, and 397, but they don’t contain "79." The only primes that do are 79, 179, and 379. I realize that only two-digit primes are relevant, as numbers like 790-799 exceed 400.

I’ve confirmed that 279 isn’t prime, but 179 and 379 are. It seems the total count of primes with "79" is three. I wonder if there are any other numbers I might have missed, like 97.\
"""
                        ),
                        Thought(
                            thought="""\
**Confirming prime counts with "79"**

I realize 79 reversed doesn't count, so I'm confirming the three primes identified: 79, 179, and 379. \n\

First, I check 79 and confirm it’s prime. For 179, I find that it passes checks for primes under its square root, so it’s also prime. 279 is composite since it's divisible by 3. I’ve previously confirmed that 379 is prime, leaving the total count as three. I reflect on whether numbers with leading zeros count but decide against it. \n\

So, the answer is simply "3."\
"""
                        ),
                        Text(text="3"),
                    ],
                    provider="openai:responses",
                    model_id="gpt-5",
                    raw_message=[
                        {
                            "id": "rs_02f178f89a7dc2940068f2980af9c081939c98cd23b6fe897e",
                            "summary": [
                                {
                                    "text": """\
**Counting primes with "79"**

I need to find primes under 400 that contain the substring "79". First, I think of 79 itself, then 179, and check if 197 doesn’t count since it has "97". I realize 279 isn't prime, and 379 seems to be prime. However, 479 and any number in the 790s are greater than 400. Therefore, the only prime under 100 containing "79" is just 79. It's quite a specific search!\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Finding primes with "79"**

I’m examining the numbers between 100 and 199 to see which contain "79," and I find that only 179 fits because it's the only one with "79" in the last digits. I'll confirm that 179 is prime — and it is!

Next, looking in the range of 200 to 299, I see that 279 is composite, as it’s divisible by 3. In this range, there are no additional candidates. Lastly, for 300 to 399, I found 379 and confirmed it’s prime too. So, 179 and 379 are our primes!\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Confirming prime counts with "79"**

I’m considering numbers like 790, which is over 400. I check other primes like 97, 197, 297, and 397, but they don’t contain "79." The only primes that do are 79, 179, and 379. I realize that only two-digit primes are relevant, as numbers like 790-799 exceed 400.

I’ve confirmed that 279 isn’t prime, but 179 and 379 are. It seems the total count of primes with "79" is three. I wonder if there are any other numbers I might have missed, like 97.\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Confirming prime counts with "79"**

I realize 79 reversed doesn't count, so I'm confirming the three primes identified: 79, 179, and 379. \n\

First, I check 79 and confirm it’s prime. For 179, I find that it passes checks for primes under its square root, so it’s also prime. 279 is composite since it's divisible by 3. I’ve previously confirmed that 379 is prime, leaving the total count as three. I reflect on whether numbers with leading zeros count but decide against it. \n\

So, the answer is simply "3."\
""",
                                    "type": "summary_text",
                                },
                            ],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_02f178f89a7dc2940068f2981f63a881938f1f5b380b083869",
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
                    provider="openai:responses",
                    model_id="gpt-5",
                    raw_message=[
                        {
                            "id": "rs_02f178f89a7dc2940068f2983c9de08193b5562b3fdec4d315",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_02f178f89a7dc2940068f2983cd9508193bbecf71995719523",
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
            "n_chunks": 6,
        }
    }
)
