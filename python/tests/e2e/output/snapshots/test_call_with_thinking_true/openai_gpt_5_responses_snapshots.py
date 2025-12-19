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
**Counting primes with "79" substring**

I need to find primes less than 400 that contain "79" as a substring. The possible candidates are 79 itself, and three-digit numbers like 179, 279, and 379. However, 790 and above don’t count since they exceed 400. It’s important to remember that "79" must be contiguous, so numbers like 97 or variations across boundaries don’t qualify. Ultimately, the valid primes are 79, 179, 279, and 379.\
"""
                        ),
                        Thought(
                            thought="""\
**Finalizing prime list with "79"**

I’m surveying numbers that can contain "79." The only valid two-digit option is 79 itself. For three-digit numbers below 400, we have 179, 279, and 379. Upon checking, 179 and 79 are confirmed as primes, while 279 is divisible by 3 and therefore not a prime. I thought about 97 but it doesn’t contain "79," and, even though 197 has 97 as digits, it doesn’t qualify either. Ultimately, my confirmed primes are 79, 179, and 379.\
"""
                        ),
                        Thought(
                            thought="""\
**Confirming prime status of candidates**

I’ve confirmed that the primes are 79, 179, and 379, which gives us three valid primes. To verify: 79 is standardly recognized as prime. Next, I checked 179 by testing divisibility with primes under its square root (about 13.38) and confirmed it’s prime through various checks. \n\

