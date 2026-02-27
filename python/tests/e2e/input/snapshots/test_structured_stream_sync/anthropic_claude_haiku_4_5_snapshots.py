from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider_id": "anthropic",
            "model_id": "anthropic/claude-haiku-4-5",
            "provider_model_name": "claude-haiku-4-5",
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="Please recommend a book to me!")]),
                AssistantMessage(
                    content=[
                        Text(
                            text='{"title": "The Midnight Library", "author": "Matt Haig", "themes": ["parallel lives", "second chances", "self-discovery", "regret", "hope"], "rating": 9}'
                        )
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-haiku-4-5",
                    provider_model_name="claude-haiku-4-5",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "text",
                                "text": '{"title": "The Midnight Library", "author": "Matt Haig", "themes": ["parallel lives", "second chances", "self-discovery", "regret", "hope"], "rating": 9}',
                            }
                        ],
                    },
                ),
            ],
            "format": {
                "name": "BookReview",
                "description": None,
                "schema": {
                    "properties": {
                        "title": {"title": "Title", "type": "string"},
                        "author": {"title": "Author", "type": "string"},
                        "themes": {
                            "items": {"type": "string"},
                            "title": "Themes",
                            "type": "array",
                        },
                        "rating": {"title": "Rating", "type": "integer"},
                    },
                    "required": ["title", "author", "themes", "rating"],
                    "title": "BookReview",
                    "type": "object",
                },
                "mode": "strict",
                "formatting_instructions": None,
            },
            "tools": [],
            "usage": {
                "input_tokens": 281,
                "output_tokens": 50,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "None",
                "total_tokens": 331,
            },
            "n_chunks": 16,
        },
        "structured_stream": [
            {"title": None, "author": None, "themes": None, "rating": None},
            {"title": "The", "author": None, "themes": None, "rating": None},
            {
                "title": "The Midnight Library",
                "author": "Matt",
                "themes": None,
                "rating": None,
            },
            {
                "title": "The Midnight Library",
                "author": "Matt Haig",
                "themes": [""],
                "rating": None,
            },
            {
                "title": "The Midnight Library",
                "author": "Matt Haig",
                "themes": ["parallel"],
                "rating": None,
            },
            {
                "title": "The Midnight Library",
                "author": "Matt Haig",
                "themes": ["parallel lives"],
                "rating": None,
            },
            {
                "title": "The Midnight Library",
                "author": "Matt Haig",
                "themes": ["parallel lives", "secon"],
                "rating": None,
            },
            {
                "title": "The Midnight Library",
                "author": "Matt Haig",
                "themes": ["parallel lives", "second chances", "self"],
                "rating": None,
            },
            {
                "title": "The Midnight Library",
                "author": "Matt Haig",
                "themes": ["parallel lives", "second chances", "self-discovery"],
                "rating": None,
            },
            {
                "title": "The Midnight Library",
                "author": "Matt Haig",
                "themes": ["parallel lives", "second chances", "self-discovery", "reg"],
                "rating": None,
            },
            {
                "title": "The Midnight Library",
                "author": "Matt Haig",
                "themes": [
                    "parallel lives",
                    "second chances",
                    "self-discovery",
                    "regret",
                ],
                "rating": None,
            },
            {
                "title": "The Midnight Library",
                "author": "Matt Haig",
                "themes": [
                    "parallel lives",
                    "second chances",
                    "self-discovery",
                    "regret",
                    "hope",
                ],
                "rating": None,
            },
            {
                "title": "The Midnight Library",
                "author": "Matt Haig",
                "themes": [
                    "parallel lives",
                    "second chances",
                    "self-discovery",
                    "regret",
                    "hope",
                ],
                "rating": 9,
            },
            {
                "title": "The Midnight Library",
                "author": "Matt Haig",
                "themes": [
                    "parallel lives",
                    "second chances",
                    "self-discovery",
                    "regret",
                    "hope",
                ],
                "rating": 9,
            },
        ],
    }
)
