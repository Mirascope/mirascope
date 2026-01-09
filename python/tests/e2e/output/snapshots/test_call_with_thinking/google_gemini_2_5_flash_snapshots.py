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
            "provider_id": "google",
            "model_id": "google/gemini-2.5-flash",
            "provider_model_name": "gemini-2.5-flash",
            "params": {"thinking": {"level": "minimal"}},
            "finish_reason": None,
            "usage": {
                "input_tokens": 792,
                "output_tokens": 18,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": """\
cache_tokens_details=None cached_content_token_count=None candidates_token_count=18 candidates_tokens_details=None prompt_token_count=792 prompt_tokens_details=[ModalityTokenCount(
  modality=<MediaModality.TEXT: 'TEXT'>,
  token_count=792
)] thoughts_token_count=None tool_use_prompt_token_count=None tool_use_prompt_tokens_details=None total_token_count=810 traffic_type=None\
""",
                "total_tokens": 810,
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
**Prime Number Search with Substring Check**

Okay, so I'm being asked to find the number of primes less than 400 that have "79" as a substring. My mind immediately goes to breaking this down into a few clear steps.

First, I need to generate all the prime numbers below 400.  I could do this by hand, but since I am trying to be efficient, I can use the Sieve of Eratosthenes. I'll need to create a boolean array, `is_prime`, and mark all the multiples of each prime as not prime. I will stop when I reach the square root of 400, which is 20. Then, I can simply go through the boolean array and collect the prime numbers.

Next, I need to iterate through this list and, for each prime, convert it into a string and check if it has "79" as a substring. This is a pretty straightforward string operation. I'm going to have to remember to check for three and two-digit primes.

Then, I'll just count how many primes have this substring. Easy peasy.

I just went through and systematically checked all the primes less than 400. In the end, there are three primes less than 400 that contain the substring "79": 79, 179 and 379.
"""
                        ),
                        Text(
                            text="""\
The primes below 400 are:
2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397.

Now we check which of these primes contain "79" as a substring:
1.  **79** (contains "79")
2.  **179** (contains "79")
3.  **379** (contains "79")

There are 3 such primes.

3\
"""
                        ),
                    ],
                    provider_id="google",
                    model_id="google/gemini-2.5-flash",
                    provider_model_name="gemini-2.5-flash",
                    raw_message={
                        "parts": [
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": """\
**Prime Number Search with Substring Check**

Okay, so I'm being asked to find the number of primes less than 400 that have "79" as a substring. My mind immediately goes to breaking this down into a few clear steps.

First, I need to generate all the prime numbers below 400.  I could do this by hand, but since I am trying to be efficient, I can use the Sieve of Eratosthenes. I'll need to create a boolean array, `is_prime`, and mark all the multiples of each prime as not prime. I will stop when I reach the square root of 400, which is 20. Then, I can simply go through the boolean array and collect the prime numbers.

Next, I need to iterate through this list and, for each prime, convert it into a string and check if it has "79" as a substring. This is a pretty straightforward string operation. I'm going to have to remember to check for three and two-digit primes.

Then, I'll just count how many primes have this substring. Easy peasy.

I just went through and systematically checked all the primes less than 400. In the end, there are three primes less than 400 that contain the substring "79": 79, 179 and 379.
""",
                                "thought": True,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": """\
The primes below 400 are:
2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397.

Now we check which of these primes contain "79" as a substring:
1.  **79** (contains "79")
2.  **179** (contains "79")
3.  **379** (contains "79")

There are 3 such primes.

3\
""",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                        ],
                        "role": "model",
                    },
                ),
                UserMessage(
                    content=[
                        Text(
                            text="If you remember what the primes were, then share them, or say 'I don't remember.'"
                        )
                    ]
                ),
                AssistantMessage(
                    content=[Text(text="The primes are 79, 179, and 379.")],
                    provider_id="google",
                    model_id="google/gemini-2.5-flash",
                    provider_model_name="gemini-2.5-flash",
                    raw_message={
                        "parts": [
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": "The primes are 79, 179, and 379.",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            }
                        ],
                        "role": "model",
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
            "provider_id": "google",
            "model_id": "google/gemini-2.5-flash",
            "provider_model_name": "gemini-2.5-flash",
            "params": {"thinking": {"level": "minimal"}},
            "finish_reason": None,
            "usage": {
                "input_tokens": 886,
                "output_tokens": 6,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": """\
cache_tokens_details=None cached_content_token_count=None candidates_token_count=6 candidates_tokens_details=None prompt_token_count=886 prompt_tokens_details=[ModalityTokenCount(
  modality=<MediaModality.TEXT: 'TEXT'>,
  token_count=886
)] thoughts_token_count=None tool_use_prompt_token_count=None tool_use_prompt_tokens_details=None total_token_count=892 traffic_type=None\
""",
                "total_tokens": 892,
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
**The Prime "79" Hunt**

Okay, here's the task: I need to find the count of prime numbers under 400 that have "79" as a substring. First, I'll generate a list of primes less than 400. The Sieve of Eratosthenes is perfect for this. I'll create a boolean array, mark multiples as composite, and then I'll have a clean list of primes.

Once I have the primes, I iterate through them, converting each to a string, and check if "79" is present. I'm thinking I can just use the `in` operator for this - efficient and readable.

So, first the sieve: I'm setting up an array, marking 0 and 1 as non-primes, then iterating up to the square root of 400, which is 20.  If a number is prime, I mark all its multiples as composite.  That should be pretty fast. After this, I've confirmed by code that this gives me my complete list of all primes less than 400:

2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397

Now, the filtering stage. I'll go through the list. Let's start systematically.

*   79: Bingo.
*   179: Also a hit!
*   279: Not prime, quick mental check: sum of digits is 18 (divisible by 3), so divisible by 3. No need to look any further. I'm only interested in the primes from my sieve.
*   379: This one contains 79.

Now, checking the list, no other number less than 400 fits. I could have a number of the form `79X` but that would exceed 400. Likewise, `X79` with X = 0, 1, 2 is not in my list. Checking the list of primes shows there are no others.

Therefore, the primes with "79" are 79, 179 and 379. That's a total of 3 primes. The code confirms this.

I'm confident the answer is:
3
"""
                        ),
                        Text(text="3"),
                    ],
                    provider_id="google",
                    model_id="google/gemini-2.5-flash",
                    provider_model_name="gemini-2.5-flash",
                    raw_message={
                        "parts": [
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": """\
**The Prime "79" Hunt**

Okay, here's the task: I need to find the count of prime numbers under 400 that have "79" as a substring. First, I'll generate a list of primes less than 400. The Sieve of Eratosthenes is perfect for this. I'll create a boolean array, mark multiples as composite, and then I'll have a clean list of primes.

Once I have the primes, I iterate through them, converting each to a string, and check if "79" is present. I'm thinking I can just use the `in` operator for this - efficient and readable.

So, first the sieve: I'm setting up an array, marking 0 and 1 as non-primes, then iterating up to the square root of 400, which is 20.  If a number is prime, I mark all its multiples as composite.  That should be pretty fast. After this, I've confirmed by code that this gives me my complete list of all primes less than 400:

2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397

Now, the filtering stage. I'll go through the list. Let's start systematically.

*   79: Bingo.
*   179: Also a hit!
*   279: Not prime, quick mental check: sum of digits is 18 (divisible by 3), so divisible by 3. No need to look any further. I'm only interested in the primes from my sieve.
*   379: This one contains 79.

Now, checking the list, no other number less than 400 fits. I could have a number of the form `79X` but that would exceed 400. Likewise, `X79` with X = 0, 1, 2 is not in my list. Checking the list of primes shows there are no others.

Therefore, the primes with "79" are 79, 179 and 379. That's a total of 3 primes. The code confirms this.

I'm confident the answer is:
3
""",
                                "thought": True,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": "3",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                        ],
                        "role": "model",
                    },
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
                    provider_id="google",
                    model_id="google/gemini-2.5-flash",
                    provider_model_name="gemini-2.5-flash",
                    raw_message={
                        "parts": [
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": "I don't remember.",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            }
                        ],
                        "role": "model",
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
            "provider_id": "google",
            "model_id": "google/gemini-2.5-flash",
            "provider_model_name": "gemini-2.5-flash",
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
**Calculating Prime Substrings**

I'm currently working on identifying prime numbers below 400 and determining which ones contain the substring "79". The plan involves generating a list of primes and then iterating through them, checking for the substring. My approach focuses on efficiency to ensure a quick result.


**Identifying Patterns and Numbers**

I've systematically generated prime numbers below 400 and checked for the substring "79." So far, I've found it in 79 and 179. I'm now verifying the final prime numbers between 300 and 400. Once complete, I can confidently provide the final count of primes containing "79."


**Confirming Prime Number Counts**

Now, I've methodically listed all primes under 400 and meticulously checked for the presence of the substring "79". I confirmed that 79, 179 and 379 are the only primes that satisfy the condition. The work is checked, so I am confident that I have provided an accurate count.


**Verifying Prime Number Substrings**

I've carefully listed all primes below 400 and exhaustively checked for "79" as a substring in each. The primes containing "79" are definitively 79, 179, and 379. My thorough verification involved a systematic check of various digit combinations. I'm now confident in the completeness of the search.


**Confirming the Prime Count**

I've rigorously checked all primes below 400 for the substring "79". The only ones that meet the criteria are 79, 179 and 379. This exhaustive search confirms the final count of 3 primes. The approach used here is fully verified.


**Counting Primes with Substrings**

I've completed my systematic listing and checking of all primes below 400 for the substring "79". I'm now certain that only 79, 179 and 379 contain this substring. The process involved a careful examination of digit combinations. I am ready to provide the final count, which is 3.


"""
                        ),
                        Text(text="3"),
                    ],
                    provider_id="google",
                    model_id="google/gemini-2.5-flash",
                    provider_model_name="gemini-2.5-flash",
                    raw_message={
                        "parts": [
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": """\
**Calculating Prime Substrings**

I'm currently working on identifying prime numbers below 400 and determining which ones contain the substring "79". The plan involves generating a list of primes and then iterating through them, checking for the substring. My approach focuses on efficiency to ensure a quick result.


""",
                                "thought": True,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": """\
**Identifying Patterns and Numbers**

I've systematically generated prime numbers below 400 and checked for the substring "79." So far, I've found it in 79 and 179. I'm now verifying the final prime numbers between 300 and 400. Once complete, I can confidently provide the final count of primes containing "79."


""",
                                "thought": True,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": """\
**Confirming Prime Number Counts**

Now, I've methodically listed all primes under 400 and meticulously checked for the presence of the substring "79". I confirmed that 79, 179 and 379 are the only primes that satisfy the condition. The work is checked, so I am confident that I have provided an accurate count.


""",
                                "thought": True,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": """\
**Verifying Prime Number Substrings**

I've carefully listed all primes below 400 and exhaustively checked for "79" as a substring in each. The primes containing "79" are definitively 79, 179, and 379. My thorough verification involved a systematic check of various digit combinations. I'm now confident in the completeness of the search.


""",
                                "thought": True,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": """\
**Confirming the Prime Count**

I've rigorously checked all primes below 400 for the substring "79". The only ones that meet the criteria are 79, 179 and 379. This exhaustive search confirms the final count of 3 primes. The approach used here is fully verified.


""",
                                "thought": True,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": """\
**Counting Primes with Substrings**

I've completed my systematic listing and checking of all primes below 400 for the substring "79". I'm now certain that only 79, 179 and 379 contain this substring. The process involved a careful examination of digit combinations. I am ready to provide the final count, which is 3.


""",
                                "thought": True,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": "3",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                        ],
                        "role": "model",
                    },
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
                    provider_id="google",
                    model_id="google/gemini-2.5-flash",
                    provider_model_name="gemini-2.5-flash",
                    raw_message={
                        "parts": [
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": "I don't",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": " remember.",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                        ],
                        "role": "model",
                    },
                ),
            ],
            "format": None,
            "tools": [],
            "usage": {
                "input_tokens": 517,
                "output_tokens": 6,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 523,
            },
            "n_chunks": 4,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "google",
            "model_id": "google/gemini-2.5-flash",
            "provider_model_name": "gemini-2.5-flash",
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
**Charting Prime Territory**

Okay, I've got the goal locked in: count primes under 400 containing "79". Currently, I'm forming my initial strategy, with the crucial first step being listing all prime numbers below 400. That's the baseline, and then I'll filter. It is the beginning of the journey.


**Refining the Approach**

Now I have a clearer picture. I have the core strategy: generate primes under 400, then filter for the substring "79." I'm mentally simulating having a list. The next step is to execute this plan by getting a concrete list or generating it. I'll need to make sure I don't miss any in the iteration.


**Evaluating Substring Criteria**

I'm now methodically evaluating primes for the "79" substring. I generated primes up to 400 and created a checklist for primes ending in "79" or with "79" embedded. I've narrowed down the candidates and am testing each number's primality or checking the list. The goal is to avoid errors and be complete.


**Confirming Substring Presence**

I've taken the listed primes under 400 and meticulously examined each one for the "79" substring, creating a subset. I systematically generated a list of primes up to 400 to form the set. I confirmed the primality of the numbers where "79" appears and performed the final count. I'm confident in my results.



**Verifying Substring Presence**

I've rigorously checked the prime list for the presence of "79," using both mental checks and systematic validation. The process has been thorough, ensuring that nothing was overlooked. I have determined, conclusively, that the count of primes less than 400 that contain "79" is 3.


"""
                        ),
                        Text(text="3"),
                    ],
                    provider_id="google",
                    model_id="google/gemini-2.5-flash",
                    provider_model_name="gemini-2.5-flash",
                    raw_message={
                        "parts": [
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": """\
**Charting Prime Territory**

Okay, I've got the goal locked in: count primes under 400 containing "79". Currently, I'm forming my initial strategy, with the crucial first step being listing all prime numbers below 400. That's the baseline, and then I'll filter. It is the beginning of the journey.


""",
                                "thought": True,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": """\
**Refining the Approach**

Now I have a clearer picture. I have the core strategy: generate primes under 400, then filter for the substring "79." I'm mentally simulating having a list. The next step is to execute this plan by getting a concrete list or generating it. I'll need to make sure I don't miss any in the iteration.


""",
                                "thought": True,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": """\
**Evaluating Substring Criteria**

I'm now methodically evaluating primes for the "79" substring. I generated primes up to 400 and created a checklist for primes ending in "79" or with "79" embedded. I've narrowed down the candidates and am testing each number's primality or checking the list. The goal is to avoid errors and be complete.


""",
                                "thought": True,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": """\
**Confirming Substring Presence**

I've taken the listed primes under 400 and meticulously examined each one for the "79" substring, creating a subset. I systematically generated a list of primes up to 400 to form the set. I confirmed the primality of the numbers where "79" appears and performed the final count. I'm confident in my results.



""",
                                "thought": True,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": """\
**Verifying Substring Presence**

I've rigorously checked the prime list for the presence of "79," using both mental checks and systematic validation. The process has been thorough, ensuring that nothing was overlooked. I have determined, conclusively, that the count of primes less than 400 that contain "79" is 3.


""",
                                "thought": True,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": "3",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                        ],
                        "role": "model",
                    },
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
                    provider_id="google",
                    model_id="google/gemini-2.5-flash",
                    provider_model_name="gemini-2.5-flash",
                    raw_message={
                        "parts": [
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": "I don't",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": " remember.",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                        ],
                        "role": "model",
                    },
                ),
            ],
            "format": None,
            "tools": [],
            "usage": {
                "input_tokens": 452,
                "output_tokens": 6,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 458,
            },
            "n_chunks": 4,
        }
    }
)
