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
            "provider": "openai:responses",
            "model_id": "gpt-4o",
            "params": {},
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
                    provider="openai:responses",
                    model_id="gpt-4o",
                    raw_message=[
                        {
                            "id": "msg_05dc1affd4c2e1a70068f2a20f37a48196a31e941a28eb5801",
                            "content": [
                                {
                                    "annotations": [],
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
            "provider": "openai:responses",
            "model_id": "gpt-4o",
            "params": {},
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
                    provider="openai:responses",
                    model_id="gpt-4o",
                    raw_message=[
                        {
                            "id": "msg_01d989b385e7efe30068f2a22af958819090d76fe43d042bf6",
                            "content": [
                                {
                                    "annotations": [],
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
            "provider": "openai:responses",
            "model_id": "gpt-4o",
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
                    provider="openai:responses",
                    model_id="gpt-4o",
                    raw_message=[
                        {
                            "id": "msg_067340a8a7e35f8c0068f2a250234c8190bd8f3120538c1b1d",
                            "content": [
                                {
                                    "annotations": [],
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
            "n_chunks": 48,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider": "openai:responses",
            "model_id": "gpt-4o",
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
                    provider="openai:responses",
                    model_id="gpt-4o",
                    raw_message=[
                        {
                            "id": "msg_0d25d69e230eec080068f2a26b0a30819782b7b8ca95defbc3",
                            "content": [
                                {
                                    "annotations": [],
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
            "n_chunks": 48,
        }
    }
)
