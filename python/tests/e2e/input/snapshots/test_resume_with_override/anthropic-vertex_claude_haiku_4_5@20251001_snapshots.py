from inline_snapshot import snapshot

from mirascope.llm import AssistantMessage, Text, UserMessage

test_snapshot = snapshot(
    {
        "response": {
            "provider": "anthropic-vertex",
            "model_id": "claude-haiku-4-5@20251001",
            "params": {},
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="Who created you?")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="I was created by Anthropic, an AI safety company. I'm Claude, an AI assistant developed by Anthropic's team of researchers and engineers."
                        )
                    ],
                    provider="anthropic",
                    model_id="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "citations": None,
                                "text": "I was created by Anthropic, an AI safety company. I'm Claude, an AI assistant developed by Anthropic's team of researchers and engineers.",
                                "type": "text",
                            }
                        ],
                    },
                ),
                UserMessage(content=[Text(text="Can you double-check that?")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Yes, I'm confident in that answer. I was created by Anthropic. This is accurate information about my origins.

Is there something specific that made you question it, or were you just checking to make sure I was being truthful?\
"""
                        )
                    ],
                    provider="anthropic-vertex",
                    model_id="claude-haiku-4-5@20251001",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "citations": None,
                                "text": """\
Yes, I'm confident in that answer. I was created by Anthropic. This is accurate information about my origins.

Is there something specific that made you question it, or were you just checking to make sure I was being truthful?\
""",
                                "type": "text",
                            }
                        ],
                    },
                ),
            ],
            "format": None,
            "tools": [],
        }
    }
)
