from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider": "openai",
            "model_id": "openai/gpt-4o:responses",
            "provider_model_id": "gpt-4o:responses",
            "params": {},
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text=""), Text(text="")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="It looks like your message was incomplete. Could you please provide more details or clarify your request?"
                        )
                    ],
                    provider="openai",
                    model_id="openai/gpt-4o:responses",
                    provider_model_id="gpt-4o:responses",
                    raw_message=[
                        {
                            "id": "msg_04e1cc63eb11c794006931e06c962881978b1589ab84126872",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": "It looks like your message was incomplete. Could you please provide more details or clarify your request?",
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
