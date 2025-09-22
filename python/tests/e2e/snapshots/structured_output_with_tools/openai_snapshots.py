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
                        id="call_FzMB6C2Yzw1uEebNCv8tLMow",
                        name="get_book_info",
                        args='{"isbn":"0-7653-1178-X"}',
                    )
                ]
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="call_FzMB6C2Yzw1uEebNCv8tLMow",
                        name="get_book_info",
                        value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text='{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006}'
                    )
                ]
            ),
        ],
        "format": {
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
                },
                "required": ["title", "author", "pages", "publication_year"],
                "title": "BookSummary",
                "type": "object",
            },
            "mode": "strict",
            "formatting_instructions": None,
        },
        "tools": [
            {
                "name": "get_book_info",
                "description": "Look up book information by ISBN.",
                "parameters": """\
{
  "properties": {
    "isbn": {
      "title": "Isbn",
      "type": "string"
    }
  },
  "required": [
    "isbn"
  ],
  "additionalProperties": false,
  "defs": null
}\
""",
                "strict": False,
            }
        ],
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
                        id="call_BkWBU0Vmbb04J1Si0fPD29ZZ",
                        name="get_book_info",
                        args='{"isbn":"0-7653-1178-X"}',
                    )
                ]
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="call_BkWBU0Vmbb04J1Si0fPD29ZZ",
                        name="get_book_info",
                        value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text='{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006}'
                    )
                ]
            ),
        ],
        "format": {
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
                },
                "required": ["title", "author", "pages", "publication_year"],
                "title": "BookSummary",
                "type": "object",
            },
            "mode": "strict",
            "formatting_instructions": None,
        },
        "tools": [
            {
                "name": "get_book_info",
                "description": "Look up book information by ISBN.",
                "parameters": """\
{
  "properties": {
    "isbn": {
      "title": "Isbn",
      "type": "string"
    }
  },
  "required": [
    "isbn"
  ],
  "additionalProperties": false,
  "defs": null
}\
""",
                "strict": False,
            }
        ],
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
                        id="call_nlPzRyF0DR73zQpt1hCmi7RK",
                        name="get_book_info",
                        args='{"isbn":"0-7653-1178-X"}',
                    )
                ]
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="call_nlPzRyF0DR73zQpt1hCmi7RK",
                        name="get_book_info",
                        value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text='{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006}'
                    )
                ]
            ),
        ],
        "format": {
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
                },
                "required": ["title", "author", "pages", "publication_year"],
                "title": "BookSummary",
                "type": "object",
            },
            "mode": "strict",
            "formatting_instructions": None,
        },
        "tools": [
            {
                "name": "get_book_info",
                "description": "Look up book information by ISBN.",
                "parameters": """\
{
  "properties": {
    "isbn": {
      "title": "Isbn",
      "type": "string"
    }
  },
  "required": [
    "isbn"
  ],
  "additionalProperties": false,
  "defs": null
}\
""",
                "strict": False,
            }
        ],
        "n_chunks": 30,
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
                        id="call_HOQ64tNdVOJXkZB8AxQBziOL",
                        name="get_book_info",
                        args='{"isbn":"0-7653-1178-X"}',
                    )
                ]
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="call_HOQ64tNdVOJXkZB8AxQBziOL",
                        name="get_book_info",
                        value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text='{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006}'
                    )
                ]
            ),
        ],
        "format": {
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
                },
                "required": ["title", "author", "pages", "publication_year"],
                "title": "BookSummary",
                "type": "object",
            },
            "mode": "strict",
            "formatting_instructions": None,
        },
        "tools": [
            {
                "name": "get_book_info",
                "description": "Look up book information by ISBN.",
                "parameters": """\
{
  "properties": {
    "isbn": {
      "title": "Isbn",
      "type": "string"
    }
  },
  "required": [
    "isbn"
  ],
  "additionalProperties": false,
  "defs": null
}\
""",
                "strict": False,
            }
        ],
        "n_chunks": 30,
    }
)
