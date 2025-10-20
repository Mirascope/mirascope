from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    ToolCall,
    ToolOutput,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "response": {
            "provider": "openai:responses",
            "model_id": "gpt-4o",
            "params": {},
            "finish_reason": None,
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
                            id="call_x62FJoHImWtl4XlNg7pnd9ij",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider="openai:responses",
                    model_id="gpt-4o",
                    raw_message=[
                        {
                            "arguments": '{"isbn":"0-7653-1178-X"}',
                            "call_id": "call_x62FJoHImWtl4XlNg7pnd9ij",
                            "name": "get_book_info",
                            "type": "function_call",
                            "id": "fc_0d500ed14dac8aa80068f2a2e557908193b64700c248f9c141",
                            "status": "completed",
                        }
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_x62FJoHImWtl4XlNg7pnd9ij",
                            name="get_book_info",
                            value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text='{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006}'
                        ),
                        Text(
                            text='{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006}'
                        ),
                    ],
                    provider="openai:responses",
                    model_id="gpt-4o",
                    raw_message=[
                        {
                            "id": "msg_0d500ed14dac8aa80068f2a2e6e1548193b7400b1814b04b63",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": '{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006}',
                                    "type": "output_text",
                                    "logprobs": [],
                                }
                            ],
                            "role": "assistant",
                            "status": "completed",
                            "type": "message",
                        },
                        {
                            "id": "msg_0d500ed14dac8aa80068f2a2e786b48193bb24b214c4aff119",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": '{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006}',
                                    "type": "output_text",
                                    "logprobs": [],
                                }
                            ],
                            "role": "assistant",
                            "status": "completed",
                            "type": "message",
                        },
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
    }
)
async_snapshot = snapshot(
    {
        "response": {
            "provider": "openai:responses",
            "model_id": "gpt-4o",
            "params": {},
            "finish_reason": None,
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
                            id="call_7o69tE63kjgocyseJ6O998CX",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider="openai:responses",
                    model_id="gpt-4o",
                    raw_message=[
                        {
                            "arguments": '{"isbn":"0-7653-1178-X"}',
                            "call_id": "call_7o69tE63kjgocyseJ6O998CX",
                            "name": "get_book_info",
                            "type": "function_call",
                            "id": "fc_0b882f93e8d7f1170068f2a3227cbc81969eacfc9dbd503923",
                            "status": "completed",
                        }
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_7o69tE63kjgocyseJ6O998CX",
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
                    raw_message=[
                        {
                            "id": "msg_0b882f93e8d7f1170068f2a323bf008196ba1d0a1f4d3ba6be",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": '{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006}',
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
    }
)
stream_snapshot = snapshot(
    {
        "response": {
            "provider": "openai:responses",
            "model_id": "gpt-4o",
            "finish_reason": None,
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
                            id="call_IxugtwYIfPlbKHwZyyt9jQ3A",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider="openai:responses",
                    model_id="gpt-4o",
                    raw_message=[
                        {
                            "arguments": '{"isbn":"0-7653-1178-X"}',
                            "call_id": "call_IxugtwYIfPlbKHwZyyt9jQ3A",
                            "name": "get_book_info",
                            "type": "function_call",
                            "id": "fc_0b43fb0f4bd678710068f2a357d2348196bf435e544d71d71d",
                            "status": "completed",
                        }
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_IxugtwYIfPlbKHwZyyt9jQ3A",
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
                    raw_message=[
                        {
                            "id": "msg_0b43fb0f4bd678710068f2a359c0608196bf9ee0484f43f7b3",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": '{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006}',
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
            "n_chunks": 29,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider": "openai:responses",
            "model_id": "gpt-4o",
            "finish_reason": None,
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
                            id="call_WQ2jLlhFv3DjImp8sd8BfGHE",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider="openai:responses",
                    model_id="gpt-4o",
                    raw_message=[
                        {
                            "arguments": '{"isbn":"0-7653-1178-X"}',
                            "call_id": "call_WQ2jLlhFv3DjImp8sd8BfGHE",
                            "name": "get_book_info",
                            "type": "function_call",
                            "id": "fc_003bcb20887d7f890068f2a38e9a5c81938921dfb7c2fc2183",
                            "status": "completed",
                        }
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_WQ2jLlhFv3DjImp8sd8BfGHE",
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
                    raw_message=[
                        {
                            "id": "msg_003bcb20887d7f890068f2a390560081938c96429f36f9e3be",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": '{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006}',
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
            "n_chunks": 29,
        }
    }
)
