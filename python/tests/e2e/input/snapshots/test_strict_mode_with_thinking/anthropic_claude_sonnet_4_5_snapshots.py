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
            "params": {"thinking": {"level": "medium"}},
            "finish_reason": None,
            "usage": {
                "input_tokens": 293,
                "output_tokens": 159,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "BetaUsage(cache_creation=BetaCacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=293, output_tokens=159, server_tool_use=None, service_tier='standard')",
                "total_tokens": 452,
            },
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
                                "signature": "EtEECkYICxgCKkBBztxF0T3qi+Qr79sEprJqw9sLbVC8j1s4AjRjfbZofKn6rAtPetncMx/prNv2Ra0zNx9vP1LBaEjBDBtWOnCYEgyp7HNAl7fMHW6ZEn4aDEYAvtDnZ/ctC+wYjiIwfrYZVKHxsWiYurqBHL9KFZsrcZ5wb/RBqxfeYCs1B9waXPu8dKdifuvO/XpBtgeWKrgD7Pj80mt7v630Eqwn46QQuhVoTUiG4jPSHratzA9TULjz44Ow1P6U8hlk0jNem2TT27I+FDh/fR+PpWMj0S64X803NKQMeTD1qUXoy0vs9MeGx6V36jOVYf4kl5rw4SmJuqlwbdN4xy6rpTIpZT6ajPIurVUf5XZ78uHx+wuOAfnLioKWy6S+27m4m/7w/ulxTMQT+zRp/9zL2V6/xHKa0WKJUf/d/w1GQKbhF0RIi0sTAZaQEH5S70PydOlcyI2VIMcJFgN1hFi7nAfamd8VcYzRzN6Y3jTtT+kIQBqq+o93v+WZC50/lS6l9MO4+8csKg7qJdM3Q8NED7P03o9GSJvXFMV9Zd7ik71uhjfKuHGYkyb3h6W7XulxmdC+Apo2WmUn03fnDHCgo8fnA/b4v4LKQlZ69MtBJsSe/FrDJOqIWcLwJMLp26+SkeDlSGwgR1SQFBnaX9x2vxs+iQbdeCynqycG/Hz0ECJHQJoQzlWWDf09C6A4vE5bVZsEJXEDqG8p1A459ca/Y1Lkq7BjYpUAdkJR/XoGfF1zMiifA9YJNtvUm9BvM5ZD5di/xTDoBapVeJF0/FwYAQ==",
                                "thinking": """\
The user is asking me to add 2 + 2, which equals 4.

I need to respond with valid JSON that matches the schema provided. The schema requires:
- integer_a: an integer
- integer_b: an integer  \n\
- answer: an integer

All three fields are required.

So for the question "What is 2 + 2?", I should set:
- integer_a: 2
- integer_b: 2
- answer: 4

The response must be a single line of JSON without any markdown or additional text.\
""",
                                "type": "thinking",
                            },
                            {
                                "text": '{"integer_a": 2, "integer_b": 2, "answer": 4}',
                                "type": "text",
                                "parsed_output": {
                                    "integer_a": 2,
                                    "integer_b": 2,
                                    "answer": 4,
                                },
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
        }
    }
)
