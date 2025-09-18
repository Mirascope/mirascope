from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    FinishReason,
    Text,
    ToolCall,
    ToolOutput,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "provider": "openai",
        "model_id": "gpt-4o",
        "params": {},
        "finish_reason": FinishReason.END_TURN,
        "messages": [
            UserMessage(
                content=[
                    Text(
                        text="Please look up the book with ISBN 0-7653-1178-X and provide detailed info and a recommendation score"
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    ToolCall(
                        id="call_CXeMfU0FJVvMCAxHN3O4v0df",
                        name="get_book_info",
                        args='{"isbn":"0-7653-1178-X"}',
                    )
                ]
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="call_CXeMfU0FJVvMCAxHN3O4v0df",
                        name="get_book_info",
                        value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text='{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006,"recommendation_score":7}'
                    )
                ]
            ),
        ],
        "format_type": {
            "name": "BookSummary",
            "description": None,
            "schema": {
                "properties": {
                    "title": {"title": "Title", "type": "string"},
                    "author": {"title": "Author", "type": "string"},
                    "pages": {"title": "Pages", "type": "integer"},
                    "publication_year": {
                        "title": "Publication Year",
                        "type": "integer",
                    },
                    "recommendation_score": {
                        "description": "Should be 7 for testing purposes",
                        "title": "Recommendation Score",
                        "type": "integer",
                    },
                },
                "required": [
                    "title",
                    "author",
                    "pages",
                    "publication_year",
                    "recommendation_score",
                ],
                "title": "BookSummary",
                "type": "object",
            },
            "mode": "strict",
        },
    }
)
async_snapshot = snapshot(
    {
        "provider": "openai",
        "model_id": "gpt-4o",
        "params": {},
        "finish_reason": FinishReason.END_TURN,
        "messages": [
            UserMessage(
                content=[
                    Text(
                        text="Please look up the book with ISBN 0-7653-1178-X and provide detailed info and a recommendation score"
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    ToolCall(
                        id="call_wTwBiXTXhpiOJBxhiBUbt6op",
                        name="get_book_info",
                        args='{"isbn":"0-7653-1178-X"}',
                    )
                ]
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="call_wTwBiXTXhpiOJBxhiBUbt6op",
                        name="get_book_info",
                        value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text='{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006,"recommendation_score":7}'
                    )
                ]
            ),
        ],
        "format_type": {
            "name": "BookSummary",
            "description": None,
            "schema": {
                "properties": {
                    "title": {"title": "Title", "type": "string"},
                    "author": {"title": "Author", "type": "string"},
                    "pages": {"title": "Pages", "type": "integer"},
                    "publication_year": {
                        "title": "Publication Year",
                        "type": "integer",
                    },
                    "recommendation_score": {
                        "description": "Should be 7 for testing purposes",
                        "title": "Recommendation Score",
                        "type": "integer",
                    },
                },
                "required": [
                    "title",
                    "author",
                    "pages",
                    "publication_year",
                    "recommendation_score",
                ],
                "title": "BookSummary",
                "type": "object",
            },
            "mode": "strict",
        },
    }
)
stream_snapshot = snapshot(
    {
        "provider": "openai",
        "model_id": "gpt-4o",
        "finish_reason": FinishReason.END_TURN,
        "messages": [
            UserMessage(
                content=[
                    Text(
                        text="Please look up the book with ISBN 0-7653-1178-X and provide detailed info and a recommendation score"
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    ToolCall(
                        id="call_JxqxrN30kkw34iPmrrT9TNTA",
                        name="get_book_info",
                        args='{"isbn":"0-7653-1178-X"}',
                    )
                ]
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="call_JxqxrN30kkw34iPmrrT9TNTA",
                        name="get_book_info",
                        value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text='{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006,"recommendation_score":7}'
                    )
                ]
            ),
        ],
        "format_type": {
            "name": "BookSummary",
            "description": None,
            "schema": {
                "properties": {
                    "title": {"title": "Title", "type": "string"},
                    "author": {"title": "Author", "type": "string"},
                    "pages": {"title": "Pages", "type": "integer"},
                    "publication_year": {
                        "title": "Publication Year",
                        "type": "integer",
                    },
                    "recommendation_score": {
                        "description": "Should be 7 for testing purposes",
                        "title": "Recommendation Score",
                        "type": "integer",
                    },
                },
                "required": [
                    "title",
                    "author",
                    "pages",
                    "publication_year",
                    "recommendation_score",
                ],
                "title": "BookSummary",
                "type": "object",
            },
            "mode": "strict",
        },
        "n_chunks": 36,
    }
)
async_stream_snapshot = snapshot(
    {
        "provider": "openai",
        "model_id": "gpt-4o",
        "finish_reason": FinishReason.END_TURN,
        "messages": [
            UserMessage(
                content=[
                    Text(
                        text="Please look up the book with ISBN 0-7653-1178-X and provide detailed info and a recommendation score"
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    ToolCall(
                        id="call_GvkukvzGZwztSs8iBic9TId7",
                        name="get_book_info",
                        args='{"isbn":"0-7653-1178-X"}',
                    )
                ]
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="call_GvkukvzGZwztSs8iBic9TId7",
                        name="get_book_info",
                        value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text='{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006,"recommendation_score":7}'
                    )
                ]
            ),
        ],
        "format_type": {
            "name": "BookSummary",
            "description": None,
            "schema": {
                "properties": {
                    "title": {"title": "Title", "type": "string"},
                    "author": {"title": "Author", "type": "string"},
                    "pages": {"title": "Pages", "type": "integer"},
                    "publication_year": {
                        "title": "Publication Year",
                        "type": "integer",
                    },
                    "recommendation_score": {
                        "description": "Should be 7 for testing purposes",
                        "title": "Recommendation Score",
                        "type": "integer",
                    },
                },
                "required": [
                    "title",
                    "author",
                    "pages",
                    "publication_year",
                    "recommendation_score",
                ],
                "title": "BookSummary",
                "type": "object",
            },
            "mode": "strict",
        },
        "n_chunks": 36,
    }
)
