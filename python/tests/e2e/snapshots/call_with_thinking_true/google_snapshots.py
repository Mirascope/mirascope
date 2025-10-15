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
            "provider": "google",
            "model_id": "gemini-2.5-flash",
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
**The Problem and My Approach**

Okay, so I'm being asked to find how many prime numbers less than 400 have "79" as a substring. My immediate thought is to create a systematic process: first, list all the prime numbers below 400, then iterate through that list, and for each number, check if the string "79" is present within it. Finally, I'll keep a running count of the numbers that satisfy the condition.

**Listing Primes**

Let's begin by generating the list of primes below 400. That part is fairly straightforward; I can either recall them or quickly compute them.  I've got the list ready: 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397.

**Substring Check and Counting**

Now the main part begins. I'll go through the primes and check for the presence of "79".

*   **Numbers below 79:** Clearly, none of these will have "79."
*   **79:** Yes, this is a prime and contains "79" (Count = 1).
*   **Numbers between 80-99:**  None will contain "79".
*   **Numbers between 100-199:**
    *   179: Yes, this contains "79" (Count = 2).
*   **Numbers between 200-299:**  The only numbers of interest will have "79" as a substring somewhere in them. So, no number containing 279, or 790 or 791 (which aren't prime).
    *   279 is out because it's divisible by 3. Checking the primes remaining, none of them will have '79'.
*   **Numbers between 300-399:**
    *   I see 379.  I need to double-check if 379 is actually prime, but it's a good candidate. I do the divisibility checks and it's indeed prime. (Count = 3)

I've been systematic, now let's summarize my findings.
**Final Count**

The primes less than 400 that have "79" as a substring are 79, 179, and 379.  Therefore, the final count is 3. I'm confident in this answer now.
"""
                        ),
                        Text(text="3"),
                    ],
                    provider="google",
                    model_id="gemini-2.5-flash",
                    raw_content=[
                        {
                            "video_metadata": None,
                            "thought": True,
                            "inline_data": None,
                            "file_data": None,
                            "thought_signature": None,
                            "code_execution_result": None,
                            "executable_code": None,
                            "function_call": None,
                            "function_response": None,
                            "text": """\
**The Problem and My Approach**

Okay, so I'm being asked to find how many prime numbers less than 400 have "79" as a substring. My immediate thought is to create a systematic process: first, list all the prime numbers below 400, then iterate through that list, and for each number, check if the string "79" is present within it. Finally, I'll keep a running count of the numbers that satisfy the condition.

**Listing Primes**

Let's begin by generating the list of primes below 400. That part is fairly straightforward; I can either recall them or quickly compute them.  I've got the list ready: 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397.

**Substring Check and Counting**

Now the main part begins. I'll go through the primes and check for the presence of "79".

*   **Numbers below 79:** Clearly, none of these will have "79."
*   **79:** Yes, this is a prime and contains "79" (Count = 1).
*   **Numbers between 80-99:**  None will contain "79".
*   **Numbers between 100-199:**
    *   179: Yes, this contains "79" (Count = 2).
*   **Numbers between 200-299:**  The only numbers of interest will have "79" as a substring somewhere in them. So, no number containing 279, or 790 or 791 (which aren't prime).
    *   279 is out because it's divisible by 3. Checking the primes remaining, none of them will have '79'.
*   **Numbers between 300-399:**
    *   I see 379.  I need to double-check if 379 is actually prime, but it's a good candidate. I do the divisibility checks and it's indeed prime. (Count = 3)

I've been systematic, now let's summarize my findings.
**Final Count**

The primes less than 400 that have "79" as a substring are 79, 179, and 379.  Therefore, the final count is 3. I'm confident in this answer now.
""",
                        },
                        {
                            "video_metadata": None,
                            "thought": None,
                            "inline_data": None,
                            "file_data": None,
                            "thought_signature": None,
                            "code_execution_result": None,
                            "executable_code": None,
                            "function_call": None,
                            "function_response": None,
                            "text": "3",
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
                    content=[
                        Text(
                            text="279 is not prime, but 277 is prime. 379 is prime. 179 is prime."
                        )
                    ],
                    provider="google",
                    model_id="gemini-2.5-flash",
                    raw_content=[
                        {
                            "video_metadata": None,
                            "thought": None,
                            "inline_data": None,
                            "file_data": None,
                            "thought_signature": None,
                            "code_execution_result": None,
                            "executable_code": None,
                            "function_call": None,
                            "function_response": None,
                            "text": "279 is not prime, but 277 is prime. 379 is prime. 179 is prime.",
                        }
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
            "provider": "google",
            "model_id": "gemini-2.5-flash",
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
**Solving the Substring Prime Counting Problem**

Okay, so I'm being asked to find the number of prime numbers less than 400 that contain the substring "79". My strategy is straightforward: first, generate a list of all primes below 400. Then, iterate through that list, checking if each prime, when converted to a string, contains "79" as a substring. Finally, I just need to count how many primes meet that condition.

I start by mentally listing the primes below 400, carefully working through the numbers. After that, I systematically check each one. For each prime, I just ask myself, "Does this number (as text) have '79' in it?"  I go through the list methodically. 79 is definitely in the list.  Then 179 pops up. And then 379.  No others appear.

To be extra certain, I decide to create a quick Python script.  I write a simple `is_prime` function and use a list comprehension to get all the primes. Then I loop through that list, check for the substring, and increment a counter. The script confirms my initial findings, outputting 3. So, I'm confident my final answer is 3.
"""
                        ),
                        Text(text="3"),
                    ],
                    provider="google",
                    model_id="gemini-2.5-flash",
                    raw_content=[
                        {
                            "video_metadata": None,
                            "thought": True,
                            "inline_data": None,
                            "file_data": None,
                            "thought_signature": None,
                            "code_execution_result": None,
                            "executable_code": None,
                            "function_call": None,
                            "function_response": None,
                            "text": """\
**Solving the Substring Prime Counting Problem**

Okay, so I'm being asked to find the number of prime numbers less than 400 that contain the substring "79". My strategy is straightforward: first, generate a list of all primes below 400. Then, iterate through that list, checking if each prime, when converted to a string, contains "79" as a substring. Finally, I just need to count how many primes meet that condition.

I start by mentally listing the primes below 400, carefully working through the numbers. After that, I systematically check each one. For each prime, I just ask myself, "Does this number (as text) have '79' in it?"  I go through the list methodically. 79 is definitely in the list.  Then 179 pops up. And then 379.  No others appear.

To be extra certain, I decide to create a quick Python script.  I write a simple `is_prime` function and use a list comprehension to get all the primes. Then I loop through that list, check for the substring, and increment a counter. The script confirms my initial findings, outputting 3. So, I'm confident my final answer is 3.
""",
                        },
                        {
                            "video_metadata": None,
                            "thought": None,
                            "inline_data": None,
                            "file_data": None,
                            "thought_signature": None,
                            "code_execution_result": None,
                            "executable_code": None,
                            "function_call": None,
                            "function_response": None,
                            "text": "3",
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
                    provider="google",
                    model_id="gemini-2.5-flash",
                    raw_content=[
                        {
                            "video_metadata": None,
                            "thought": None,
                            "inline_data": None,
                            "file_data": None,
                            "thought_signature": None,
                            "code_execution_result": None,
                            "executable_code": None,
                            "function_call": None,
                            "function_response": None,
                            "text": "I don't remember.",
                        }
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
            "provider": "google",
            "model_id": "gemini-2.5-flash",
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
**Examining Prime Substrings**

Okay, I've got a handle on the prime number generation up to 400. Currently, I'm focusing on efficiently checking each prime number against the substring "79". The plan is to filter for any primes that do include that string.


**Identifying Candidate Primes**

I've got the prime list below 400 ready. I'm systematically checking each one to see if "79" appears as a substring. So far, 79, 179 and 379 have been found as primes. My focus has shifted to efficiently searching this sorted list and I'm looking for any pattern or formula to quickly select probable primes with the target substring. I also considered excluding numbers ending in '9' as potential candidates.


**Analyzing Substring Presence**

Okay, the prime numbers are already listed, and now, I'm meticulously checking each one. I've streamlined the process to identify any primes containing "79". I'm specifically focused on numbers less than 400. Currently, the primes containing "79" are 79, 179 and 379. It appears I have all the primes.


**Calculating the Count**

I've carefully listed the primes below 400 and double-checked my work.  After systematic analysis, I'm confident that only 79, 179, and 379 contain "79" as a substring. This makes the total count 3 primes that fit the criteria.

**Finalizing the Prime Count**

I've carefully verified that only 79, 179 and 379 contain "79". I'm certain that the count of primes less than 400 with "79" as a substring is exactly 3. My analysis has been rigorous.


"""
                        ),
                        Text(text="3"),
                    ],
                    provider="google",
                    model_id="gemini-2.5-flash",
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
                    content=[Text(text="I don't remember.")],
                    provider="google",
                    model_id="gemini-2.5-flash",
                    raw_content=[],
                ),
            ],
            "format": None,
            "tools": [],
            "n_chunks": 4,
        },
        "logging": [],
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider": "google",
            "model_id": "gemini-2.5-flash",
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
**Pinpointing Prime Candidates**

I'm now zeroing in on the "79" substring constraint. I've switched gears and am using it to refine my prime number search. The goal is the *count*, not the list itself. I'm focusing on efficiency, aiming to avoid unnecessary calculations. The numbers generated must be prime!


**Revising Approach to Primes**

My focus has shifted again. I initially built candidates around the "79" substring, but now I'm starting with prime candidates below 400 and testing for the substring. I'm building a list of prime numbers, then looking for "79". I was incorrect when listing the candidates as 790-799 is out of range.


**Evaluating Candidate Primality**

I'm now methodically evaluating the primality of 79 and 179. I've eliminated some three-digit combinations, recognizing they exceeded the 400 boundary. Currently, I'm verifying the 79 and 179 are prime. With these two numbers, the answer might be quite simple.


**Calculating Candidate Counts**

Okay, I've narrowed it down to 79, 179 and 379.  I'm now methodically evaluating each candidate for primality within the given constraints. So far, 79 and 179 are confirmed prime, and I need to check 379. I'm building a concise count and will finish soon.


**Calculating the Prime Total**

I'm wrapping up the count of prime numbers, meticulously verifying the primality of each candidate. The process has been thorough, and I've double-checked my work. I've now checked primality for 79, 179 and 379 and I am confident in the list of candidates.  I am finalizing the answer and ensuring there are no errors.


**Refining the Candidate List**

I've revised the candidate list based on the "less than 400" constraint, and I'm methodically checking each for primality. I'm taking care not to miss any numbers that fit the criteria. I've narrowed down the list. I've begun prime testing.


"""
                        ),
                        Text(text="3"),
                    ],
                    provider="google",
                    model_id="gemini-2.5-flash",
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
                    content=[Text(text="I don't remember.")],
                    provider="google",
                    model_id="gemini-2.5-flash",
                    raw_content=[],
                ),
            ],
            "format": None,
            "tools": [],
            "n_chunks": 4,
        },
        "logging": [],
    }
)
without_raw_content_snapshot = snapshot(
    {
        "exception": {
            "type": "CannotOverwriteExistingCassetteException",
            "args": "(\"Can't overwrite existing cassette ('/Users/dandelion/git/mirascope/v2/python/tests/e2e/cassettes/call_with_thinking_true/google/without_raw_content.yaml') in your current record mode ('once').\\nNo match for the request (<Request (POST) https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent>) was found.\\nFound 1 similar requests with 1 different matcher(s) :\\n\\n1 - (<Request (POST) https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent>).\\nMatchers succeeded : ['method', 'uri']\\nMatchers failed :\\nbody - assertion failure :\\n\\n\",)",
            "cassette": "<Cassette containing 1 recorded response(s)>",
            "failed_request": "<Request (POST) https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent>",
        },
        "logging": [],
    }
)
