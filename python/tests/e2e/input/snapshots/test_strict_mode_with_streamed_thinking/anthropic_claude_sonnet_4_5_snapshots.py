from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    Thought,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider": "anthropic",
            "model_id": "anthropic/claude-sonnet-4-5",
            "finish_reason": None,
            "messages": [
                UserMessage(
                    content=[Text(text="Answer this question: What is 2 + 2?")]
                ),
                AssistantMessage(
                    content=[
                        Thought(
                            thought="""\
The user is asking me to answer "What is 2 + 2?" and I need to respond with valid JSON that matches the provided schema.

The schema requires:
- integer_a: integer
- integer_b: integer
- answer: integer

All three fields are required.

The question is "What is 2 + 2?" so:
- integer_a = 2
- integer_b = 2
- answer = 2 + 2 = 4

I need to respond with a JSON object on a single line without any markdown or extra formatting.\
"""
                        ),
                        Text(text='{"integer_a": 2, "integer_b": 2, "answer": 4}'),
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-5",
                    provider_model_name="claude-sonnet-4-5",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "thinking",
                                "thinking": """\
The user is asking me to answer "What is 2 + 2?" and I need to respond with valid JSON that matches the provided schema.

The schema requires:
- integer_a: integer
- integer_b: integer
- answer: integer

All three fields are required.

The question is "What is 2 + 2?" so:
- integer_a = 2
- integer_b = 2
- answer = 2 + 2 = 4

I need to respond with a JSON object on a single line without any markdown or extra formatting.\
""",
                                "signature": "EsUECkYIChgCKkBVfIvsuU7abyN1VAn4iOuarOKChrpRcTgYCvkqVFxnrIouN1diNge7Kuyc6ZtSKYGlkOoSrzmXKbmb5i1ICeAFEgyjjnZv+HG/GZsl3osaDGTxBmp1yOXX15HWLyIwWpGmCEWxdncyqPHVK7Zc1l+j+v8JTBioputEQEnBrG3P3Sf1JvH7/ZNmh5StrPWTKqwDvjs42Ygf6nL1ZChGUXtyvBCAaLCPq534aPsG0aqUJs34NZw5ZHDx0dCwcM5qT9lbQxJzHtPHQ+Gumu1pPgTwXCEL5ZJiVFjcWI0+DpKMqYp3sCMIhKGJG22I7AoGT5zg03K0voN3XbBcwF49pAChya5/B3YHOuchVGKyWqCmbaenhTrGd3tXHzmwlqwGU4NThuAKZupbg5H734BY79NInUOKnmyNHPMXEdKeSxGVXven5/IBMqNrgRvOk1ZdNuuPWE7wA51/BPndF5REOkZl7hJ2DTRTW33IOOKMDNGf72f57CQCp37nHGgiWr0GSFZfV1uQBeODGPG8C5p0kxK8zs5T/cwtJ5/xuieGT/fau1ARrQpLd30KARSuOhTtXJrSytcksGfnpzHXd4z5RbI3WS3r3j8Rr+TrV1aF5Ccrw5NJnEEfRtBLvZu/UpMHMCYziS8EX8/Xo7zDpsCWjYKOR7ydW9TElzs8K+fzAfntTSwrki2nLjv+ha/ONqBt7MDFFiw/GU9orNEuBcq53lgrmLtx31j0oJX+sudritV93HfC3+TONfbz5ZQ5X1kYAQ==",
                            },
                            {
                                "type": "text",
                                "text": '{"integer_a": 2, "integer_b": 2, "answer": 4}',
                            },
                        ],
                    },
                ),
            ],
            "format": {
                "name": "IntegerAdditionResponse",
                "description": "A simple response for testing.",
                "schema": {
                    "description": "A simple response for testing.",
                    "properties": {
                        "integer_a": {"title": "Integer A", "type": "integer"},
                        "integer_b": {"title": "Integer B", "type": "integer"},
                        "answer": {"title": "Answer", "type": "integer"},
                    },
                    "required": ["integer_a", "integer_b", "answer"],
                    "title": "IntegerAdditionResponse",
                    "type": "object",
                },
                "mode": "strict",
                "formatting_instructions": None,
            },
            "tools": [],
            "usage": {
                "input_tokens": 293,
                "output_tokens": 161,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
            },
            "n_chunks": 40,
        }
    }
)
