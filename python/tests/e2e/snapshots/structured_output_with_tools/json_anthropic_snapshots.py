from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    FinishReason,
    SystemMessage,
    Text,
    ToolCall,
    ToolOutput,
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
Respond only with valid JSON that matches this exact schema:
{
  "properties": {
    "title": {
      "title": "Title",
      "type": "string"
    },
    "author": {
      "title": "Author",
      "type": "string"
    },
    "pages": {
      "title": "Pages",
      "type": "integer"
    },
    "publication_year": {
      "title": "Publication Year",
      "type": "integer"
    }
  },
  "required": [
    "title",
    "author",
    "pages",
    "publication_year"
  ],
  "title": "BookSummary",
  "type": "object"
}\
"""
                )
            ),
            UserMessage(
                content=[
                    Text(
                        text="Please look up the book with ISBN 0-7653-1178-X and provide detailed info and a recommendation score"
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="I'll look up the book information for ISBN 0-7653-1178-X."
                    ),
                    ToolCall(
                        id="toolu_01XAV8SzAYW1s424CW83ThCy",
                        name="get_book_info",
                        args='{"isbn": "0-7653-1178-X"}',
                    ),
                ]
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="toolu_01XAV8SzAYW1s424CW83ThCy",
                        name="get_book_info",
                        value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}\
"""
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
            "mode": "json",
            "formatting_instructions": """\
Respond only with valid JSON that matches this exact schema:
{
  "properties": {
    "title": {
      "title": "Title",
      "type": "string"
    },
    "author": {
      "title": "Author",
      "type": "string"
    },
    "pages": {
      "title": "Pages",
      "type": "integer"
    },
    "publication_year": {
      "title": "Publication Year",
      "type": "integer"
    }
  },
  "required": [
    "title",
    "author",
    "pages",
    "publication_year"
  ],
  "title": "BookSummary",
  "type": "object"
}\
""",
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
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-0",
        "params": {},
        "finish_reason": FinishReason.END_TURN,
        "messages": [
            SystemMessage(
                content=Text(
                    text="""\
Respond only with valid JSON that matches this exact schema:
{
  "properties": {
    "title": {
      "title": "Title",
      "type": "string"
    },
    "author": {
      "title": "Author",
      "type": "string"
    },
    "pages": {
      "title": "Pages",
      "type": "integer"
    },
    "publication_year": {
      "title": "Publication Year",
      "type": "integer"
    }
  },
  "required": [
    "title",
    "author",
    "pages",
    "publication_year"
  ],
  "title": "BookSummary",
  "type": "object"
}\
"""
                )
            ),
            UserMessage(
                content=[
                    Text(
                        text="Please look up the book with ISBN 0-7653-1178-X and provide detailed info and a recommendation score"
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="I'll look up the book information for ISBN 0-7653-1178-X."
                    ),
                    ToolCall(
                        id="toolu_018tw1WJDw6DLu46vd8id2m8",
                        name="get_book_info",
                        args='{"isbn": "0-7653-1178-X"}',
                    ),
                ]
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="toolu_018tw1WJDw6DLu46vd8id2m8",
                        name="get_book_info",
                        value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
```json
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}
```\
"""
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
            "mode": "json",
            "formatting_instructions": """\
Respond only with valid JSON that matches this exact schema:
{
  "properties": {
    "title": {
      "title": "Title",
      "type": "string"
    },
    "author": {
      "title": "Author",
      "type": "string"
    },
    "pages": {
      "title": "Pages",
      "type": "integer"
    },
    "publication_year": {
      "title": "Publication Year",
      "type": "integer"
    }
  },
  "required": [
    "title",
    "author",
    "pages",
    "publication_year"
  ],
  "title": "BookSummary",
  "type": "object"
}\
""",
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
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-0",
        "finish_reason": FinishReason.END_TURN,
        "messages": [
            SystemMessage(
                content=Text(
                    text="""\
Respond only with valid JSON that matches this exact schema:
{
  "properties": {
    "title": {
      "title": "Title",
      "type": "string"
    },
    "author": {
      "title": "Author",
      "type": "string"
    },
    "pages": {
      "title": "Pages",
      "type": "integer"
    },
    "publication_year": {
      "title": "Publication Year",
      "type": "integer"
    }
  },
  "required": [
    "title",
    "author",
    "pages",
    "publication_year"
  ],
  "title": "BookSummary",
  "type": "object"
}\
"""
                )
            ),
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
                        id="toolu_01R3Vtivons4MceJSju6zEcg",
                        name="get_book_info",
                        args='{"isbn": "0-7653-1178-X"}',
                    )
                ]
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="toolu_01R3Vtivons4MceJSju6zEcg",
                        name="get_book_info",
                        value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
```json
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}
```\
"""
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
            "mode": "json",
            "formatting_instructions": """\
Respond only with valid JSON that matches this exact schema:
{
  "properties": {
    "title": {
      "title": "Title",
      "type": "string"
    },
    "author": {
      "title": "Author",
      "type": "string"
    },
    "pages": {
      "title": "Pages",
      "type": "integer"
    },
    "publication_year": {
      "title": "Publication Year",
      "type": "integer"
    }
  },
  "required": [
    "title",
    "author",
    "pages",
    "publication_year"
  ],
  "title": "BookSummary",
  "type": "object"
}\
""",
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
        "n_chunks": 7,
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
Respond only with valid JSON that matches this exact schema:
{
  "properties": {
    "title": {
      "title": "Title",
      "type": "string"
    },
    "author": {
      "title": "Author",
      "type": "string"
    },
    "pages": {
      "title": "Pages",
      "type": "integer"
    },
    "publication_year": {
      "title": "Publication Year",
      "type": "integer"
    }
  },
  "required": [
    "title",
    "author",
    "pages",
    "publication_year"
  ],
  "title": "BookSummary",
  "type": "object"
}\
"""
                )
            ),
            UserMessage(
                content=[
                    Text(
                        text="Please look up the book with ISBN 0-7653-1178-X and provide detailed info and a recommendation score"
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="I'll look up the book information for ISBN 0-7653-1178-X."
                    ),
                    ToolCall(
                        id="toolu_01Frb4XcLWS36HNUZy4ANF1W",
                        name="get_book_info",
                        args='{"isbn": "0-7653-1178-X"}',
                    ),
                ]
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="toolu_01Frb4XcLWS36HNUZy4ANF1W",
                        name="get_book_info",
                        value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}\
"""
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
            "mode": "json",
            "formatting_instructions": """\
Respond only with valid JSON that matches this exact schema:
{
  "properties": {
    "title": {
      "title": "Title",
      "type": "string"
    },
    "author": {
      "title": "Author",
      "type": "string"
    },
    "pages": {
      "title": "Pages",
      "type": "integer"
    },
    "publication_year": {
      "title": "Publication Year",
      "type": "integer"
    }
  },
  "required": [
    "title",
    "author",
    "pages",
    "publication_year"
  ],
  "title": "BookSummary",
  "type": "object"
}\
""",
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
        "n_chunks": 6,
    }
)
