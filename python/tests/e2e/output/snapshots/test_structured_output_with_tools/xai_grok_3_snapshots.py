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
        "response": {
            "provider": "xai",
            "model_id": "grok-3",
            "params": {},
            "finish_reason": None,
            "messages": [
                SystemMessage(
                    content=Text(
                        text="Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output."
                    )
                ),
                UserMessage(
                    content=(
                        Text(
                            text="Please look up the book with ISBN 0-7653-1178-X and provide detailed info and a recommendation score"
                        ),
                    )
                ),
                AssistantMessage(
                    content=(
                        ToolCall(
                            id="tool_call_001",
                            name="get_book_info",
                            args="[xai tool call args]",
                        ),
                    ),
                    provider="xai",
                    model_id="grok-3",
                    raw_message={
                        "content": [
                            {
                                "type": "tool_call",
                                "id": "tool_call_001",
                                "name": "get_book_info",
                                "args": "[xai tool call args]",
                            }
                        ],
                        "tool_calls": [
                            {
                                "id": "tool_call_001",
                                "function": {
                                    "name": "get_book_info",
                                    "arguments": "[xai tool call args]",
                                },
                            }
                        ],
                    },
                ),
                UserMessage(
                    content=(
                        ToolOutput(
                            id="tool_call_001",
                            name="get_book_info",
                            value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        ),
                    )
                ),
                AssistantMessage(
                    content=(Text(text="[xai assistant text]"),),
                    provider="xai",
                    model_id="grok-3",
                    raw_message={
                        "content": [
                            {
                                "type": "tool_call",
                                "id": "tool_call_002",
                                "name": "__mirascope_formatted_output_tool__",
                                "args": "[xai tool call args]",
                            }
                        ],
                        "tool_calls": [
                            {
                                "id": "tool_call_002",
                                "function": {
                                    "name": "__mirascope_formatted_output_tool__",
                                    "arguments": "[xai tool call args]",
                                },
                            }
                        ],
                    },
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
    }
)
async_snapshot = snapshot(
    {
        "response": {
            "provider": "xai",
            "model_id": "grok-3",
            "params": {},
            "finish_reason": None,
            "messages": [
                SystemMessage(
                    content=Text(
                        text="Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output."
                    )
                ),
                UserMessage(
                    content=(
                        Text(
                            text="Please look up the book with ISBN 0-7653-1178-X and provide detailed info and a recommendation score"
                        ),
                    )
                ),
                AssistantMessage(
                    content=(
                        ToolCall(
                            id="tool_call_001",
                            name="get_book_info",
                            args="[xai tool call args]",
                        ),
                    ),
                    provider="xai",
                    model_id="grok-3",
                    raw_message={
                        "content": [
                            {
                                "type": "tool_call",
                                "id": "tool_call_001",
                                "name": "get_book_info",
                                "args": "[xai tool call args]",
                            }
                        ],
                        "tool_calls": [
                            {
                                "id": "tool_call_001",
                                "function": {
                                    "name": "get_book_info",
                                    "arguments": "[xai tool call args]",
                                },
                            }
                        ],
                    },
                ),
                UserMessage(
                    content=(
                        ToolOutput(
                            id="tool_call_001",
                            name="get_book_info",
                            value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        ),
                    )
                ),
                AssistantMessage(
                    content=(Text(text="[xai assistant text]"),),
                    provider="xai",
                    model_id="grok-3",
                    raw_message={
                        "content": [
                            {
                                "type": "tool_call",
                                "id": "tool_call_002",
                                "name": "__mirascope_formatted_output_tool__",
                                "args": "[xai tool call args]",
                            }
                        ],
                        "tool_calls": [
                            {
                                "id": "tool_call_002",
                                "function": {
                                    "name": "__mirascope_formatted_output_tool__",
                                    "arguments": "[xai tool call args]",
                                },
                            }
                        ],
                    },
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
    }
)
stream_snapshot = snapshot(
    {
        "response": {
            "provider": "xai",
            "model_id": "grok-3",
            "finish_reason": None,
            "messages": [
                SystemMessage(
                    content=Text(
                        text="Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output."
                    )
                ),
                UserMessage(
                    content=(
                        Text(
                            text="Please look up the book with ISBN 0-7653-1178-X and provide detailed info and a recommendation score"
                        ),
                    )
                ),
                AssistantMessage(
                    content=(
                        ToolCall(
                            id="tool_call_001",
                            name="get_book_info",
                            args="[xai tool call args]",
                        ),
                    ),
                    provider="xai",
                    model_id="grok-3",
                    raw_message={
                        "content": [
                            {
                                "type": "tool_call",
                                "id": "tool_call_001",
                                "name": "get_book_info",
                                "args": "[xai tool call args]",
                            }
                        ],
                        "tool_calls": [
                            {
                                "id": "tool_call_001",
                                "function": {
                                    "name": "get_book_info",
                                    "arguments": "[xai tool call args]",
                                },
                            }
                        ],
                    },
                ),
                UserMessage(
                    content=(
                        ToolOutput(
                            id="tool_call_001",
                            name="get_book_info",
                            value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        ),
                    )
                ),
                AssistantMessage(
                    content=(Text(text="[xai assistant text]"),),
                    provider="xai",
                    model_id="grok-3",
                    raw_message={
                        "content": [
                            {
                                "type": "tool_call",
                                "id": "tool_call_002",
                                "name": "__mirascope_formatted_output_tool__",
                                "args": "[xai tool call args]",
                            }
                        ],
                        "tool_calls": [
                            {
                                "id": "tool_call_002",
                                "function": {
                                    "name": "__mirascope_formatted_output_tool__",
                                    "arguments": "[xai tool call args]",
                                },
                            }
                        ],
                    },
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
            "n_chunks": "variable",
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider": "xai",
            "model_id": "grok-3",
            "finish_reason": None,
            "messages": [
                SystemMessage(
                    content=Text(
                        text="Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output."
                    )
                ),
                UserMessage(
                    content=(
                        Text(
                            text="Please look up the book with ISBN 0-7653-1178-X and provide detailed info and a recommendation score"
                        ),
                    )
                ),
                AssistantMessage(
                    content=(
                        ToolCall(
                            id="tool_call_001",
                            name="get_book_info",
                            args="[xai tool call args]",
                        ),
                    ),
                    provider="xai",
                    model_id="grok-3",
                    raw_message={
                        "content": [
                            {
                                "type": "tool_call",
                                "id": "tool_call_001",
                                "name": "get_book_info",
                                "args": "[xai tool call args]",
                            }
                        ],
                        "tool_calls": [
                            {
                                "id": "tool_call_001",
                                "function": {
                                    "name": "get_book_info",
                                    "arguments": "[xai tool call args]",
                                },
                            }
                        ],
                    },
                ),
                UserMessage(
                    content=(
                        ToolOutput(
                            id="tool_call_001",
                            name="get_book_info",
                            value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        ),
                    )
                ),
                AssistantMessage(
                    content=(Text(text="[xai assistant text]"),),
                    provider="xai",
                    model_id="grok-3",
                    raw_message={
                        "content": [
                            {
                                "type": "tool_call",
                                "id": "tool_call_002",
                                "name": "__mirascope_formatted_output_tool__",
                                "args": "[xai tool call args]",
                            }
                        ],
                        "tool_calls": [
                            {
                                "id": "tool_call_002",
                                "function": {
                                    "name": "__mirascope_formatted_output_tool__",
                                    "arguments": "[xai tool call args]",
                                },
                            }
                        ],
                    },
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
            "n_chunks": "variable",
        }
    }
)
