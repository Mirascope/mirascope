from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider": "azure-openai:completions",
            "model_id": "gpt-4o-mini",
            "params": {},
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="Who created you?")]),
                AssistantMessage(
                    content=[Text(text="I was created by Anthropic.")],
                    provider="anthropic",
                    model_id="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "citations": None,
                                "text": "I was created by Anthropic.",
                                "type": "text",
                            }
                        ],
                    },
                ),
                UserMessage(content=[Text(text="Can you double-check that?")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="I don’t have the capability to verify or double-check information. However, I can tell you that I was developed by Anthropic, a company focused on advancing AI technology. If you have any specific questions or need information, feel free to ask!"
                        )
                    ],
                    provider="azure-openai:completions",
                    model_id="gpt-4o-mini",
                    raw_message={
                        "content": "I don’t have the capability to verify or double-check information. However, I can tell you that I was developed by Anthropic, a company focused on advancing AI technology. If you have any specific questions or need information, feel free to ask!",
                        "role": "assistant",
                        "annotations": [],
                    },
                ),
            ],
            "format": None,
            "tools": [],
        }
    }
)
