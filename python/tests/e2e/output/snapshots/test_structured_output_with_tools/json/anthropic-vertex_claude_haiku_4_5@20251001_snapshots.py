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
            "provider": "anthropic-vertex",
            "model_id": "claude-haiku-4-5@20251001",
            "params": {},
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
                            id="toolu_vrtx_01CbkBygQnJve7h3iAxDt6iU",
                            name="get_book_info",
                            args='{"isbn": "0-7653-1178-X"}',
                        )
                    ],
                    provider="anthropic",
                    model_id="claude-haiku-4-5@20251001",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "id": "toolu_vrtx_01CbkBygQnJve7h3iAxDt6iU",
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
                            id="toolu_vrtx_01CbkBygQnJve7h3iAxDt6iU",
                            name="get_book_info",
                            value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Based on the lookup, here is the book information:

```json
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}
```

**Detailed Information & Recommendation:**

**Mistborn: The Final Empire** is the first book in Brandon Sanderson's acclaimed Mistborn series. Here's what makes it notable:

- **Genre**: Epic Fantasy with innovative magic system
- **Setting**: The Final Empire, a dark world ruled by an immortal tyrant
- **Strengths**: \n\
  - Uniquely designed "Allomancy" magic system with clear, logical rules
  - Compelling character-driven narrative focused on a street urchin turned hero
  - Excellent world-building and intricate plotting
  - Highly satisfying ending that resolves the main conflict while opening new possibilities
  - 544 pages of engaging storytelling

- **Target Audience**: Fantasy readers who enjoy detailed magic systems, character development, and heist-like plotting with epic stakes

**Recommendation Score: 9/10**

This is an exceptional entry point into epic fantasy. Sanderson's disciplined writing, innovative magic system, and engaging cast of characters make this a must-read for fantasy enthusiasts. It's particularly appealing if you enjoy:
- Complex magic systems with internal logic
- Character-driven stories
- Political intrigue and rebellion narratives
- Standalone-satisfying books (though with sequel potential)

Highly recommended! 📚\
"""
                        )
                    ],
                    provider="anthropic",
                    model_id="claude-haiku-4-5@20251001",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "citations": None,
                                "text": """\
Based on the lookup, here is the book information:

```json
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}
```

**Detailed Information & Recommendation:**

**Mistborn: The Final Empire** is the first book in Brandon Sanderson's acclaimed Mistborn series. Here's what makes it notable:

- **Genre**: Epic Fantasy with innovative magic system
- **Setting**: The Final Empire, a dark world ruled by an immortal tyrant
- **Strengths**: \n\
  - Uniquely designed "Allomancy" magic system with clear, logical rules
  - Compelling character-driven narrative focused on a street urchin turned hero
  - Excellent world-building and intricate plotting
  - Highly satisfying ending that resolves the main conflict while opening new possibilities
  - 544 pages of engaging storytelling

- **Target Audience**: Fantasy readers who enjoy detailed magic systems, character development, and heist-like plotting with epic stakes

**Recommendation Score: 9/10**

This is an exceptional entry point into epic fantasy. Sanderson's disciplined writing, innovative magic system, and engaging cast of characters make this a must-read for fantasy enthusiasts. It's particularly appealing if you enjoy:
- Complex magic systems with internal logic
- Character-driven stories
- Political intrigue and rebellion narratives
- Standalone-satisfying books (though with sequel potential)

Highly recommended! 📚\
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
            "provider": "anthropic-vertex",
            "model_id": "claude-haiku-4-5@20251001",
            "params": {},
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
                            id="toolu_vrtx_0137nm9uqWd7CazcdzkQYige",
                            name="get_book_info",
                            args='{"isbn": "0-7653-1178-X"}',
                        )
                    ],
                    provider="anthropic",
                    model_id="claude-haiku-4-5@20251001",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "id": "toolu_vrtx_0137nm9uqWd7CazcdzkQYige",
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
                            id="toolu_vrtx_0137nm9uqWd7CazcdzkQYige",
                            name="get_book_info",
                            value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Based on the ISBN lookup, here's the information for the book:

```json
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}
```

## Detailed Information & Recommendation

**Book Summary:**
"Mistborn: The Final Empire" is the first novel in Brandon Sanderson's acclaimed Mistborn fantasy series. It's an epic fantasy novel set in a unique world with an intricate magic system based on metal ingestion (Allomancy).

**Key Details:**
- **Pages:** 544
- **Published:** 2006
- **Genre:** Epic Fantasy
- **Series:** Mistborn (Book 1)