279 isn’t prime since it's divisible by 3. Lastly, I checked 379, and after testing it against primes below its square root (about 19.4), it turns out to be prime too. So, the final count remains three, but 97, 197, and 297 don’t qualify.\
"""
                        ),
                        Thought(
                            thought="""\
**Finalizing primes containing "79"**

I’m checking 397, but it actually contains "97" as digits 2-3, not "79." My valid primes so far are 79, 179, and 379, which totals three. I need to be careful here because I want to ensure there aren’t any other primes under 400 that include "79" in a non-contiguous way, but that doesn’t apply. Numbers like 197 don’t count either, as it spells "97," not "79." So, the final count of primes with "79" as a substring is exactly three.\
"""
                        ),
                        Thought(
                            thought="""\
**Final check on primes with "79"**

I’m confirming if there are any primes under 400 that have "79" as non-consecutive digits. It turns out there aren’t any. To be thorough, I checked possible patterns like x79, where x ranges from 0 to 3. I found 79, 179, and 379 as primes, but 279 is composite. The pattern 79x leads to 790-799, all of which exceed 400. Thus, I reaffirm that the only valid primes containing "79" are three: 79, 179, and 379.\
"""
                        ),
                        Text(text="3"),
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-5:responses",
                    provider_model_name="gpt-5:responses",
                    raw_message=[
                        {
                            "id": "rs_0d53aa13846e03a60068f9676daff881959d7f269101ba6689",
                            "summary": [
                                {
                                    "text": """\
**Counting primes with "79" substring**

I need to find primes less than 400 that contain "79" as a substring. The possible candidates are 79 itself, and three-digit numbers like 179, 279, and 379. However, 790 and above don’t count since they exceed 400. It’s important to remember that "79" must be contiguous, so numbers like 97 or variations across boundaries don’t qualify. Ultimately, the valid primes are 79, 179, 279, and 379.\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Finalizing prime list with "79"**

I’m surveying numbers that can contain "79." The only valid two-digit option is 79 itself. For three-digit numbers below 400, we have 179, 279, and 379. Upon checking, 179 and 79 are confirmed as primes, while 279 is divisible by 3 and therefore not a prime. I thought about 97 but it doesn’t contain "79," and, even though 197 has 97 as digits, it doesn’t qualify either. Ultimately, my confirmed primes are 79, 179, and 379.\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Confirming prime status of candidates**

I’ve confirmed that the primes are 79, 179, and 379, which gives us three valid primes. To verify: 79 is standardly recognized as prime. Next, I checked 179 by testing divisibility with primes under its square root (about 13.38) and confirmed it’s prime through various checks. \n\

279 isn’t prime since it's divisible by 3. Lastly, I checked 379, and after testing it against primes below its square root (about 19.4), it turns out to be prime too. So, the final count remains three, but 97, 197, and 297 don’t qualify.\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Finalizing primes containing "79"**

I’m checking 397, but it actually contains "97" as digits 2-3, not "79." My valid primes so far are 79, 179, and 379, which totals three. I need to be careful here because I want to ensure there aren’t any other primes under 400 that include "79" in a non-contiguous way, but that doesn’t apply. Numbers like 197 don’t count either, as it spells "97," not "79." So, the final count of primes with "79" as a substring is exactly three.\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Final check on primes with "79"**

I’m confirming if there are any primes under 400 that have "79" as non-consecutive digits. It turns out there aren’t any. To be thorough, I checked possible patterns like x79, where x ranges from 0 to 3. I found 79, 179, and 379 as primes, but 279 is composite. The pattern 79x leads to 790-799, all of which exceed 400. Thus, I reaffirm that the only valid primes containing "79" are three: 79, 179, and 379.\
""",
                                    "type": "summary_text",
                                },
                            ],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_0d53aa13846e03a60068f96780d46c819584f9622a799dc650",
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
                            "id": "rs_0d53aa13846e03a60068f96782110c819595e243559c4243eb",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_0d53aa13846e03a60068f96782397c81958e1c8a764e02de61",
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
**Identifying primes with substring "79"**

I need to find prime numbers less than 400 that have the substring "79." That means I should consider numbers like 79, 179, 279, and 379. But now, I realize any numbers like 790 or higher are not applicable since they're over 400. I’ve ruled out any instances where "79" is not in that exact order. So, the valid primes under 400 containing "79" are 79, 179, 279, and 379.\
"""
                        ),
                        Thought(
                            thought="""\
**Checking primality of numbers with "79"**

I’m looking at numbers that contain "79" as a substring and checking if they are prime. The valid numbers are 79, 179, 279, and 379. \n\

For 79, it is indeed prime since it’s not divisible by any small primes. \n\

179 is also prime after checking divisibility against smaller primes. \n\

However, 279 is composite because its digits sum to 18, which is divisible by 3, and thus it’s ruled out. \n\

I still need to check the primality of 379!\
"""
                        ),
                        Thought(
                            thought="""\
**Confirming prime counts with "79"**

I’m checking the primality of 379. I verified it against smaller primes: it isn’t divisible by 2, 3, 5, 7, 11, 13, 17, or 19. So, it turns out 379 is prime!

Now, counting the primes: we have 79, 179, and 379, bringing the total to three. I checked for additional numbers under 400 with the substring "79," but only found those three. Numbers like 197 and 97 don’t count, so the final answer is three.\
"""
                        ),
                        Thought(
                            thought="""\
**Finalizing prime count**

I want to double-check the primality of 179. It has a remainder of 4 when divided by 7, 3 when divided by 11, and 10 when divided by 13, confirming that it's prime. So, I can confidently say we have three primes under 400. It’s important to clarify that we're looking for primes strictly less than 400. \n\

The final answer is simply "3." Great, let's go with that!\
"""
                        ),
                        Text(text="3"),
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-5:responses",
                    provider_model_name="gpt-5:responses",
                    raw_message=[
                        {
                            "id": "rs_0ab4ebd2bc7242170068f96799c350819580541603dcce2ade",
                            "summary": [
                                {
                                    "text": """\
**Identifying primes with substring "79"**

I need to find prime numbers less than 400 that have the substring "79." That means I should consider numbers like 79, 179, 279, and 379. But now, I realize any numbers like 790 or higher are not applicable since they're over 400. I’ve ruled out any instances where "79" is not in that exact order. So, the valid primes under 400 containing "79" are 79, 179, 279, and 379.\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Checking primality of numbers with "79"**

I’m looking at numbers that contain "79" as a substring and checking if they are prime. The valid numbers are 79, 179, 279, and 379. \n\

For 79, it is indeed prime since it’s not divisible by any small primes. \n\

179 is also prime after checking divisibility against smaller primes. \n\

However, 279 is composite because its digits sum to 18, which is divisible by 3, and thus it’s ruled out. \n\

I still need to check the primality of 379!\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Confirming prime counts with "79"**

I’m checking the primality of 379. I verified it against smaller primes: it isn’t divisible by 2, 3, 5, 7, 11, 13, 17, or 19. So, it turns out 379 is prime!

Now, counting the primes: we have 79, 179, and 379, bringing the total to three. I checked for additional numbers under 400 with the substring "79," but only found those three. Numbers like 197 and 97 don’t count, so the final answer is three.\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Finalizing prime count**

I want to double-check the primality of 179. It has a remainder of 4 when divided by 7, 3 when divided by 11, and 10 when divided by 13, confirming that it's prime. So, I can confidently say we have three primes under 400. It’s important to clarify that we're looking for primes strictly less than 400. \n\

The final answer is simply "3." Great, let's go with that!\
""",
                                    "type": "summary_text",
                                },
                            ],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_0ab4ebd2bc7242170068f967b1153c8195a162cecc2604f8db",
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
                            "id": "rs_0ab4ebd2bc7242170068f967b2afc08195ad15d0afaf6cec91",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_0ab4ebd2bc7242170068f967b2d81081958962a3e63e620d52",
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
            "provider_model_name": "gpt-5:responses",
            "model_id": "openai/gpt-5:responses",
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

I need to count prime numbers less than 400 that contain '79' as a substring. This means I’m looking for numbers like 79, 179, and 279, but I realized that 197 doesn't fit because it contains 97 instead. So the valid numbers are 79, 179, 279, and 379. For three-digit numbers starting with '79', the range is 790-799, which exceeds 400, so they’re not applicable. My focus remains on 79, 179, 279, and 379 only.\
"""
                        ),
                        Thought(
                            thought="""\
**Evaluating primes with '79'**

I’ve got three-digit numbers like 179, 279, and 379 that have '79.' For two-digit, there's 79 itself. Now, I need to check which of these are prime. We know 79 is prime. I think 179 is also prime, but 279 is not since it’s divisible by 3. For 379, it appears to be prime; I checked and '79' indeed appears consecutively within it. However, 797 exceeds 400, so I won't count that. So, the primes I'm left with are 79, 179, and 379.\
"""
                        ),
                        Thought(
                            thought="""\
**Identifying numbers with '79'**

Let’s find all numbers under 400 that contain '79.' The two-digit number is 79. For three-digit numbers, the possible patterns are 179, 279, and 379 while anything starting with '79' (like 790-799) is out since they're above 400. So, the valid numbers are just 79, 179, 279, and 379. \n\

Now, I need to check for primes among them. I know that 79 is prime. For 179, I confirmed it’s not divisible by 3, 5, 7, 11, or 13, so it should be prime too!\
"""
                        ),
                        Thought(
                            thought="""\
**Verifying primes and counts**

For 179, I checked it against several primes and confirmed that it’s indeed prime. As for 279, it’s divisible by 3, so it’s not prime. \n\

Then I turned to 379. The square root is about 19.467, so I checked against all prime numbers up to 19 and found that none divide it evenly. Thus, 379 is also prime. \n\

So, I have three primes: 79, 179, and 379. I made sure to rule out other numbers containing '79' and concluded that the answer is 3 primes altogether.\
"""
                        ),
                        Text(text="3"),
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-5:responses",
                    provider_model_name="gpt-5:responses",
                    raw_message=[
                        {
                            "id": "rs_0322c5b1ca9ff7880068f967837b6c8197a69ef0a078c97a0e",
                            "summary": [
                                {
                                    "text": """\
**Counting primes with substring '79'**

I need to count prime numbers less than 400 that contain '79' as a substring. This means I’m looking for numbers like 79, 179, and 279, but I realized that 197 doesn't fit because it contains 97 instead. So the valid numbers are 79, 179, 279, and 379. For three-digit numbers starting with '79', the range is 790-799, which exceeds 400, so they’re not applicable. My focus remains on 79, 179, 279, and 379 only.\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Evaluating primes with '79'**

I’ve got three-digit numbers like 179, 279, and 379 that have '79.' For two-digit, there's 79 itself. Now, I need to check which of these are prime. We know 79 is prime. I think 179 is also prime, but 279 is not since it’s divisible by 3. For 379, it appears to be prime; I checked and '79' indeed appears consecutively within it. However, 797 exceeds 400, so I won't count that. So, the primes I'm left with are 79, 179, and 379.\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Identifying numbers with '79'**

Let’s find all numbers under 400 that contain '79.' The two-digit number is 79. For three-digit numbers, the possible patterns are 179, 279, and 379 while anything starting with '79' (like 790-799) is out since they're above 400. So, the valid numbers are just 79, 179, 279, and 379. \n\

Now, I need to check for primes among them. I know that 79 is prime. For 179, I confirmed it’s not divisible by 3, 5, 7, 11, or 13, so it should be prime too!\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Verifying primes and counts**

For 179, I checked it against several primes and confirmed that it’s indeed prime. As for 279, it’s divisible by 3, so it’s not prime. \n\

Then I turned to 379. The square root is about 19.467, so I checked against all prime numbers up to 19 and found that none divide it evenly. Thus, 379 is also prime. \n\

So, I have three primes: 79, 179, and 379. I made sure to rule out other numbers containing '79' and concluded that the answer is 3 primes altogether.\
""",
                                    "type": "summary_text",
                                },
                            ],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_0322c5b1ca9ff7880068f9679731808197b75d13ae2de5a285",
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
                            "id": "rs_0322c5b1ca9ff7880068f9679857988197b0db6ead99086fd3",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_0322c5b1ca9ff7880068f9679893288197903c261cea7774dc",
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
            "provider_model_name": "gpt-5:responses",
            "model_id": "openai/gpt-5:responses",
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
**Counting substring primes**

I need to count the prime numbers less than 400 that contain "79" as a substring, which means the digits should include "79" together. \n\

Okay, so I start with 79, which is prime. Next is 179; that also works since it has "79" at the end. For 197, it doesn’t count because the digits are 1-9-7. I check others too, like 279, 379—actually, 379 works—now for others up to 399. \n\

But 793 is over my limit, so I’ll focus only on numbers below 400.\
"""
                        ),
                        Thought(
                            thought="""\
**Analyzing prime candidates**

I’m looking into numbers with "79" in them. For three-digit numbers below 400, I see patterns: those ending in 79 (like 179, 279, 379) and starting with 79 don’t count since they exceed 400. \n\

The only two-digit option is 79 itself. I already checked the endings; now I realize 279 isn't prime because it's divisible by 3. So, I need to verify if 379 is prime next. \n\

That narrows down my candidates for primes containing "79"!\
"""
                        ),
                        Thought(
                            thought="""\
**Verifying prime numbers**

I’m testing if 379 is prime. The square root is around 19.4, so I’ll check primality against smaller primes like 3, 5, 7, 11, 13, 17, and 19. It’s not divisible by any of those. \n\

Next, I check 179, and it’s prime too. So far, I have 79, 179, and 379 as primes. I wonder if there are others below 400. \n\

But 297 doesn’t count, since it doesn't have "79" together, and 790 is over my limit. So, I’m stuck with those three!\
"""
                        ),
                        Thought(
                            thought="""\
**Finalizing prime count**

I realize that since "substring" refers to something contiguous, 97 can't count as "79" reversed. So, I still think there are 3 valid primes: 79, 179, and 379. I double-check other three-digit possibilities starting with "79," but none qualify since they’d exceed 400. \n\

I confirmed each candidate: 79, 179, and 379 are primes, while 279 isn’t. Thus, the total count remains three. I’ll summarize the answer as “3” and make sure everything is accurate.\
"""
                        ),
                        Thought(
                            thought="""\
**Delivering the answer**

The user wants a straightforward response, just the number without explanations. I need to stick to that and confirm again: the count is indeed "3." \n\

I’ll double-check for any primes like 197, but it doesn't have "79." And 297 isn’t prime, nor does it contain the substring. So I’m all set to deliver the answer without any additional text. The final output is "3."\
"""
                        ),
                        Text(text="3"),
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-5:responses",
                    provider_model_name="gpt-5:responses",
                    raw_message=[
                        {
                            "id": "rs_00b850169f72b9300068f967b4c96481948d13a53c8867e8d8",
                            "summary": [
                                {
                                    "text": """\
**Counting substring primes**

I need to count the prime numbers less than 400 that contain "79" as a substring, which means the digits should include "79" together. \n\

Okay, so I start with 79, which is prime. Next is 179; that also works since it has "79" at the end. For 197, it doesn’t count because the digits are 1-9-7. I check others too, like 279, 379—actually, 379 works—now for others up to 399. \n\

But 793 is over my limit, so I’ll focus only on numbers below 400.\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Analyzing prime candidates**

I’m looking into numbers with "79" in them. For three-digit numbers below 400, I see patterns: those ending in 79 (like 179, 279, 379) and starting with 79 don’t count since they exceed 400. \n\

The only two-digit option is 79 itself. I already checked the endings; now I realize 279 isn't prime because it's divisible by 3. So, I need to verify if 379 is prime next. \n\

That narrows down my candidates for primes containing "79"!\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Verifying prime numbers**

I’m testing if 379 is prime. The square root is around 19.4, so I’ll check primality against smaller primes like 3, 5, 7, 11, 13, 17, and 19. It’s not divisible by any of those. \n\

Next, I check 179, and it’s prime too. So far, I have 79, 179, and 379 as primes. I wonder if there are others below 400. \n\

But 297 doesn’t count, since it doesn't have "79" together, and 790 is over my limit. So, I’m stuck with those three!\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Finalizing prime count**

I realize that since "substring" refers to something contiguous, 97 can't count as "79" reversed. So, I still think there are 3 valid primes: 79, 179, and 379. I double-check other three-digit possibilities starting with "79," but none qualify since they’d exceed 400. \n\

I confirmed each candidate: 79, 179, and 379 are primes, while 279 isn’t. Thus, the total count remains three. I’ll summarize the answer as “3” and make sure everything is accurate.\
""",
                                    "type": "summary_text",
                                },
                                {
                                    "text": """\
**Delivering the answer**

The user wants a straightforward response, just the number without explanations. I need to stick to that and confirm again: the count is indeed "3." \n\

I’ll double-check for any primes like 197, but it doesn't have "79." And 297 isn’t prime, nor does it contain the substring. So I’m all set to deliver the answer without any additional text. The final output is "3."\
""",
                                    "type": "summary_text",
                                },
                            ],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_00b850169f72b9300068f967cac6b08194a3d0922427ac66db",
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
                            "id": "rs_00b850169f72b9300068f967cc559c8194a05a106b3f51420e",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_00b850169f72b9300068f967ccb18081949c250217c44c88b7",
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
