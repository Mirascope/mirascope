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
            "provider_id": "bedrock",
            "model_id": "bedrock/us.anthropic.claude-haiku-4-5-20251001-v1:0",
            "provider_model_name": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 968,
                "output_tokens": 109,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "Usage(cache_creation=CacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=968, output_tokens=109, server_tool_use=None, service_tier=None)",
                "total_tokens": 1077,
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
                            id="toolu_bdrk_01Vmvxcpu3EWo3FEZo1XnWV4",
                            name="get_book_info",
                            args='{"isbn": "0-7653-1178-X"}',
                        )
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    provider_model_name="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "id": "toolu_bdrk_01Vmvxcpu3EWo3FEZo1XnWV4",
                                "input": {"isbn": "0-7653-1178-X"},
                                "name": "get_book_info",
                                "type": "tool_use",
                            }
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="toolu_bdrk_01Vmvxcpu3EWo3FEZo1XnWV4",
                            name="get_book_info",
                            result="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text='{"title": "Mistborn: The Final Empire", "author": "Brandon Sanderson", "pages": 544, "publication_year": 2006}'
                        )
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    provider_model_name="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "id": "toolu_bdrk_01V6wyPHhTJ1e5amxidWxp8t",
                                "input": {
                                    "title": "Mistborn: The Final Empire",
                                    "author": "Brandon Sanderson",
                                    "pages": 544,
                                    "publication_year": 2006,
                                },
                                "name": "__mirascope_formatted_output_tool__",
                                "type": "tool_use",
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
                    "strict": None,
                }
            ],
        }
    }
)
async_snapshot = snapshot(
    {
        "response": {
            "provider_id": "bedrock",
            "model_id": "bedrock/us.anthropic.claude-haiku-4-5-20251001-v1:0",
            "provider_model_name": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 968,
                "output_tokens": 109,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "Usage(cache_creation=CacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=968, output_tokens=109, server_tool_use=None, service_tier=None)",
                "total_tokens": 1077,
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
                            id="toolu_bdrk_015QXSCqf6pKn8Zj2Ez4mj92",
                            name="get_book_info",
                            args='{"isbn": "0-7653-1178-X"}',
                        )
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    provider_model_name="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "id": "toolu_bdrk_015QXSCqf6pKn8Zj2Ez4mj92",
                                "input": {"isbn": "0-7653-1178-X"},
                                "name": "get_book_info",
                                "type": "tool_use",
                            }
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="toolu_bdrk_015QXSCqf6pKn8Zj2Ez4mj92",
                            name="get_book_info",
                            result="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text='{"title": "Mistborn: The Final Empire", "author": "Brandon Sanderson", "pages": 544, "publication_year": 2006}'
                        )
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    provider_model_name="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "id": "toolu_bdrk_01AcCCAbEaukJwoZUx3cPj1Y",
                                "input": {
                                    "title": "Mistborn: The Final Empire",
                                    "author": "Brandon Sanderson",
                                    "pages": 544,
                                    "publication_year": 2006,
                                },
                                "name": "__mirascope_formatted_output_tool__",
                                "type": "tool_use",
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
                    "strict": None,
                }
            ],
        }
    }
)
stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "bedrock",
            "model_id": "bedrock/us.anthropic.claude-haiku-4-5-20251001-v1:0",
            "provider_model_name": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
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
                            id="toolu_bdrk_011bhoCbUCBKC6DdzbruGpSu",
                            name="get_book_info",
                            args='{"isbn": "0-7653-1178-X"}',
                        )
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    provider_model_name="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "tool_use",
                                "id": "toolu_bdrk_011bhoCbUCBKC6DdzbruGpSu",
                                "name": "get_book_info",
                                "input": {"isbn": "0-7653-1178-X"},
                            }
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="toolu_bdrk_011bhoCbUCBKC6DdzbruGpSu",
                            name="get_book_info",
                            result="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text='{"title": "Mistborn: The Final Empire", "author": "Brandon Sanderson", "pages": 544, "publication_year": 2006}'
                        )
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    provider_model_name="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "tool_use",
                                "id": "toolu_bdrk_01PSiESec4vjeXQ3NsEQjqVP",
                                "name": "__mirascope_formatted_output_tool__",
                                "input": {
                                    "title": "Mistborn: The Final Empire",
                                    "author": "Brandon Sanderson",
                                    "pages": 544,
                                    "publication_year": 2006,
                                },
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
                    "strict": None,
                }
            ],
            "usage": {
                "input_tokens": 0,
                "output_tokens": 109,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 109,
            },
            "n_chunks": 19,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "bedrock",
            "model_id": "bedrock/us.anthropic.claude-haiku-4-5-20251001-v1:0",
            "provider_model_name": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
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
                            id="toolu_bdrk_01TVheWLxTxaBmvHVaJQnPjT",
                            name="get_book_info",
                            args='{"isbn": "0-7653-1178-X"}',
                        )
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    provider_model_name="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "tool_use",
                                "id": "toolu_bdrk_01TVheWLxTxaBmvHVaJQnPjT",
                                "name": "get_book_info",
                                "input": {"isbn": "0-7653-1178-X"},
                            }
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="toolu_bdrk_01TVheWLxTxaBmvHVaJQnPjT",
                            name="get_book_info",
                            result="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text='{"title": "Mistborn: The Final Empire", "author": "Brandon Sanderson", "pages": 544, "publication_year": 2006}'
                        )
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    provider_model_name="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "tool_use",
                                "id": "toolu_bdrk_01UcPp2vKiMMyJwHXStoyZX5",
                                "name": "__mirascope_formatted_output_tool__",
                                "input": {
                                    "title": "Mistborn: The Final Empire",
                                    "author": "Brandon Sanderson",
                                    "pages": 544,
                                    "publication_year": 2006,
                                },
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
                    "strict": None,
                }
            ],
            "usage": {
                "input_tokens": 0,
                "output_tokens": 109,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 109,
            },
            "n_chunks": 20,
        }
    }
)
