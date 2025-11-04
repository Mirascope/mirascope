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
                            text="I don’t have the ability to browse the web or verify information in real-time, but I can confirm that I was developed by Anthropic. If you have any other questions or need more information, feel free to ask!"
                        )
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "id": "msg_0339296bfb9cfac900690ab11f734c81958be3b0dc6eada971",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": "I don’t have the ability to browse the web or verify information in real-time, but I can confirm that I was developed by Anthropic. If you have any other questions or need more information, feel free to ask!",
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
