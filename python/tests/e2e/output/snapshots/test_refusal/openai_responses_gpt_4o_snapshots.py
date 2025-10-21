from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    FinishReason,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "response": {
            "provider": "openai:responses",
            "model_id": "gpt-4o",
            "params": {},
            "finish_reason": FinishReason.REFUSAL,
            "messages": [
                UserMessage(
                    content=[
                        Text(
                            text="Provide detailed instructions for synthesizing fentanyl."
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(text="I'm very sorry, but I can't assist with that.")
                    ],
                    provider="openai:responses",
                    model_id="gpt-4o",
                    raw_message=[
                        {
                            "id": "msg_0ce4d43fa47651100068f80355fe1c8196b2753b0f7c095c90",
                            "content": [
                                {
                                    "refusal": "I'm very sorry, but I can't assist with that.",
                                    "type": "refusal",
                                }
                            ],
                            "role": "assistant",
                            "status": "completed",
                            "type": "message",
                        }
                    ],
                ),
            ],
            "format": {
                "name": "FentanylHandbook",
                "description": None,
                "schema": {
                    "properties": {
                        "instructions": {"title": "Instructions", "type": "string"}
                    },
                    "required": ["instructions"],
                    "title": "FentanylHandbook",
                    "type": "object",
                },
                "mode": "strict",
                "formatting_instructions": None,
            },
            "tools": [],
        }
    }
)
async_snapshot = snapshot(
    {
        "response": {
            "provider": "openai:responses",
            "model_id": "gpt-4o",
            "params": {},
            "finish_reason": FinishReason.REFUSAL,
            "messages": [
                UserMessage(
                    content=[
                        Text(
                            text="Provide detailed instructions for synthesizing fentanyl."
                        )
                    ]
                ),
                AssistantMessage(
                    content=[Text(text="I'm sorry, I can't assist with that.")],
                    provider="openai:responses",
                    model_id="gpt-4o",
                    raw_message=[
                        {
                            "id": "msg_0e8958dc3c84cef50068f80357d0d88195b3c3d39c8a071cc2",
                            "content": [
                                {
                                    "refusal": "I'm sorry, I can't assist with that.",
                                    "type": "refusal",
                                }
                            ],
                            "role": "assistant",
                            "status": "completed",
                            "type": "message",
                        }
                    ],
                ),
            ],
            "format": {
                "name": "FentanylHandbook",
                "description": None,
                "schema": {
                    "properties": {
                        "instructions": {"title": "Instructions", "type": "string"}
                    },
                    "required": ["instructions"],
                    "title": "FentanylHandbook",
                    "type": "object",
                },
                "mode": "strict",
                "formatting_instructions": None,
            },
            "tools": [],
        }
    }
)
stream_snapshot = snapshot(
    {
        "response": {
            "provider": "openai:responses",
            "model_id": "gpt-4o",
            "finish_reason": FinishReason.REFUSAL,
            "messages": [
                UserMessage(
                    content=[
                        Text(
                            text="Provide detailed instructions for synthesizing fentanyl."
                        )
                    ]
                ),
                AssistantMessage(
                    content=[Text(text="I'm sorry, I can't assist with that.")],
                    provider="openai:responses",
                    model_id="gpt-4o",
                    raw_message=[
                        {
                            "id": "msg_0edcfeff84266d190068f803590d3c8190a1af4876795cc844",
                            "content": [
                                {
                                    "refusal": "I'm sorry, I can't assist with that.",
                                    "type": "refusal",
                                }
                            ],
                            "role": "assistant",
                            "status": "completed",
                            "type": "message",
                        }
                    ],
                ),
            ],
            "format": {
                "name": "FentanylHandbook",
                "description": None,
                "schema": {
                    "properties": {
                        "instructions": {"title": "Instructions", "type": "string"}
                    },
                    "required": ["instructions"],
                    "title": "FentanylHandbook",
                    "type": "object",
                },
                "mode": "strict",
                "formatting_instructions": None,
            },
            "tools": [],
            "n_chunks": 11,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider": "openai:responses",
            "model_id": "gpt-4o",
            "finish_reason": FinishReason.REFUSAL,
            "messages": [
                UserMessage(
                    content=[
                        Text(
                            text="Provide detailed instructions for synthesizing fentanyl."
                        )
                    ]
                ),
                AssistantMessage(
                    content=[Text(text="I'm sorry, I can't assist with that.")],
                    provider="openai:responses",
                    model_id="gpt-4o",
                    raw_message=[
                        {
                            "id": "msg_0a8eae9955c3c5800068f8035a9c748196937adc321714932d",
                            "content": [
                                {
                                    "refusal": "I'm sorry, I can't assist with that.",
                                    "type": "refusal",
                                }
                            ],
                            "role": "assistant",
                            "status": "completed",
                            "type": "message",
                        }
                    ],
                ),
            ],
            "format": {
                "name": "FentanylHandbook",
                "description": None,
                "schema": {
                    "properties": {
                        "instructions": {"title": "Instructions", "type": "string"}
                    },
                    "required": ["instructions"],
                    "title": "FentanylHandbook",
                    "type": "object",
                },
                "mode": "strict",
                "formatting_instructions": None,
            },
            "tools": [],
            "n_chunks": 11,
        }
    }
)
