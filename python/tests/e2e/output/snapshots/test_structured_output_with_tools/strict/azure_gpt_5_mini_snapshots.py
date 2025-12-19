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
            "model_id": "azure/gpt-5-mini",
            "provider_model_name": "gpt-5-mini",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 286,
                "output_tokens": 937,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 896,
                "raw": "CompletionUsage(completion_tokens=937, prompt_tokens=286, total_tokens=1223, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=896, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0))",
                "total_tokens": 1223,
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
                            id="call_eMHppBGomIVD6e1nsd8vfAG0",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider_id="azure",
                    model_id="azure/gpt-5-mini",
                    provider_model_name="gpt-5-mini",
                    raw_message={
                        "role": "assistant",
                        "annotations": [],
                        "tool_calls": [
                            {
                                "id": "call_eMHppBGomIVD6e1nsd8vfAG0",
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
                            id="call_eMHppBGomIVD6e1nsd8vfAG0",
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
                    provider_id="azure",
                    model_id="azure/gpt-5-mini",
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
                    "strict": False,
                }
            ],
        }
    }
)
async_snapshot = snapshot(
    {
        "response": {
            "provider_id": "azure",
            "model_id": "azure/gpt-5-mini",
            "provider_model_name": "gpt-5-mini",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 286,
                "output_tokens": 11832,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 640,
                "raw": "CompletionUsage(completion_tokens=11832, prompt_tokens=286, total_tokens=12118, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=640, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0))",
                "total_tokens": 12118,
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
                            id="call_5KF0HJRRZJXe9GxXvG8b9WFk",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider_id="azure",
                    model_id="azure/gpt-5-mini",
                    provider_model_name="gpt-5-mini",
                    raw_message={
                        "role": "assistant",
                        "annotations": [],
                        "tool_calls": [
                            {
                                "id": "call_5KF0HJRRZJXe9GxXvG8b9WFk",
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
                            id="call_5KF0HJRRZJXe9GxXvG8b9WFk",
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
\r



\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r

























































\r

\r

\r
\r

\r
\r
\r

\r
\r
\r

\r
\r
\r

\r
\r
\r

\r
\r
\r

\r
\r
\r
\r

\r
\r
\r

\r
\r
\r

\r
\r
\r
\r

\r
\r
\r

\r
\r
\r

\r
\r
\r
\r
\r
\r
\r
\r

\r
\r
\r

\r
\r
\r

\r
\r
\r

\r
\r
\r

\r
\r
\r

\r
\r
\r

\r
\r
\r

\r
\r
\r

\r
\r
\r

\r
\r
\r

\r
\r
\r

\r
\r
\r
\r

\r
\r
\r
\r


\r





\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r
\r
\r


\r




\r




\r




\r
\r
\r




\r







\r




\r
\r
\r
\r




\r







\r
\r
\r




\r







\r
\r
\r




\r







\r
\r
\r




\r







\r
\r
\r




\r







\r
\r
\r




\r







\r
\r
\r




\r







\r
\r
\r




\r







\r
\r
\r




\r







\r
\r
\r




\r







\r
\r
\r




\r







\r
\r
\r




\r







\r
\r
\r




\r







\r
\r
\r




\r







\r
\r
\r




\r







\r
\r
\r




\r







\r
\r
\r




"""
                        )
                    ],
                    provider_id="azure",
                    model_id="azure/gpt-5-mini",
                    provider_model_name="gpt-5-mini",
                    raw_message={
                        "content": """\
{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006} \n\

 \n\
\r



\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r

























































\r

\r

\r
\r

\r
\r
\r

\r
\r
\r

\r
\r
\r

\r
\r
\r

\r
\r
\r

\r
\r
\r
\r

\r
\r
\r

\r
\r
\r

\r
\r
\r
\r

\r
\r
\r

\r
\r
\r

\r
\r
\r
\r
\r
\r
\r
\r

\r
\r
\r

\r
\r
\r

\r
\r
\r

\r
\r
\r

\r
\r
\r

\r
\r
\r

\r
\r
\r

\r
\r
\r

\r
\r
\r

\r
\r
\r

\r
\r
\r

\r
\r
\r
\r

\r
\r
\r
\r


\r





\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r




\r
\r
\r


\r




\r




\r




\r
\r
\r




\r







\r




\r
\r
\r
\r




\r







\r
\r
\r




\r







\r
\r
\r




\r







\r
\r
\r




\r







\r
\r
\r




\r







\r
\r
\r




\r







\r
\r
\r




\r







\r
\r
\r




\r







\r
\r
\r




\r







\r
\r
\r




\r







\r
\r
\r




\r







\r
\r
\r




\r







\r
\r
\r




\r







\r
\r
\r




\r







\r
\r
\r




\r







\r
\r
\r




\r







\r
\r
\r




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
                    "strict": False,
                }
            ],
        }
    }
)
stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "azure",
            "model_id": "azure/gpt-5-mini",
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
                            id="call_DneOGmaERuEYIuqAsOUOk978",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider_id="azure",
                    model_id="azure/gpt-5-mini",
                    provider_model_name="gpt-5-mini",
                    raw_message=None,
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_DneOGmaERuEYIuqAsOUOk978",
                            name="get_book_info",
                            value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006}
 \n\




























































































































































































































































































































