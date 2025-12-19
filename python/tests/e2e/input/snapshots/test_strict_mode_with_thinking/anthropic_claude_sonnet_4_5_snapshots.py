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
            "model_id": "anthropic/claude-sonnet-4-5",
            "provider_model_name": "claude-sonnet-4-5",
            "params": {"thinking": True},
            "finish_reason": None,
            "usage": {
                "input_tokens": 293,
                "output_tokens": 154,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "BetaUsage(cache_creation=BetaCacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=293, output_tokens=154, server_tool_use=None, service_tier='standard')",
                "total_tokens": 447,
            },
            "messages": [
                UserMessage(
                    content=[Text(text="Answer this question: What is 2 + 2?")]
                ),
                AssistantMessage(
                    content=[
                        Thought(
                            thought="""\
The user is asking me to answer "What is 2 + 2?" and I need to respond in JSON format according to the schema provided.

The schema requires:
- integer_a: integer
- integer_b: integer  \n\
- answer: integer

All three fields are required.

So for the question "What is 2 + 2?":
- integer_a = 2
- integer_b = 2
- answer = 4

I need to return this as a single line JSON object without any markdown formatting or extra text.\
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
                                "signature": "EssECkYIChgCKkDSbncMSCfIvPhvksJ7pyjCQVYbrDYBjuOWsITZO+AeQKkcvd58HG844sHCDtvCzGM55gYpa7Iembnd4s3c4hpYEgxl/81Itls4Waxfr4UaDC2aJrCfP4zsKDJihCIwsnV5o60f+L558a4hnwJwkcjYPvdIPHevytWAkNlJ+WVLS2vRQGtaur0z/WOFpKwuKrIDhEA8dJsIBild7IOfBd/m+QD3/q3mSXfyjzUMQowZCqUP2ha7gyGuKYpkqd4rqxMkD9fTXe7kRBeXB6uK6dmgfKrIK2PjRNvhyHRBAGlfRmTyLNLUTNHTGWrVkAgHQvOZQj7lBKQvdh96pKJH3KTGJixRBS0G75yqkLbc6etdp2usHLZ5Sg56VPDRq8y3H1UtsmNp7bLUtl5fOX1AGjAdNE/GDfDKHttWIXbytKv8elBiByksFO70A6msC06CMOy3Aa6uf6OyYu/dBWr3rz+Ys39XYdrcgMS9QsgMcOiU+FT0yC+RqfnGXMMf6d4YDVrS/pSjNw8vqkiZXyCHxRoAJ651s4vEfixU+Rf5CtZy9hvJhfGMLGvLq+rBM/VYQhylyYoD882/1OD4D2IjdNtMu583fefYMecdf9mbMPHQSwWc/57oFBAKqSpg1lI6ZyXhz4Qf8KBi51+f0+kUjTlrsLIL+ne5C7wiL53f010B/7A0Mx62YYiogM1SpBt/OGKwxflq7ns3ngO4MStH1sqUvJVyNXWlUttTNaxA6GO0mw0QZmMkdvrjrx/fD2afalwRVTQYAQ==",
                                "thinking": """\
The user is asking me to answer "What is 2 + 2?" and I need to respond in JSON format according to the schema provided.

The schema requires:
- integer_a: integer
- integer_b: integer  \n\
- answer: integer

All three fields are required.

So for the question "What is 2 + 2?":
- integer_a = 2
- integer_b = 2
- answer = 4

I need to return this as a single line JSON object without any markdown formatting or extra text.\
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
