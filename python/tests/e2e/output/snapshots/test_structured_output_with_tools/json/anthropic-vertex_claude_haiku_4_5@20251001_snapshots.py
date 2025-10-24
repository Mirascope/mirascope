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
                            id="toolu_vrtx_011ohFD7XyNp81FkePMUxFVY",
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
                                "id": "toolu_vrtx_011ohFD7XyNp81FkePMUxFVY",
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
                            id="toolu_vrtx_011ohFD7XyNp81FkePMUxFVY",
                            name="get_book_info",
                            value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Based on the book information retrieved, here is the detailed info:

```json
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}
```

**Detailed Information & Recommendation:**

**Mistborn: The Final Empire** is the first book in Brandon Sanderson's acclaimed Mistborn trilogy. Here are some highlights:

- **Author:** Brandon Sanderson, known for intricate worldbuilding and magic systems
- **Length:** 544 pages - a substantial read that's appropriately sized for epic fantasy
- **Publication:** 2006 - well-established in the fantasy canon

**Why You Should Read It:**
- **Innovative Magic System:** The allomancy magic system is unique and well-developed
- **Strong World-building:** Sanderson creates a richly detailed world with interesting lore
- **Character Development:** Features a compelling protagonist, Vin, and solid supporting characters
- **Page-Turner Plot:** Despite its length, the book maintains excellent pacing with surprising twists

**Recommendation Score: 8.5/10**

This is an excellent choice for fantasy lovers who enjoy:
- Epic fantasy with original magic systems
- Character-driven narratives
- Intricate plots with good pacing
- Strong world-building and lore

Perfect for readers who loved series like *The Stormlight Archive* or *The Wheel of Time*, though more accessible than some epic fantasy doorstops.\
"""
                        )
                    ],
                    provider="anthropic-vertex",
                    model_id="claude-haiku-4-5@20251001",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "citations": None,
                                "text": """\
Based on the book information retrieved, here is the detailed info:

```json
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}
```

**Detailed Information & Recommendation:**

**Mistborn: The Final Empire** is the first book in Brandon Sanderson's acclaimed Mistborn trilogy. Here are some highlights:

- **Author:** Brandon Sanderson, known for intricate worldbuilding and magic systems
- **Length:** 544 pages - a substantial read that's appropriately sized for epic fantasy
- **Publication:** 2006 - well-established in the fantasy canon

**Why You Should Read It:**
- **Innovative Magic System:** The allomancy magic system is unique and well-developed
- **Strong World-building:** Sanderson creates a richly detailed world with interesting lore
- **Character Development:** Features a compelling protagonist, Vin, and solid supporting characters
- **Page-Turner Plot:** Despite its length, the book maintains excellent pacing with surprising twists

**Recommendation Score: 8.5/10**

This is an excellent choice for fantasy lovers who enjoy:
- Epic fantasy with original magic systems
- Character-driven narratives
- Intricate plots with good pacing
- Strong world-building and lore

Perfect for readers who loved series like *The Stormlight Archive* or *The Wheel of Time*, though more accessible than some epic fantasy doorstops.\
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
                            id="toolu_vrtx_01C3uUjNXvj2WukCo28pdosc",
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
                                "id": "toolu_vrtx_01C3uUjNXvj2WukCo28pdosc",
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
                            id="toolu_vrtx_01C3uUjNXvj2WukCo28pdosc",
                            name="get_book_info",
                            value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Here's the detailed information for the book:

```json
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}
```

**Detailed Review & Recommendation:**

**Book Summary:**
"Mistborn: The Final Empire" is the first novel in Brandon Sanderson's acclaimed Mistborn series. It's an epic fantasy novel set in a world ruled by an immortal tyrant called the Lord Ruler. The story follows Vin, a street orphan who discovers she possesses Mistborn powers and gets drawn into a rebellion against the oppressive regime.

