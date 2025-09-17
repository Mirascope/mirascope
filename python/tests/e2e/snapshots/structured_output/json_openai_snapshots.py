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
        "provider": "openai",
        "model_id": "gpt-4o",
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
}\
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
    },
)
async_snapshot = snapshot(
    {
        "provider": "openai",
        "model_id": "gpt-4o",
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
}\
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
    },
)
stream_snapshot = snapshot(
    {
        "provider": "openai",
        "model_id": "gpt-4o",
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
}\
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
        "n_chunks": 26,
    },
)
async_stream_snapshot = snapshot(
    {
        "provider": "openai",
        "model_id": "gpt-4o",
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
}\
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
        "n_chunks": 26,
    },
)
