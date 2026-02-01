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
            "provider_id": "azure",
            "model_id": "azure/openai/gpt-5-mini",
            "provider_model_name": "gpt-5-mini",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 286,
                "output_tokens": 12260,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 704,
                "raw": "CompletionUsage(completion_tokens=12260, prompt_tokens=286, total_tokens=12546, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=704, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0))",
                "total_tokens": 12546,
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
                            id="call_KP7g79w6dZJG8snXRwqTnq91",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider_id="azure",
                    model_id="azure/openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini",
                    raw_message={
                        "role": "assistant",
                        "annotations": [],
                        "tool_calls": [
                            {
                                "id": "call_KP7g79w6dZJG8snXRwqTnq91",
                                "function": {
                                    "arguments": '{"isbn":"0-7653-1178-X"}',
                                    "name": "get_book_info",
                                },
                                "type": "function",
                            }
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_KP7g79w6dZJG8snXRwqTnq91",
                            name="get_book_info",
                            result="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006} \n\




"""
                        )
                    ],
                    provider_id="azure",
                    model_id="azure/openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini",
                    raw_message={
                        "content": """\
{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006} \n\




""",
                        "role": "assistant",
                        "annotations": [],
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
                    "strict": None,
                }
            ],
        }
    }
)
async_snapshot = snapshot(
    {
        "response": {
            "provider_id": "azure",
            "model_id": "azure/openai/gpt-5-mini",
            "provider_model_name": "gpt-5-mini",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 286,
                "output_tokens": 809,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 768,
                "raw": "CompletionUsage(completion_tokens=809, prompt_tokens=286, total_tokens=1095, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=768, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0))",
                "total_tokens": 1095,
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
                            id="call_jsqRUuiKfVZg0SbH149Nmqbm",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider_id="azure",
                    model_id="azure/openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini",
                    raw_message={
                        "role": "assistant",
                        "annotations": [],
                        "tool_calls": [
                            {
                                "id": "call_jsqRUuiKfVZg0SbH149Nmqbm",
                                "function": {
                                    "arguments": '{"isbn":"0-7653-1178-X"}',
                                    "name": "get_book_info",
                                },
                                "type": "function",
                            }
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_jsqRUuiKfVZg0SbH149Nmqbm",
                            name="get_book_info",
                            result="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text='{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006}'
                        )
                    ],
                    provider_id="azure",
                    model_id="azure/openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini",
                    raw_message={
                        "content": '{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006}',
                        "role": "assistant",
                        "annotations": [],
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
                    "strict": None,
                }
            ],
        }
    }
)
stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "azure",
            "model_id": "azure/openai/gpt-5-mini",
            "provider_model_name": "gpt-5-mini",
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
                            id="call_8qeGGxk8awCFrLPBaQGGeJ8j",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider_id="azure",
                    model_id="azure/openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini",
                    raw_message=None,
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_8qeGGxk8awCFrLPBaQGGeJ8j",
                            name="get_book_info",
                            result="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006}
  \n\
  \r

    \n\
  \n\
  \n\
  \r

  \n\
 \n\



{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006}
{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006}\
"""
                        )
                    ],
                    provider_id="azure",
                    model_id="azure/openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini",
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
                    "strict": None,
                }
            ],
            "usage": {
                "input_tokens": 286,
                "output_tokens": 897,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 768,
                "raw": "None",
                "total_tokens": 1183,
            },
            "n_chunks": 99,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "azure",
            "model_id": "azure/openai/gpt-5-mini",
            "provider_model_name": "gpt-5-mini",
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
                            id="call_wZTzgmyOk80XpQ6F45PsVArN",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider_id="azure",
                    model_id="azure/openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini",
                    raw_message=None,
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_wZTzgmyOk80XpQ6F45PsVArN",
                            name="get_book_info",
                            result="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006}
 \n\






 \n\

 \n\
 \n\
 \n\
 \n\
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
                        )
                    ],
                    provider_id="azure",
                    model_id="azure/openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini",
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
                    "strict": None,
                }
            ],
            "usage": {
                "input_tokens": 286,
                "output_tokens": 986,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 704,
                "raw": "None",
                "total_tokens": 1272,
            },
            "n_chunks": 270,
        }
    }
)
