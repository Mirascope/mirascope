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
                        text="Please look up the book with ISBN 0-7653-1178-X and provide detailed info and a recommendation score"
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    ToolCall(
                        id="call_taztVjN7NXAvAMrg5PH9F0d0",
                        name="get_book_info",
                        args='{"isbn":"0-7653-1178-X"}',
                    )
                ],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "arguments": '{"isbn":"0-7653-1178-X"}',
                        "call_id": "call_taztVjN7NXAvAMrg5PH9F0d0",
                        "name": "get_book_info",
                        "type": "function_call",
                        "id": "fc_03630795d254ef490068e70541b0348195bb5533052e479723",
                        "status": "completed",
                    }
                ],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="call_taztVjN7NXAvAMrg5PH9F0d0",
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
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "arguments": '{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006}',
                        "call_id": "call_uLmJCg5vvqBYItFAzcoSVDNp",
                        "name": "__mirascope_formatted_output_tool__",
                        "type": "function_call",
                        "id": "fc_03630795d254ef490068e70542b6f48195aa74e349ed55a47d",
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
                        text="Please look up the book with ISBN 0-7653-1178-X and provide detailed info and a recommendation score"
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    ToolCall(
                        id="call_k4zHxAe8ErDpEtTCY0i32jGC",
                        name="get_book_info",
                        args='{"isbn":"0-7653-1178-X"}',
                    )
                ],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "arguments": '{"isbn":"0-7653-1178-X"}',
                        "call_id": "call_k4zHxAe8ErDpEtTCY0i32jGC",
                        "name": "get_book_info",
                        "type": "function_call",
                        "id": "fc_0c5b5f1dd1eb58fc0068e7054fbde08197a357674385e5a829",
                        "status": "completed",
                    }
                ],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="call_k4zHxAe8ErDpEtTCY0i32jGC",
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
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "arguments": '{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006}',
                        "call_id": "call_UZL8RIGcHsUpN5QISicysx7E",
                        "name": "__mirascope_formatted_output_tool__",
                        "type": "function_call",
                        "id": "fc_0c5b5f1dd1eb58fc0068e70550d7b08197969e7cdf769164d4",
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
                        text="Please look up the book with ISBN 0-7653-1178-X and provide detailed info and a recommendation score"
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    ToolCall(
                        id="call_dcok8XE3eK4y1IWtu0KghoJ8",
                        name="get_book_info",
                        args='{"isbn":"0-7653-1178-X"}',
                    )
                ],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "arguments": '{"isbn":"0-7653-1178-X"}',
                        "call_id": "call_dcok8XE3eK4y1IWtu0KghoJ8",
                        "name": "get_book_info",
                        "type": "function_call",
                        "id": "fc_087b9325d4505d3d0068e81643009c819483ad60ee223417c3",
                        "status": "completed",
                    }
                ],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="call_dcok8XE3eK4y1IWtu0KghoJ8",
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
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "arguments": '{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006}',
                        "call_id": "call_OMLtB8la9zGkBOeYHRNUhX8j",
                        "name": "__mirascope_formatted_output_tool__",
                        "type": "function_call",
                        "id": "fc_087b9325d4505d3d0068e8164431d48194a0c82b883b15ee5e",
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
                        text="Please look up the book with ISBN 0-7653-1178-X and provide detailed info and a recommendation score"
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    ToolCall(
                        id="call_adthpdoEAlfogiJjGHpHwLw5",
                        name="get_book_info",
                        args='{"isbn":"0-7653-1178-X"}',
                    )
                ],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "arguments": '{"isbn":"0-7653-1178-X"}',
                        "call_id": "call_adthpdoEAlfogiJjGHpHwLw5",
                        "name": "get_book_info",
                        "type": "function_call",
                        "id": "fc_033235db0a585c280068e81651da588196a5096f6e6a481867",
                        "status": "completed",
                    }
                ],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="call_adthpdoEAlfogiJjGHpHwLw5",
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
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "arguments": '{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006}',
                        "call_id": "call_OOFM9BSHJ3z2DT8qKOXEjCZz",
                        "name": "__mirascope_formatted_output_tool__",
                        "type": "function_call",
                        "id": "fc_033235db0a585c280068e816535cd481968a36dc2f48d15978",
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
)
