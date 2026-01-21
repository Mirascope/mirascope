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
            "provider_id": "openai",
            "model_id": "openai/gpt-5-mini",
            "provider_model_name": "gpt-5-mini:responses",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 327,
                "output_tokens": 47,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "ResponseUsage(input_tokens=327, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=47, output_tokens_details=OutputTokensDetails(reasoning_tokens=0), total_tokens=374)",
                "total_tokens": 374,
            },
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
                            id="call_iEqaUc2wWOMk1mGjF4PTVY8X",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini:responses",
                    raw_message=[
                        {
                            "id": "rs_036e8194829a9a000069492ee745e08193a1dd2295251e669b",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "arguments": '{"isbn":"0-7653-1178-X"}',
                            "call_id": "call_iEqaUc2wWOMk1mGjF4PTVY8X",
                            "name": "get_book_info",
                            "type": "function_call",
                            "id": "fc_036e8194829a9a000069492ee8748081938f419a79f53dd5eb",
                            "status": "completed",
                        },
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_iEqaUc2wWOMk1mGjF4PTVY8X",
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
                            "arguments": '{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006}',
                            "call_id": "call_VWNTUGve8nuo5aZC1z2YIZc1",
                            "name": "__mirascope_formatted_output_tool__",
                            "type": "function_call",
                            "id": "fc_036e8194829a9a000069492eeb5f8081939edd7894fb32efa9",
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
            "provider_id": "openai",
            "model_id": "openai/gpt-5-mini",
            "provider_model_name": "gpt-5-mini:responses",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 447,
                "output_tokens": 433,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 384,
                "raw": "ResponseUsage(input_tokens=447, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=433, output_tokens_details=OutputTokensDetails(reasoning_tokens=384), total_tokens=880)",
                "total_tokens": 880,
            },
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
                            id="call_jYaVyjxdoGQubNMHZHtzN5wS",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini:responses",
                    raw_message=[
                        {
                            "id": "rs_000f030ddf7019ee0069492f11e8bc819398ffe337708074f7",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "arguments": '{"isbn":"0-7653-1178-X"}',
                            "call_id": "call_jYaVyjxdoGQubNMHZHtzN5wS",
                            "name": "get_book_info",
                            "type": "function_call",
                            "id": "fc_000f030ddf7019ee0069492f14a2e08193b7ac60352c135cc3",
                            "status": "completed",
                        },
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_jYaVyjxdoGQubNMHZHtzN5wS",
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
                            "id": "rs_000f030ddf7019ee0069492f161674819393b10ac40dee4b7a",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "arguments": '{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006}',
                            "call_id": "call_LKXSRLMtfGD7gfRNacV1L1Nt",
                            "name": "__mirascope_formatted_output_tool__",
                            "type": "function_call",
                            "id": "fc_000f030ddf7019ee0069492f1b652c819390ec8ab5318f2cf9",
                            "status": "completed",
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
            "provider_id": "openai",
            "model_id": "openai/gpt-5-mini",
            "provider_model_name": "gpt-5-mini:responses",
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
                            id="call_Ncy6QjCCWlKWhq3ST9rli9bg",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini:responses",
                    raw_message=[
                        {
                            "id": "rs_0e25d3ddb0c105930069492f4040288190aec1da21ff21ee9e",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "arguments": '{"isbn":"0-7653-1178-X"}',
                            "call_id": "call_Ncy6QjCCWlKWhq3ST9rli9bg",
                            "name": "get_book_info",
                            "type": "function_call",
                            "id": "fc_0e25d3ddb0c105930069492f4a21d0819096a2310c8852e2ae",
                            "status": "completed",
                        },
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_Ncy6QjCCWlKWhq3ST9rli9bg",
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
                            "id": "rs_0e25d3ddb0c105930069492f4baf1081908e349b4d4e6bd978",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "arguments": '{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006}',
                            "call_id": "call_DvLS2Iwl8KvI04YO5bgNlsp0",
                            "name": "__mirascope_formatted_output_tool__",
                            "type": "function_call",
                            "id": "fc_0e25d3ddb0c105930069492f4eb34881908ef4f08234c9b659",
                            "status": "completed",
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
            "usage": {
                "input_tokens": 1015,
                "output_tokens": 241,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 192,
                "raw": "None",
                "total_tokens": 1256,
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
                            id="call_cCbtYgAKJ4cMUD3EtKoHzNn8",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini:responses",
                    raw_message=[
                        {
                            "id": "rs_00e3e0abdde604d60069492f7369b08197b35328b3d5cc95cb",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "arguments": '{"isbn":"0-7653-1178-X"}',
                            "call_id": "call_cCbtYgAKJ4cMUD3EtKoHzNn8",
                            "name": "get_book_info",
                            "type": "function_call",
                            "id": "fc_00e3e0abdde604d60069492f78eb7c81978d4cf90abb8919e8",
                            "status": "completed",
                        },
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_cCbtYgAKJ4cMUD3EtKoHzNn8",
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
                            "id": "rs_00e3e0abdde604d60069492f79fdb08197a12e81bafc70feb7",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "arguments": '{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006}',
                            "call_id": "call_1HGbDuaOi86arTzzCKD0uCgd",
                            "name": "__mirascope_formatted_output_tool__",
                            "type": "function_call",
                            "id": "fc_00e3e0abdde604d60069492f801b348197b2f7a0d514d94eac",
                            "status": "completed",
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
            "usage": {
                "input_tokens": 751,
                "output_tokens": 497,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 448,
                "raw": "None",
                "total_tokens": 1248,
            },
            "n_chunks": 29,
        }
    }
)
