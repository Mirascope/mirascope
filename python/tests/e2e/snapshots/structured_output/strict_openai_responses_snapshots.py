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
                        text='{"title":"THE NAME OF THE WIND","author":{"first_name":"Patrick","last_name":"Rothfuss"},"rating":7}'
                    )
                ],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "id": "msg_0a25952eb6f376b30068dc21c0fe088197ad5101834e13c491",
                        "content": [
                            {
                                "annotations": [],
                                "text": '{"title":"THE NAME OF THE WIND","author":{"first_name":"Patrick","last_name":"Rothfuss"},"rating":7}',
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
        "format": {
            "name": "Book",
            "description": "A book with a rating. The title should be in all caps!",
            "schema": {
                "$defs": {
                    "Author": {
                        "description": "The author of a book.",
                        "properties": {
                            "first_name": {"title": "First Name", "type": "string"},
                            "last_name": {"title": "Last Name", "type": "string"},
                        },
                        "required": ["first_name", "last_name"],
                        "title": "Author",
                        "type": "object",
                        "additionalProperties": False,
                    }
                },
                "description": "A book with a rating. The title should be in all caps!",
                "properties": {
                    "title": {"title": "Title", "type": "string"},
                    "author": {"$ref": "#/$defs/Author"},
                    "rating": {
                        "description": "For testing purposes, the rating should be 7",
                        "title": "Rating",
                        "type": "integer",
                    },
                },
                "required": ["title", "author", "rating"],
                "title": "Book",
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
        "finish_reason": None,
        "messages": [
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
                        text='{"title":"THE NAME OF THE WIND","author":{"first_name":"Patrick","last_name":"Rothfuss"},"rating":7}'
                    )
                ],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "id": "msg_0d911b9b7292601f0068dc21cce23081949303b66b15e9e8a5",
                        "content": [
                            {
                                "annotations": [],
                                "text": '{"title":"THE NAME OF THE WIND","author":{"first_name":"Patrick","last_name":"Rothfuss"},"rating":7}',
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
        "format": {
            "name": "Book",
            "description": "A book with a rating. The title should be in all caps!",
            "schema": {
                "$defs": {
                    "Author": {
                        "description": "The author of a book.",
                        "properties": {
                            "first_name": {"title": "First Name", "type": "string"},
                            "last_name": {"title": "Last Name", "type": "string"},
                        },
                        "required": ["first_name", "last_name"],
                        "title": "Author",
                        "type": "object",
                        "additionalProperties": False,
                    }
                },
                "description": "A book with a rating. The title should be in all caps!",
                "properties": {
                    "title": {"title": "Title", "type": "string"},
                    "author": {"$ref": "#/$defs/Author"},
                    "rating": {
                        "description": "For testing purposes, the rating should be 7",
                        "title": "Rating",
                        "type": "integer",
                    },
                },
                "required": ["title", "author", "rating"],
                "title": "Book",
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
        "finish_reason": None,
        "messages": [
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
                        text='{"title":"THE NAME OF THE WIND","author":{"first_name":"Patrick","last_name":"Rothfuss"},"rating":7}'
                    )
                ],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "id": "msg_0f8a74675e9c79510068dc21d3d6ac81969fdada43d6b3f8ab",
                        "content": [
                            {
                                "annotations": [],
                                "text": '{"title":"THE NAME OF THE WIND","author":{"first_name":"Patrick","last_name":"Rothfuss"},"rating":7}',
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
        "format": {
            "name": "Book",
            "description": "A book with a rating. The title should be in all caps!",
            "schema": {
                "$defs": {
                    "Author": {
                        "description": "The author of a book.",
                        "properties": {
                            "first_name": {"title": "First Name", "type": "string"},
                            "last_name": {"title": "Last Name", "type": "string"},
                        },
                        "required": ["first_name", "last_name"],
                        "title": "Author",
                        "type": "object",
                        "additionalProperties": False,
                    }
                },
                "description": "A book with a rating. The title should be in all caps!",
                "properties": {
                    "title": {"title": "Title", "type": "string"},
                    "author": {"$ref": "#/$defs/Author"},
                    "rating": {
                        "description": "For testing purposes, the rating should be 7",
                        "title": "Rating",
                        "type": "integer",
                    },
                },
                "required": ["title", "author", "rating"],
                "title": "Book",
                "type": "object",
            },
            "mode": "strict",
            "formatting_instructions": None,
        },
        "tools": [],
        "n_chunks": 31,
    }
)
async_stream_snapshot = snapshot(
    {
        "provider": "openai:responses",
        "model_id": "gpt-4o",
        "finish_reason": None,
        "messages": [
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
                        text='{"title":"THE NAME OF THE WIND","author":{"first_name":"Patrick","last_name":"Rothfuss"},"rating":7}'
                    )
                ],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "id": "msg_05391735c2f6550b0068dc21da470c81949ff4a050c3a52555",
                        "content": [
                            {
                                "annotations": [],
                                "text": '{"title":"THE NAME OF THE WIND","author":{"first_name":"Patrick","last_name":"Rothfuss"},"rating":7}',
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
        "format": {
            "name": "Book",
            "description": "A book with a rating. The title should be in all caps!",
            "schema": {
                "$defs": {
                    "Author": {
                        "description": "The author of a book.",
                        "properties": {
                            "first_name": {"title": "First Name", "type": "string"},
                            "last_name": {"title": "Last Name", "type": "string"},
                        },
                        "required": ["first_name", "last_name"],
                        "title": "Author",
                        "type": "object",
                        "additionalProperties": False,
                    }
                },
                "description": "A book with a rating. The title should be in all caps!",
                "properties": {
                    "title": {"title": "Title", "type": "string"},
                    "author": {"$ref": "#/$defs/Author"},
                    "rating": {
                        "description": "For testing purposes, the rating should be 7",
                        "title": "Rating",
                        "type": "integer",
                    },
                },
                "required": ["title", "author", "rating"],
                "title": "Book",
                "type": "object",
            },
            "mode": "strict",
            "formatting_instructions": None,
        },
        "tools": [],
        "n_chunks": 31,
    }
)
