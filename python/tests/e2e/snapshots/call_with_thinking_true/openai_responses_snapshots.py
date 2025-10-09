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
**Counting primes with substring '79'**

I need to count primes below 400 that have "79" as a substring. The candidates so far are 79, 179, 279, and 379. I remember that anything above 400 is out, so numbers like 790-799 won't count. Since two-digit numbers yield only 79, we focus on three-digit numbers. I confirm that 179, 279, and 379 fit the criteria. Oh, and 197 is out since it doesn't contain "79." I think I'm on the right track!\
"""
                        ),
                        Thought(
                            thought="""\
**Identifying prime candidates**

So, let's see if I'm counting correctly. 197 has the digits '1, 9, 7', but it doesn't include "79" in the right order, just '9, 7' which isn't consecutive. Now, 379, 279, and 179 do meet the criteria. Numbers like 790-799 are above 400, so they won't count. I just want to double-check the primality of my candidates: 79, 179, 279, and 379. For 79, I confirm it's prime. Now to check 179, testing divisibility against primes up to the square root!\
"""
                        ),
                        Thought(
                            thought="""\
**Checking for primality**

Alright, I’m checking the primality of my candidates. For 179, I found it's not divisible by 2, 3, 5, 7, 11, or 13, confirming it's prime. Now, for 279, it’s a no-go since its digit sum (2 + 7 + 9) is 18, meaning it's divisible by 3, making it composite. Moving on to 379, it seems prime based on checks with primes up to about 19. I can count my primes: 79, 179, and 379, giving us a total of 3!\
"""
                        ),
                        Thought(
                            thought="""\
**Double-checking for substring '79'**

I want to ensure that no other numbers below 400 contain the substring "79." For example, 297 has the digits '2, 9, 7', not '7, 9'. I confirm that the numbers from 170-179 only include 179 with "79," while other groups like 270-279 and 370-379 include 279 and 379, respectively. Also, numbers like 790 are above 400 and don’t count. After reviewing all candidates, I finalize the count at 3 and confirm that 379 is indeed prime. I’m ready to deliver the answer: 3!\
"""
                        ),
                        Text(text="3"),
                    ],
                    provider="openai:responses",
                    model_id="gpt-5",
                    raw_content=[
                        {
                            "id": "rs_057d8eab6aa601aa0068e70ff854b881968f85dbff3d07f2c8",
                            "summary": [
                                {
                                    "text": """\
**Counting primes with substring '79'**

I need to count primes below 400 that have "79" as a substring. The candidates so far are 79, 179, 279, and 379. I remember that anything above 400 is out, so numbers like 790-799 won't count. Since two-digit numbers yield only 79, we focus on three-digit numbers. I confirm that 179, 279, and 379 fit the criteria. Oh, and 197 is out since it doesn't contain "79." I think I'm on the right track!\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Identifying prime candidates**

So, let's see if I'm counting correctly. 197 has the digits '1, 9, 7', but it doesn't include "79" in the right order, just '9, 7' which isn't consecutive. Now, 379, 279, and 179 do meet the criteria. Numbers like 790-799 are above 400, so they won't count. I just want to double-check the primality of my candidates: 79, 179, 279, and 379. For 79, I confirm it's prime. Now to check 179, testing divisibility against primes up to the square root!\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Checking for primality**

Alright, I’m checking the primality of my candidates. For 179, I found it's not divisible by 2, 3, 5, 7, 11, or 13, confirming it's prime. Now, for 279, it’s a no-go since its digit sum (2 + 7 + 9) is 18, meaning it's divisible by 3, making it composite. Moving on to 379, it seems prime based on checks with primes up to about 19. I can count my primes: 79, 179, and 379, giving us a total of 3!\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Double-checking for substring '79'**

I want to ensure that no other numbers below 400 contain the substring "79." For example, 297 has the digits '2, 9, 7', not '7, 9'. I confirm that the numbers from 170-179 only include 179 with "79," while other groups like 270-279 and 370-379 include 279 and 379, respectively. Also, numbers like 790 are above 400 and don’t count. After reviewing all candidates, I finalize the count at 3 and confirm that 379 is indeed prime. I’m ready to deliver the answer: 3!\
""",
                                    "type": "summary_text",
                                },
                            ],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_057d8eab6aa601aa0068e7100e66e4819697ee9d4b6fa2f649",
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
                    raw_content=[
                        {
                            "id": "rs_057d8eab6aa601aa0068e7100f65748196b04c25b03e540844",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_057d8eab6aa601aa0068e7100f8e888196bad2676be217aac0",
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
        },
        "logging": [],
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
**Counting prime numbers with substring '79'**

I need to count the prime numbers under 400 that have '79' as a substring. First, I should systematically generate the primes less than 400. Notably, the only 2-digit prime containing '79' is 79 itself. For 3-digit numbers, '79' can appear in forms like 79x, but since we're limited to under 400, we won't have additional valid primes because anything starting with 79 exceeds our limit. So, in this case, I’m focused on just 79.\
"""
                        ),
                        Thought(
                            thought="""\
**Determining if numbers are prime**

I’m checking which of these numbers are prime. First, 79 is a prime number, so that one checks out. For 179, I need to test divisibility by small primes up to about 13.38. After going through 2, 3, 5, 7, 11, and 13, I confirm that 179 is indeed prime. \n\

279, however, is clearly not prime since it's divisible by 3. Now onto 379: I need to check divisibility with primes up to 19.467. After testing with 3, 5, 7, 11, 13, 17, and 19, I find that 379 is prime too!\
"""
                        ),
                        Thought(
                            thought="""\
**Finalizing prime number count**

I’ve confirmed that 79, 179, and 379 are prime, totaling 3 primes. Now, I want to double-check for any other numbers under 400 that contain '79' as a substring. The two-digit number '79' counts, but three-digit checks must have '79' consecutively, not separated by another digit. \n\

I've excluded numbers like 97, 197, and 297, which don’t count, and 793 exceeds 400. In the end, I reaffirm that there are no other primes with '79,' so the answer remains 3.\
"""
                        ),
                        Thought(
                            thought="""\
**Final count confirmation**

I’ve confirmed that the count of primes that contain '79' as a substring is 3. I considered whether '79' could span multiple digit places in three-digit numbers, but it appears I've covered all cases. Now, I just need to ensure I only present the final count as instructed. \n\

I also did a quick triple-check on the primality of 179, confirming it with mod 7, 11, and 13. Now, it's time to present the answer: “3.”\
"""
                        ),
                        Text(text="3"),
                    ],
                    provider="openai:responses",
                    model_id="gpt-5",
                    raw_content=[
                        {
                            "id": "rs_01fb41c50d251fd10068e71010b4a48190979f9b5023f07ce8",
                            "summary": [
                                {
                                    "text": """\
**Counting prime numbers with substring '79'**

I need to count the prime numbers under 400 that have '79' as a substring. First, I should systematically generate the primes less than 400. Notably, the only 2-digit prime containing '79' is 79 itself. For 3-digit numbers, '79' can appear in forms like 79x, but since we're limited to under 400, we won't have additional valid primes because anything starting with 79 exceeds our limit. So, in this case, I’m focused on just 79.\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Determining if numbers are prime**

I’m checking which of these numbers are prime. First, 79 is a prime number, so that one checks out. For 179, I need to test divisibility by small primes up to about 13.38. After going through 2, 3, 5, 7, 11, and 13, I confirm that 179 is indeed prime. \n\

279, however, is clearly not prime since it's divisible by 3. Now onto 379: I need to check divisibility with primes up to 19.467. After testing with 3, 5, 7, 11, 13, 17, and 19, I find that 379 is prime too!\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Finalizing prime number count**

I’ve confirmed that 79, 179, and 379 are prime, totaling 3 primes. Now, I want to double-check for any other numbers under 400 that contain '79' as a substring. The two-digit number '79' counts, but three-digit checks must have '79' consecutively, not separated by another digit. \n\

I've excluded numbers like 97, 197, and 297, which don’t count, and 793 exceeds 400. In the end, I reaffirm that there are no other primes with '79,' so the answer remains 3.\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Final count confirmation**

I’ve confirmed that the count of primes that contain '79' as a substring is 3. I considered whether '79' could span multiple digit places in three-digit numbers, but it appears I've covered all cases. Now, I just need to ensure I only present the final count as instructed. \n\

I also did a quick triple-check on the primality of 179, confirming it with mod 7, 11, and 13. Now, it's time to present the answer: “3.”\
""",
                                    "type": "summary_text",
                                },
                            ],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_01fb41c50d251fd10068e710223d9c8190be37d08d02589127",
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
                    content=[Text(text="I don’t remember.")],
                    provider="openai:responses",
                    model_id="gpt-5",
                    raw_content=[
                        {
                            "id": "rs_01fb41c50d251fd10068e710231d1481908b8fb99348ee61f7",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_01fb41c50d251fd10068e710234b44819098554c4b1ebb2ddf",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": "I don’t remember.",
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
        },
        "logging": [],
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
**Counting primes with "79"**

I need to find prime numbers less than 400 that contain the substring "79." \n\

The only two-digit prime is 79 itself. For three-digit patterns, I can look for numbers like 179, 279, and 379. However, I need to ensure "79" appears consecutively. \n\

So, my final list of primes containing "79" is: 79, 179, 279, and 379. I don't need to include values like 197 and 97, as they don't fit the criteria.\
"""
                        ),
                        Thought(
                            thought="""\
**Verifying primes with "79"**

I'm checking if any numbers with "79" in their decimal representation fall below 400. \n\

I consider 794, which includes "79," but it's above 400, so I can't include it. The confirmed numbers are 79, 179, 279, and 379, though I need to check their primality. \n\

For 79, it’s prime, as it isn’t divisible by small primes. The same goes for 179. I still need to verify the primality of 279 and 379.\
"""
                        ),
                        Thought(
                            thought="""\
**Finalizing prime counts**

I’ve confirmed that 179 is indeed prime. \n\

For 279, it’s composite because the sum of its digits (2+7+9=18) is divisible by 3. \n\

Now, checking 379 shows it's prime as well; no small primes divide it successfully. \n\

So the primes I have confirmed are 79, 179, and 379—three in total. I’ll double-check that there are no other relevant numbers below 400, and I confirm that only these three qualify.\
"""
                        ),
                        Thought(
                            thought="""\
**Confirming final count**

I've confirmed that 379 is indeed under 400, as are 79 and 179—so that's three primes total. \n\

I also considered any edge cases like 197, but that doesn't count. I checked for occurrences of "79" across place boundaries, but that doesn’t apply here since the problem just asks for it to be a substring. \n\

So, I'll keep it simple and just return the number: 3.\
"""
                        ),
                        Text(text="3"),
                    ],
                    provider="openai:responses",
                    model_id="gpt-5",
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
                    content=[Text(text="79, 179, 379")],
                    provider="openai:responses",
                    model_id="gpt-5",
                    raw_content=[],
                ),
            ],
            "format": None,
            "tools": [],
            "n_chunks": 9,
        },
        "logging": [],
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
**Counting primes with '79'**

