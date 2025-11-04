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
            "provider": "azure-openai:responses",
            "model_id": "gpt-4o-mini",
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
                            id="call_ILYYAT1b5ZZdj7xChEl8Vjts",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "arguments": '{"isbn":"0-7653-1178-X"}',
                            "call_id": "call_ILYYAT1b5ZZdj7xChEl8Vjts",
                            "name": "get_book_info",
                            "type": "function_call",
                            "id": "fc_0f59dca76a9bcf3400690ac6439f0c81908be66bab52239721",
                            "status": "completed",
                        }
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_ILYYAT1b5ZZdj7xChEl8Vjts",
                            name="get_book_info",
                            value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006} \n\

   \n\
   \n\
   \n\
  \
"""
                        )
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "id": "msg_0a888f69b5295c2900690ac644b7408197829071e75f34a5a9",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006} \n\

   \n\
   \n\
   \n\
  \
""",
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
async_snapshot = snapshot(
    {
        "response": {
            "provider": "azure-openai:responses",
            "model_id": "gpt-4o-mini",
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
                            id="call_IBQPN6jbciIVtwoDm3tExmDm",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "arguments": '{"isbn":"0-7653-1178-X"}',
                            "call_id": "call_IBQPN6jbciIVtwoDm3tExmDm",
                            "name": "get_book_info",
                            "type": "function_call",
                            "id": "fc_0c90562db458b99c00690ac65319448196a8fcc9c2f0fba7b5",
                            "status": "completed",
                        }
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_IBQPN6jbciIVtwoDm3tExmDm",
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
                            "id": "msg_01e7e4994ba41bde00690ac65468f48193b3c9668ea2bf9958",
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
            "provider": "azure-openai:responses",
            "model_id": "gpt-4o-mini",
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
                            id="call_LDIseXrPKnkC5eAxK51fTZZG",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "arguments": '{"isbn":"0-7653-1178-X"}',
                            "call_id": "call_LDIseXrPKnkC5eAxK51fTZZG",
                            "name": "get_book_info",
                            "type": "function_call",
                            "id": "fc_054d0ea2deda040100690ac65fef6c8193bef0a6f8b91bbcd9",
                            "status": "completed",
                        }
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_LDIseXrPKnkC5eAxK51fTZZG",
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
                            "id": "msg_029b6ee2a9e9608d00690ac661349081979250171050c5674d",
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
            "provider": "azure-openai:responses",
            "model_id": "gpt-4o-mini",
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
                            id="call_ATOFWHHBVM6KWKyW1ABCEYk5",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "arguments": '{"isbn":"0-7653-1178-X"}',
                            "call_id": "call_ATOFWHHBVM6KWKyW1ABCEYk5",
                            "name": "get_book_info",
                            "type": "function_call",
                            "id": "fc_0e1d121ef68fb62300690ac6d379c48197a47ba5a6b1cb47d0",
                            "status": "completed",
                        }
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_ATOFWHHBVM6KWKyW1ABCEYk5",
                            name="get_book_info",
                            value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006}  \n\

  \n\
  \n\
  \n\
  \n\
  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
"""
                        ),
                        Text(
                            text="""\
{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006} \n\

 \n\

  \n\
  \n\

  \n\
   \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\
  \n\
  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

   \n\
  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

   \n\
   \n\
  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

   \n\
  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

   \n\
  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

   \n\
  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

   \n\
  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

   \n\
  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

   \n\
  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\


 \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

   \n\
  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\




  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

   \n\
  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

   \n\
  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

 \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

   \n\
  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \
"""
                        ),
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "id": "msg_0f476aeb06add9db00690ac6d4988c8196bd126906edc7f991",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006}  \n\

  \n\
  \n\
  \n\
  \n\
  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
""",
                                    "type": "output_text",
                                    "logprobs": [],
                                }
                            ],
                            "role": "assistant",
                            "status": "completed",
                            "type": "message",
                        },
                        {
                            "id": "msg_0f476aeb06add9db00690ac6f367148196b3889825ed5c21b8",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006} \n\

 \n\

  \n\
  \n\

  \n\
   \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\
  \n\
  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

   \n\
  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

   \n\
   \n\
  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

   \n\
  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

   \n\
  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

   \n\
  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

   \n\
  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

   \n\
  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

   \n\
  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\


 \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

   \n\
  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\




  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

   \n\
  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

   \n\
  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

 \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

   \n\
  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \
""",
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
            "n_chunks": 2520,
        }
    }
)