"""
                        )
                    ],
                    provider_id="azure",
                    model_id="azure/gpt-5-mini",
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
                    "strict": False,
                }
            ],
            "usage": {
                "input_tokens": 286,
                "output_tokens": 985,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 640,
                "raw": "None",
                "total_tokens": 1271,
            },
            "n_chunks": 333,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "azure",
            "model_id": "azure/gpt-5-mini",
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
                            id="call_c4CzWM4dWYAnmdPyROkxfATe",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider_id="azure",
                    model_id="azure/gpt-5-mini",
                    provider_model_name="gpt-5-mini",
                    raw_message=None,
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_c4CzWM4dWYAnmdPyROkxfATe",
                            name="get_book_info",
                            value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
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




  \n\
  \n\
  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\










  \n\
  \n\




  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\



  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\




  \n\
  \n\










  \n\
  \n\




  \n\
  \n\





  \n\
  \n\



  \n\




  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\





  \n\
  \n\










  \n\
  \n\





  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\






  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\










  \n\
  \n\





  \n\
  \n\





  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\










  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\










  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\










  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\






  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\




  \n\
  \n\





  \n\
  \n\

  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\




  \n\
  \n\





  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\






  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\






  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\










  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\






  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\










  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\




    \n\
    \n\




    \n\
 \n\




  \n\
  \n\




  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\

  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\






  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\






  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\






  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\






  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\




  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\










  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\
  \n\
  \n\




  \n\




  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\






  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\



  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\
  \n\
  \n\




  \n\




  \n\
  \n\




  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\










  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\



  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\




 \n\






 \n\
 \n\
 \n\





 \n\
 \n\





 \n\
 \n\



 \n\




 \n\

 \n\
 \n\
 \n\













 \n\







 \n\
 \n\







 \n\
 \n\













 \n\





 \n\



 \n\




 \n\












 \n\

 \n\
 \n\
 \n\











 \n\
 \n\
 \n\





 \n\








 \n\












 \n\







 \n\
 \n\


 \n\


 \n\


 \n\





 \n\


 \n\








 \n\












 \n\
 \n\
 \n\
 \n\
 \n\






 \n\












 \n\








 \n\


 \n\















 \n\








 \n\











 \n\


 \n\



 \n\


 \n\











 \n\












 \n\


 \n\












 \n\











 \n\












 \n\











 \n\








 \n\















 \n\




















 \n\











 \n\








 \n\
 \n\






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
  \n\





  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\










  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\






 \n\
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
                    model_id="azure/gpt-5-mini",
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
                    "strict": False,
                }
            ],
            "usage": {
                "input_tokens": 286,
                "output_tokens": 5118,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 640,
                "raw": "None",
                "total_tokens": 5404,
            },
            "n_chunks": 4457,
        }
    }
)
