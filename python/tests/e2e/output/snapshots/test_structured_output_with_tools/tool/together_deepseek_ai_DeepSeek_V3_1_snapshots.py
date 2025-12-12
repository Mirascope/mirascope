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
            "provider_id": "together",
            "model_id": "together/deepseek-ai/DeepSeek-V3.1",
            "provider_model_name": "deepseek-ai/DeepSeek-V3.1",
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
                            id="call_20d4a086df414fe891686363",
                            name="get_book_info",
                            args='{"isbn": "0-7653-1178-X"}',
                        )
                    ],
                    provider_id="together",
                    model_id="together/deepseek-ai/DeepSeek-V3.1",
                    provider_model_name="deepseek-ai/DeepSeek-V3.1",
                    raw_message={
                        "role": "assistant",
                        "content": "",
                        "tool_calls": [
                            {
                                "id": "call_20d4a086df414fe891686363",
                                "type": "function",
                                "function": {
                                    "name": "get_book_info",
                                    "arguments": '{"isbn": "0-7653-1178-X"}',
                                },
                                "index": -1,
                            }
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_20d4a086df414fe891686363",
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
                    provider_id="together",
                    model_id="together/deepseek-ai/DeepSeek-V3.1",
                    provider_model_name="deepseek-ai/DeepSeek-V3.1",
                    raw_message={
                        "role": "assistant",
                        "content": "",
                        "tool_calls": [
                            {
                                "id": "call_11a6958eb75748f2bf497020",
                                "type": "function",
                                "function": {
                                    "name": "__mirascope_formatted_output_tool__",
                                    "arguments": '{"title": "Mistborn: The Final Empire", "author": "Brandon Sanderson", "pages": 544, "publication_year": 2006}',
                                },
                                "index": -1,
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
            "provider_id": "together",
            "model_id": "together/deepseek-ai/DeepSeek-V3.1",
            "provider_model_name": "deepseek-ai/DeepSeek-V3.1",
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
                        Text(
                            text="I'll look up that book for you using the ISBN you provided."
                        ),
                        ToolCall(
                            id="call_ede395c17d324cd0bb9e3462",
                            name="get_book_info",
                            args='{"isbn": "0-7653-1178-X"}',
                        ),
                    ],
                    provider_id="together",
                    model_id="together/deepseek-ai/DeepSeek-V3.1",
                    provider_model_name="deepseek-ai/DeepSeek-V3.1",
                    raw_message={
                        "role": "assistant",
                        "content": "I'll look up that book for you using the ISBN you provided.",
                        "tool_calls": [
                            {
                                "id": "call_ede395c17d324cd0bb9e3462",
                                "type": "function",
                                "function": {
                                    "name": "get_book_info",
                                    "arguments": '{"isbn": "0-7653-1178-X"}',
                                },
                                "index": -1,
                            }
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_ede395c17d324cd0bb9e3462",
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
                    provider_id="together",
                    model_id="together/deepseek-ai/DeepSeek-V3.1",
                    provider_model_name="deepseek-ai/DeepSeek-V3.1",
                    raw_message={
                        "role": "assistant",
                        "content": "",
                        "tool_calls": [
                            {
                                "id": "call_54a9ddf0ec724bbebbc39022",
                                "type": "function",
                                "function": {
                                    "name": "__mirascope_formatted_output_tool__",
                                    "arguments": '{"title": "Mistborn: The Final Empire", "author": "Brandon Sanderson", "pages": 544, "publication_year": 2006}',
                                },
                                "index": -1,
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
            "provider": "together",
            "model_id": "together/deepseek-ai/DeepSeek-V3.1",
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
                        Text(
                            text="I'll look up the book with ISBN 0-7653-1178-X for you."
                        ),
                        ToolCall(
                            id="call_68717d20a62643bb8074c615",
                            name="get_book_info",
                            args='{"isbn": "0-7653-1178-X"}',
                        ),
                    ],
                    provider_id="together",
                    model_id="together/deepseek-ai/DeepSeek-V3.1",
                    provider_model_name="deepseek-ai/DeepSeek-V3.1",
                    raw_message=None,
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_68717d20a62643bb8074c615",
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
                    provider_id="together",
                    model_id="together/deepseek-ai/DeepSeek-V3.1",
                    provider_model_name="deepseek-ai/DeepSeek-V3.1",
                    raw_message=None,
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
            "n_chunks": 12,
        }
    }
)
async_stream_snapshot = snapshot()
