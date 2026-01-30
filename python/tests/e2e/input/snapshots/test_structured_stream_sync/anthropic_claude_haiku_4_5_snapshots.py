from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    SystemMessage,
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
                SystemMessage(
                    content=Text(
                        text="Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output."
                    )
                ),
                UserMessage(content=[Text(text="Please recommend a book to me!")]),
                AssistantMessage(
                    content=[
                        Text(
                            text='{"title": "The Midnight Library", "author": "Matt Haig", "themes": ["parallel universes","life choices","second chances","self-discovery","hope"], "rating": 5}'
                        )
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-haiku-4-5",
                    provider_model_name="claude-haiku-4-5",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "tool_use",
                                "id": "toolu_01VtJVjJct4grKZJd5pkzDYF",
                                "name": "__mirascope_formatted_output_tool__",
                                "input": {
                                    "title": "The Midnight Library",
                                    "author": "Matt Haig",
                                    "themes": [
                                        "parallel universes",
                                        "life choices",
                                        "second chances",
                                        "self-discovery",
                                        "hope",
                                    ],
                                    "rating": 5,
                                },
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
                "mode": "tool",
                "formatting_instructions": "Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output.",
            },
            "tools": [],
            "usage": {
                "input_tokens": 793,
                "output_tokens": 101,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "None",
                "total_tokens": 894,
            },
            "n_chunks": 27,
        },
        "structured_stream": [
            {"title": "T", "author": None, "themes": None, "rating": None},
            {"title": "The Midnight", "author": None, "themes": None, "rating": None},
            {
                "title": "The Midnight Li",
                "author": None,
                "themes": None,
                "rating": None,
            },
            {
                "title": "The Midnight Library",
                "author": None,
                "themes": None,
                "rating": None,
            },
            {
                "title": "The Midnight Library",
                "author": None,
                "themes": None,
                "rating": None,
            },
            {
                "title": "The Midnight Library",
                "author": "Matt H",
                "themes": None,
                "rating": None,
            },
            {
                "title": "The Midnight Library",
                "author": "Matt Hai",
                "themes": None,
                "rating": None,
            },
            {
                "title": "The Midnight Library",
                "author": "Matt Haig",
                "themes": None,
                "rating": None,
            },
            {
                "title": "The Midnight Library",
                "author": "Matt Haig",
                "themes": None,
                "rating": None,
            },
            {
                "title": "The Midnight Library",
                "author": "Matt Haig",
                "themes": None,
                "rating": None,
            },
            {
                "title": "The Midnight Library",
                "author": "Matt Haig",
                "themes": ["para"],
                "rating": None,
            },
            {
                "title": "The Midnight Library",
                "author": "Matt Haig",
                "themes": ["parallel uni"],
                "rating": None,
            },
            {
                "title": "The Midnight Library",
                "author": "Matt Haig",
                "themes": ["parallel unive"],
                "rating": None,
            },
            {
                "title": "The Midnight Library",
                "author": "Matt Haig",
                "themes": ["parallel universes", "li"],
                "rating": None,
            },
            {
                "title": "The Midnight Library",
                "author": "Matt Haig",
                "themes": ["parallel universes", "life choices"],
                "rating": None,
            },
            {
                "title": "The Midnight Library",
                "author": "Matt Haig",
                "themes": ["parallel universes", "life choices", "second ch"],
                "rating": None,
            },
            {
                "title": "The Midnight Library",
                "author": "Matt Haig",
                "themes": ["parallel universes", "life choices", "second chances"],
                "rating": None,
            },
            {
                "title": "The Midnight Library",
                "author": "Matt Haig",
                "themes": [
                    "parallel universes",
                    "life choices",
                    "second chances",
                    "self-dis",
                ],
                "rating": None,
            },
            {
                "title": "The Midnight Library",
                "author": "Matt Haig",
                "themes": [
                    "parallel universes",
                    "life choices",
                    "second chances",
                    "self-discovery",
                    "",
                ],
                "rating": None,
            },
            {
                "title": "The Midnight Library",
                "author": "Matt Haig",
                "themes": [
                    "parallel universes",
                    "life choices",
                    "second chances",
                    "self-discovery",
                    "hope",
                ],
                "rating": None,
            },
            {
                "title": "The Midnight Library",
                "author": "Matt Haig",
                "themes": [
                    "parallel universes",
                    "life choices",
                    "second chances",
                    "self-discovery",
                    "hope",
                ],
                "rating": None,
            },
            {
                "title": "The Midnight Library",
                "author": "Matt Haig",
                "themes": [
                    "parallel universes",
                    "life choices",
                    "second chances",
                    "self-discovery",
                    "hope",
                ],
                "rating": None,
            },
            {
                "title": "The Midnight Library",
                "author": "Matt Haig",
                "themes": [
                    "parallel universes",
                    "life choices",
                    "second chances",
                    "self-discovery",
                    "hope",
                ],
                "rating": None,
            },
            {
                "title": "The Midnight Library",
                "author": "Matt Haig",
                "themes": [
                    "parallel universes",
                    "life choices",
                    "second chances",
                    "self-discovery",
                    "hope",
                ],
                "rating": 5,
            },
        ],
    }
)
