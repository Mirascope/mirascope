from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "provider": "openai:responses",
        "model_id": "gpt-4o",
        "params": {},
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="Who created you?")]),
            AssistantMessage(
                content=[Text(text="I was created by Anthropic.")],
                provider="anthropic",
                model_id="claude-sonnet-4-0",
                raw_content=[
                    {
                        "citations": None,
                        "text": "I was created by Anthropic.",
                        "type": "text",
                    }
                ],
            ),
            UserMessage(content=[Text(text="Can you double-check that?")]),
            AssistantMessage(
                content=[Text(text="I was indeed created by Anthropic.")],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "id": "msg_0a79f0b8618fd3640068e81bd15b0081939f3eebbf58f60a9a",
                        "content": [
                            {
                                "annotations": [],
                                "text": "I was indeed created by Anthropic.",
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
)
async_snapshot = snapshot(
    {
        "provider": "openai:responses",
        "model_id": "gpt-4o",
        "params": {},
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="Who created you?")]),
            AssistantMessage(
                content=[Text(text="I was created by Anthropic.")],
                provider="anthropic",
                model_id="claude-sonnet-4-0",
                raw_content=[
                    {
                        "citations": None,
                        "text": "I was created by Anthropic.",
                        "type": "text",
                    }
                ],
            ),
            UserMessage(content=[Text(text="Can you double-check that?")]),
            AssistantMessage(
                content=[Text(text="Certainly! I was created by Anthropic.")],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "id": "msg_037bfe49fad7f3020068e81bdc53e881979808beac7140fa31",
                        "content": [
                            {
                                "annotations": [],
                                "text": "Certainly! I was created by Anthropic.",
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
)
stream_snapshot = snapshot(
    {
        "provider": "openai:responses",
        "model_id": "gpt-4o",
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="Who created you?")]),
            AssistantMessage(
                content=[Text(text="I was created by Anthropic.")],
                provider="anthropic",
                model_id="claude-sonnet-4-0",
                raw_content=[{"type": "text", "text": "I was created by Anthropic."}],
            ),
            UserMessage(content=[Text(text="Can you double-check that?")]),
            AssistantMessage(
                content=[Text(text="Yes, I'm definitely created by Anthropic!")],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "id": "msg_085a34355e7cd43c0068e81be8c0dc819695b3095782c73155",
                        "content": [
                            {
                                "annotations": [],
                                "text": "Yes, I'm definitely created by Anthropic!",
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
        "n_chunks": 11,
    }
)
async_stream_snapshot = snapshot(
    {
        "provider": "openai:responses",
        "model_id": "gpt-4o",
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="Who created you?")]),
            AssistantMessage(
                content=[Text(text="I was created by Anthropic.")],
                provider="anthropic",
                model_id="claude-sonnet-4-0",
                raw_content=[{"type": "text", "text": "I was created by Anthropic."}],
            ),
            UserMessage(content=[Text(text="Can you double-check that?")]),
            AssistantMessage(
                content=[
                    Text(text="Yes, I can confirm that I was created by Anthropic.")
                ],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "id": "msg_0ae62be960f936480068e81bf355d88197b9526725c0be2bfd",
                        "content": [
                            {
                                "annotations": [],
                                "text": "Yes, I can confirm that I was created by Anthropic.",
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
        "n_chunks": 15,
    }
)
