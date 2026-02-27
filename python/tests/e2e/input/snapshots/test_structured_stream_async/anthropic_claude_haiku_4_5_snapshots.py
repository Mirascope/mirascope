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
                            text='{"title":"The Great Gatsby","author":"F. Scott Fitzgerald","themes":["wealth and class","love and obsession","the American Dream","moral decay"],"rating":9}'
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
                                "text": '{"title":"The Great Gatsby","author":"F. Scott Fitzgerald","themes":["wealth and class","love and obsession","the American Dream","moral decay"],"rating":9}',
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
                "output_tokens": 43,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "None",
                "total_tokens": 324,
            },
            "n_chunks": 12,
        },
        "structured_stream": [
            {
                "title": "The Great Gatsby",
                "author": None,
                "themes": None,
                "rating": None,
            },
            {
                "title": "The Great Gatsby",
                "author": "F. Scott Fitzgerald",
                "themes": None,
                "rating": None,
            },
            {
                "title": "The Great Gatsby",
                "author": "F. Scott Fitzgerald",
                "themes": ["wealth"],
                "rating": None,
            },
            {
                "title": "The Great Gatsby",
                "author": "F. Scott Fitzgerald",
                "themes": ["wealth an"],
                "rating": None,
            },
            {
                "title": "The Great Gatsby",
                "author": "F. Scott Fitzgerald",
                "themes": ["wealth and class"],
                "rating": None,
            },
            {
                "title": "The Great Gatsby",
                "author": "F. Scott Fitzgerald",
                "themes": ["wealth and class", "love and obs"],
                "rating": None,
            },
            {
                "title": "The Great Gatsby",
                "author": "F. Scott Fitzgerald",
                "themes": ["wealth and class", "love and obsession", "the"],
                "rating": None,
            },
            {
                "title": "The Great Gatsby",
                "author": "F. Scott Fitzgerald",
                "themes": [
                    "wealth and class",
                    "love and obsession",
                    "the American Dream",
                    "moral decay",
                ],
                "rating": None,
            },
            {
                "title": "The Great Gatsby",
                "author": "F. Scott Fitzgerald",
                "themes": [
                    "wealth and class",
                    "love and obsession",
                    "the American Dream",
                    "moral decay",
                ],
                "rating": 9,
            },
            {
                "title": "The Great Gatsby",
                "author": "F. Scott Fitzgerald",
                "themes": [
                    "wealth and class",
                    "love and obsession",
                    "the American Dream",
                    "moral decay",
                ],
                "rating": 9,
            },
        ],
    }
)
