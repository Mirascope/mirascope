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
**Counting primes with substring "79"**

I need to find the count of prime numbers under 400 that have "79" as a substring. The relevant candidates are 79, 179, 279, and 379 since those are all below 400. I also checked 797, but that's above the limit. I want to ensure I only consider valid primes containing the substring "79" while excluding any that don’t meet the criteria. The confirmed primes are 79, 179, 279, and 379.\
"""
                        ),
                        Thought(
                            thought="""\
**Verifying prime candidates with "79"**

I confirmed that 379 is in the list. I’m trying to figure out if there are any numbers with 7 and 9 as non-adjacent digits, but since the question specifies “as a substring,” it looks like I only have the four candidates: 79, 179, 279, and 379. I've checked each one for primality: 79 and 179 are prime, while 279 is divisible by 3 and not prime. Finally, I verified that 379 is prime, so the total count of primes containing "79" is three.\
"""
                        ),
                        Thought(
                            thought="""\
**Finalizing count of primes**

The answer is 3! But just to be thorough, I double-checked that 179 is indeed prime by testing its divisibility against primes up to the square root. It's not divisible by 2, 3, 5, 7, 11, or 13, so it checks out. I swiftly confirmed that 79 is also prime. Although I wondered about other combinations, numbers like 97 have a different order and don’t count. I've ruled out other forms that exceed 400, so I’m confident in reporting the result as "3" without any additional punctuation.\
"""
                        ),
                        Text(text="3"),
                    ],
                    provider="openai:responses",
                    model_id="gpt-5",
                    raw_message=[
                        {
                            "id": "rs_0c9d4e63dac6126a00690a207bfc148195b3c6f4868dd0a013",
                            "summary": [
                                {
                                    "text": """\
**Counting primes with substring "79"**

I need to find the count of prime numbers under 400 that have "79" as a substring. The relevant candidates are 79, 179, 279, and 379 since those are all below 400. I also checked 797, but that's above the limit. I want to ensure I only consider valid primes containing the substring "79" while excluding any that don’t meet the criteria. The confirmed primes are 79, 179, 279, and 379.\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Verifying prime candidates with "79"**

I confirmed that 379 is in the list. I’m trying to figure out if there are any numbers with 7 and 9 as non-adjacent digits, but since the question specifies “as a substring,” it looks like I only have the four candidates: 79, 179, 279, and 379. I've checked each one for primality: 79 and 179 are prime, while 279 is divisible by 3 and not prime. Finally, I verified that 379 is prime, so the total count of primes containing "79" is three.\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Finalizing count of primes**

The answer is 3! But just to be thorough, I double-checked that 179 is indeed prime by testing its divisibility against primes up to the square root. It's not divisible by 2, 3, 5, 7, 11, or 13, so it checks out. I swiftly confirmed that 79 is also prime. Although I wondered about other combinations, numbers like 97 have a different order and don’t count. I've ruled out other forms that exceed 400, so I’m confident in reporting the result as "3" without any additional punctuation.\
""",
                                    "type": "summary_text",
                                },
                            ],
                            "type": "reasoning",
                            "response_id": "resp_0c9d4e63dac6126a00690a207b84688195ac01b41a1dae52f2",
                        },
                        {
                            "id": "msg_0c9d4e63dac6126a00690a208d912c8195a727cd0635b50a91",
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
                            "id": "rs_0c9d4e63dac6126a00690a208e9df08195a6003482efd32d90",
                            "summary": [],
                            "type": "reasoning",
                            "response_id": "resp_0c9d4e63dac6126a00690a208e35648195bdfdfdfb1a9ce78a",
                        },
                        {
                            "id": "msg_0c9d4e63dac6126a00690a208ede048195a6c26b94ea75774c",
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
**Counting primes with substring**

I need to count primes below 400 that include the substring "79." That means I should consider both 2-digit and 3-digit primes. The number 79 itself is prime, and I should check if 179, 279, and 379 qualify. 279 isn’t prime, and while I'm wondering about 3-digit numbers, I realize "79" can appear in various positions, but then I remember numbers from 790 to 799 exceed 400. So, let’s focus on valid candidates!\
"""
                        ),
                        Thought(
                            thought="""\
**Determining valid primes**

I realize that numbers 790-799 are irrelevant since they're greater than 400. For the numbers below 400, I can only consider "x79," meaning the last two digits would be 79. That includes 79, 179, 279, and 379. 79 counts as itself, but I have to remember that other combinations like 97 or separated digits don't work since the substring must be consecutive. Now, let’s check the primality of 179, since I need to find all the primes under 400.\
"""
                        ),
                        Thought(
                            thought="""\
**Identifying prime candidates**

I have the candidates to consider: 79 and 179 are primes, but 279 isn’t since it’s divisible by 3. I also look at 379, which seems prime. I think about 97 and 197, but neither contains "79". For 379, I check divisibility: it isn't divisible by primes up to about 19, confirming that it is prime. Then, I check 179: the same method shows it’s not divisible by primes up to 13, meaning 179 is also prime.\
"""
                        ),
                        Thought(
                            thought="""\
**Confirming prime counts**

Alright, I've confirmed that 79, 179, and 379 are indeed primes, making a total of three primes. I'm also checking if there are any other forms of numbers under 400 that contain the substring "79." The only 2-digit representation is 79. For 3-digit numbers, "x79" works, while "79x" exceeds 400. \n\

I ruled out any combinations like "7 9" since the substring needs to be consecutive. Besides 279 being composite, I've checked that 179 and 379 contain "79." That means my count remains three primes, and I also checked if 297 contains "79."\
"""
                        ),
                        Thought(
                            thought="""\
**Finalizing the count of primes**

I checked that 297 doesn’t contain the substring "79," so it doesn't count. I also looked at 97, which isn’t "79" either. This confirms that the count is still three. I made sure I didn't overlook anything with 3-digit numbers starting with "79," which would be 790-799, and those exceed 400. \n\

Finally, I’ve verified that both 179 and 379 are indeed primes. So, I’ll return the final count: "3."\
"""
                        ),
                        Text(text="3"),
                    ],
                    provider="openai:responses",
                    model_id="gpt-5",
                    raw_message=[
                        {
                            "id": "rs_03efd3e35645773100690a20aba26c8190b7044f0ebd19ed26",
                            "summary": [
                                {
                                    "text": """\
**Counting primes with substring**

I need to count primes below 400 that include the substring "79." That means I should consider both 2-digit and 3-digit primes. The number 79 itself is prime, and I should check if 179, 279, and 379 qualify. 279 isn’t prime, and while I'm wondering about 3-digit numbers, I realize "79" can appear in various positions, but then I remember numbers from 790 to 799 exceed 400. So, let’s focus on valid candidates!\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Determining valid primes**

I realize that numbers 790-799 are irrelevant since they're greater than 400. For the numbers below 400, I can only consider "x79," meaning the last two digits would be 79. That includes 79, 179, 279, and 379. 79 counts as itself, but I have to remember that other combinations like 97 or separated digits don't work since the substring must be consecutive. Now, let’s check the primality of 179, since I need to find all the primes under 400.\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Identifying prime candidates**

I have the candidates to consider: 79 and 179 are primes, but 279 isn’t since it’s divisible by 3. I also look at 379, which seems prime. I think about 97 and 197, but neither contains "79". For 379, I check divisibility: it isn't divisible by primes up to about 19, confirming that it is prime. Then, I check 179: the same method shows it’s not divisible by primes up to 13, meaning 179 is also prime.\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Confirming prime counts**

Alright, I've confirmed that 79, 179, and 379 are indeed primes, making a total of three primes. I'm also checking if there are any other forms of numbers under 400 that contain the substring "79." The only 2-digit representation is 79. For 3-digit numbers, "x79" works, while "79x" exceeds 400. \n\

I ruled out any combinations like "7 9" since the substring needs to be consecutive. Besides 279 being composite, I've checked that 179 and 379 contain "79." That means my count remains three primes, and I also checked if 297 contains "79."\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Finalizing the count of primes**

I checked that 297 doesn’t contain the substring "79," so it doesn't count. I also looked at 97, which isn’t "79" either. This confirms that the count is still three. I made sure I didn't overlook anything with 3-digit numbers starting with "79," which would be 790-799, and those exceed 400. \n\

Finally, I’ve verified that both 179 and 379 are indeed primes. So, I’ll return the final count: "3."\
""",
                                    "type": "summary_text",
                                },
                            ],
                            "type": "reasoning",
                            "response_id": "resp_03efd3e35645773100690a20ab24d88190be5d1d2fd174909f",
                        },
                        {
                            "id": "msg_03efd3e35645773100690a20c8401081909c0f265d52fec173",
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
                            "id": "rs_03efd3e35645773100690a20c96dd48190a7806ac3d88183ac",
                            "summary": [],
                            "type": "reasoning",
                            "response_id": "resp_03efd3e35645773100690a20c8d71881908a9e639c1d6cd4d0",
                        },
                        {
                            "id": "msg_03efd3e35645773100690a20c9b38c8190badf0fe60cccad56",
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
**Counting prime numbers with '79'**

I'm looking for prime numbers less than 400 that have the substring "79." First, I’ll identify all primes below 400. Then, I’ll check two-digit and three-digit numbers that contain "79." \n\

In the two-digit range, we only have 79 itself. For three-digit numbers, the relevant candidates are 179, 279, and 379. However, numbers like 790 or above don’t count since they exceed 400. So, the confirmed candidates are 79, 179, 279, and 379.\
"""
                        ),
                        Thought(
                            thought="""\
**Verifying prime status of candidates**

I need to ensure that "79" is specifically in that order, which means I’m working with four candidates: 79, 179, 279, and 379. \n\

First, I know 79 is prime. For 179, I’ll check primality by testing divisibility against primes up to its square root. It passes all the tests, so it’s prime. \n\

Next, I check 279; it’s divisible by 3, so it's not prime. Lastly, I test 379, and it also checks out as prime after verifying divisibility.\
"""
                        ),
                        Thought(
                            thought="""\
**Confirming prime count**

I’ve identified the primes below 400 that contain "79": they are 79, 179, and 379, totaling three primes. I've confirmed that 279 is not prime and that 1979 exceeds 400. Additionally, 97 doesn't count since it doesn't have "79." I checked 297 for containment, and it doesn't apply either. Just to be thorough, I noted that "79" occurs in "279," but it’s not prime. So, my final answer is simply: 3.\
"""
                        ),
                        Text(text="3"),
                    ],
                    provider="openai:responses",
                    model_id="gpt-5",
                    raw_message=[
                        {
                            "id": "rs_049d8e19d65d9d4d00690a2090bfb88197be797d1935059879",
                            "summary": [
                                {
                                    "text": """\
**Counting prime numbers with '79'**

I'm looking for prime numbers less than 400 that have the substring "79." First, I’ll identify all primes below 400. Then, I’ll check two-digit and three-digit numbers that contain "79." \n\

In the two-digit range, we only have 79 itself. For three-digit numbers, the relevant candidates are 179, 279, and 379. However, numbers like 790 or above don’t count since they exceed 400. So, the confirmed candidates are 79, 179, 279, and 379.\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Verifying prime status of candidates**

I need to ensure that "79" is specifically in that order, which means I’m working with four candidates: 79, 179, 279, and 379. \n\

First, I know 79 is prime. For 179, I’ll check primality by testing divisibility against primes up to its square root. It passes all the tests, so it’s prime. \n\

Next, I check 279; it’s divisible by 3, so it's not prime. Lastly, I test 379, and it also checks out as prime after verifying divisibility.\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Confirming prime count**

I’ve identified the primes below 400 that contain "79": they are 79, 179, and 379, totaling three primes. I've confirmed that 279 is not prime and that 1979 exceeds 400. Additionally, 97 doesn't count since it doesn't have "79." I checked 297 for containment, and it doesn't apply either. Just to be thorough, I noted that "79" occurs in "279," but it’s not prime. So, my final answer is simply: 3.\
""",
                                    "type": "summary_text",
                                },
                            ],
                            "type": "reasoning",
                            "response_id": "resp_049d8e19d65d9d4d00690a209028b081979bb792da41dd6c13",
                        },
                        {
                            "id": "msg_049d8e19d65d9d4d00690a20a83d7481978d09e51d19ce822f",
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
                            "id": "rs_049d8e19d65d9d4d00690a20aa0f6c8197a18f7003fe24148f",
                            "summary": [],
                            "type": "reasoning",
                            "response_id": "resp_049d8e19d65d9d4d00690a20a92a64819799ec460e235c6a49",
                        },
                        {
                            "id": "msg_049d8e19d65d9d4d00690a20aa50148197a23142e2a293fe62",
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
**Counting primes with substring "79"**

I need to count prime numbers less than 400 that contain "79" as a substring. I’ll start by considering two-digit and three-digit numbers. The two-digit number is 79 itself. For three-digit numbers, anything in the form of 79x (like 790-799) exceeds 400, so those don’t count. However, the format x79 yields 179, 279, and 379—all less than 400. I have to keep in mind that I need to check which of these are prime!\
"""
                        ),
                        Thought(
                            thought="""\
**Identifying primes with "79"**

Next, I’m looking for numbers where the hundreds and tens digits are 7 and 9. For two digits, it's just 79, and for three-digit numbers, I've already covered 79x and x79. \n\

Now, checking 297, it contains "97," but not "79." So, I only want the exact "79" in order. \n\

The candidates less than 400 with "79" are 79, 179, 279, and 379. Additionally, I have ruled out others like 709, since it doesn’t contain "79" consecutively.\
"""
                        ),
                        Thought(
                            thought="""\
**Testing primality of candidates**

I can rule out any four-digit numbers since they exceed 400. So, I just need to test the primality of 79, 179, 279, and 379. \n\

First, 79 is prime—no doubt there. For 179, I check divisibility using primes up to around √179, confirming it's also prime. \n\

Now, 279 is divisible by 3 because the sum of its digits is 18, so it's not prime. Finally, I check 379 against several primes, and it turns out to be prime as well! \n\

This gives me three primes: 79, 179, and 379.\
"""
                        ),
                        Thought(
                            thought="""\
**Final checks on candidates with "79"**

I’m going over the numbers less than 400 again for any that contain "79." \n\

Checking 297 and 197, neither fit since 197 has "19" and not "79." I already ruled out 279 as composite, and 379 is prime. For other combinations like "x79" and patterns with "79" in the middle, only 179, 279, and 379 qualify. I also remember checking 397, but it has "97," not "79."

After thorough checks, the only primes are 79, 179, and 379, totaling three.\
"""
                        ),
                        Thought(
                            thought="""\
**Confirming substring criteria**

I realize that "substring" means I’m only looking for consecutive digits. So, that confirms my answer is just 3. \n\

Still, I want to double-check any other potential candidates like 179, 197, 279, 297, 379, and 397. However, they don't have the consecutive "79" pairs. \n\

Therefore, I'm confident in concluding that the final answer is indeed just 3! It’s good to be thorough!\
"""
                        ),
                        Text(text="3"),
                    ],
                    provider="openai:responses",
                    model_id="gpt-5",
                    raw_message=[
                        {
                            "id": "rs_0c1021cd9b668f0300690a20cbbf848195837624e59b466ea8",
                            "summary": [
                                {
                                    "text": """\
**Counting primes with substring "79"**

I need to count prime numbers less than 400 that contain "79" as a substring. I’ll start by considering two-digit and three-digit numbers. The two-digit number is 79 itself. For three-digit numbers, anything in the form of 79x (like 790-799) exceeds 400, so those don’t count. However, the format x79 yields 179, 279, and 379—all less than 400. I have to keep in mind that I need to check which of these are prime!\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Identifying primes with "79"**

Next, I’m looking for numbers where the hundreds and tens digits are 7 and 9. For two digits, it's just 79, and for three-digit numbers, I've already covered 79x and x79. \n\

Now, checking 297, it contains "97," but not "79." So, I only want the exact "79" in order. \n\

The candidates less than 400 with "79" are 79, 179, 279, and 379. Additionally, I have ruled out others like 709, since it doesn’t contain "79" consecutively.\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Testing primality of candidates**

I can rule out any four-digit numbers since they exceed 400. So, I just need to test the primality of 79, 179, 279, and 379. \n\

First, 79 is prime—no doubt there. For 179, I check divisibility using primes up to around √179, confirming it's also prime. \n\

Now, 279 is divisible by 3 because the sum of its digits is 18, so it's not prime. Finally, I check 379 against several primes, and it turns out to be prime as well! \n\

This gives me three primes: 79, 179, and 379.\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Final checks on candidates with "79"**

I’m going over the numbers less than 400 again for any that contain "79." \n\

Checking 297 and 197, neither fit since 197 has "19" and not "79." I already ruled out 279 as composite, and 379 is prime. For other combinations like "x79" and patterns with "79" in the middle, only 179, 279, and 379 qualify. I also remember checking 397, but it has "97," not "79."

After thorough checks, the only primes are 79, 179, and 379, totaling three.\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Confirming substring criteria**

I realize that "substring" means I’m only looking for consecutive digits. So, that confirms my answer is just 3. \n\

Still, I want to double-check any other potential candidates like 179, 197, 279, 297, 379, and 397. However, they don't have the consecutive "79" pairs. \n\

Therefore, I'm confident in concluding that the final answer is indeed just 3! It’s good to be thorough!\
""",
                                    "type": "summary_text",
                                },
                            ],
                            "type": "reasoning",
                            "response_id": "resp_0c1021cd9b668f0300690a20cb500481958c37063c69f21862",
                        },
                        {
                            "id": "msg_0c1021cd9b668f0300690a20e5b9c88195aa321691cf19a81e",
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
                    raw_message=[
                        {
                            "id": "rs_0c1021cd9b668f0300690a20e6c55081959b805f2d010cc49a",
                            "summary": [],
                            "type": "reasoning",
                            "response_id": "resp_0c1021cd9b668f0300690a20e6560c8195a98850f36195d7fb",
                        },
                        {
                            "id": "msg_0c1021cd9b668f0300690a20e70a4c8195a949f875a1d60242",
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
            "n_chunks": 7,
        }
    }
)
