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
            "provider": "anthropic-bedrock",
            "model_id": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
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
                            id="toolu_bdrk_01JQVvd7aToxbKGDs1UAUXdJ",
                            name="get_book_info",
                            args='{"isbn": "0-7653-1178-X"}',
                        )
                    ],
                    provider="anthropic-bedrock",
                    model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "id": "toolu_bdrk_01JQVvd7aToxbKGDs1UAUXdJ",
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
                            id="toolu_bdrk_01JQVvd7aToxbKGDs1UAUXdJ",
                            name="get_book_info",
                            value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Based on the lookup, here is the book information in the required format:

```json
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}
```

**Detailed Information & Recommendation:**

**Mistborn: The Final Empire** is the first book in Brandon Sanderson's acclaimed Mistborn trilogy. Published in 2006, this 544-page fantasy novel has become a modern classic in the genre.

**What makes this book special:**
- **Innovative Magic System**: Features Allomancy, a unique magic system based on consuming metals to gain abilities
- **Strong World-building**: Set in a richly detailed fantasy world under eternal ash and oppressive imperial rule
- **Character Development**: Follows Vin, a street urchin who discovers her incredible potential
- **Page-turner Plot**: Combines heist elements with epic fantasy adventure

**Recommendation Score: 9/10**

This is highly recommended for:
- Fantasy fans seeking original magic systems
- Readers who enjoy character-driven narratives
- Those interested in series with excellent continuity
- Anyone looking for a standalone story with sequel options

**Perfect for**: Fantasy enthusiasts, especially those who appreciate intricate world-building and well-developed characters. If you enjoyed other epic fantasies, this is a must-read that won't disappoint.\
"""
                        )
                    ],
                    provider="anthropic-bedrock",
                    model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "citations": None,
                                "text": """\
Based on the lookup, here is the book information in the required format:

```json
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}
```

**Detailed Information & Recommendation:**

**Mistborn: The Final Empire** is the first book in Brandon Sanderson's acclaimed Mistborn trilogy. Published in 2006, this 544-page fantasy novel has become a modern classic in the genre.

**What makes this book special:**
- **Innovative Magic System**: Features Allomancy, a unique magic system based on consuming metals to gain abilities
- **Strong World-building**: Set in a richly detailed fantasy world under eternal ash and oppressive imperial rule
- **Character Development**: Follows Vin, a street urchin who discovers her incredible potential
- **Page-turner Plot**: Combines heist elements with epic fantasy adventure

**Recommendation Score: 9/10**

This is highly recommended for:
- Fantasy fans seeking original magic systems
- Readers who enjoy character-driven narratives
- Those interested in series with excellent continuity
- Anyone looking for a standalone story with sequel options

**Perfect for**: Fantasy enthusiasts, especially those who appreciate intricate world-building and well-developed characters. If you enjoyed other epic fantasies, this is a must-read that won't disappoint.\
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
            "provider": "anthropic-bedrock",
            "model_id": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
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
                            id="toolu_bdrk_011vCh7qM4iXatNwL4BScHg1",
                            name="get_book_info",
                            args='{"isbn": "0-7653-1178-X"}',
                        )
                    ],
                    provider="anthropic-bedrock",
                    model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "id": "toolu_bdrk_011vCh7qM4iXatNwL4BScHg1",
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
                            id="toolu_bdrk_011vCh7qM4iXatNwL4BScHg1",
                            name="get_book_info",
                            value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
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

**Detailed Information & Recommendation:**

**Mistborn: The Final Empire** by Brandon Sanderson is the first book in the acclaimed Mistborn trilogy. Here are some key points:

- **Genre**: Epic Fantasy
- **Length**: 544 pages - a substantial read that's well-paced
- **Publication**: 2006 - a modern classic in the fantasy genre

**Recommendation Score: 9/10**

**Why I recommend it:**
- **Innovative Magic System**: Sanderson is renowned for creating intricate, rule-based magic systems. Mistborn features a unique allomancy system that's both creative and well-executed
- **Strong Character Development**: The protagonist Vin undergoes compelling growth throughout the narrative
- **Excellent World-Building**: Despite being set in a darker world, the setting is richly detailed and immersive
- **Page-Turner Quality**: With 544 pages, it manages to stay engaging without feeling bloated
- **Gateway Fantasy**: Perfect for both experienced fantasy readers and newcomers to the genre

**Best for**: Readers who enjoy epic fantasy with strong magic systems, character arcs, and intricate plots. Great starting point for anyone wanting to explore Brandon Sanderson's works.\
"""
                        )
                    ],
                    provider="anthropic-bedrock",
                    model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
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

