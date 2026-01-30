from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "response": {
            "provider_id": "google",
            "model_id": "google/gemini-2.5-flash",
            "provider_model_name": "gemini-2.5-flash",
            "params": {"thinking": {"level": "medium", "include_thoughts": False}},
            "finish_reason": None,
            "usage": {
                "input_tokens": 30,
                "output_tokens": 2742,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 1973,
                "provider_tool_usage": None,
                "raw": """\
cache_tokens_details=None cached_content_token_count=None candidates_token_count=769 candidates_tokens_details=None prompt_token_count=30 prompt_tokens_details=[ModalityTokenCount(
  modality=<MediaModality.TEXT: 'TEXT'>,
  token_count=30
)] thoughts_token_count=1973 tool_use_prompt_token_count=None tool_use_prompt_tokens_details=None total_token_count=2772 traffic_type=None\
""",
                "total_tokens": 2772,
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
                        Text(
                            text="""\
To find the number of primes below 400 that contain "79" as a substring, we can systematically check numbers in ranges.

1.  **Numbers less than 79:**
    No prime in this range can contain "79" as a substring, as "79" is a two-digit number.

2.  **The number 79 itself:**
    79 is a prime number, and it contains "79" as a substring.
    *Count = 1*

3.  **Numbers between 80 and 99:**
    No prime in this range can contain "79" as a substring, as the first digit would have to be 7.

4.  **Numbers between 100 and 399:**
    For a number `N` in this range to contain "79" as a substring, `N` must be a 3-digit number. The "79" substring can appear in two ways:
    *   **The number starts with 79 (e.g., 79X):**
        These numbers would be 790, 791, 792, ..., 799. All of these are greater than 400. So, no primes from this form are below 400.
    *   **The number ends with 79 (e.g., X79):**
        We need to check numbers of the form 179, 279, 379 for primality.
        *   **179:**
            To check if 179 is prime, we test divisibility by primes up to sqrt(179) which is approx 13.3.
            179 is not divisible by 2, 3 (1+7+9=17), 5.
            179 / 7 = 25 R 4
            179 / 11 = 16 R 3
            179 / 13 = 13 R 10
            So, 179 is prime.
            *Count = 1 + 1 = 2*
        *   **279:**
            The sum of digits is 2+7+9 = 18, which is divisible by 3.
            279 = 3 * 93 = 3 * 3 * 31. So, 279 is not prime.
        *   **379:**
            To check if 379 is prime, we test divisibility by primes up to sqrt(379) which is approx 19.4.
            379 is not divisible by 2, 3 (3+7+9=19), 5.
            379 / 7 = 54 R 1
            379 / 11 = 34 R 5
            379 / 13 = 29 R 2
            379 / 17 = 22 R 5
            379 / 19 = 19 R 18
            So, 379 is prime.
            *Count = 2 + 1 = 3*

The primes below 400 that contain "79" as a substring are 79, 179, and 379. There are 3 such primes.

3\
"""
                        )
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
To find the number of primes below 400 that contain "79" as a substring, we can systematically check numbers in ranges.

1.  **Numbers less than 79:**
    No prime in this range can contain "79" as a substring, as "79" is a two-digit number.

2.  **The number 79 itself:**
    79 is a prime number, and it contains "79" as a substring.
    *Count = 1*

3.  **Numbers between 80 and 99:**
    No prime in this range can contain "79" as a substring, as the first digit would have to be 7.

4.  **Numbers between 100 and 399:**
    For a number `N` in this range to contain "79" as a substring, `N` must be a 3-digit number. The "79" substring can appear in two ways:
    *   **The number starts with 79 (e.g., 79X):**
        These numbers would be 790, 791, 792, ..., 799. All of these are greater than 400. So, no primes from this form are below 400.
    *   **The number ends with 79 (e.g., X79):**
        We need to check numbers of the form 179, 279, 379 for primality.
        *   **179:**
            To check if 179 is prime, we test divisibility by primes up to sqrt(179) which is approx 13.3.
            179 is not divisible by 2, 3 (1+7+9=17), 5.
            179 / 7 = 25 R 4
            179 / 11 = 16 R 3
            179 / 13 = 13 R 10
            So, 179 is prime.
            *Count = 1 + 1 = 2*
        *   **279:**
            The sum of digits is 2+7+9 = 18, which is divisible by 3.
            279 = 3 * 93 = 3 * 3 * 31. So, 279 is not prime.
        *   **379:**
            To check if 379 is prime, we test divisibility by primes up to sqrt(379) which is approx 19.4.
            379 is not divisible by 2, 3 (3+7+9=19), 5.
            379 / 7 = 54 R 1
            379 / 11 = 34 R 5
            379 / 13 = 29 R 2
            379 / 17 = 22 R 5
            379 / 19 = 19 R 18
            So, 379 is prime.
            *Count = 2 + 1 = 3*

The primes below 400 that contain "79" as a substring are 79, 179, and 379. There are 3 such primes.

3\
""",
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
            "params": {"thinking": {"level": "medium", "include_thoughts": False}},
            "finish_reason": None,
            "usage": {
                "input_tokens": 30,
                "output_tokens": 3069,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 3068,
                "provider_tool_usage": None,
                "raw": """\
cache_tokens_details=None cached_content_token_count=None candidates_token_count=1 candidates_tokens_details=None prompt_token_count=30 prompt_tokens_details=[ModalityTokenCount(
  modality=<MediaModality.TEXT: 'TEXT'>,
  token_count=30
)] thoughts_token_count=3068 tool_use_prompt_token_count=None tool_use_prompt_tokens_details=None total_token_count=3099 traffic_type=None\
""",
                "total_tokens": 3099,
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
                    content=[Text(text="3")],
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
                                "text": "3",
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
                    content=[Text(text="3")],
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
                                "text": "3",
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
            "usage": {
                "input_tokens": 30,
                "output_tokens": 1,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 2814,
                "provider_tool_usage": None,
                "raw": "None",
                "total_tokens": 31,
            },
            "n_chunks": 3,
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
                    content=[Text(text="3")],
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
                                "text": "3",
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
            "usage": {
                "input_tokens": 30,
                "output_tokens": 1,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 2306,
                "provider_tool_usage": None,
                "raw": "None",
                "total_tokens": 31,
            },
            "n_chunks": 3,
        }
    }
)
