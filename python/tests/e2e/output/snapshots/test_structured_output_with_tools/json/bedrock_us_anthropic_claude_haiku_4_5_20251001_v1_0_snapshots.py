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
            "provider_id": "bedrock",
            "model_id": "bedrock/us.anthropic.claude-haiku-4-5-20251001-v1:0",
            "provider_model_name": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 884,
                "output_tokens": 361,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "Usage(cache_creation=CacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=884, output_tokens=361, server_tool_use=None, service_tier=None)",
                "total_tokens": 1245,
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
                            id="toolu_bdrk_01Dk1B8AiBqv2aJXVDvRKnBE",
                            name="get_book_info",
                            args='{"isbn": "0-7653-1178-X"}',
                        )
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    provider_model_name="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "id": "toolu_bdrk_01Dk1B8AiBqv2aJXVDvRKnBE",
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
                            id="toolu_bdrk_01Dk1B8AiBqv2aJXVDvRKnBE",
                            name="get_book_info",
                            result="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Based on the lookup, here is the information for the book:

```json
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}
```

**Additional Details & Recommendation:**

This is the first book in Brandon Sanderson's acclaimed Mistborn series. Here are some key points:

**Book Overview:**
- **Title:** Mistborn: The Final Empire
- **Author:** Brandon Sanderson
- **Pages:** 544
- **Published:** 2006

**Why It's Recommended:**
- **Innovative Magic System:** Sanderson is known for creating intricate, well-defined magic systems, and Mistborn features an excellent allomancy system (metal-based magic)
- **Strong Worldbuilding:** The book is set in a richly detailed fantasy world with excellent lore and atmosphere
- **Character Development:** Features compelling character arcs and a well-developed protagonist
- **Page-turner:** Despite its 544-page length, it's highly engaging with great pacing

**Recommendation Score: 8.5/10**

This is an excellent starting point for fantasy readers, whether you're new to Brandon Sanderson or experienced fantasy readers. It's particularly recommended if you enjoy:
- Epic fantasy with unique magic systems
- Heist-style plots with a fantasy twist
- Character-driven narratives
- Well-crafted worldbuilding

The book has a large, dedicated fanbase and serves as a perfect entry into the Mistborn universe.\
"""
                        )
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    provider_model_name="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "citations": None,
                                "text": """\
Based on the lookup, here is the information for the book:

```json
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}
```

**Additional Details & Recommendation:**

This is the first book in Brandon Sanderson's acclaimed Mistborn series. Here are some key points:

**Book Overview:**
- **Title:** Mistborn: The Final Empire
- **Author:** Brandon Sanderson
- **Pages:** 544
- **Published:** 2006

**Why It's Recommended:**
- **Innovative Magic System:** Sanderson is known for creating intricate, well-defined magic systems, and Mistborn features an excellent allomancy system (metal-based magic)
- **Strong Worldbuilding:** The book is set in a richly detailed fantasy world with excellent lore and atmosphere
- **Character Development:** Features compelling character arcs and a well-developed protagonist
- **Page-turner:** Despite its 544-page length, it's highly engaging with great pacing

**Recommendation Score: 8.5/10**

This is an excellent starting point for fantasy readers, whether you're new to Brandon Sanderson or experienced fantasy readers. It's particularly recommended if you enjoy:
- Epic fantasy with unique magic systems
- Heist-style plots with a fantasy twist
- Character-driven narratives
- Well-crafted worldbuilding

The book has a large, dedicated fanbase and serves as a perfect entry into the Mistborn universe.\
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
            "provider_id": "bedrock",
            "model_id": "bedrock/us.anthropic.claude-haiku-4-5-20251001-v1:0",
            "provider_model_name": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 884,
                "output_tokens": 320,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "Usage(cache_creation=CacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=884, output_tokens=320, server_tool_use=None, service_tier=None)",
                "total_tokens": 1204,
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
                            id="toolu_bdrk_01W9NKAfCdP4pT1xWSWw9RqS",
                            name="get_book_info",
                            args='{"isbn": "0-7653-1178-X"}',
                        )
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    provider_model_name="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "id": "toolu_bdrk_01W9NKAfCdP4pT1xWSWw9RqS",
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
                            id="toolu_bdrk_01W9NKAfCdP4pT1xWSWw9RqS",
                            name="get_book_info",
                            result="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Based on the information retrieved, here's the book summary in the requested format:

```json
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}
```

**Recommendation Score: 9.2/10**

**Detailed Information & Recommendation:**

