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

I need to count the prime numbers below 400 that contain the substring "79." First off, I can identify "79" itself as a prime. Then for three-digit numbers, I recognize 179, 279, and 379 as potential candidates.

When I think about the arrangements of the digits, only those three-digit numbers end with '79,' namely 179, 279, and 379. It seems I've correctly covered the cases!\
"""
                        ),
                        Thought(
                            thought="""\
**Identifying prime candidates with '79'**

I’m analyzing numbers less than 400 that contain "79." The only two-digit candidate is 79 itself. For three-digit numbers, I find 179, 279, and 379, though 793 exceeds my limit.

Next, I check which of these are prime. 79 is undoubtedly prime. For 179, I test divisibility and confirm it is also prime. However, 279 is divisible by 3, so it's not prime. Finally, I need to check 379, which will involve looking at its divisibility too.\
"""
                        ),
                        Thought(
                            thought="""\
**Confirming primes and final count**

I’m checking for primes among my candidates: 79, 179, and 379. I test divisibility against known primes up to 19 and find that 379 is indeed prime. \n\

Now, to make sure there aren't any other eligible numbers below 400 containing the substring "79," I realize I only need to consider those ending in '79' or equal to 79 itself. \n\

I confirm 79, 179, and 379 as the only candidates, so my final count is 3. I’ll just output "3."\
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
**Counting primes with substring "79"**

I need to count the prime numbers less than 400 that have "79" as a substring, meaning that the digits "7" and "9" appear consecutively in their decimal form. The obvious candidate is 79 itself. For three-digit numbers, I have 179, 279, and 379 qualifying. Numbers like 790 and those starting with "79" go over 400. \n\
Finally, from my checks, 79, 179, 279, and 379 all fit the criteria.\
"""
                        ),
                        Thought(
                            thought="""\
**Validating prime candidates with "79"**

I'm considering numbers like 790, but that’s over 400, so it’s not valid. The same with 97; it doesn’t contain "79." I check 197, which has "97," and 793 is also over 400. So my valid candidates for "79" as a substring are 79, 179, 279, and 379. \n\

Now I need to check if these are prime. Starting with 79, it's prime. For 179, I’ll test divisibility by small primes up to around 13, and none divide it, confirming that 179 is also a prime.\
"""
                        ),
                        Thought(
                            thought="""\
**Finalizing prime counts with "79"**

I've checked the candidates, starting with 279, which is composite since it's divisible by 3. For 379, I test its primality. The square root is about 19.4, so I’ll test divisibility against primes up to 19. \n\

It turns out 379 is prime. So, the primes under 400 that contain "79" are 79, 179, and 379. That gives me a total count of 3. I’ve also verified edge cases and confirmed there are no others, so the final answer is just "3."\
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
