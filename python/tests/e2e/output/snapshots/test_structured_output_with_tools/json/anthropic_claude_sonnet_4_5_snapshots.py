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
                "output_tokens": 231,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "BetaUsage(cache_creation=BetaCacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=884, output_tokens=231, server_tool_use=None, service_tier='standard', inference_geo='not_available')",
                "total_tokens": 1115,
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
                            id="toolu_01F7Jn5SbxV7QB7Kgx9YDXHv",
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
                                "id": "toolu_01F7Jn5SbxV7QB7Kgx9YDXHv",
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
                            id="toolu_01F7Jn5SbxV7QB7Kgx9YDXHv",
                            name="get_book_info",
                            result="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Based on the book information retrieved, here is the response in the required format:

```json
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}
```

**Additional Information:**

*Mistborn: The Final Empire* is the first book in Brandon Sanderson's acclaimed Mistborn trilogy. This epic fantasy novel features a unique magic system based on metals and follows a street urchin named Vin who joins a crew attempting to overthrow the immortal Lord Ruler.

**Recommendation Score: 9/10**

This book is highly recommended for fans of:
- Complex, well-developed magic systems
- Heist storylines mixed with epic fantasy
- Strong character development
- Political intrigue and rebellion themes
- Brandon Sanderson's signature detailed world-building

The book has become a modern fantasy classic and is an excellent entry point into Sanderson's Cosmere universe.\
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
                                "text": """\
Based on the book information retrieved, here is the response in the required format:

```json
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}
```

**Additional Information:**

*Mistborn: The Final Empire* is the first book in Brandon Sanderson's acclaimed Mistborn trilogy. This epic fantasy novel features a unique magic system based on metals and follows a street urchin named Vin who joins a crew attempting to overthrow the immortal Lord Ruler.

**Recommendation Score: 9/10**

This book is highly recommended for fans of:
- Complex, well-developed magic systems
- Heist storylines mixed with epic fantasy
- Strong character development
- Political intrigue and rebellion themes
- Brandon Sanderson's signature detailed world-building

The book has become a modern fantasy classic and is an excellent entry point into Sanderson's Cosmere universe.\
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
                    "strict": None,
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
                "output_tokens": 293,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "BetaUsage(cache_creation=BetaCacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=884, output_tokens=293, server_tool_use=None, service_tier='standard', inference_geo='not_available')",
                "total_tokens": 1177,
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
                            id="toolu_01NhysLThit4TbG1A8hqEZPW",
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
                                "id": "toolu_01NhysLThit4TbG1A8hqEZPW",
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
                            id="toolu_01NhysLThit4TbG1A8hqEZPW",
                            name="get_book_info",
                            result="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
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

**Additional Details:**

"Mistborn: The Final Empire" is the first book in Brandon Sanderson's acclaimed Mistborn trilogy. This epic fantasy novel features a unique magic system based on "Allomancy" - the ability to ingest and "burn" metals to gain supernatural powers. The story follows Vin, a street thief who discovers she's a Mistborn (someone who can use all Allomantic metals), as she joins a crew of rebel skaa attempting to overthrow the immortal Lord Ruler who has oppressed the land for a thousand years.

**Recommendation Score: 9/10**

This book is highly recommended for:
- Fantasy readers looking for innovative magic systems
- Fans of heist stories with intricate plotting
- Readers who enjoy complex world-building and character development
- Those who appreciate darker, grittier fantasy settings

Brandon Sanderson is known for his meticulous magic systems and satisfying plot resolutions, and this book showcases both strengths brilliantly. It's an excellent entry point into Sanderson's Cosmere universe.\
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
                                "text": """\
```json
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}
```

**Additional Details:**

"Mistborn: The Final Empire" is the first book in Brandon Sanderson's acclaimed Mistborn trilogy. This epic fantasy novel features a unique magic system based on "Allomancy" - the ability to ingest and "burn" metals to gain supernatural powers. The story follows Vin, a street thief who discovers she's a Mistborn (someone who can use all Allomantic metals), as she joins a crew of rebel skaa attempting to overthrow the immortal Lord Ruler who has oppressed the land for a thousand years.

**Recommendation Score: 9/10**

This book is highly recommended for:
- Fantasy readers looking for innovative magic systems
- Fans of heist stories with intricate plotting
- Readers who enjoy complex world-building and character development
- Those who appreciate darker, grittier fantasy settings

Brandon Sanderson is known for his meticulous magic systems and satisfying plot resolutions, and this book showcases both strengths brilliantly. It's an excellent entry point into Sanderson's Cosmere universe.\
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
                    "strict": None,
                }
            ],
        }
    }
)
stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "anthropic",
            "model_id": "anthropic/claude-sonnet-4-5",
            "provider_model_name": "claude-sonnet-4-5",
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
                            id="toolu_01KmRWPDvdWdaL3Dm2NzGNnM",
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
                                "id": "toolu_01KmRWPDvdWdaL3Dm2NzGNnM",
                                "name": "get_book_info",
                                "input": {"isbn": "0-7653-1178-X"},
                            },
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="toolu_01KmRWPDvdWdaL3Dm2NzGNnM",
                            name="get_book_info",
                            result="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
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

