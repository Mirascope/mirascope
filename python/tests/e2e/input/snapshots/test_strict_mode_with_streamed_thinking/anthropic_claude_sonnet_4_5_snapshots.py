from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider_id": "anthropic",
            "model_id": "anthropic/claude-sonnet-4-5",
            "provider_model_name": "claude-sonnet-4-5",
            "finish_reason": None,
            "messages": [
                UserMessage(
                    content=[Text(text="Answer this question: What is 2 + 2?")]
                ),
                AssistantMessage(
                    content=[
                        Text(text='{"integer_a": 2, "integer_b": 2, "answer": 4}')
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
The user is asking me to answer "What is 2 + 2?" and I need to respond with JSON that matches the given schema.

The schema requires:
- integer_a: an integer
- integer_b: an integer  \n\
- answer: an integer

For the question "What is 2 + 2?":
- integer_a = 2
- integer_b = 2
- answer = 4

I need to return valid JSON on a single line without markdown or backticks.\
""",
                                "signature": "Eo4ECkYICxgCKkCzGEyrWBGBRfXysUznxzhrNuf7jCKeBd8BzOKVGiBWmhpk+atVtOG5vNNDUkuAnFmHRf5n9YdtQTBXVHoNfjdrEgzqGXQv/n0URthiz/YaDPhy3osMp+A0udKrfiIwlWvKVjzh33NulT66ng+X9jnbl9df1pqyFUBx+mDeFxI7kJLwhl+GMD4bkBkKLzlyKvUCUxcGgMNkUnTMV+hYfolrpInZW5dTeCEgoOIsdVlE5HVnJEgOisAZZAdXeoO9VeAmWTyH08yu2yhqGz//nCaNG5IoArl5R8n9N4NJFTc9EpfN2IixznnVvmEEL/tHsNB3HcjkFpSSUmer4kF5XwyXIq4vWYcJh6yo7CBnZc60AVaW0R9yFhm5d0kS66d/I5IWALHUD34SGQ9Q67l6RqzFeRV5QU8sXan+QVVLxFQPqlFvOY/Sbeu9x4p8jZJLGJg4biZ57PCbwSoIPMtvTrlJA4sp7KIE/c3uHLKD94BnpMRUeZWIwB55NI8WNa0jb3it/3oT7ifsJgz7ndZgu1xLKt4eGTH7mqwqaMU3upLq/1kPDVKxIRkZmJxSyrXMjHAuSroZ07NHvjHenDsboioSBGomX5d/5OAYCjUpxKgZIy5pcTbHuhmczfzET2ToZ3QX5XCFavvKrqmfIpNiVA4YGzEhjFN7R9C7waUfCG7jJ3jIW0wdXBgB",
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
                "output_tokens": 146,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "None",
                "total_tokens": 439,
            },
            "n_chunks": 6,
        }
    }
)
