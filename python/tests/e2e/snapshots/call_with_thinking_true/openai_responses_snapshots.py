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
**Calculating primes with substring "79"**

I need to find the number of prime numbers below 400 that have "79" as a substring. Primes to consider are those less than 400, specifically from 2 to 397. I found that 79, 179, 197, 279, and 379 meet this condition. I double-checked to ensure they contain "79" correctly. \n\

So, to count: the valid primes with "79" are 79, 179, 197, 279, and 379. That's five primes in total!\
"""
                        ),
                        Thought(
                            thought="""\
**Reviewing prime numbers with "79"**

I’m focusing on how "79" can appear within three-digit numbers. It can be at the end, like in "x79," but those don't apply since we're looking at values less than 400. The candidates I've identified so far are 79, 179, 279, and 379.

I also need to correct myself on 197—it doesn’t contain "79" either, as it reads as "1, 9, 7." So, the valid primes remain 79, 179, 279, and 379.\
"""
                        ),
                        Thought(
                            thought="""\
**Finalizing prime candidates with "79"**

Let’s review the primes again. 197 doesn't work because it has the digits in the order "9, 7" instead of "7, 9." For 179 and 279, they both end with "79," so they count. I confirm that 379 is also prime.

However, 297 has "97," so it’s out. 279 is actually divisible by 3, which means it’s not prime. I confirm that 79, 179, and 379 are the valid primes containing "79" as a substring.\
"""
                        ),
                        Thought(
                            thought="""\
**Verifying prime numbers**

I need to check if 179 is prime by testing divisibility with several primes. After calculations, I confirm it’s not divisible by 2, 3, 5, 7, 11, or 13, so 179 is indeed prime. \n\

Then, I look at 379; after testing against smaller primes like 2, 3, 5, 7, 11, 13, 17, and 19, I find that it’s also not divisible by any, so it’s prime too. \n\

The only numbers under 400 that contain "79" as a substring are 79, 179, and 379. 97 is reversed and doesn’t count!\
"""
                        ),
                        Thought(
                            thought="""\
**Confirming prime count with "79"**

We have the substring "79," which lets us identify the primes as 79, 179, and 379, totaling three primes. I considered 97 but confirmed that it doesn't contain "79" in a circular way. \n\

I double-checked all the relevant primes and their properties, including that 279 isn't prime, so it doesn't count.

In the end, the final answer is simply "3," without any extra information. No whitespace or additional comments—just the number.\
"""
                        ),
                        Text(text="3"),
                    ],
                    provider="openai:responses",
                    model_id="gpt-5",
                    raw_content=[
                        {
                            "id": "rs_05b488542ecdb1480068e815ff0bb881969c5939f518eca198",
                            "summary": [
                                {
                                    "text": """\
**Calculating primes with substring "79"**

I need to find the number of prime numbers below 400 that have "79" as a substring. Primes to consider are those less than 400, specifically from 2 to 397. I found that 79, 179, 197, 279, and 379 meet this condition. I double-checked to ensure they contain "79" correctly. \n\

So, to count: the valid primes with "79" are 79, 179, 197, 279, and 379. That's five primes in total!\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Reviewing prime numbers with "79"**

I’m focusing on how "79" can appear within three-digit numbers. It can be at the end, like in "x79," but those don't apply since we're looking at values less than 400. The candidates I've identified so far are 79, 179, 279, and 379.

I also need to correct myself on 197—it doesn’t contain "79" either, as it reads as "1, 9, 7." So, the valid primes remain 79, 179, 279, and 379.\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Finalizing prime candidates with "79"**

Let’s review the primes again. 197 doesn't work because it has the digits in the order "9, 7" instead of "7, 9." For 179 and 279, they both end with "79," so they count. I confirm that 379 is also prime.

However, 297 has "97," so it’s out. 279 is actually divisible by 3, which means it’s not prime. I confirm that 79, 179, and 379 are the valid primes containing "79" as a substring.\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Verifying prime numbers**

I need to check if 179 is prime by testing divisibility with several primes. After calculations, I confirm it’s not divisible by 2, 3, 5, 7, 11, or 13, so 179 is indeed prime. \n\

Then, I look at 379; after testing against smaller primes like 2, 3, 5, 7, 11, 13, 17, and 19, I find that it’s also not divisible by any, so it’s prime too. \n\

The only numbers under 400 that contain "79" as a substring are 79, 179, and 379. 97 is reversed and doesn’t count!\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Confirming prime count with "79"**

We have the substring "79," which lets us identify the primes as 79, 179, and 379, totaling three primes. I considered 97 but confirmed that it doesn't contain "79" in a circular way. \n\

I double-checked all the relevant primes and their properties, including that 279 isn't prime, so it doesn't count.

In the end, the final answer is simply "3," without any extra information. No whitespace or additional comments—just the number.\
""",
                                    "type": "summary_text",
                                },
                            ],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_05b488542ecdb1480068e8161814a4819686496b078b12a807",
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
                            "id": "rs_05b488542ecdb1480068e8161a5e308196b234b662d6533fca",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_05b488542ecdb1480068e8161a81b88196825f8eac75d6f33c",
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
**Counting prime numbers with substring**

I need to find prime numbers under 400 containing "79" as a consecutive substring. So, it’s numbers like 79, 179, 279, and 379 — but not 479 since it's over 400. I also realized numbers like 297 don’t count since they have '97' instead of '79'. For numbers under 400, I’m looking at 79 and those beginning with '79' or ending with '79'. I need to confirm which of these numbers are prime.\
"""
                        ),
                        Thought(
                            thought="""\
**Checking primality of numbers**

I’m confirming the primality of several numbers containing "79." First, 79 is prime because it has no divisors up to about 8.8. Next, I checked 179 and found it's prime too. For 279, since the sum of its digits is divisible by 3, it’s not prime. Now 379, I checked and confirmed it's prime as well. I also considered if there are any other numbers containing '79', but nothing new turns up, and 1979 is over 400.\
"""
                        ),
                        Thought(
                            thought="""\
**Finalizing prime count with substring**

I'm confirming the count of prime numbers containing "79" as a substring. I found that numbers like 790-799 are above the limit, and while 379 is prime, 279 isn’t. I see that the likely primes are 79, 179, and 379, making it three primes. I've checked others like 97 and 297, but they don’t contain "79." So, after considering all options, the final answer is 3 confirmed primes. I just need to present this succinctly!\
"""
                        ),
                        Thought(
                            thought="""\
**Confirming final count of primes**

I’m outputting the final count: 3 primes, but I want to ensure I've considered all possibilities. For two-digit numbers, there's only 79. When looking at three-digit numbers under 400, I see '79' can only appear as the last two digits in 179, 279, and 379. But 279 isn’t prime. So, counting just primes gives me 79, 179, and 379, which total three. I’m ready to return "3" as the answer!\
"""
                        ),
                        Text(text="3"),
                    ],
                    provider="openai:responses",
                    model_id="gpt-5",
                    raw_content=[
                        {
                            "id": "rs_07d88975760f76030068e8161d40748194a12557069ab14804",
                            "summary": [
                                {
                                    "text": """\
**Counting prime numbers with substring**

I need to find prime numbers under 400 containing "79" as a consecutive substring. So, it’s numbers like 79, 179, 279, and 379 — but not 479 since it's over 400. I also realized numbers like 297 don’t count since they have '97' instead of '79'. For numbers under 400, I’m looking at 79 and those beginning with '79' or ending with '79'. I need to confirm which of these numbers are prime.\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Checking primality of numbers**

I’m confirming the primality of several numbers containing "79." First, 79 is prime because it has no divisors up to about 8.8. Next, I checked 179 and found it's prime too. For 279, since the sum of its digits is divisible by 3, it’s not prime. Now 379, I checked and confirmed it's prime as well. I also considered if there are any other numbers containing '79', but nothing new turns up, and 1979 is over 400.\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Finalizing prime count with substring**

I'm confirming the count of prime numbers containing "79" as a substring. I found that numbers like 790-799 are above the limit, and while 379 is prime, 279 isn’t. I see that the likely primes are 79, 179, and 379, making it three primes. I've checked others like 97 and 297, but they don’t contain "79." So, after considering all options, the final answer is 3 confirmed primes. I just need to present this succinctly!\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Confirming final count of primes**

I’m outputting the final count: 3 primes, but I want to ensure I've considered all possibilities. For two-digit numbers, there's only 79. When looking at three-digit numbers under 400, I see '79' can only appear as the last two digits in 179, 279, and 379. But 279 isn’t prime. So, counting just primes gives me 79, 179, and 379, which total three. I’m ready to return "3" as the answer!\
""",
                                    "type": "summary_text",
                                },
                            ],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_07d88975760f76030068e8162c6ca08194adfad57a0dcfa839",
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
                            "id": "rs_07d88975760f76030068e8162e9790819483388702295b15f9",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_07d88975760f76030068e8162ecd88819480578a0d394d69dc",
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
        },
        "logging": [],
    }
)