**Detailed Information & Recommendation:**

**Mistborn: The Final Empire** by Brandon Sanderson is the first book in the acclaimed Mistborn trilogy. Here are some key points:

- **Genre**: Epic Fantasy
- **Length**: 544 pages - a substantial read that's well-paced
- **Publication**: 2006 - a modern classic in the fantasy genre

**Recommendation Score: 9/10**

**Why I recommend it:**
- **Innovative Magic System**: Sanderson is renowned for creating intricate, rule-based magic systems. Mistborn features a unique allomancy system that's both creative and well-executed
- **Strong Character Development**: The protagonist Vin undergoes compelling growth throughout the narrative
- **Excellent World-Building**: Despite being set in a darker world, the setting is richly detailed and immersive
- **Page-Turner Quality**: With 544 pages, it manages to stay engaging without feeling bloated
- **Gateway Fantasy**: Perfect for both experienced fantasy readers and newcomers to the genre

**Best for**: Readers who enjoy epic fantasy with strong magic systems, character arcs, and intricate plots. Great starting point for anyone wanting to explore Brandon Sanderson's works.\
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
            "provider": "anthropic-bedrock",
            "model_id": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
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
                            id="toolu_bdrk_012ia7FVwG16cTPuuEr43FLC",
                            name="get_book_info",
                            args='{"isbn": "0-7653-1178-X"}',
                        )
                    ],
                    provider="anthropic-bedrock",
                    model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "tool_use",
                                "id": "toolu_bdrk_012ia7FVwG16cTPuuEr43FLC",
                                "name": "get_book_info",
                                "input": {"isbn": "0-7653-1178-X"},
                            }
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="toolu_bdrk_012ia7FVwG16cTPuuEr43FLC",
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

**Detailed Information:**

"Mistborn: The Final Empire" is the first novel in Brandon Sanderson's acclaimed Mistborn trilogy. Published in 2006, this epic fantasy novel spans 544 pages and introduces readers to a richly developed world with a unique magic system based on metal allomancy.

**Recommendation Score: 9/10**

**Why I recommend it:**

✓ **Exceptional World-Building** - Sanderson creates an intricate magic system that's both innovative and internally consistent
✓ **Compelling Characters** - The protagonist Vin is a well-developed character with real growth throughout the story
✓ **Engaging Plot** - A perfect blend of heist elements, political intrigue, and epic fantasy adventure
✓ **High-Quality Writing** - Sanderson is known for his meticulous plotting and prose
✓ **Page-Turner Quality** - At 544 pages, it's substantial but hard to put down
✓ **Series Potential** - An excellent entry point to a completed trilogy

