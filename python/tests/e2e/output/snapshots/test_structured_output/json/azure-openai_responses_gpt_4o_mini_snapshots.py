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
                            "id": "msg_0b851f0696accd0300690c21bc6c188196bfd8bca0892a60d7",
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
                            "id": "msg_03155315ae5b2e0500690c21cb169c819382a23a469d51b66e",
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
                            "id": "msg_0db6a96090eebb2b00690c21e9257c8196960e0913d2517c67",
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
                            "id": "msg_082ab73ec75328b100690c21fabfa48197aa19c39231f048ac",
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