**Key Strengths:**
- **Innovative Magic System**: Sanderson's Allomancy system is one of the most creative and well-defined magic systems in fantasy literature
- **Strong Character Development**: Vin's journey from street urchin to powerful Mistborn is compelling and emotionally resonant
- **Plot Twists**: The story features excellent pacing with shocking revelations that recontextualize the narrative
- **World-Building**: Rich, detailed world with interesting cultures and histories
- **Length**: At 544 pages, it's substantial but very readable and engaging

**Recommendation Score: 9/10**

This book is highly recommended for:
- Fantasy fans seeking original magic systems
- Readers who enjoy character-driven narratives
- Anyone looking for an epic fantasy series starter
- Fans of Brandon Sanderson's other works

**Best For:** This is an excellent entry point into fantasy literature and a must-read for serious fantasy enthusiasts. It's accessible enough for newer readers but sophisticated enough for veterans of the genre.\
"""
                        )
                    ],
                    provider="anthropic-vertex",
                    model_id="claude-haiku-4-5@20251001",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "citations": None,
                                "text": """\
Here's the detailed information for the book:

```json
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}
```

**Detailed Review & Recommendation:**

**Book Summary:**
"Mistborn: The Final Empire" is the first novel in Brandon Sanderson's acclaimed Mistborn series. It's an epic fantasy novel set in a world ruled by an immortal tyrant called the Lord Ruler. The story follows Vin, a street orphan who discovers she possesses Mistborn powers and gets drawn into a rebellion against the oppressive regime.

**Key Strengths:**
- **Innovative Magic System**: Sanderson's Allomancy system is one of the most creative and well-defined magic systems in fantasy literature
- **Strong Character Development**: Vin's journey from street urchin to powerful Mistborn is compelling and emotionally resonant
- **Plot Twists**: The story features excellent pacing with shocking revelations that recontextualize the narrative
- **World-Building**: Rich, detailed world with interesting cultures and histories
- **Length**: At 544 pages, it's substantial but very readable and engaging

**Recommendation Score: 9/10**

This book is highly recommended for:
- Fantasy fans seeking original magic systems
- Readers who enjoy character-driven narratives
- Anyone looking for an epic fantasy series starter
- Fans of Brandon Sanderson's other works

**Best For:** This is an excellent entry point into fantasy literature and a must-read for serious fantasy enthusiasts. It's accessible enough for newer readers but sophisticated enough for veterans of the genre.\
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
                            id="toolu_vrtx_01XwFs4djTFks33t6ws2B6pA",
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
                                "id": "toolu_vrtx_01XwFs4djTFks33t6ws2B6pA",
                                "name": "get_book_info",
                                "input": {"isbn": "0-7653-1178-X"},
                            }
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="toolu_vrtx_01XwFs4djTFks33t6ws2B6pA",
                            name="get_book_info",
                            value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Based on the book information retrieved, here's what I found:

```json
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}
```

**Detailed Information & Recommendation:**

**Mistborn: The Final Empire** is the first book in Brandon Sanderson's acclaimed Mistborn series. Published in 2006, this epic fantasy novel spans 544 pages and launches readers into a richly detailed world with a unique magic system.

**Key Highlights:**
- **Setting**: A dark, ash-covered world ruled by an immortal tyrant
- **Protagonist**: Vin, a street thief with latent magical powers
- **Magic System**: The intricate Allomancy system, where users "burn" metals to gain different abilities
- **Themes**: Rebellion, self-discovery, and challenging oppressive systems

**Recommendation Score: 9/10**

This is an excellent choice for fantasy readers! The book is highly recommended if you enjoy:
- Complex, well-thought-out magic systems
- Character-driven narratives with strong development
- Epic fantasy with a page-turning plot
- Heist elements mixed with larger world-building

**Why it deserves a high score**: Sanderson's worldbuilding is exceptional, the magic system is innovative and internally consistent, and the character arcs are compelling. The pacing is excellent for a 544-page book, keeping readers engaged throughout. It's the perfect entry point into the Mistborn universe and stands well on its own while opening doors to the broader series.\
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
Based on the book information retrieved, here's what I found:

```json
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}
```

**Detailed Information & Recommendation:**

**Mistborn: The Final Empire** is the first book in Brandon Sanderson's acclaimed Mistborn series. Published in 2006, this epic fantasy novel spans 544 pages and launches readers into a richly detailed world with a unique magic system.

**Key Highlights:**
- **Setting**: A dark, ash-covered world ruled by an immortal tyrant
- **Protagonist**: Vin, a street thief with latent magical powers
- **Magic System**: The intricate Allomancy system, where users "burn" metals to gain different abilities
- **Themes**: Rebellion, self-discovery, and challenging oppressive systems

**Recommendation Score: 9/10**

This is an excellent choice for fantasy readers! The book is highly recommended if you enjoy:
- Complex, well-thought-out magic systems
- Character-driven narratives with strong development
- Epic fantasy with a page-turning plot
- Heist elements mixed with larger world-building

**Why it deserves a high score**: Sanderson's worldbuilding is exceptional, the magic system is innovative and internally consistent, and the character arcs are compelling. The pacing is excellent for a 544-page book, keeping readers engaged throughout. It's the perfect entry point into the Mistborn universe and stands well on its own while opening doors to the broader series.\
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
            "n_chunks": 114,
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
                            id="toolu_vrtx_01BMQsUJTYqipnD4opWHa1b3",
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
                                "id": "toolu_vrtx_01BMQsUJTYqipnD4opWHa1b3",
                                "name": "get_book_info",
                                "input": {"isbn": "0-7653-1178-X"},
                            }
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="toolu_vrtx_01BMQsUJTYqipnD4opWHa1b3",
                            name="get_book_info",
                            value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Here's the detailed information for the book with ISBN 0-7653-1178-X:

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

**Why I Recommend This Book:**

This is the first book in Brandon Sanderson's acclaimed Mistborn trilogy. It's an excellent choice for fantasy fans because:

1. **Innovative Magic System** - Sanderson is renowned for creating intricate, rule-based magic systems, and Mistborn's "Allomancy" is one of his best works, featuring unique metal-based powers that are both creative and internally consistent.

2. **Compelling Characters** - The protagonist Kel is relatable and well-developed, with a journey that feels earned and meaningful.

3. **Engaging Plot** - The 544 pages move at a great pace, blending political intrigue, action, mystery, and character development seamlessly.

4. **World-Building** - The setting is richly detailed with a unique culture, history, and atmosphere that sets it apart from typical fantasy.

5. **High Quality Writing** - Sanderson is known for his meticulous craftsmanship and this book showcases his ability to write compelling fantasy.

It's perfect for fans of complex fantasy with strong character arcs and is an excellent starting point for those wanting to explore Sanderson's work!\
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
Here's the detailed information for the book with ISBN 0-7653-1178-X:

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

**Why I Recommend This Book:**

This is the first book in Brandon Sanderson's acclaimed Mistborn trilogy. It's an excellent choice for fantasy fans because:

1. **Innovative Magic System** - Sanderson is renowned for creating intricate, rule-based magic systems, and Mistborn's "Allomancy" is one of his best works, featuring unique metal-based powers that are both creative and internally consistent.

2. **Compelling Characters** - The protagonist Kel is relatable and well-developed, with a journey that feels earned and meaningful.

3. **Engaging Plot** - The 544 pages move at a great pace, blending political intrigue, action, mystery, and character development seamlessly.

4. **World-Building** - The setting is richly detailed with a unique culture, history, and atmosphere that sets it apart from typical fantasy.

5. **High Quality Writing** - Sanderson is known for his meticulous craftsmanship and this book showcases his ability to write compelling fantasy.

It's perfect for fans of complex fantasy with strong character arcs and is an excellent starting point for those wanting to explore Sanderson's work!\
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
            "n_chunks": 103,
        }
    }
)
