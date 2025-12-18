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
- integer_a: an integer
- integer_b: an integer  \n\
- answer: an integer

The question is "What is 2 + 2?" so:
- integer_a = 2
- integer_b = 2
- answer = 4

I need to return valid JSON with no markdown, no backticks, just the JSON object on a single line.\
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
                                "signature": "ErQECkYIChgCKkAtm18SjxEMOZZLFdTofDI+NGF+Wn+F2lXZKK5xmS8Xuh+Nn/Rs+X2ad6yEOiZJ1nJSbhOW2FaEGuXBHm+mOEPGEgyZeimNXYK6Q3spgCwaDC9y3BoizE8nJnyGPiIwmTEeY4B0y0Kk7SXuCRM4yQIyBw/TA9TFOYMvq3xZGDTVCyXv8tXUiYVy0s1VM4FaKpsDTi8/qcEp7Hpch6t4Ymn1WzyMAvvvtrSFax7nk9+SZYb2E6THPwoEVmIwLyFj6E+2CitTFDRTxkeRrRxetp9QJYqQhZmHF8Hawhgw/q+eFSwcDwR5vpCJmahvsyzT9JXACTeqPSVpmSFblre1BEmNBpqfVcuB9MHMF+t2mPTDY8NJENw+1IMlGnrf9W430UPFEnfJ3OcMsBlIcm4rBF4Ed4Qoy1pg2wzP8TBSHCmh5qgdWThP/rB+SLPYxYROOedmbG7l8suJ3RzAi3sWKZDTjmpnuWMC1n2+6O9ZaiRsiBbltd7zAwpI5wHP+fx3fxTjtadhdkT4S7z/DXW2U5AWjqZ7HN530ceGymQ2sbd5bWdelSP2xBeTzwa2LiuNOTQkK0MHikcGrVJiYny64m9u1o2q8WtZYEwkID/MP87JW1lZKYztHRnDyKog17dfUcK4wkAd9DHjfGyZtatdmW4iY1TPIsYBgpOaBInJLH+01zjEzn/YQuRSlcRPZar4owCEIC82SGzhxkQsgz8AitDq8EbFuCOJObZJUkoIGAE=",
                                "thinking": """\
The user is asking me to answer "What is 2 + 2?" and I need to respond in JSON format according to the schema provided.

The schema requires:
- integer_a: an integer
- integer_b: an integer  \n\
- answer: an integer

The question is "What is 2 + 2?" so:
- integer_a = 2
- integer_b = 2
- answer = 4

I need to return valid JSON with no markdown, no backticks, just the JSON object on a single line.\
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
