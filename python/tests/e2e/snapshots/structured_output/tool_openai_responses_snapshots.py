from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    SystemMessage,
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
            SystemMessage(
                content=Text(
                    text="Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output."
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
                        text='{"title":"THE NAME OF THE WIND","author":{"first_name":"Patrick","last_name":"Rothfuss"},"rating":7}'
                    )
                ],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "arguments": '{"title":"THE NAME OF THE WIND","author":{"first_name":"Patrick","last_name":"Rothfuss"},"rating":7}',
                        "call_id": "call_6k4XQb0bQFkH3uvlKTDZV1eS",
                        "name": "__mirascope_formatted_output_tool__",
                        "type": "function_call",
                        "id": "fc_0705a02db4c162530068dc21c6a2d48194990250d94486d5a6",
                        "status": "completed",
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
            "mode": "tool",
            "formatting_instructions": "Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output.",
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
            SystemMessage(
                content=Text(
                    text="Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output."
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
                        text='{"title":"THE NAME OF THE WIND","author":{"first_name":"Patrick","last_name":"Rothfuss"},"rating":7}'
                    )
                ],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "arguments": '{"title":"THE NAME OF THE WIND","author":{"first_name":"Patrick","last_name":"Rothfuss"},"rating":7}',
                        "call_id": "call_AvTXFaymhPAzmOjhAuLsPc4R",
                        "name": "__mirascope_formatted_output_tool__",
                        "type": "function_call",
                        "id": "fc_034ee170e6d7aea20068dc21d096e081948d9e1db408a2f2a3",
                        "status": "completed",
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
            "mode": "tool",
            "formatting_instructions": "Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output.",
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
            SystemMessage(
                content=Text(
                    text="Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output."
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
                        text='{"title":"THE NAME OF THE WIND","author":{"first_name":"Patrick","last_name":"Rothfuss"},"rating":7}'
                    )
                ],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "arguments": '{"title":"THE NAME OF THE WIND","author":{"first_name":"Patrick","last_name":"Rothfuss"},"rating":7}',
                        "call_id": "call_JPmIyFzpIkbF3dElXevhiiDd",
                        "name": "__mirascope_formatted_output_tool__",
                        "type": "function_call",
                        "id": "fc_08dd94f1b664d8250068dc21d739988195bc6b1a6ac6b03270",
                        "status": "completed",
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
            "mode": "tool",
            "formatting_instructions": "Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output.",
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
            SystemMessage(
                content=Text(
                    text="Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output."
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
                        text='{"title":"THE NAME OF THE WIND","author":{"first_name":"Patrick","last_name":"Rothfuss"},"rating":7}'
                    )
                ],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "arguments": '{"title":"THE NAME OF THE WIND","author":{"first_name":"Patrick","last_name":"Rothfuss"},"rating":7}',
                        "call_id": "call_foGb7f0gM9wV9qFDi9oLWkDg",
                        "name": "__mirascope_formatted_output_tool__",
                        "type": "function_call",
                        "id": "fc_02ef47e0eee50c380068dc21df4198819684c785265ab7fb4c",
                        "status": "completed",
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
            "mode": "tool",
            "formatting_instructions": "Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output.",
        },
        "tools": [],
        "n_chunks": 31,
    }
)
