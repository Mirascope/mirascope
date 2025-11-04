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
                            id="call_Nmc3mZgWKNMgmmWdy9PV1x7i",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "arguments": '{"isbn":"0-7653-1178-X"}',
                            "call_id": "call_Nmc3mZgWKNMgmmWdy9PV1x7i",
                            "name": "get_book_info",
                            "type": "function_call",
                            "id": "fc_0a0a4703cc83f36c00690c221f24708193ac2977db7a9052dc",
                            "status": "completed",
                        }
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_Nmc3mZgWKNMgmmWdy9PV1x7i",
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



"""
                        )
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "id": "msg_04949f2ef3e29b3400690c222072e88193b8ae5d680320e80f",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006} \n\



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
                            id="call_GpdeIKUzgFDSfgvyTsHVqJL7",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "arguments": '{"isbn":"0-7653-1178-X"}',
                            "call_id": "call_GpdeIKUzgFDSfgvyTsHVqJL7",
                            "name": "get_book_info",
                            "type": "function_call",
                            "id": "fc_0e6d470903ec138d00690c2254a3a48196887fde4b8f25c9cc",
                            "status": "completed",
                        }
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_GpdeIKUzgFDSfgvyTsHVqJL7",
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
                            "id": "msg_01ee124f3e8cb8df00690c2255c06881979e2cdc203ab398f9",
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
                            id="call_h1pdM8cQrvlSBe9RFQ7m6LHK",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "arguments": '{"isbn":"0-7653-1178-X"}',
                            "call_id": "call_h1pdM8cQrvlSBe9RFQ7m6LHK",
                            "name": "get_book_info",
                            "type": "function_call",
                            "id": "fc_0b76bb72c7c277f800690c22c976f481908cef42cf54cec78a",
                            "status": "completed",
                        }
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_h1pdM8cQrvlSBe9RFQ7m6LHK",
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

 \
"""
                        )
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "id": "msg_023cf4f2cffb503b00690c22caa6588197871e096183c6c42a",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006} \n\

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
            "n_chunks": 32,
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
                            id="call_rFC6RTPaBJMdqL0QWHbJvggP",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "arguments": '{"isbn":"0-7653-1178-X"}',
                            "call_id": "call_rFC6RTPaBJMdqL0QWHbJvggP",
                            "name": "get_book_info",
                            "type": "function_call",
                            "id": "fc_0deafaffa94b8c7400690c23a0562c8197bf240f1e79b45275",
                            "status": "completed",
                        }
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_rFC6RTPaBJMdqL0QWHbJvggP",
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

 \n\

   \n\

   \n\
 \n\

   \n\

 \n\

 \n\

   \n\

 \n\

   \n\

 \n\

 \n\

 \n\

   \n\

 \n\

   \n\

 \n\

   \n\

 \n\

   \n\

 \n\

    \n\

  \n\

 \n\

   \n\

 \n\

   \n\

 \n\

   \n\

   \n\

 \n\

   \n\

   \n\

   \n\


   \n\

  \n\

  \n\

  \n\

  \n\

  \n\

  \n\

  \n\

   \n\
 \n\

 \n\

 \n\

 \n\

   \n\

 \n\

   \n\

  \n\

 \n\

  \n\

 \n\

  \n\

   \n\

 \n\

   \n\

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
                        )
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "id": "msg_0dd00f6e57c7128c00690c23a1bee081909b6af43a798c2d9a",
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
            "n_chunks": 698,
        }
    }
)