**Why You Should Read It:**
- ⭐ Excellent world-building with a unique and innovative magic system
- ⭐ Compelling protagonist in Vin, a young heroine discovering her powers
- ⭐ Thrilling plot with great plot twists and an unforgettable ending
- ⭐ Brandon Sanderson is known for his meticulous storytelling and character development
- ⭐ Perfect entry point for fantasy readers seeking something fresh and engaging

**Recommendation Score: 9/10**

This is a must-read for fantasy enthusiasts and a great starting point for anyone new to Brandon Sanderson's work. The book brilliantly balances action, mystery, and character development. Highly recommended for readers aged 15+ who enjoy epic fantasy with strong protagonists and imaginative magic systems.\
"""
                        )
                    ],
                    provider="anthropic",
                    model_id="claude-haiku-4-5@20251001",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "citations": None,
                                "text": """\
Based on the ISBN lookup, here's the information for the book:

```json
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}
```

## Detailed Information & Recommendation

**Book Summary:**
"Mistborn: The Final Empire" is the first novel in Brandon Sanderson's acclaimed Mistborn fantasy series. It's an epic fantasy novel set in a unique world with an intricate magic system based on metal ingestion (Allomancy).

**Key Details:**
- **Pages:** 544
- **Published:** 2006
- **Genre:** Epic Fantasy
- **Series:** Mistborn (Book 1)

**Why You Should Read It:**
- ⭐ Excellent world-building with a unique and innovative magic system
- ⭐ Compelling protagonist in Vin, a young heroine discovering her powers
- ⭐ Thrilling plot with great plot twists and an unforgettable ending
- ⭐ Brandon Sanderson is known for his meticulous storytelling and character development
- ⭐ Perfect entry point for fantasy readers seeking something fresh and engaging

**Recommendation Score: 9/10**

This is a must-read for fantasy enthusiasts and a great starting point for anyone new to Brandon Sanderson's work. The book brilliantly balances action, mystery, and character development. Highly recommended for readers aged 15+ who enjoy epic fantasy with strong protagonists and imaginative magic systems.\
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
            "provider": "anthropic-vertex",
            "model_id": "claude-haiku-4-5@20251001",
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
                            id="toolu_vrtx_014we89QMnZd4kSKBH2tStaK",
                            name="get_book_info",
                            args='{"isbn": "0-7653-1178-X"}',
                        )
                    ],
                    provider="anthropic-vertex",
                    model_id="claude-haiku-4-5@20251001",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "tool_use",
                                "id": "toolu_vrtx_014we89QMnZd4kSKBH2tStaK",
                                "name": "get_book_info",
                                "input": {"isbn": "0-7653-1178-X"},
                            }
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="toolu_vrtx_014we89QMnZd4kSKBH2tStaK",
                            name="get_book_info",
                            value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Based on the ISBN lookup, here's the book information:

```json
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}
```

## Detailed Information & Recommendation

**Book Details:**
- **Title:** Mistborn: The Final Empire
- **Author:** Brandon Sanderson
- **Pages:** 544
- **Published:** 2006

**About the Book:**
This is the first novel in Brandon Sanderson's acclaimed Mistborn trilogy. It's an epic fantasy novel set in a dark world under the tyrannical rule of the Lord Ruler. The story follows Vin, a street orphan who discovers she has special magical powers, and becomes embroiled in a rebellion against an oppressive empire. The book is renowned for its intricate magic system (Allomancy), well-developed characters, and compelling plot twists.

**Recommendation Score: 9/10**

**Why recommend it:**
✓ Exceptional world-building with a unique and detailed magic system
✓ Strong character development and compelling protagonist
✓ Fast-paced plotting with excellent plot twists
✓ Perfect entry point for fantasy readers
✓ Brandon Sanderson is known for detailed, immersive storytelling
✓ Gateway to a complete trilogy with consistent quality

**Best for:** Fantasy enthusiasts, readers who enjoy epic adventures with intricate magic systems, and those looking for a well-crafted trilogy starter.\
"""
                        )
                    ],
                    provider="anthropic-vertex",
                    model_id="claude-haiku-4-5@20251001",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "text",
                                "text": """\
Based on the ISBN lookup, here's the book information:

```json
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}
```

## Detailed Information & Recommendation

**Book Details:**
- **Title:** Mistborn: The Final Empire
- **Author:** Brandon Sanderson
- **Pages:** 544
- **Published:** 2006

**About the Book:**
This is the first novel in Brandon Sanderson's acclaimed Mistborn trilogy. It's an epic fantasy novel set in a dark world under the tyrannical rule of the Lord Ruler. The story follows Vin, a street orphan who discovers she has special magical powers, and becomes embroiled in a rebellion against an oppressive empire. The book is renowned for its intricate magic system (Allomancy), well-developed characters, and compelling plot twists.

**Recommendation Score: 9/10**

**Why recommend it:**
✓ Exceptional world-building with a unique and detailed magic system
✓ Strong character development and compelling protagonist
✓ Fast-paced plotting with excellent plot twists
✓ Perfect entry point for fantasy readers
✓ Brandon Sanderson is known for detailed, immersive storytelling
✓ Gateway to a complete trilogy with consistent quality

**Best for:** Fantasy enthusiasts, readers who enjoy epic adventures with intricate magic systems, and those looking for a well-crafted trilogy starter.\
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
            "n_chunks": 101,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider": "anthropic-vertex",
            "model_id": "claude-haiku-4-5@20251001",
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
                            id="toolu_vrtx_016ZVtMSvUGsc9bVzSTU736g",
                            name="get_book_info",
                            args='{"isbn": "0-7653-1178-X"}',
                        )
                    ],
                    provider="anthropic-vertex",
                    model_id="claude-haiku-4-5@20251001",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "tool_use",
                                "id": "toolu_vrtx_016ZVtMSvUGsc9bVzSTU736g",
                                "name": "get_book_info",
                                "input": {"isbn": "0-7653-1178-X"},
                            }
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="toolu_vrtx_016ZVtMSvUGsc9bVzSTU736g",
                            name="get_book_info",
                            value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Based on the book information retrieved, here's the detailed information in the requested JSON format:

```json
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}
```

**Additional Recommendation Details:**

**Book Summary:** Mistborn: The Final Empire is the first book in Brandon Sanderson's epic fantasy Mistborn series. It introduces readers to a world under the dominion of an immortal tyrant called the Lord Ruler, and follows Vin, a street orphan who discovers she has extraordinary magical powers.

**Key Strengths:**
- **Innovative Magic System**: Sanderson is renowned for creating detailed, internally consistent magic systems. Mistborn features "Allomancy," where consuming specific metals grants magical abilities
- **Compelling Protagonist**: Vin's journey from oppressed orphan to powerful Mistborn is engaging and emotionally resonant
- **Fast-Paced Plot**: At 544 pages, the story moves quickly with excellent pacing and plot twists
- **World-Building**: The dark, fantasy world with unique cultures and history is well-developed

**Recommendation Score: 8.5/10**

This book is highly recommended for:
- Fantasy enthusiasts who enjoy complex magic systems
- Readers looking for a strong female protagonist
- Those interested in character-driven narratives
- Fans of epic fantasy with action and intrigue

It's an excellent starting point for Sanderson's Mistborn series and remains one of the most popular modern fantasy novels.\
"""
                        )
                    ],
                    provider="anthropic-vertex",
                    model_id="claude-haiku-4-5@20251001",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "text",
                                "text": """\
Based on the book information retrieved, here's the detailed information in the requested JSON format:

```json
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}
```

**Additional Recommendation Details:**

**Book Summary:** Mistborn: The Final Empire is the first book in Brandon Sanderson's epic fantasy Mistborn series. It introduces readers to a world under the dominion of an immortal tyrant called the Lord Ruler, and follows Vin, a street orphan who discovers she has extraordinary magical powers.

**Key Strengths:**
- **Innovative Magic System**: Sanderson is renowned for creating detailed, internally consistent magic systems. Mistborn features "Allomancy," where consuming specific metals grants magical abilities
- **Compelling Protagonist**: Vin's journey from oppressed orphan to powerful Mistborn is engaging and emotionally resonant
- **Fast-Paced Plot**: At 544 pages, the story moves quickly with excellent pacing and plot twists
- **World-Building**: The dark, fantasy world with unique cultures and history is well-developed

**Recommendation Score: 8.5/10**

This book is highly recommended for:
- Fantasy enthusiasts who enjoy complex magic systems
- Readers looking for a strong female protagonist
- Those interested in character-driven narratives
- Fans of epic fantasy with action and intrigue

It's an excellent starting point for Sanderson's Mistborn series and remains one of the most popular modern fantasy novels.\
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
            "n_chunks": 105,
        }
    }
)
