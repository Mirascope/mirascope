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
                            id="call_tK7VDRPOKuy20I2ixdsRlNUj",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "arguments": '{"isbn":"0-7653-1178-X"}',
                            "call_id": "call_tK7VDRPOKuy20I2ixdsRlNUj",
                            "name": "get_book_info",
                            "type": "function_call",
                            "id": "fc_047bc6c5bd74166b00690ac639dd48819097dc6ba246e32ec3",
                            "status": "completed",
                        }
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_tK7VDRPOKuy20I2ixdsRlNUj",
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
                            "id": "msg_0dce55e6e248483800690ac63b08ec8195a193a50278244a6a",
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
                            id="call_NW3qDN1IGSWQMZsDxslT2V4m",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "arguments": '{"isbn":"0-7653-1178-X"}',
                            "call_id": "call_NW3qDN1IGSWQMZsDxslT2V4m",
                            "name": "get_book_info",
                            "type": "function_call",
                            "id": "fc_053dab074dbc8c0a00690ac6470f308193a67e59d02c1b6edb",
                            "status": "completed",
                        }
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_NW3qDN1IGSWQMZsDxslT2V4m",
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
                            "id": "msg_001d1f2bf06d0fa400690ac6484eb48190adb21f126a83afa4",
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
                            id="call_l3W4ZmcSWu5wY4Mdg9FXkiow",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "arguments": '{"isbn":"0-7653-1178-X"}',
                            "call_id": "call_l3W4ZmcSWu5wY4Mdg9FXkiow",
                            "name": "get_book_info",
                            "type": "function_call",
                            "id": "fc_0919b9ddf7913d5100690ac6567d40819687ed2d863cb548c4",
                            "status": "completed",
                        }
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_l3W4ZmcSWu5wY4Mdg9FXkiow",
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
                            "id": "msg_06ef637097342b1100690ac657d90081949b97fa043aabc146",
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
                            id="call_iOhepLqxYqN6NoKtStZqkFyi",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "arguments": '{"isbn":"0-7653-1178-X"}',
                            "call_id": "call_iOhepLqxYqN6NoKtStZqkFyi",
                            "name": "get_book_info",
                            "type": "function_call",
                            "id": "fc_048e8e9a0454492f00690ac663f32481978957d81fcae27f8c",
                            "status": "completed",
                        }
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_iOhepLqxYqN6NoKtStZqkFyi",
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

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

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

 \
"""
                        ),
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "id": "msg_0229adf74979ffa600690ac6654ad081909d64f5db56c3ca1c",
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
                            "id": "msg_0229adf74979ffa600690ac69fefac81909001e12782a4488a",
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
                            "id": "msg_0229adf74979ffa600690ac6c6f630819099dd03658344847e",
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
            "n_chunks": 1450,
        }
    }
)
