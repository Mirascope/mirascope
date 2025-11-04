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
            "provider": "azure-openai:responses",
            "model_id": "gpt-4o-mini",
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
                            id="call_rmLQcjSsqFc8B3KM59e5WVZv",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "arguments": '{"isbn":"0-7653-1178-X"}',
                            "call_id": "call_rmLQcjSsqFc8B3KM59e5WVZv",
                            "name": "get_book_info",
                            "type": "function_call",
                            "id": "fc_07b9c61b9aba94a500690c2218f06c8195b3baa2b7b3003158",
                            "status": "completed",
                        }
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_rmLQcjSsqFc8B3KM59e5WVZv",
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
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "arguments": '{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006}',
                            "call_id": "call_MQS4udZpyqQrl5nElshImHRR",
                            "name": "__mirascope_formatted_output_tool__",
                            "type": "function_call",
                            "id": "fc_0df6f3c60b5566dc00690c221a660c81938b100487d0fb5fa3",
                            "status": "completed",
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
    }
)
async_snapshot = snapshot(
    {
        "response": {
            "provider": "azure-openai:responses",
            "model_id": "gpt-4o-mini",
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
                            id="call_PqRXmevD9HVMUMRPP4ksDFYb",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "arguments": '{"isbn":"0-7653-1178-X"}',
                            "call_id": "call_PqRXmevD9HVMUMRPP4ksDFYb",
                            "name": "get_book_info",
                            "type": "function_call",
                            "id": "fc_0d22d33f323354bc00690c224d7dd08195b1964d09a0615b96",
                            "status": "completed",
                        }
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_PqRXmevD9HVMUMRPP4ksDFYb",
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
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "arguments": '{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006}',
                            "call_id": "call_YvvQWuMSiZfBLVKxhqujjc3u",
                            "name": "__mirascope_formatted_output_tool__",
                            "type": "function_call",
                            "id": "fc_094fe0ebcfd9ed3f00690c224ea9b48194b8326c635849e314",
                            "status": "completed",
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
    }
)
stream_snapshot = snapshot(
    {
        "response": {
            "provider": "azure-openai:responses",
            "model_id": "gpt-4o-mini",
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
                            id="call_x7yHzjumLijee2hrt0d1IRTP",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "arguments": '{"isbn":"0-7653-1178-X"}',
                            "call_id": "call_x7yHzjumLijee2hrt0d1IRTP",
                            "name": "get_book_info",
                            "type": "function_call",
                            "id": "fc_08401aee891685e900690c22c560088197b9bc4286f6b42e8d",
                            "status": "completed",
                        }
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_x7yHzjumLijee2hrt0d1IRTP",
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
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "arguments": '{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006}',
                            "call_id": "call_oRoEM0hQ23Ql0bDulaRFcZbp",
                            "name": "__mirascope_formatted_output_tool__",
                            "type": "function_call",
                            "id": "fc_004539c95c46341a00690c22c67de881968bf60f4136de0f7c",
                            "status": "completed",
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
            "n_chunks": 29,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider": "azure-openai:responses",
            "model_id": "gpt-4o-mini",
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
                            id="call_drvn1X0xCoDL9hdXSbpKtHBg",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "arguments": '{"isbn":"0-7653-1178-X"}',
                            "call_id": "call_drvn1X0xCoDL9hdXSbpKtHBg",
                            "name": "get_book_info",
                            "type": "function_call",
                            "id": "fc_0fa5ad674be77b3200690c2399759881909067b717a7b9fc2b",
                            "status": "completed",
                        }
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_drvn1X0xCoDL9hdXSbpKtHBg",
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
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "arguments": '{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006}',
                            "call_id": "call_R3X3EPJVn5PpLRBEbnHTJeuf",
                            "name": "__mirascope_formatted_output_tool__",
                            "type": "function_call",
                            "id": "fc_0eb30b0a4ebe260700690c239aae6881939c0632ec243d7114",
                            "status": "completed",
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
            "n_chunks": 29,
        }
    }
)
