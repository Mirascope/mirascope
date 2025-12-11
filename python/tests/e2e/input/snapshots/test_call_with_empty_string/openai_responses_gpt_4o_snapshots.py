from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider": "openai:responses",
            "model_id": "openai:responses/gpt-4o",
            "provider_model_id": "gpt-4o:responses",
            "params": {},
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="It looks like you're trying to share an image or details about a scene or object. How can I assist you with it?"
                        )
                    ],
                    provider="openai:responses",
                    model_id="openai:responses/gpt-4o",
                    provider_model_id="gpt-4o:responses",
                    raw_message=[
                        {
                            "id": "msg_02aecbd82c76cb54006931df309ef08197a1a028224b73014e",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": "It looks like you're trying to share an image or details about a scene or object. How can I assist you with it?",
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