I need to count the primes less than 400 that have "79" as a substring. I'll first generate the list of primes under 400 and specifically look for ones containing "79." \n\

So let's check: 79 itself, 179, 279 (not prime), 379, and 197 (doesn't fit the criteria). The number 379 does contain "79." I realize I should also consider where "79" can appear in the middle, but four-digit numbers won't count since we're under 400.\
"""
                        ),
                        Thought(
                            thought="""\
**Identifying relevant primes**

I'm focused on identifying primes containing "79" as a substring and less than 400. I’ll list the candidates: 79, 179, 279, and 379. Since we're under 400, I realize that starting with 79 isn't possible for three-digit numbers, as they would exceed that limit.

Next, I want to check the primality of these numbers. 79 is prime, but I need to verify if 179 is by checking for divisibility. The approximate square root of 179 is around 13.38, so I’ll look into that.\
"""
                        ),
                        Thought(
                            thought="""\
**Testing for prime numbers**

I’m testing if 179 is prime. It’s an odd number, and the sum of its digits (1+7+9=17) isn’t divisible by 3. It doesn’t end in 5, so that’s good. For 7, there’s a remainder, so not divisible. I check against 11 and 13, and since there are no remainders, 179 is confirmed prime. \n\

Now, for 279, it’s divisible by 3. So, it's not prime. For 379, I’ll check all smaller primes, and it turns out to be prime too. I wonder if I missed any numbers like 297.\
"""
                        ),
                        Thought(
                            thought="""\
**Counting primes with '79'**

I’m checking if 297 is prime and contains "79." It’s not prime, and the digits are in the wrong order. I already confirmed that 379 works. Then I consider 197, which doesn't fit, and 792 exceeds 400. \n\

So far, I have 79, 179, and 379 as the only qualifying primes—totaling three. I realize that 97 contains "79" reversed, but doesn’t meet our criteria. After double-checking for any three-digit combinations, it appears only those three primes hold up. I confirm that 79 itself counts since it contains "79."\
"""
                        ),
                        Text(text="3"),
                    ],
                    provider="openai:responses",
                    model_id="gpt-5",
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
                    content=[Text(text="79, 179, 379")],
                    provider="openai:responses",
                    model_id="gpt-5",
                    raw_content=[],
                ),
            ],
            "format": None,
            "tools": [],
            "n_chunks": 9,
        },
        "logging": [],
    }
)
