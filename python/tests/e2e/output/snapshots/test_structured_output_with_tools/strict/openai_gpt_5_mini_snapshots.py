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
            "provider_id": "openai",
            "model_id": "openai/gpt-5-mini",
            "provider_model_name": "gpt-5-mini:responses",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 274,
                "output_tokens": 741,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 704,
                "raw": "ResponseUsage(input_tokens=274, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=741, output_tokens_details=OutputTokensDetails(reasoning_tokens=704), total_tokens=1015)",
                "total_tokens": 1015,
            },
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
                            id="call_N6FByDeVDnfY9NnRdFvTG6Te",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini:responses",
                    raw_message=[
                        {
                            "id": "rs_001703d35b32a5c30069492eceb2348193a0317e8d8bbf261c",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "arguments": '{"isbn":"0-7653-1178-X"}',
                            "call_id": "call_N6FByDeVDnfY9NnRdFvTG6Te",
                            "name": "get_book_info",
                            "type": "function_call",
                            "id": "fc_001703d35b32a5c30069492ed1580c819380c36b4abd935bb9",
                            "status": "completed",
                        },
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_N6FByDeVDnfY9NnRdFvTG6Te",
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
                    provider_id="openai",
                    model_id="openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini:responses",
                    raw_message=[
                        {
                            "id": "rs_001703d35b32a5c30069492ed265188193a4cfbbf3d63b9d2d",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_001703d35b32a5c30069492edd21288193811cf42ec0eff360",
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
            "provider_id": "openai",
            "model_id": "openai/gpt-5-mini",
            "provider_model_name": "gpt-5-mini:responses",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 295,
                "output_tokens": 778,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 704,
                "raw": "ResponseUsage(input_tokens=295, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=778, output_tokens_details=OutputTokensDetails(reasoning_tokens=704), total_tokens=1073)",
                "total_tokens": 1073,
            },
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
                            id="call_ZEd4PzZlJeMWx17uzboBFriS",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini:responses",
                    raw_message=[
                        {
                            "id": "rs_06f2255021c598930069492efc11f08197b0f865ffd4a02e47",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "arguments": '{"isbn":"0-7653-1178-X"}',
                            "call_id": "call_ZEd4PzZlJeMWx17uzboBFriS",
                            "name": "get_book_info",
                            "type": "function_call",
                            "id": "fc_06f2255021c598930069492efe3be881979133d2e0aaf82492",
                            "status": "completed",
                        },
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_ZEd4PzZlJeMWx17uzboBFriS",
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
                    provider_id="openai",
                    model_id="openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini:responses",
                    raw_message=[
                        {
                            "id": "rs_06f2255021c598930069492eff36688197a128fc1f5d18be95",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_06f2255021c598930069492f0911e08197bc5425087f7bc19d",
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
                            "id": "msg_06f2255021c598930069492f09918c8197ae9a5d1f4c5515c6",
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
stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "openai",
            "model_id": "openai/gpt-5-mini",
            "provider_model_name": "gpt-5-mini:responses",
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
                            id="call_9SQFiTSfXVlIxpSBo5qfBw6h",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini:responses",
                    raw_message=[
                        {
                            "id": "rs_0bf6b46b944b41640069492f2b4708819386b4c31ed6af2e46",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "arguments": '{"isbn":"0-7653-1178-X"}',
                            "call_id": "call_9SQFiTSfXVlIxpSBo5qfBw6h",
                            "name": "get_book_info",
                            "type": "function_call",
                            "id": "fc_0bf6b46b944b41640069492f3125f881939aaa3a4f0483d64b",
                            "status": "completed",
                        },
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_9SQFiTSfXVlIxpSBo5qfBw6h",
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
                    provider_id="openai",
                    model_id="openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini:responses",
                    raw_message=[
                        {
                            "id": "rs_0bf6b46b944b41640069492f3229a48193b67e81dd0793cd59",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_0bf6b46b944b41640069492f375cdc81939952c2e41aec0466",
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
            "usage": {
                "input_tokens": 631,
                "output_tokens": 421,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 384,
                "raw": "None",
                "total_tokens": 1052,
            },
            "n_chunks": 29,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "openai",
            "model_id": "openai/gpt-5-mini",
            "provider_model_name": "gpt-5-mini:responses",
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
                            id="call_sxjqy7H69iHi3N2ejSXl7PF4",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini:responses",
                    raw_message=[
                        {
                            "id": "rs_0b5ffc931f67f2060069492f60fba481958ace11c5922da08e",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "arguments": '{"isbn":"0-7653-1178-X"}',
                            "call_id": "call_sxjqy7H69iHi3N2ejSXl7PF4",
                            "name": "get_book_info",
                            "type": "function_call",
                            "id": "fc_0b5ffc931f67f2060069492f61b40081958ae073014a682d5e",
                            "status": "completed",
                        },
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_sxjqy7H69iHi3N2ejSXl7PF4",
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
                    provider_id="openai",
                    model_id="openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini:responses",
                    raw_message=[
                        {
                            "id": "rs_0b5ffc931f67f2060069492f62b5d08195b2bf7f7ce851ebee",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_0b5ffc931f67f2060069492f6c148c8195b15a39c482c3f983",
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
            "usage": {
                "input_tokens": 264,
                "output_tokens": 933,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 896,
                "raw": "None",
                "total_tokens": 1197,
            },
            "n_chunks": 29,
        }
    }
)
