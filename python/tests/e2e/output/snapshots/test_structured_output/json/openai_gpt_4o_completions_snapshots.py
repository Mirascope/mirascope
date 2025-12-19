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
            "model_id": "openai/gpt-4o:completions",
            "provider_model_name": "gpt-4o:completions",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 278,
                "output_tokens": 46,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "CompletionUsage(completion_tokens=46, prompt_tokens=278, total_tokens=324, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=0, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0))",
                "total_tokens": 324,
            },
            "messages": [
                SystemMessage(
                    content=Text(
                        text="""\
Respond only with valid JSON that matches this exact schema:
{
  "$defs": {
    "Author": {
      "description": "The author of a book.",
      "properties": {
        "first_name": {
          "title": "First Name",
          "type": "string"
        },
        "last_name": {
          "title": "Last Name",
          "type": "string"
        }
      },
      "required": [
        "first_name",
        "last_name"
      ],
      "title": "Author",
      "type": "object"
    }
  },
  "description": "A book with a rating. The title should be in all caps!",
  "properties": {
    "title": {
      "title": "Title",
      "type": "string"
    },
    "author": {
      "$ref": "#/$defs/Author"
    },
    "rating": {
      "description": "For testing purposes, the rating should be 7",
      "title": "Rating",
      "type": "integer"
    }
  },
  "required": [
    "title",
    "author",
    "rating"
  ],
  "title": "Book",
  "type": "object"
}\
"""
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
                    provider_id="openai",
                    model_id="openai/gpt-4o:completions",
                    provider_model_name="gpt-4o:completions",
                    raw_message={
                        "content": """\
{
  "title": "THE NAME OF THE WIND",
  "author": {
    "first_name": "Patrick",
    "last_name": "Rothfuss"
  },
  "rating": 7
}\
""",
                        "role": "assistant",
                        "annotations": [],
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
                "mode": "json",
                "formatting_instructions": """\
Respond only with valid JSON that matches this exact schema:
{
  "$defs": {
    "Author": {
      "description": "The author of a book.",
      "properties": {
        "first_name": {
          "title": "First Name",
          "type": "string"
        },
        "last_name": {
          "title": "Last Name",
          "type": "string"
        }
      },
      "required": [
        "first_name",
        "last_name"
      ],
      "title": "Author",
      "type": "object"
    }
  },
  "description": "A book with a rating. The title should be in all caps!",
  "properties": {
    "title": {
      "title": "Title",
      "type": "string"
    },
    "author": {
      "$ref": "#/$defs/Author"
    },
    "rating": {
      "description": "For testing purposes, the rating should be 7",
      "title": "Rating",
      "type": "integer"
    }
  },
  "required": [
    "title",
    "author",
    "rating"
  ],
  "title": "Book",
  "type": "object"
}\
""",
            },
            "tools": [],
        }
    }
)
async_snapshot = snapshot(
    {
        "response": {
            "provider_id": "openai",
            "model_id": "openai/gpt-4o:completions",
            "provider_model_name": "gpt-4o:completions",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 278,
                "output_tokens": 46,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "CompletionUsage(completion_tokens=46, prompt_tokens=278, total_tokens=324, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=0, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0))",
                "total_tokens": 324,
            },
            "messages": [
                SystemMessage(
                    content=Text(
                        text="""\
Respond only with valid JSON that matches this exact schema:
{
  "$defs": {
    "Author": {
      "description": "The author of a book.",
      "properties": {
        "first_name": {
          "title": "First Name",
          "type": "string"
        },
        "last_name": {
          "title": "Last Name",
          "type": "string"
        }
      },
      "required": [
        "first_name",
        "last_name"
      ],
      "title": "Author",
      "type": "object"
    }
  },
  "description": "A book with a rating. The title should be in all caps!",
  "properties": {
    "title": {
      "title": "Title",
      "type": "string"
    },
    "author": {
      "$ref": "#/$defs/Author"
    },
    "rating": {
      "description": "For testing purposes, the rating should be 7",
      "title": "Rating",
      "type": "integer"
    }
  },
  "required": [
    "title",
    "author",
    "rating"
  ],
  "title": "Book",
  "type": "object"
}\
"""
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
                    provider_id="openai",
                    model_id="openai/gpt-4o:completions",
                    provider_model_name="gpt-4o:completions",
                    raw_message={
                        "content": """\
{
  "title": "THE NAME OF THE WIND",
  "author": {
    "first_name": "Patrick",
    "last_name": "Rothfuss"
  },
  "rating": 7
}\
""",
                        "role": "assistant",
                        "annotations": [],
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
                "mode": "json",
                "formatting_instructions": """\
Respond only with valid JSON that matches this exact schema:
{
  "$defs": {
    "Author": {
      "description": "The author of a book.",
      "properties": {
        "first_name": {
          "title": "First Name",
          "type": "string"
        },
        "last_name": {
          "title": "Last Name",
          "type": "string"
        }
      },
      "required": [
        "first_name",
        "last_name"
      ],
      "title": "Author",
      "type": "object"
    }
  },
  "description": "A book with a rating. The title should be in all caps!",
  "properties": {
    "title": {
      "title": "Title",
      "type": "string"
    },
    "author": {
      "$ref": "#/$defs/Author"
    },
    "rating": {
      "description": "For testing purposes, the rating should be 7",
      "title": "Rating",
      "type": "integer"
    }
  },
  "required": [
    "title",
    "author",
    "rating"
  ],
  "title": "Book",
  "type": "object"
}\
""",
            },
            "tools": [],
        }
    }
)
stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "openai",
            "provider_model_name": "gpt-4o:completions",
            "model_id": "openai/gpt-4o:completions",
            "finish_reason": None,
            "messages": [
                SystemMessage(
                    content=Text(
                        text="""\
Respond only with valid JSON that matches this exact schema:
{
  "$defs": {
    "Author": {
      "description": "The author of a book.",
      "properties": {
        "first_name": {
          "title": "First Name",
          "type": "string"
        },
        "last_name": {
          "title": "Last Name",
          "type": "string"
        }
      },
      "required": [
        "first_name",
        "last_name"
      ],
      "title": "Author",
      "type": "object"
    }
  },
  "description": "A book with a rating. The title should be in all caps!",
  "properties": {
    "title": {
      "title": "Title",
      "type": "string"
    },
    "author": {
      "$ref": "#/$defs/Author"
    },
    "rating": {
      "description": "For testing purposes, the rating should be 7",
      "title": "Rating",
      "type": "integer"
    }
  },
  "required": [
    "title",
    "author",
    "rating"
  ],
  "title": "Book",
  "type": "object"
}\
"""
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
                    provider_id="openai",
                    model_id="openai/gpt-4o:completions",
                    provider_model_name="gpt-4o:completions",
                    raw_message=None,
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
                "mode": "json",
                "formatting_instructions": """\
Respond only with valid JSON that matches this exact schema:
{
  "$defs": {
    "Author": {
      "description": "The author of a book.",
      "properties": {
        "first_name": {
          "title": "First Name",
          "type": "string"
        },
        "last_name": {
          "title": "Last Name",
          "type": "string"
        }
      },
      "required": [
        "first_name",
        "last_name"
      ],
      "title": "Author",
      "type": "object"
    }
  },
  "description": "A book with a rating. The title should be in all caps!",
  "properties": {
    "title": {
      "title": "Title",
      "type": "string"
    },
    "author": {
      "$ref": "#/$defs/Author"
    },
    "rating": {
      "description": "For testing purposes, the rating should be 7",
      "title": "Rating",
      "type": "integer"
    }
  },
  "required": [
    "title",
    "author",
    "rating"
  ],
  "title": "Book",
  "type": "object"
}\
""",
            },
            "tools": [],
            "usage": {
                "input_tokens": 278,
                "output_tokens": 46,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 324,
            },
            "n_chunks": 48,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "openai",
            "provider_model_name": "gpt-4o:completions",
            "model_id": "openai/gpt-4o:completions",
            "finish_reason": None,
            "messages": [
                SystemMessage(
                    content=Text(
                        text="""\
Respond only with valid JSON that matches this exact schema:
{
  "$defs": {
    "Author": {
      "description": "The author of a book.",
      "properties": {
        "first_name": {
          "title": "First Name",
          "type": "string"
        },
        "last_name": {
          "title": "Last Name",
          "type": "string"
        }
      },
      "required": [
        "first_name",
        "last_name"
      ],
      "title": "Author",
      "type": "object"
    }
  },
  "description": "A book with a rating. The title should be in all caps!",
  "properties": {
    "title": {
      "title": "Title",
      "type": "string"
    },
    "author": {
      "$ref": "#/$defs/Author"
    },
    "rating": {
      "description": "For testing purposes, the rating should be 7",
      "title": "Rating",
      "type": "integer"
    }
  },
  "required": [
    "title",
    "author",
    "rating"
  ],
  "title": "Book",
  "type": "object"
}\
"""
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
                    provider_id="openai",
                    model_id="openai/gpt-4o:completions",
                    provider_model_name="gpt-4o:completions",
                    raw_message=None,
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
                "mode": "json",
                "formatting_instructions": """\
Respond only with valid JSON that matches this exact schema:
{
  "$defs": {
    "Author": {
      "description": "The author of a book.",
      "properties": {
        "first_name": {
          "title": "First Name",
          "type": "string"
        },
        "last_name": {
          "title": "Last Name",
          "type": "string"
        }
      },
      "required": [
        "first_name",
        "last_name"
      ],
      "title": "Author",
      "type": "object"
    }
  },
  "description": "A book with a rating. The title should be in all caps!",
  "properties": {
    "title": {
      "title": "Title",
      "type": "string"
    },
    "author": {
      "$ref": "#/$defs/Author"
    },
    "rating": {
      "description": "For testing purposes, the rating should be 7",
      "title": "Rating",
      "type": "integer"
    }
  },
  "required": [
    "title",
    "author",
    "rating"
  ],
  "title": "Book",
  "type": "object"
}\
""",
            },
            "tools": [],
            "usage": {
                "input_tokens": 278,
                "output_tokens": 46,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 324,
            },
            "n_chunks": 48,
        }
    }
)
