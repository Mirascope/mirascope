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
            "provider": "azure-openai:responses",
            "model_id": "gpt-4o-mini",
            "params": {},
            "finish_reason": None,
            "messages": [
                SystemMessage(
                    content=Text(
                        text="""\
Respond only with valid JSON that matches this exact schema:
{
  "properties": {
    "title": {
      "title": "Title",
      "type": "string"
    },
    "author": {
      "title": "Author",
      "type": "string"
    },
    "pages": {
      "title": "Pages",
      "type": "integer"
    },
    "publication_year": {
      "title": "Publication Year",
      "type": "integer"
    }
  },
  "required": [
    "title",
    "author",
    "pages",
    "publication_year"
  ],
  "title": "BookSummary",
  "type": "object"
}\
"""
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
                            id="call_ylql1fDIgrMiRwIYyhBYcfc5",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "arguments": '{"isbn":"0-7653-1178-X"}',
                            "call_id": "call_ylql1fDIgrMiRwIYyhBYcfc5",
                            "name": "get_book_info",
                            "type": "function_call",
                            "id": "fc_08bead234466cf8900690c2212a4388197975877442ae1ef5e",
                            "status": "completed",
                        }
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_ylql1fDIgrMiRwIYyhBYcfc5",
                            name="get_book_info",
                            value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}\
"""
                        )
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "id": "msg_0d4b79a9fa8ccd8300690c2213b8ac8195bc3d34cfe28a8a56",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}\
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
                "mode": "json",
                "formatting_instructions": """\
Respond only with valid JSON that matches this exact schema:
{
  "properties": {
    "title": {
      "title": "Title",
      "type": "string"
    },
    "author": {
      "title": "Author",
      "type": "string"
    },
    "pages": {
      "title": "Pages",
      "type": "integer"
    },
    "publication_year": {
      "title": "Publication Year",
      "type": "integer"
    }
  },
  "required": [
    "title",
    "author",
    "pages",
    "publication_year"
  ],
  "title": "BookSummary",
  "type": "object"
}\
""",
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
                SystemMessage(
                    content=Text(
                        text="""\
Respond only with valid JSON that matches this exact schema:
{
  "properties": {
    "title": {
      "title": "Title",
      "type": "string"
    },
    "author": {
      "title": "Author",
      "type": "string"
    },
    "pages": {
      "title": "Pages",
      "type": "integer"
    },
    "publication_year": {
      "title": "Publication Year",
      "type": "integer"
    }
  },
  "required": [
    "title",
    "author",
    "pages",
    "publication_year"
  ],
  "title": "BookSummary",
  "type": "object"
}\
"""
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
                            id="call_k8kHGZMW3rXvvJF1Tq3WsfDE",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "arguments": '{"isbn":"0-7653-1178-X"}',
                            "call_id": "call_k8kHGZMW3rXvvJF1Tq3WsfDE",
                            "name": "get_book_info",
                            "type": "function_call",
                            "id": "fc_0ebfb6c1736f3dae00690c2246505081978e0b9beb297df49a",
                            "status": "completed",
                        }
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_k8kHGZMW3rXvvJF1Tq3WsfDE",
                            name="get_book_info",
                            value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}\
"""
                        )
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "id": "msg_01b398d5b43a02a800690c224762848194927e9791dfe3e816",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}\
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
                "mode": "json",
                "formatting_instructions": """\
Respond only with valid JSON that matches this exact schema:
{
  "properties": {
    "title": {
      "title": "Title",
      "type": "string"
    },
    "author": {
      "title": "Author",
      "type": "string"
    },
    "pages": {
      "title": "Pages",
      "type": "integer"
    },
    "publication_year": {
      "title": "Publication Year",
      "type": "integer"
    }
  },
  "required": [
    "title",
    "author",
    "pages",
    "publication_year"
  ],
  "title": "BookSummary",
  "type": "object"
}\
""",
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
                SystemMessage(
                    content=Text(
                        text="""\
Respond only with valid JSON that matches this exact schema:
{
  "properties": {
    "title": {
      "title": "Title",
      "type": "string"
    },
    "author": {
      "title": "Author",
      "type": "string"
    },
    "pages": {
      "title": "Pages",
      "type": "integer"
    },
    "publication_year": {
      "title": "Publication Year",
      "type": "integer"
    }
  },
  "required": [
    "title",
    "author",
    "pages",
    "publication_year"
  ],
  "title": "BookSummary",
  "type": "object"
}\
"""
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
                            id="call_nvWswFGKVpYZOvRS0Z18YmfZ",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "arguments": '{"isbn":"0-7653-1178-X"}',
                            "call_id": "call_nvWswFGKVpYZOvRS0Z18YmfZ",
                            "name": "get_book_info",
                            "type": "function_call",
                            "id": "fc_0b18a46c988d44a600690c22c012f08196ad6ffca214d4e820",
                            "status": "completed",
                        }
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_nvWswFGKVpYZOvRS0Z18YmfZ",
                            name="get_book_info",
                            value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}\
"""
                        )
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "id": "msg_09d7ed2eaed74fce00690c22c0fefc8196889cf4fba077e8bb",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}\
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
                "mode": "json",
                "formatting_instructions": """\
Respond only with valid JSON that matches this exact schema:
{
  "properties": {
    "title": {
      "title": "Title",
      "type": "string"
    },
    "author": {
      "title": "Author",
      "type": "string"
    },
    "pages": {
      "title": "Pages",
      "type": "integer"
    },
    "publication_year": {
      "title": "Publication Year",
      "type": "integer"
    }
  },
  "required": [
    "title",
    "author",
    "pages",
    "publication_year"
  ],
  "title": "BookSummary",
  "type": "object"
}\
""",
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
            "n_chunks": 42,
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
                SystemMessage(
                    content=Text(
                        text="""\
Respond only with valid JSON that matches this exact schema:
{
  "properties": {
    "title": {
      "title": "Title",
      "type": "string"
    },
    "author": {
      "title": "Author",
      "type": "string"
    },
    "pages": {
      "title": "Pages",
      "type": "integer"
    },
    "publication_year": {
      "title": "Publication Year",
      "type": "integer"
    }
  },
  "required": [
    "title",
    "author",
    "pages",
    "publication_year"
  ],
  "title": "BookSummary",
  "type": "object"
}\
"""
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
                            id="call_qyw755M45MIASQZRa9O3B9HJ",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "arguments": '{"isbn":"0-7653-1178-X"}',
                            "call_id": "call_qyw755M45MIASQZRa9O3B9HJ",
                            "name": "get_book_info",
                            "type": "function_call",
                            "id": "fc_07987e5e4dabd10000690c238514148197b070bfe86d06d402",
                            "status": "completed",
                        }
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_qyw755M45MIASQZRa9O3B9HJ",
                            name="get_book_info",
                            value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}\
"""
                        )
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "id": "msg_076fe7632dc1849900690c23860fb48194b403fdb9c04c369a",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}\
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
                "mode": "json",
                "formatting_instructions": """\
Respond only with valid JSON that matches this exact schema:
{
  "properties": {
    "title": {
      "title": "Title",
      "type": "string"
    },
    "author": {
      "title": "Author",
      "type": "string"
    },
    "pages": {
      "title": "Pages",
      "type": "integer"
    },
    "publication_year": {
      "title": "Publication Year",
      "type": "integer"
    }
  },
  "required": [
    "title",
    "author",
    "pages",
    "publication_year"
  ],
  "title": "BookSummary",
  "type": "object"
}\
""",
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
            "n_chunks": 42,
        }
    }
)