**Mistborn: The Final Empire** is an excellent choice for fantasy readers. This epic fantasy novel is the first book in Brandon Sanderson's acclaimed Mistborn trilogy. \n\

**Key Highlights:**
- **Author**: Brandon Sanderson is renowned for his intricate worldbuilding and innovative magic systems
- **Length**: At 544 pages, it offers substantial content without excessive length
- **Publication**: Released in 2006, it has had nearly two decades to establish itself as a modern fantasy classic
- **Why Recommended**: \n\
  - Features an innovative "Allomancy" magic system with clear, logical rules
  - Strong character development and compelling protagonist in Vin
  - Excellent pacing and plot twists
  - Perfect for fans of dark fantasy with elements of rebellion and hope
  - Highly regarded by both critics and readers

**Best For**: Fantasy enthusiasts who enjoy character-driven stories, unique magic systems, and well-crafted worlds. Suitable for both experienced fantasy readers and those new to the genre.\
"""
                        )
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    provider_model_name="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "citations": None,
                                "text": """\
Based on the information retrieved, here's the book summary in the requested format:

```json
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}
```

**Recommendation Score: 9.2/10**

**Detailed Information & Recommendation:**

**Mistborn: The Final Empire** is an excellent choice for fantasy readers. This epic fantasy novel is the first book in Brandon Sanderson's acclaimed Mistborn trilogy. \n\

**Key Highlights:**
- **Author**: Brandon Sanderson is renowned for his intricate worldbuilding and innovative magic systems
- **Length**: At 544 pages, it offers substantial content without excessive length
- **Publication**: Released in 2006, it has had nearly two decades to establish itself as a modern fantasy classic
- **Why Recommended**: \n\
  - Features an innovative "Allomancy" magic system with clear, logical rules
  - Strong character development and compelling protagonist in Vin
  - Excellent pacing and plot twists
  - Perfect for fans of dark fantasy with elements of rebellion and hope
  - Highly regarded by both critics and readers

**Best For**: Fantasy enthusiasts who enjoy character-driven stories, unique magic systems, and well-crafted worlds. Suitable for both experienced fantasy readers and those new to the genre.\
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
            "provider_id": "bedrock",
            "model_id": "bedrock/us.anthropic.claude-haiku-4-5-20251001-v1:0",
            "provider_model_name": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
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
                        Text(text="I'll look up that book for you."),
                        ToolCall(
                            id="toolu_bdrk_0123idFGXBL9pQxjcF2XcK45",
                            name="get_book_info",
                            args='{"isbn": "0-7653-1178-X"}',
                        ),
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    provider_model_name="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {"type": "text", "text": "I'll look up that book for you."},
                            {
                                "type": "tool_use",
                                "id": "toolu_bdrk_0123idFGXBL9pQxjcF2XcK45",
                                "name": "get_book_info",
                                "input": {"isbn": "0-7653-1178-X"},
                            },
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="toolu_bdrk_0123idFGXBL9pQxjcF2XcK45",
                            name="get_book_info",
                            result="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Here's the information for the book with ISBN 0-7653-1178-X:

```json
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}
```

**Detailed Information & Recommendation:**

**Title:** Mistborn: The Final Empire  \n\
**Author:** Brandon Sanderson  \n\
**Pages:** 544  \n\
**Published:** 2006

**Recommendation Score:** ⭐⭐⭐⭐⭐ (5/5)

**Why I recommend this book:**

Mistborn: The Final Empire is an excellent fantasy novel that serves as the first book in Brandon Sanderson's acclaimed Mistborn trilogy. Here's why it's worth reading:

1. **Innovative Magic System** - Sanderson is known for creating detailed, rule-based magic systems, and Mistborn features one of his best: Allomancy, a fascinating system where people burn metals to gain supernatural abilities.

2. **Compelling Characters** - The protagonist, Vin, is a complex and relatable character who grows significantly throughout the story. The supporting cast is equally well-developed.

3. **Engaging Plot** - The story combines heist elements with epic fantasy, creating an exciting narrative that keeps readers engaged throughout its 544 pages.

4. **World-Building** - The world of Scadrial is richly constructed with a unique history and interesting social structure.

5. **Perfect Entry Point** - While it's a fantasy novel, it's accessible to readers new to the genre and also satisfying for veteran fantasy fans.

This is a must-read for fantasy enthusiasts and is widely considered one of the best fantasy series of the 21st century.\
"""
                        )
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    provider_model_name="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "text",
                                "text": """\
Here's the information for the book with ISBN 0-7653-1178-X:

```json
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}
```

