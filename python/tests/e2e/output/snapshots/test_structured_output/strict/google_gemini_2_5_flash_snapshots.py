from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "response": {
            "provider_id": "google",
            "model_id": "google/gemini-2.5-flash",
            "provider_model_name": "gemini-2.5-flash",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 11,
                "output_tokens": 256,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 227,
                "provider_tool_usage": None,
                "raw": """\
cache_tokens_details=None cached_content_token_count=None candidates_token_count=29 candidates_tokens_details=None prompt_token_count=11 prompt_tokens_details=[ModalityTokenCount(
  modality=<MediaModality.TEXT: 'TEXT'>,
  token_count=11
)] thoughts_token_count=227 tool_use_prompt_token_count=None tool_use_prompt_tokens_details=None total_token_count=267 traffic_type=None\
""",
                "total_tokens": 267,
            },
            "messages": [
                UserMessage(
                    content=[
                        Text(
                            text="Please recommend the most popular book by Patrick Rothfuss"
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text='{"title":"THE NAME OF THE WIND","author":{"first_name":"Patrick","last_name":"Rothfuss"},"rating":7}'
                        )
                    ],
                    provider_id="google",
                    model_id="google/gemini-2.5-flash",
                    provider_model_name="gemini-2.5-flash",
                    raw_message={
                        "parts": [
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": '{"title":"THE NAME OF THE WIND","author":{"first_name":"Patrick","last_name":"Rothfuss"},"rating":7}',
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            }
                        ],
                        "role": "model",
                    },
                ),
            ],
            "format": {
                "name": "Book",
                "description": "A book with a rating. The title should be in all caps!",
                "schema": {
                    "$defs": {
                        "Author": {
                            "description": "The author of a book.",
                            "properties": {
                                "first_name": {"title": "First Name", "type": "string"},
                                "last_name": {"title": "Last Name", "type": "string"},
                            },
                            "required": ["first_name", "last_name"],
                            "title": "Author",
                            "type": "object",
                            "propertyOrdering": ["first_name", "last_name"],
                        }
                    },
                    "description": "A book with a rating. The title should be in all caps!",
                    "properties": {
                        "title": {"title": "Title", "type": "string"},
                        "author": {
                            "description": "The author of a book.",
                            "properties": {
                                "first_name": {"title": "First Name", "type": "string"},
                                "last_name": {"title": "Last Name", "type": "string"},
                            },
                            "required": ["first_name", "last_name"],
                            "title": "Author",
                            "type": "object",
                            "propertyOrdering": ["first_name", "last_name"],
                        },
                        "rating": {
                            "description": "For testing purposes, the rating should be 7",
                            "title": "Rating",
                            "type": "integer",
                        },
                    },
                    "required": ["title", "author", "rating"],
                    "title": "Book",
                    "type": "object",
                },
                "mode": "strict",
                "formatting_instructions": None,
            },
            "tools": [],
        }
    }
)
async_snapshot = snapshot(
    {
        "response": {
            "provider_id": "google",
            "model_id": "google/gemini-2.5-flash",
            "provider_model_name": "gemini-2.5-flash",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 11,
                "output_tokens": 361,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 309,
                "provider_tool_usage": None,
                "raw": """\
cache_tokens_details=None cached_content_token_count=None candidates_token_count=52 candidates_tokens_details=None prompt_token_count=11 prompt_tokens_details=[ModalityTokenCount(
  modality=<MediaModality.TEXT: 'TEXT'>,
  token_count=11
)] thoughts_token_count=309 tool_use_prompt_token_count=None tool_use_prompt_tokens_details=None total_token_count=372 traffic_type=None\
""",
                "total_tokens": 372,
            },
            "messages": [
                UserMessage(
                    content=[
                        Text(
                            text="Please recommend the most popular book by Patrick Rothfuss"
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
{
  "title": "THE NAME OF THE WIND",
  "author": {
    "first_name": "Patrick",
    "last_name": "Rothfuss"
  },
  "rating": 7
}\
"""
                        )
                    ],
                    provider_id="google",
                    model_id="google/gemini-2.5-flash",
                    provider_model_name="gemini-2.5-flash",
                    raw_message={
                        "parts": [
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": """\
{
  "title": "THE NAME OF THE WIND",
  "author": {
    "first_name": "Patrick",
    "last_name": "Rothfuss"
  },
  "rating": 7
}\
""",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            }
                        ],
                        "role": "model",
                    },
                ),
            ],
            "format": {
                "name": "Book",
                "description": "A book with a rating. The title should be in all caps!",
                "schema": {
                    "$defs": {
                        "Author": {
                            "description": "The author of a book.",
                            "properties": {
                                "first_name": {"title": "First Name", "type": "string"},
                                "last_name": {"title": "Last Name", "type": "string"},
                            },
                            "required": ["first_name", "last_name"],
                            "title": "Author",
                            "type": "object",
                            "propertyOrdering": ["first_name", "last_name"],
                        }
                    },
                    "description": "A book with a rating. The title should be in all caps!",
                    "properties": {
                        "title": {"title": "Title", "type": "string"},
                        "author": {
                            "description": "The author of a book.",
                            "properties": {
                                "first_name": {"title": "First Name", "type": "string"},
                                "last_name": {"title": "Last Name", "type": "string"},
                            },
                            "required": ["first_name", "last_name"],
                            "title": "Author",
                            "type": "object",
                            "propertyOrdering": ["first_name", "last_name"],
                        },
                        "rating": {
                            "description": "For testing purposes, the rating should be 7",
                            "title": "Rating",
                            "type": "integer",
                        },
                    },
                    "required": ["title", "author", "rating"],
                    "title": "Book",
                    "type": "object",
                },
                "mode": "strict",
                "formatting_instructions": None,
            },
            "tools": [],
        }
    }
)
stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "google",
            "model_id": "google/gemini-2.5-flash",
            "provider_model_name": "gemini-2.5-flash",
            "finish_reason": None,
            "messages": [
                UserMessage(
                    content=[
                        Text(
                            text="Please recommend the most popular book by Patrick Rothfuss"
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text='{"title":"THE NAME OF THE WIND","author":{"first_name":"Patrick","last_name":"Rothfuss"},"rating":7}'
                        )
                    ],
                    provider_id="google",
                    model_id="google/gemini-2.5-flash",
                    provider_model_name="gemini-2.5-flash",
                    raw_message={
                        "parts": [
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": '{"title":"THE NAME OF THE WIND","author":{"first_name":"Patrick","last_name":"Rothfuss"},"rating":7}',
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            }
                        ],
                        "role": "model",
                    },
                ),
            ],
            "format": {
                "name": "Book",
                "description": "A book with a rating. The title should be in all caps!",
                "schema": {
                    "$defs": {
                        "Author": {
                            "description": "The author of a book.",
                            "properties": {
                                "first_name": {"title": "First Name", "type": "string"},
                                "last_name": {"title": "Last Name", "type": "string"},
                            },
                            "required": ["first_name", "last_name"],
                            "title": "Author",
                            "type": "object",
                            "propertyOrdering": ["first_name", "last_name"],
                        }
                    },
                    "description": "A book with a rating. The title should be in all caps!",
                    "properties": {
                        "title": {"title": "Title", "type": "string"},
                        "author": {
                            "description": "The author of a book.",
                            "properties": {
                                "first_name": {"title": "First Name", "type": "string"},
                                "last_name": {"title": "Last Name", "type": "string"},
                            },
                            "required": ["first_name", "last_name"],
                            "title": "Author",
                            "type": "object",
                            "propertyOrdering": ["first_name", "last_name"],
                        },
                        "rating": {
                            "description": "For testing purposes, the rating should be 7",
                            "title": "Rating",
                            "type": "integer",
                        },
                    },
                    "required": ["title", "author", "rating"],
                    "title": "Book",
                    "type": "object",
                },
                "mode": "strict",
                "formatting_instructions": None,
            },
            "tools": [],
            "usage": {
                "input_tokens": 11,
                "output_tokens": 29,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 264,
                "provider_tool_usage": None,
                "raw": "None",
                "total_tokens": 40,
            },
            "n_chunks": 3,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "google",
            "model_id": "google/gemini-2.5-flash",
            "provider_model_name": "gemini-2.5-flash",
            "finish_reason": None,
            "messages": [
                UserMessage(
                    content=[
                        Text(
                            text="Please recommend the most popular book by Patrick Rothfuss"
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text='{"title":"THE NAME OF THE WIND","author":{"first_name":"Patrick","last_name":"Rothfuss"},"rating":7}'
                        )
                    ],
                    provider_id="google",
                    model_id="google/gemini-2.5-flash",
                    provider_model_name="gemini-2.5-flash",
                    raw_message={
                        "parts": [
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": '{"title":"THE NAME OF THE WIND","author":{"first_name":"Patrick","last_name":"Rothfuss"},"rating":7}',
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            }
                        ],
                        "role": "model",
                    },
                ),
            ],
            "format": {
                "name": "Book",
                "description": "A book with a rating. The title should be in all caps!",
                "schema": {
                    "$defs": {
                        "Author": {
                            "description": "The author of a book.",
                            "properties": {
                                "first_name": {"title": "First Name", "type": "string"},
                                "last_name": {"title": "Last Name", "type": "string"},
                            },
                            "required": ["first_name", "last_name"],
                            "title": "Author",
                            "type": "object",
                            "propertyOrdering": ["first_name", "last_name"],
                        }
                    },
                    "description": "A book with a rating. The title should be in all caps!",
                    "properties": {
                        "title": {"title": "Title", "type": "string"},
                        "author": {
                            "description": "The author of a book.",
                            "properties": {
                                "first_name": {"title": "First Name", "type": "string"},
                                "last_name": {"title": "Last Name", "type": "string"},
                            },
                            "required": ["first_name", "last_name"],
                            "title": "Author",
                            "type": "object",
                            "propertyOrdering": ["first_name", "last_name"],
                        },
                        "rating": {
                            "description": "For testing purposes, the rating should be 7",
                            "title": "Rating",
                            "type": "integer",
                        },
                    },
                    "required": ["title", "author", "rating"],
                    "title": "Book",
                    "type": "object",
                },
                "mode": "strict",
                "formatting_instructions": None,
            },
            "tools": [],
            "usage": {
                "input_tokens": 11,
                "output_tokens": 29,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 212,
                "provider_tool_usage": None,
                "raw": "None",
                "total_tokens": 40,
            },
            "n_chunks": 3,
        }
    }
)