**Mistborn: The Final Empire** by Brandon Sanderson is an epic fantasy novel and the first book in the Mistborn trilogy. Published in 2006, this 544-page novel is set in a dark, ash-covered world where the Lord Ruler has reigned for a thousand years and the skies are perpetually red.

The story follows Vin, a young street thief who discovers she has powerful magical abilities called Allomancy - a system where practitioners can "burn" metals internally to gain various supernatural powers. She joins a crew of rebels led by Kelsier, a charismatic Mistborn (someone who can use all Allomantic metals), who plans to overthrow the seemingly immortal Lord Ruler.

**Recommendation Score: 9/10**

This book is highly recommended for readers who enjoy:
- Intricate, well-defined magic systems
- Heist/rebellion storylines with strategic planning
- Strong character development
- Dark fantasy settings
- Political intrigue

Brandon Sanderson's signature meticulous worldbuilding and innovative magic system make this a standout in modern fantasy literature. It's an excellent entry point into Sanderson's work and the broader Cosmere universe.\
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
```

**Detailed Information:**

**Mistborn: The Final Empire** by Brandon Sanderson is an epic fantasy novel and the first book in the Mistborn trilogy. Published in 2006, this 544-page novel is set in a dark, ash-covered world where the Lord Ruler has reigned for a thousand years and the skies are perpetually red.

The story follows Vin, a young street thief who discovers she has powerful magical abilities called Allomancy - a system where practitioners can "burn" metals internally to gain various supernatural powers. She joins a crew of rebels led by Kelsier, a charismatic Mistborn (someone who can use all Allomantic metals), who plans to overthrow the seemingly immortal Lord Ruler.

**Recommendation Score: 9/10**

This book is highly recommended for readers who enjoy:
- Intricate, well-defined magic systems
- Heist/rebellion storylines with strategic planning
- Strong character development
- Dark fantasy settings
- Political intrigue

Brandon Sanderson's signature meticulous worldbuilding and innovative magic system make this a standout in modern fantasy literature. It's an excellent entry point into Sanderson's work and the broader Cosmere universe.\
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
                    "strict": None,
                }
            ],
            "usage": {
                "input_tokens": 904,
                "output_tokens": 328,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "None",
                "total_tokens": 1232,
            },
            "n_chunks": 110,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "anthropic",
            "model_id": "anthropic/claude-sonnet-4-5",
            "provider_model_name": "claude-sonnet-4-5",
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
                            id="toolu_018ZfveWtNE97MSDJXddwnsZ",
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
                                "id": "toolu_018ZfveWtNE97MSDJXddwnsZ",
                                "name": "get_book_info",
                                "input": {"isbn": "0-7653-1178-X"},
                            }
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="toolu_018ZfveWtNE97MSDJXddwnsZ",
                            name="get_book_info",
                            result="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
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

**Additional Details:**

*Mistborn: The Final Empire* is an epic fantasy novel by Brandon Sanderson and the first book in the Mistborn series. The story is set in a world where ash falls from the sky, mist dominates the night, and the immortal Lord Ruler has reigned with absolute power for a thousand years. The novel follows a street thief named Vin who discovers she has magical abilities and joins a crew planning to overthrow the empire.

The magic system, called Allomancy, is one of the most innovative and well-crafted in fantasy literature, where users "burn" different metals to gain various powers.

**Recommendation Score: 9/10**

This book is highly recommended for fans of fantasy literature, especially those who enjoy:
- Unique, well-defined magic systems
- Heist/rebellion storylines
- Strong character development
- Complex world-building
- Fast-paced action mixed with political intrigue

It's an excellent entry point into Brandon Sanderson's works and modern epic fantasy in general.\
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
```

**Additional Details:**

*Mistborn: The Final Empire* is an epic fantasy novel by Brandon Sanderson and the first book in the Mistborn series. The story is set in a world where ash falls from the sky, mist dominates the night, and the immortal Lord Ruler has reigned with absolute power for a thousand years. The novel follows a street thief named Vin who discovers she has magical abilities and joins a crew planning to overthrow the empire.

The magic system, called Allomancy, is one of the most innovative and well-crafted in fantasy literature, where users "burn" different metals to gain various powers.

**Recommendation Score: 9/10**

This book is highly recommended for fans of fantasy literature, especially those who enjoy:
- Unique, well-defined magic systems
- Heist/rebellion storylines
- Strong character development
- Complex world-building
- Fast-paced action mixed with political intrigue

It's an excellent entry point into Brandon Sanderson's works and modern epic fantasy in general.\
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
                    "strict": None,
                }
            ],
            "usage": {
                "input_tokens": 884,
                "output_tokens": 286,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "None",
                "total_tokens": 1170,
            },
            "n_chunks": 92,
        }
    }
)
