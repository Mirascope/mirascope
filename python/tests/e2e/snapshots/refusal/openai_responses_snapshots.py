from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    FinishReason,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
    {
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
                raw_content=[
                    {
                        "id": "msg_0a2028ae02b411660068deb8e728f8819089525b6f37075e04",
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
)
async_snapshot = snapshot(
    {
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
                raw_content=[
                    {
                        "id": "msg_0b201b578ba57afc0068debe4d72e88197a47600f64022fd89",
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
)
stream_snapshot = snapshot(
    {
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
                raw_content=[
                    {
                        "id": "msg_0968ea696d21eaad0068debe513ea88195a8b00d13e437f707",
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
)
async_stream_snapshot = snapshot(
    {
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
                raw_content=[
                    {
                        "id": "msg_062ae008f4125cd00068debe5486948196901732514186e8f8",
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
)
