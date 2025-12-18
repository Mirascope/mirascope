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
            "provider_id": "anthropic",
            "model_id": "anthropic/claude-sonnet-4-5",
            "provider_model_name": "claude-sonnet-4-5",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 884,
                "output_tokens": 300,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
            },
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
                            id="toolu_017ixfwjNEJtpg1bS3mUJVsf",
                            name="get_book_info",
                            args='{"isbn": "0-7653-1178-X"}',
                        )
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-5",
                    provider_model_name="claude-sonnet-4-5",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "id": "toolu_017ixfwjNEJtpg1bS3mUJVsf",
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
                            id="toolu_017ixfwjNEJtpg1bS3mUJVsf",
                            name="get_book_info",
                            value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
```json
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}
```

**Additional Information:**

"Mistborn: The Final Empire" is the first book in Brandon Sanderson's acclaimed Mistborn trilogy. This epic fantasy novel is set in a dystopian world where ash falls from the sky, and the nobility possess magical abilities called Allomancy - the ability to "burn" metals ingested in their bodies to gain superhuman powers.

The story follows Kelsier, a charismatic thief with extraordinary Allomantic abilities, and Vin, a young street urchin who discovers she has similar powers. Together, they plan an audacious heist to overthrow the seemingly immortal Lord Ruler who has dominated the world for a thousand years.

**Recommendation Score: 9/10**

This book is highly recommended for fans of:
- Complex magic systems with detailed rules
- Heist plots and strategic planning
- Strong character development
- Dark, atmospheric fantasy settings
- Epic world-building

The novel is particularly praised for its innovative magic system, compelling characters, and intricate plot twists. It's an excellent entry point for readers new to Brandon Sanderson's work.\
"""
                        )
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-5",
                    provider_model_name="claude-sonnet-4-5",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "citations": None,
                                "text": """\
```json
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}
```

**Additional Information:**

"Mistborn: The Final Empire" is the first book in Brandon Sanderson's acclaimed Mistborn trilogy. This epic fantasy novel is set in a dystopian world where ash falls from the sky, and the nobility possess magical abilities called Allomancy - the ability to "burn" metals ingested in their bodies to gain superhuman powers.

The story follows Kelsier, a charismatic thief with extraordinary Allomantic abilities, and Vin, a young street urchin who discovers she has similar powers. Together, they plan an audacious heist to overthrow the seemingly immortal Lord Ruler who has dominated the world for a thousand years.

**Recommendation Score: 9/10**

This book is highly recommended for fans of:
- Complex magic systems with detailed rules
- Heist plots and strategic planning
- Strong character development
- Dark, atmospheric fantasy settings
- Epic world-building

The novel is particularly praised for its innovative magic system, compelling characters, and intricate plot twists. It's an excellent entry point for readers new to Brandon Sanderson's work.\
""",
                                "type": "text",
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
            "provider_id": "anthropic",
            "model_id": "anthropic/claude-sonnet-4-5",
            "provider_model_name": "claude-sonnet-4-5",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 884,
                "output_tokens": 220,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
            },
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
                            id="toolu_012Z6zYsjZLUdcUPBbkfyz9Y",
                            name="get_book_info",
                            args='{"isbn": "0-7653-1178-X"}',
                        )
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-5",
                    provider_model_name="claude-sonnet-4-5",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "id": "toolu_012Z6zYsjZLUdcUPBbkfyz9Y",
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
                            id="toolu_012Z6zYsjZLUdcUPBbkfyz9Y",
                            name="get_book_info",
                            value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
```json
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}
```

**Detailed Information:**

This is the first book in Brandon Sanderson's acclaimed Mistborn trilogy. Set in a dark fantasy world where ash falls from the sky and mists dominate the night, the story follows Vin, a street urchin who discovers she possesses powerful magical abilities. The magic system, called Allomancy, allows certain individuals to "burn" metals to gain superhuman powers.

**Recommendation Score: 9/10**

This book is highly recommended for fans of fantasy with unique magic systems, intricate plotting, and compelling characters. Sanderson is known for his detailed world-building and innovative approach to magic, and this book showcases both brilliantly. It's particularly great if you enjoy heist stories combined with epic fantasy elements.\
"""
                        )
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-5",
                    provider_model_name="claude-sonnet-4-5",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "citations": None,
                                "text": """\
```json
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}
```

**Detailed Information:**

This is the first book in Brandon Sanderson's acclaimed Mistborn trilogy. Set in a dark fantasy world where ash falls from the sky and mists dominate the night, the story follows Vin, a street urchin who discovers she possesses powerful magical abilities. The magic system, called Allomancy, allows certain individuals to "burn" metals to gain superhuman powers.

**Recommendation Score: 9/10**

This book is highly recommended for fans of fantasy with unique magic systems, intricate plotting, and compelling characters. Sanderson is known for his detailed world-building and innovative approach to magic, and this book showcases both brilliantly. It's particularly great if you enjoy heist stories combined with epic fantasy elements.\
""",
                                "type": "text",
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
            "provider": "anthropic",
            "model_id": "anthropic/claude-sonnet-4-5",
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
                        Text(
                            text="I'll look up the book information for ISBN 0-7653-1178-X."
                        ),
                        ToolCall(
                            id="toolu_01GRNUscW1x8wu9Zms9qbuke",
                            name="get_book_info",
                            args='{"isbn": "0-7653-1178-X"}',
                        ),
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-5",
                    provider_model_name="claude-sonnet-4-5",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "text",
                                "text": "I'll look up the book information for ISBN 0-7653-1178-X.",
                            },
                            {
                                "type": "tool_use",
                                "id": "toolu_01GRNUscW1x8wu9Zms9qbuke",
                                "name": "get_book_info",
                                "input": {"isbn": "0-7653-1178-X"},
                            },
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="toolu_01GRNUscW1x8wu9Zms9qbuke",
                            name="get_book_info",
                            value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Based on the book information retrieved, here is the detailed response:

