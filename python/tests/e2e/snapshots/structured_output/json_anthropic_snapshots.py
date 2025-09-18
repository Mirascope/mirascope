from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    FinishReason,
    SystemMessage,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-0",
        "params": {},
        "finish_reason": FinishReason.END_TURN,
        "messages": [
            SystemMessage(
                content=Text(
                    text="""\
Respond with valid JSON that matches this exact schema:
{
  "properties": {
    "title": {
      "title": "Title",
      "type": "string"
    },
    "author": {
      "title": "Author",
      "type": "string"
    }
  },
  "required": [
    "title",
    "author"
  ],
  "title": "Book",
  "type": "object"
}

Respond ONLY with valid JSON, and no other text.\
"""
                )
            ),
            UserMessage(
                content=[
                    Text(
                        text="Please recommend the most popular book by Patrick Rothfuss"
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
{
  "title": "The Name of the Wind",
  "author": "Patrick Rothfuss"
}\
"""
                    )
                ]
            ),
        ],
        "format_type": {
            "name": "Book",
            "description": None,
            "schema": {
                "properties": {
                    "title": {"title": "Title", "type": "string"},
                    "author": {"title": "Author", "type": "string"},
                },
                "required": ["title", "author"],
                "title": "Book",
                "type": "object",
            },
            "mode": "json",
        },
    }
)
async_snapshot = snapshot(
    {
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-0",
        "params": {},
        "finish_reason": FinishReason.END_TURN,
        "messages": [
            SystemMessage(
                content=Text(
                    text="""\
Respond with valid JSON that matches this exact schema:
{
  "properties": {
    "title": {
      "title": "Title",
      "type": "string"
    },
    "author": {
      "title": "Author",
      "type": "string"
    }
  },
  "required": [
    "title",
    "author"
  ],
  "title": "Book",
  "type": "object"
}

Respond ONLY with valid JSON, and no other text.\
"""
                )
            ),
            UserMessage(
                content=[
                    Text(
                        text="Please recommend the most popular book by Patrick Rothfuss"
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
{
  "title": "The Name of the Wind",
  "author": "Patrick Rothfuss"
}\
"""
                    )
                ]
            ),
        ],
        "format_type": {
            "name": "Book",
            "description": None,
            "schema": {
                "properties": {
                    "title": {"title": "Title", "type": "string"},
                    "author": {"title": "Author", "type": "string"},
                },
                "required": ["title", "author"],
                "title": "Book",
                "type": "object",
            },
            "mode": "json",
        },
    }
)
stream_snapshot = snapshot(
    {
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-0",
        "finish_reason": FinishReason.END_TURN,
        "messages": [
            SystemMessage(
                content=Text(
                    text="""\
Respond with valid JSON that matches this exact schema:
{
  "properties": {
    "title": {
      "title": "Title",
      "type": "string"
    },
    "author": {
      "title": "Author",
      "type": "string"
    }
  },
  "required": [
    "title",
    "author"
  ],
  "title": "Book",
  "type": "object"
}

Respond ONLY with valid JSON, and no other text.\
"""
                )
            ),
            UserMessage(
                content=[
                    Text(
                        text="Please recommend the most popular book by Patrick Rothfuss"
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
{
  "title": "The Name of the Wind",
  "author": "Patrick Rothfuss"
}\
"""
                    )
                ]
            ),
        ],
        "format_type": {
            "name": "Book",
            "description": None,
            "schema": {
                "properties": {
                    "title": {"title": "Title", "type": "string"},
                    "author": {"title": "Author", "type": "string"},
                },
                "required": ["title", "author"],
                "title": "Book",
                "type": "object",
            },
            "mode": "json",
        },
        "n_chunks": 6,
    }
)
async_stream_snapshot = snapshot(
    {
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-0",
        "finish_reason": FinishReason.END_TURN,
        "messages": [
            SystemMessage(
                content=Text(
                    text="""\
Respond with valid JSON that matches this exact schema:
{
  "properties": {
    "title": {
      "title": "Title",
      "type": "string"
    },
    "author": {
      "title": "Author",
      "type": "string"
    }
  },
  "required": [
    "title",
    "author"
  ],
  "title": "Book",
  "type": "object"
}

Respond ONLY with valid JSON, and no other text.\
"""
                )
            ),
            UserMessage(
                content=[
                    Text(
                        text="Please recommend the most popular book by Patrick Rothfuss"
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
{
  "title": "The Name of the Wind",
  "author": "Patrick Rothfuss"
}\
"""
                    )
                ]
            ),
        ],
        "format_type": {
            "name": "Book",
            "description": None,
            "schema": {
                "properties": {
                    "title": {"title": "Title", "type": "string"},
                    "author": {"title": "Author", "type": "string"},
                },
                "required": ["title", "author"],
                "title": "Book",
                "type": "object",
            },
            "mode": "json",
        },
        "n_chunks": 5,
    }
)
