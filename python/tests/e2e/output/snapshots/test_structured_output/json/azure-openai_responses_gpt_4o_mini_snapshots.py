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
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "id": "msg_079fbf85772bf00c00690a43789c108190ab2a358ee8962a70",
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
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "id": "msg_012ff9749036931c00690a4381858081978208602a301b46e6",
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
            "provider": "azure-openai:responses",
            "model_id": "gpt-4o-mini",
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
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "id": "msg_01e8fa7c7166153300690a4389c5848196b3f41722788821ce",
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
            "provider": "azure-openai:responses",
            "model_id": "gpt-4o-mini",
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
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "id": "msg_0a6795970002ad8800690a43936d48819790b93611cd9e8598",
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
