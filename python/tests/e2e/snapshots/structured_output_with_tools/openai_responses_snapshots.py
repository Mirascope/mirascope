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
                        id="call_Inw3vIMJki73wnVMOrcQHLiP",
                        name="get_book_info",
                        args='{"isbn":"0-7653-1178-X"}',
                    )
                ],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "arguments": '{"isbn":"0-7653-1178-X"}',
                        "call_id": "call_Inw3vIMJki73wnVMOrcQHLiP",
                        "name": "get_book_info",
                        "type": "function_call",
                        "id": "fc_06a3cb3c81526f470068e70544c2fc81979c2fdee6c9dcc4c3",
                        "status": "completed",
                    }
                ],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="call_Inw3vIMJki73wnVMOrcQHLiP",
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
                        "id": "msg_06a3cb3c81526f470068e70545e5a081978a01a165f92a0456",
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
)
async_snapshot = snapshot(
    {
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
                        id="call_pLaC9KO0zPOgGuV0xn1nd0CN",
                        name="get_book_info",
                        args='{"isbn":"0-7653-1178-X"}',
                    )
                ],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "arguments": '{"isbn":"0-7653-1178-X"}',
                        "call_id": "call_pLaC9KO0zPOgGuV0xn1nd0CN",
                        "name": "get_book_info",
                        "type": "function_call",
                        "id": "fc_0c07ba056a2a9dd40068e7055251008190a14ce05b5017b921",
                        "status": "completed",
                    }
                ],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="call_pLaC9KO0zPOgGuV0xn1nd0CN",
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
                raw_content=[
                    {
                        "id": "msg_0c07ba056a2a9dd40068e7055338c48190b18b876e72bd12ab",
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
                        "id": "msg_0c07ba056a2a9dd40068e70553d98881909255faa9c0ae751f",
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
)
stream_snapshot = snapshot(
    {
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
                        id="call_qQuw4DYict4f0qC4SJZvbxW7",
                        name="get_book_info",
                        args='{"isbn":"0-7653-1178-X"}',
                    )
                ],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "arguments": '{"isbn":"0-7653-1178-X"}',
                        "call_id": "call_qQuw4DYict4f0qC4SJZvbxW7",
                        "name": "get_book_info",
                        "type": "function_call",
                        "id": "fc_0b6f4d67e35f13710068e8164588a48196b8d672a9d3a891ea",
                        "status": "completed",
                    }
                ],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="call_qQuw4DYict4f0qC4SJZvbxW7",
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
                raw_content=[
                    {
                        "id": "msg_0b6f4d67e35f13710068e8164693fc8196a1818058517c0c53",
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
                        "id": "msg_0b6f4d67e35f13710068e816475e3081968466113a8e201788",
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
        "n_chunks": 58,
    }
)
async_stream_snapshot = snapshot(
    {
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
                        id="call_3a5qsyGWGTXnZ8TGAHQtxwp7",
                        name="get_book_info",
                        args='{"isbn":"0-7653-1178-X"}',
                    )
                ],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "arguments": '{"isbn":"0-7653-1178-X"}',
                        "call_id": "call_3a5qsyGWGTXnZ8TGAHQtxwp7",
                        "name": "get_book_info",
                        "type": "function_call",
                        "id": "fc_04e8582c477966980068e8165546788197b48b31d1d5262640",
                        "status": "completed",
                    }
                ],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="call_3a5qsyGWGTXnZ8TGAHQtxwp7",
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
                raw_content=[
                    {
                        "id": "msg_04e8582c477966980068e81656b77c8197b23a58b5ecb0a212",
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
                        "id": "msg_04e8582c477966980068e816579ff08197883a2363743c3f8e",
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
        "n_chunks": 58,
    }
)
