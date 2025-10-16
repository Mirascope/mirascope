from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
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
                        text="Please look up the book with ISBN 0-7653-1178-X and provide detailed info and a recommendation score"
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    ToolCall(
                        id="toolu_01QUBtKQhcU5U5zAWFqA93Lz",
                        name="get_book_info",
                        args='{"isbn": "0-7653-1178-X"}',
                    )
                ],
                provider="anthropic",
                model_id="claude-sonnet-4-0",
                raw_content=[
                    {
                        "id": "toolu_01QUBtKQhcU5U5zAWFqA93Lz",
                        "input": {"isbn": "0-7653-1178-X"},
                        "name": "get_book_info",
                        "type": "tool_use",
                    }
                ],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="toolu_01QUBtKQhcU5U5zAWFqA93Lz",
                        name="get_book_info",
                        value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text='{"title": "Mistborn: The Final Empire", "author": "Brandon Sanderson", "pages": 544, "publication_year": 2006}'
                    )
                ],
                provider="anthropic",
                model_id="claude-sonnet-4-0",
                raw_content=[
                    {
                        "id": "toolu_01Nk47Ju7e3GVSAQn3Lu27yh",
                        "input": {
                            "title": "Mistborn: The Final Empire",
                            "author": "Brandon Sanderson",
                            "pages": 544,
                            "publication_year": 2006,
                        },
                        "name": "__mirascope_formatted_output_tool__",
                        "type": "tool_use",
                    }
                ],
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
            "mode": "tool",
            "formatting_instructions": "Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output.",
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
                        text="Please look up the book with ISBN 0-7653-1178-X and provide detailed info and a recommendation score"
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    ToolCall(
                        id="toolu_016FcY5hYcCQYT7qTH6acypC",
                        name="get_book_info",
                        args='{"isbn": "0-7653-1178-X"}',
                    )
                ],
                provider="anthropic",
                model_id="claude-sonnet-4-0",
                raw_content=[
                    {
                        "id": "toolu_016FcY5hYcCQYT7qTH6acypC",
                        "input": {"isbn": "0-7653-1178-X"},
                        "name": "get_book_info",
                        "type": "tool_use",
                    }
                ],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="toolu_016FcY5hYcCQYT7qTH6acypC",
                        name="get_book_info",
                        value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text='{"title": "Mistborn: The Final Empire", "author": "Brandon Sanderson", "pages": 544, "publication_year": 2006}'
                    )
                ],
                provider="anthropic",
                model_id="claude-sonnet-4-0",
                raw_content=[
                    {
                        "id": "toolu_01G4jabRuYsFZioSE1dSEDCc",
                        "input": {
                            "title": "Mistborn: The Final Empire",
                            "author": "Brandon Sanderson",
                            "pages": 544,
                            "publication_year": 2006,
                        },
                        "name": "__mirascope_formatted_output_tool__",
                        "type": "tool_use",
                    }
                ],
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
            "mode": "tool",
            "formatting_instructions": "Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output.",
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
                        text="Please look up the book with ISBN 0-7653-1178-X and provide detailed info and a recommendation score"
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    ToolCall(
                        id="toolu_01WvYbeP7pboD2CNAsnnG14f",
                        name="get_book_info",
                        args='{"isbn": "0-7653-1178-X"}',
                    )
                ],
                provider="anthropic",
                model_id="claude-sonnet-4-0",
                raw_content=[
                    {
                        "type": "tool_use",
                        "id": "toolu_01WvYbeP7pboD2CNAsnnG14f",
                        "name": "get_book_info",
                        "input": {"isbn": "0-7653-1178-X"},
                    }
                ],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="toolu_01WvYbeP7pboD2CNAsnnG14f",
                        name="get_book_info",
                        value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text='{"title": "Mistborn: The Final Empire", "author": "Brandon Sanderson", "pages": 544, "publication_year": 2006}'
                    )
                ],
                provider="anthropic",
                model_id="claude-sonnet-4-0",
                raw_content=[
                    {
                        "type": "tool_use",
                        "id": "toolu_019XGjpt5MeVFoDBCdGMmCh6",
                        "name": "__mirascope_formatted_output_tool__",
                        "input": {
                            "title": "Mistborn: The Final Empire",
                            "author": "Brandon Sanderson",
                            "pages": 544,
                            "publication_year": 2006,
                        },
                    }
                ],
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
            "mode": "tool",
            "formatting_instructions": "Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output.",
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
        "n_chunks": 19,
    }
)
async_stream_snapshot = snapshot(
    {
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-0",
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
                        text="Please look up the book with ISBN 0-7653-1178-X and provide detailed info and a recommendation score"
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    ToolCall(
                        id="toolu_018H2ZPCx3rF15Naj4FJNdzj",
                        name="get_book_info",
                        args='{"isbn": "0-7653-1178-X"}',
                    )
                ],
                provider="anthropic",
                model_id="claude-sonnet-4-0",
                raw_content=[
                    {
                        "type": "tool_use",
                        "id": "toolu_018H2ZPCx3rF15Naj4FJNdzj",
                        "name": "get_book_info",
                        "input": {"isbn": "0-7653-1178-X"},
                    }
                ],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="toolu_018H2ZPCx3rF15Naj4FJNdzj",
                        name="get_book_info",
                        value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text='{"title": "Mistborn: The Final Empire", "author": "Brandon Sanderson", "pages": 544, "publication_year": 2006}'
                    )
                ],
                provider="anthropic",
                model_id="claude-sonnet-4-0",
                raw_content=[
                    {
                        "type": "tool_use",
                        "id": "toolu_01LteLyDa79rSPXcb1e5nY2F",
                        "name": "__mirascope_formatted_output_tool__",
                        "input": {
                            "title": "Mistborn: The Final Empire",
                            "author": "Brandon Sanderson",
                            "pages": 544,
                            "publication_year": 2006,
                        },
                    }
                ],
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
            "mode": "tool",
            "formatting_instructions": "Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output.",
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
        "n_chunks": 21,
    }
)