**Detailed Information & Recommendation:**

**Title:** Mistborn: The Final Empire  \n\
**Author:** Brandon Sanderson  \n\
**Pages:** 544  \n\
**Published:** 2006

**Recommendation Score:** ⭐⭐⭐⭐⭐ (5/5)

**Why I recommend this book:**

Mistborn: The Final Empire is an excellent fantasy novel that serves as the first book in Brandon Sanderson's acclaimed Mistborn trilogy. Here's why it's worth reading:

1. **Innovative Magic System** - Sanderson is known for creating detailed, rule-based magic systems, and Mistborn features one of his best: Allomancy, a fascinating system where people burn metals to gain supernatural abilities.

2. **Compelling Characters** - The protagonist, Vin, is a complex and relatable character who grows significantly throughout the story. The supporting cast is equally well-developed.

3. **Engaging Plot** - The story combines heist elements with epic fantasy, creating an exciting narrative that keeps readers engaged throughout its 544 pages.

4. **World-Building** - The world of Scadrial is richly constructed with a unique history and interesting social structure.

5. **Perfect Entry Point** - While it's a fantasy novel, it's accessible to readers new to the genre and also satisfying for veteran fantasy fans.

This is a must-read for fantasy enthusiasts and is widely considered one of the best fantasy series of the 21st century.\
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
                "input_tokens": 0,
                "output_tokens": 410,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 410,
            },
            "n_chunks": 124,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "bedrock",
            "model_id": "bedrock/us.anthropic.claude-haiku-4-5-20251001-v1:0",
            "provider_model_name": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
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
                            id="toolu_bdrk_016qvntQtTCvYirDGKdUaFG6",
                            name="get_book_info",
                            args='{"isbn": "0-7653-1178-X"}',
                        )
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    provider_model_name="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "tool_use",
                                "id": "toolu_bdrk_016qvntQtTCvYirDGKdUaFG6",
                                "name": "get_book_info",
                                "input": {"isbn": "0-7653-1178-X"},
                            }
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="toolu_bdrk_016qvntQtTCvYirDGKdUaFG6",
                            name="get_book_info",
                            result="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Based on the lookup, here's the detailed information for the book:

```json
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}
```

**Detailed Information:**
- **Title:** Mistborn: The Final Empire
- **Author:** Brandon Sanderson
- **Pages:** 544
- **Publication Year:** 2006

**Recommendation Score: 9/10**

**Why I recommend this book:**
- **Excellent worldbuilding:** Sanderson creates a rich, detailed fantasy world with an innovative magic system based on the use of metals (Allomancy)
- **Compelling narrative:** The story follows Vin, a street orphan who discovers she has extraordinary powers, combined with an engaging heist narrative
- **Strong character development:** Well-crafted protagonist and supporting cast with meaningful character arcs
- **Page-turner quality:** Despite its 544-page length, it's highly engaging and difficult to put down
- **Beginning of a great series:** This is the first book in the Mistborn trilogy, with each installment being highly acclaimed
- **Perfect for:** Fantasy fans who enjoy intricate magic systems, character-driven stories, and epic worldbuilding

This is widely considered one of the best modern fantasy series and is an excellent starting point for readers new to Brandon Sanderson's work.\
"""
                        )
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    provider_model_name="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "text",
                                "text": """\
Based on the lookup, here's the detailed information for the book:

```json
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}
```

**Detailed Information:**
- **Title:** Mistborn: The Final Empire
- **Author:** Brandon Sanderson
- **Pages:** 544
- **Publication Year:** 2006

**Recommendation Score: 9/10**

**Why I recommend this book:**
- **Excellent worldbuilding:** Sanderson creates a rich, detailed fantasy world with an innovative magic system based on the use of metals (Allomancy)
- **Compelling narrative:** The story follows Vin, a street orphan who discovers she has extraordinary powers, combined with an engaging heist narrative
- **Strong character development:** Well-crafted protagonist and supporting cast with meaningful character arcs
- **Page-turner quality:** Despite its 544-page length, it's highly engaging and difficult to put down
- **Beginning of a great series:** This is the first book in the Mistborn trilogy, with each installment being highly acclaimed
- **Perfect for:** Fantasy fans who enjoy intricate magic systems, character-driven stories, and epic worldbuilding

This is widely considered one of the best modern fantasy series and is an excellent starting point for readers new to Brandon Sanderson's work.\
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
                "input_tokens": 0,
                "output_tokens": 326,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 326,
            },
            "n_chunks": 102,
        }
    }
)
