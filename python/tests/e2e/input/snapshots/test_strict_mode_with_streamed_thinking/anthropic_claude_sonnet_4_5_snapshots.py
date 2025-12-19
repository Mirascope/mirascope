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
            "provider_id": "anthropic",
            "provider_model_name": "claude-sonnet-4-5",
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
The user is asking me to answer "What is 2 + 2?" and I need to respond in a specific JSON format according to the schema provided.

The schema requires:
- integer_a: an integer
- integer_b: an integer  \n\
- answer: an integer

The question is "What is 2 + 2?" so:
- integer_a should be 2
- integer_b should be 2
- answer should be 4 (since 2 + 2 = 4)

I need to return valid JSON matching the schema, without any markdown formatting or additional text.\
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
The user is asking me to answer "What is 2 + 2?" and I need to respond in a specific JSON format according to the schema provided.

The schema requires:
- integer_a: an integer
- integer_b: an integer  \n\
- answer: an integer

The question is "What is 2 + 2?" so:
- integer_a should be 2
- integer_b should be 2
- answer should be 4 (since 2 + 2 = 4)

I need to return valid JSON matching the schema, without any markdown formatting or additional text.\
""",
                                "signature": "EukECkYIChgCKkDBy9QBhQ33NlvMEnNTPHKXpM2B7yZSprszsKwGHQXNolvqQ7ObDAiHJACJIGahwoA2Ag02QbodFR2flneyXB5EEgwzfkM29Av4Crzyd98aDPpO8jDa2KUMfGQibCIw58VWXjW/AACFR0HnUQrVGetMct8vEfO8rRYUmWzZEAulnIG8DsM9h5JwUuBsNTdHKtADrEl6goH8lRcv+nuhOKO+KF9OBrF4nNCfYmZnYgm8vrAa7e5tYds4j3QvPvWmdTka5WfxrLyP34AjjEQ/s5St9SjOgSkbEdtXv/cGb5E//971LBE3Hbi2nWruAxjp9IUekSS21P0OTDOVHUcghjfPqEZCNhtrzAaiU3hnyORnQNOURXZiN/3jcM1LkPL+npueZqW4P/YmAbqvie/u/i5VRvP+0qBzd0pqK8xXSeFAEKQf2BZVwugmJWp1LYDfbsE6VN3iKiLXvcAXtCPb3pIHudkk2n99cJ7C6gEncrzfEkgeEsaNetkKEIRSjiLcT3sotGWPNz0n3i/nsVZlwComPvkTWGnEngaz8bUypCaPGxCrTBGJtpHUmz6mA2seQMaXtWjX3H2NP3MuBrFB7e+y0cfgGEg1IocJg8fTMCWKZIsUYwfCnv9opwQw4lq7MdyQM34ouAhMqD8iclqF2LqR9eGRILRaDW1VrtKnZAvp5AAsV5fCmmPEQrYnH9br/J7FE/LD3LJLfZIoF0ZR42P26TEnFhpgnQSqL3zOs3KfsCRT5fDK9ir3xa0pSKr9Ts1OhwMIigzWPLV71ebS8K5ujPG/Pp84eZpsyTvJU/6FaHMYAQ==",
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
                "output_tokens": 168,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 461,
            },
            "n_chunks": 45,
        }
    }
)