**Best for:** Fantasy readers who enjoy intricate magic systems, character development, and epic world-building. Ideal for fans of authors like Patrick Rothfuss or Joe Abercrombie.\
"""
                        )
                    ],
                    provider="anthropic-bedrock",
                    model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
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

**Detailed Information:**

"Mistborn: The Final Empire" is the first novel in Brandon Sanderson's acclaimed Mistborn trilogy. Published in 2006, this epic fantasy novel spans 544 pages and introduces readers to a richly developed world with a unique magic system based on metal allomancy.

**Recommendation Score: 9/10**

**Why I recommend it:**

✓ **Exceptional World-Building** - Sanderson creates an intricate magic system that's both innovative and internally consistent
✓ **Compelling Characters** - The protagonist Vin is a well-developed character with real growth throughout the story
✓ **Engaging Plot** - A perfect blend of heist elements, political intrigue, and epic fantasy adventure
✓ **High-Quality Writing** - Sanderson is known for his meticulous plotting and prose
✓ **Page-Turner Quality** - At 544 pages, it's substantial but hard to put down
✓ **Series Potential** - An excellent entry point to a completed trilogy

**Best for:** Fantasy readers who enjoy intricate magic systems, character development, and epic world-building. Ideal for fans of authors like Patrick Rothfuss or Joe Abercrombie.\
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
            "n_chunks": 36,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider": "anthropic-bedrock",
            "model_id": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
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
                            id="toolu_bdrk_01Kb4iZEkrmsKA279uuj2U9r",
                            name="get_book_info",
                            args='{"isbn": "0-7653-1178-X"}',
                        )
                    ],
                    provider="anthropic-bedrock",
                    model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "tool_use",
                                "id": "toolu_bdrk_01Kb4iZEkrmsKA279uuj2U9r",
                                "name": "get_book_info",
                                "input": {"isbn": "0-7653-1178-X"},
                            }
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="toolu_bdrk_01Kb4iZEkrmsKA279uuj2U9r",
                            name="get_book_info",
                            value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Based on the book information retrieved, here's the detailed information:

```json
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}
```

**Additional Recommendations:**

**Recommendation Score: 9/10**

**Why you should read this book:**

- **Epic Fantasy Excellence**: Mistborn is the first book in an acclaimed fantasy series that has become a cornerstone of modern epic fantasy literature.

- **Innovative Magic System**: Brandon Sanderson is renowned for his intricate and well-defined magic systems. Mistborn features "Allomancy," a unique magic system based on the ingestion and burning of metals, which is truly creative and engaging.

- **Strong Character Development**: The protagonist Kel and the supporting cast are well-developed with compelling arcs and realistic character growth.

- **Page-Turner Plot**: With 544 pages, the book is substantial yet highly engaging. The pacing is excellent with multiple plot twists and surprises that keep you invested.

- **World-Building**: Sanderson excels at creating immersive worlds, and this book features a richly detailed fantasy world with a compelling history and social structure.

- **Accessibility**: While epic in scope, it's more accessible than some dense fantasy epics, making it great for both newcomers to the genre and experienced fantasy readers.

**Best for**: Fantasy enthusiasts, readers who enjoy well-constructed magic systems, and those looking for character-driven stories within epic settings.\
"""
                        )
                    ],
                    provider="anthropic-bedrock",
                    model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "text",
                                "text": """\
Based on the book information retrieved, here's the detailed information:

```json
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}
```

**Additional Recommendations:**

**Recommendation Score: 9/10**

**Why you should read this book:**

- **Epic Fantasy Excellence**: Mistborn is the first book in an acclaimed fantasy series that has become a cornerstone of modern epic fantasy literature.

- **Innovative Magic System**: Brandon Sanderson is renowned for his intricate and well-defined magic systems. Mistborn features "Allomancy," a unique magic system based on the ingestion and burning of metals, which is truly creative and engaging.

- **Strong Character Development**: The protagonist Kel and the supporting cast are well-developed with compelling arcs and realistic character growth.

- **Page-Turner Plot**: With 544 pages, the book is substantial yet highly engaging. The pacing is excellent with multiple plot twists and surprises that keep you invested.

- **World-Building**: Sanderson excels at creating immersive worlds, and this book features a richly detailed fantasy world with a compelling history and social structure.

- **Accessibility**: While epic in scope, it's more accessible than some dense fantasy epics, making it great for both newcomers to the genre and experienced fantasy readers.

**Best for**: Fantasy enthusiasts, readers who enjoy well-constructed magic systems, and those looking for character-driven stories within epic settings.\
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
            "n_chunks": 35,
        }
    }
)