```json
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}
```

**Additional Details & Recommendation:**

**Mistborn: The Final Empire** by Brandon Sanderson is the first book in the acclaimed Mistborn series. This epic fantasy novel is set in a world where ash falls from the sky, mists dominate the night, and the immortal Lord Ruler has reigned for a thousand years.

**Key Highlights:**
- **Innovative Magic System**: Features "Allomancy," where people can ingest and "burn" metals to gain supernatural powers
- **Heist Plot**: Combines epic fantasy with a clever heist storyline
- **Strong Characters**: Features memorable protagonist Vin and the charismatic thief Kelsier
- **World-building**: Rich, dark atmospheric setting with unique mechanics

**Recommendation Score: 9/10**

This book is highly recommended for:
- Fans of epic fantasy with unique magic systems
- Readers who enjoy heist narratives
- Those looking for well-developed characters and plot twists
- Brandon Sanderson fans (it's one of his most popular works)

The book is accessible to newcomers while offering depth for experienced fantasy readers. It's the perfect starting point for the Cosmere universe!\
"""
                        )
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-5",
                    provider_model_name="claude-sonnet-4-5",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "text",
                                "text": """\
Based on the book information retrieved, here is the detailed response:

```json
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}
```

**Additional Details & Recommendation:**

**Mistborn: The Final Empire** by Brandon Sanderson is the first book in the acclaimed Mistborn series. This epic fantasy novel is set in a world where ash falls from the sky, mists dominate the night, and the immortal Lord Ruler has reigned for a thousand years.

**Key Highlights:**
- **Innovative Magic System**: Features "Allomancy," where people can ingest and "burn" metals to gain supernatural powers
- **Heist Plot**: Combines epic fantasy with a clever heist storyline
- **Strong Characters**: Features memorable protagonist Vin and the charismatic thief Kelsier
- **World-building**: Rich, dark atmospheric setting with unique mechanics

**Recommendation Score: 9/10**

This book is highly recommended for:
- Fans of epic fantasy with unique magic systems
- Readers who enjoy heist narratives
- Those looking for well-developed characters and plot twists
- Brandon Sanderson fans (it's one of his most popular works)

The book is accessible to newcomers while offering depth for experienced fantasy readers. It's the perfect starting point for the Cosmere universe!\
""",
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
            "usage": {
                "input_tokens": 904,
                "output_tokens": 332,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
            },
            "n_chunks": 97,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider": "anthropic",
            "model_id": "anthropic/claude-sonnet-4-5",
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
                            id="toolu_016nrHmi6KDhtJ6F4Ax2pgG2",
                            name="get_book_info",
                            args='{"isbn": "0-7653-1178-X"}',
                        )
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-5",
                    provider_model_name="claude-sonnet-4-5",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "tool_use",
                                "id": "toolu_016nrHmi6KDhtJ6F4Ax2pgG2",
                                "name": "get_book_info",
                                "input": {"isbn": "0-7653-1178-X"},
                            }
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="toolu_016nrHmi6KDhtJ6F4Ax2pgG2",
                            name="get_book_info",
                            value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
```json
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}
```\
"""
                        )
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-5",
                    provider_model_name="claude-sonnet-4-5",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "text",
                                "text": """\
```json
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}
```\
""",
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
            "usage": {
                "input_tokens": 884,
                "output_tokens": 54,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
            },
            "n_chunks": 10,
        }
    }
)
