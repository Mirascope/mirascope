from inline_snapshot import snapshot

from mirascope.llm import AssistantMessage, Text, UserMessage

test_snapshot = snapshot(
    {
        "response": {
            "provider": "azure-openai:responses",
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
                            text="I can't verify details in real-time, but I was developed by Anthropic as part of their AI research efforts. If you're looking for specific information, I recommend checking their official website or resources."
                        )
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "id": "msg_0a077339808a0fd300690ab12da06c81938ced4c7c6958288f",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": "I can't verify details in real-time, but I was developed by Anthropic as part of their AI research efforts. If you're looking for specific information, I recommend checking their official website or resources.",
                                    "type": "output_text",
                                    "logprobs": [],
                                }
                            ],
                            "role": "assistant",
                            "status": "completed",
                            "type": "message",
                        }
                    ],
                ),
            ],
            "format": None,
            "tools": [],
        }
    }
)
