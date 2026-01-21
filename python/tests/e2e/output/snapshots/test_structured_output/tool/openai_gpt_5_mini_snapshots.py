from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    SystemMessage,
    Text,
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
                "input_tokens": 159,
                "output_tokens": 371,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 320,
                "raw": "ResponseUsage(input_tokens=159, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=371, output_tokens_details=OutputTokensDetails(reasoning_tokens=320), total_tokens=530)",
                "total_tokens": 530,
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
                    provider_id="openai",
                    model_id="openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini:responses",
                    raw_message=[
                        {
                            "id": "rs_0b5b1162cd094a860069492e76f194819099ea6e9c4f3f1454",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "arguments": '{"title":"THE NAME OF THE WIND","author":{"first_name":"Patrick","last_name":"Rothfuss"},"rating":7}',
                            "call_id": "call_x4d2nXfDdNlffAJwGs6e1pUK",
                            "name": "__mirascope_formatted_output_tool__",
                            "type": "function_call",
                            "id": "fc_0b5b1162cd094a860069492e7abb348190a6d39223458019d1",
                            "status": "completed",
                        },
                    ],
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
                        }
                    },
                    "description": "A book with a rating. The title should be in all caps!",
                    "properties": {
                        "title": {"title": "Title", "type": "string"},
                        "author": {"$ref": "#/$defs/Author"},
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
                "mode": "tool",
                "formatting_instructions": "Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output.",
            },
            "tools": [],
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
                "input_tokens": 159,
                "output_tokens": 371,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 320,
                "raw": "ResponseUsage(input_tokens=159, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=371, output_tokens_details=OutputTokensDetails(reasoning_tokens=320), total_tokens=530)",
                "total_tokens": 530,
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
                    provider_id="openai",
                    model_id="openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini:responses",
                    raw_message=[
                        {
                            "id": "rs_0a0c0a70f59ebe410069492e8eb25c8196b8fe2a4b5b09ad6d",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "arguments": '{"title":"THE NAME OF THE WIND","author":{"first_name":"Patrick","last_name":"Rothfuss"},"rating":7}',
                            "call_id": "call_nxtlv8HquW81O9CaUbS75vvH",
                            "name": "__mirascope_formatted_output_tool__",
                            "type": "function_call",
                            "id": "fc_0a0c0a70f59ebe410069492e94ed4c8196ac94ecfab36d1449",
                            "status": "completed",
                        },
                    ],
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
                        }
                    },
                    "description": "A book with a rating. The title should be in all caps!",
                    "properties": {
                        "title": {"title": "Title", "type": "string"},
                        "author": {"$ref": "#/$defs/Author"},
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
                "mode": "tool",
                "formatting_instructions": "Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output.",
            },
            "tools": [],
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
                    provider_id="openai",
                    model_id="openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini:responses",
                    raw_message=[
                        {
                            "id": "rs_07ab68104920adf10069492ea70a748193b2b87eece877bee8",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "arguments": '{"title":"THE NAME OF THE WIND","author":{"first_name":"Patrick","last_name":"Rothfuss"},"rating":7}',
                            "call_id": "call_MfHmQ3iFygdsUyYETnWWfLq5",
                            "name": "__mirascope_formatted_output_tool__",
                            "type": "function_call",
                            "id": "fc_07ab68104920adf10069492eac25a08193a27fc6d22bb01886",
                            "status": "completed",
                        },
                    ],
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
                        }
                    },
                    "description": "A book with a rating. The title should be in all caps!",
                    "properties": {
                        "title": {"title": "Title", "type": "string"},
                        "author": {"$ref": "#/$defs/Author"},
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
                "mode": "tool",
                "formatting_instructions": "Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output.",
            },
            "tools": [],
            "usage": {
                "input_tokens": 159,
                "output_tokens": 371,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 320,
                "raw": "None",
                "total_tokens": 530,
            },
            "n_chunks": 31,
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
                    provider_id="openai",
                    model_id="openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini:responses",
                    raw_message=[
                        {
                            "id": "rs_0a0de582ceb78a9c0069492ebca1f08197a999eec8cbdf48c4",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "arguments": '{"title":"THE NAME OF THE WIND","author":{"first_name":"Patrick","last_name":"Rothfuss"},"rating":7}',
                            "call_id": "call_rl6UXd6z5Y4wCBO3btDD5939",
                            "name": "__mirascope_formatted_output_tool__",
                            "type": "function_call",
                            "id": "fc_0a0de582ceb78a9c0069492ec6885c81979d376392ee747bc3",
                            "status": "completed",
                        },
                    ],
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
                        }
                    },
                    "description": "A book with a rating. The title should be in all caps!",
                    "properties": {
                        "title": {"title": "Title", "type": "string"},
                        "author": {"$ref": "#/$defs/Author"},
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
                "mode": "tool",
                "formatting_instructions": "Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output.",
            },
            "tools": [],
            "usage": {
                "input_tokens": 159,
                "output_tokens": 563,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 512,
                "raw": "None",
                "total_tokens": 722,
            },
            "n_chunks": 31,
        }
    }
)
