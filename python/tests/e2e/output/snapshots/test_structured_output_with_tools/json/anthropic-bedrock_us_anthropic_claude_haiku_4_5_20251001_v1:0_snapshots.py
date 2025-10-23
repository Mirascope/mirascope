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
                            id="toolu_bdrk_012uaLyACAipedC8JkvK9uTH",
                            name="get_book_info",
                            args='{"isbn": "0-7653-1178-X"}',
                        )
                    ],
                    provider="anthropic",
                    model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "id": "toolu_bdrk_012uaLyACAipedC8JkvK9uTH",
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
                            id="toolu_bdrk_012uaLyACAipedC8JkvK9uTH",
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

**Detailed Information:**

**Mistborn: The Final Empire** is an epic fantasy novel by Brandon Sanderson, published in 2006. This 544-page book marks the beginning of the original Mistborn trilogy and is renowned for introducing one of the most intricate magic systems in modern fantasy literature.

**Key Highlights:**
- **Setting**: A dark fantasy world ruled by an immortal tyrant
- **Magic System**: Features "Allomancy," a unique system where metals grant magical powers when ingested and burned
- **Protagonist**: Vin, a street urchin who discovers her incredible potential
- **Themes**: Revolution, identity, loyalty, and the cost of freedom

**Recommendation Score: 9/10**

This book is highly recommended for:
- Fantasy readers seeking innovative magic systems
- Those who enjoy character-driven narratives with strong protagonists
- Readers looking for a well-plotted trilogy starter with excellent world-building
- Anyone who appreciates Brandon Sanderson's meticulous storytelling

**Why the high score**: The novel combines compelling character development, an intricate and logical magic system, engaging plot twists, and excellent pacing. It's considered a modern classic in the fantasy genre and has sparked a thriving fan community. The only minor deduction is that some readers may find the pacing slow in the opening chapters, but this pays off magnificently as the story progresses.\
"""
                        )
                    ],
                    provider="anthropic",
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

**Detailed Information:**

**Mistborn: The Final Empire** is an epic fantasy novel by Brandon Sanderson, published in 2006. This 544-page book marks the beginning of the original Mistborn trilogy and is renowned for introducing one of the most intricate magic systems in modern fantasy literature.

**Key Highlights:**
- **Setting**: A dark fantasy world ruled by an immortal tyrant
- **Magic System**: Features "Allomancy," a unique system where metals grant magical powers when ingested and burned
- **Protagonist**: Vin, a street urchin who discovers her incredible potential
- **Themes**: Revolution, identity, loyalty, and the cost of freedom

**Recommendation Score: 9/10**

This book is highly recommended for:
- Fantasy readers seeking innovative magic systems
- Those who enjoy character-driven narratives with strong protagonists
- Readers looking for a well-plotted trilogy starter with excellent world-building
- Anyone who appreciates Brandon Sanderson's meticulous storytelling

**Why the high score**: The novel combines compelling character development, an intricate and logical magic system, engaging plot twists, and excellent pacing. It's considered a modern classic in the fantasy genre and has sparked a thriving fan community. The only minor deduction is that some readers may find the pacing slow in the opening chapters, but this pays off magnificently as the story progresses.\
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
                        Text(
                            text="I'll look up the book information for you using that ISBN."
                        ),
                        ToolCall(
                            id="toolu_bdrk_019LKRBgq9bRvJRLZmPZiycu",
                            name="get_book_info",
                            args='{"isbn": "0-7653-1178-X"}',
                        ),
                    ],
                    provider="anthropic",
                    model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "citations": None,
                                "text": "I'll look up the book information for you using that ISBN.",
                                "type": "text",
                            },
                            {
                                "id": "toolu_bdrk_019LKRBgq9bRvJRLZmPZiycu",
                                "input": {"isbn": "0-7653-1178-X"},
                                "name": "get_book_info",
                                "type": "tool_use",
                            },
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="toolu_bdrk_019LKRBgq9bRvJRLZmPZiycu",
                            name="get_book_info",
                            value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Great! Here's the detailed information for the book:

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

This is the first book in Brandon Sanderson's acclaimed Mistborn trilogy. It's an epic fantasy novel featuring an intricate magic system based on metal alloys, complex world-building, and compelling characters.

**Recommendation Score: 9/10**

**Why I recommend it:**
- **Exceptional worldbuilding**: Sanderson creates a rich, detailed world with a unique magic system
- **Compelling narrative**: The story follows Vin, a street orphan who discovers her hidden powers, offering both personal growth and high-stakes adventure
- **Strong character development**: The protagonist's journey is particularly well-crafted
- **Page-turner quality**: At 544 pages, it maintains excellent pacing despite its length
- **Highly regarded**: This series is beloved by fantasy fans and critics alike
- **Great starting point**: Perfect for those new to Brandon Sanderson or fantasy in general

**Best for:** Fans of epic fantasy, intricate magic systems, and character-driven narratives. Also excellent for readers who enjoy series.\
"""
                        )
                    ],
                    provider="anthropic",
                    model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "citations": None,
                                "text": """\
Great! Here's the detailed information for the book:

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

This is the first book in Brandon Sanderson's acclaimed Mistborn trilogy. It's an epic fantasy novel featuring an intricate magic system based on metal alloys, complex world-building, and compelling characters.

**Recommendation Score: 9/10**

**Why I recommend it:**
- **Exceptional worldbuilding**: Sanderson creates a rich, detailed world with a unique magic system
- **Compelling narrative**: The story follows Vin, a street orphan who discovers her hidden powers, offering both personal growth and high-stakes adventure
- **Strong character development**: The protagonist's journey is particularly well-crafted
- **Page-turner quality**: At 544 pages, it maintains excellent pacing despite its length
- **Highly regarded**: This series is beloved by fantasy fans and critics alike
- **Great starting point**: Perfect for those new to Brandon Sanderson or fantasy in general

**Best for:** Fans of epic fantasy, intricate magic systems, and character-driven narratives. Also excellent for readers who enjoy series.\
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
                            id="toolu_bdrk_01XydmuHNB6V8EqaK1HpjNvr",
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
                                "id": "toolu_bdrk_01XydmuHNB6V8EqaK1HpjNvr",
                                "name": "get_book_info",
                                "input": {"isbn": "0-7653-1178-X"},
                            }
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="toolu_bdrk_01XydmuHNB6V8EqaK1HpjNvr",
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

**Book Details:**
- **Title:** Mistborn: The Final Empire
- **Author:** Brandon Sanderson
- **Pages:** 544
- **Publication Year:** 2006
- **ISBN:** 0-7653-1178-X

**Recommendation Score: 9/10**

**Why this book is highly recommended:**

1. **Exceptional World-Building:** Sanderson creates an intricate fantasy world with unique magic systems based on metal alloys (Allomancy), which is incredibly creative and well-explained.

2. **Strong Character Development:** The protagonist Vin's journey from slave to empowered mistborn is compelling and emotionally resonant.

3. **Engaging Plot:** The story combines heist elements, political intrigue, and epic fantasy, making it a page-turner that keeps readers invested.

4. **Series Potential:** This is the first book in the original Mistborn trilogy, offering excellent value for fantasy readers who want to dive into a longer saga.

5. **Accessibility:** Despite its complexity, Sanderson's prose is clear and engaging, making it accessible to both newcomers to fantasy and seasoned readers.

**Best For:** Fantasy enthusiasts, particularly those who enjoy intricate magic systems, character-driven narratives, and epic world-building. A perfect starting point for Brandon Sanderson's work.\
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
Here's the detailed information for the book:

```json
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}
```

**Book Details:**
- **Title:** Mistborn: The Final Empire
- **Author:** Brandon Sanderson
- **Pages:** 544
- **Publication Year:** 2006
- **ISBN:** 0-7653-1178-X

**Recommendation Score: 9/10**

**Why this book is highly recommended:**

1. **Exceptional World-Building:** Sanderson creates an intricate fantasy world with unique magic systems based on metal alloys (Allomancy), which is incredibly creative and well-explained.

2. **Strong Character Development:** The protagonist Vin's journey from slave to empowered mistborn is compelling and emotionally resonant.

3. **Engaging Plot:** The story combines heist elements, political intrigue, and epic fantasy, making it a page-turner that keeps readers invested.

4. **Series Potential:** This is the first book in the original Mistborn trilogy, offering excellent value for fantasy readers who want to dive into a longer saga.

5. **Accessibility:** Despite its complexity, Sanderson's prose is clear and engaging, making it accessible to both newcomers to fantasy and seasoned readers.

**Best For:** Fantasy enthusiasts, particularly those who enjoy intricate magic systems, character-driven narratives, and epic world-building. A perfect starting point for Brandon Sanderson's work.\
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
                            id="toolu_bdrk_01BwXgYx99L8TRz2EsaQMcff",
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
                                "id": "toolu_bdrk_01BwXgYx99L8TRz2EsaQMcff",
                                "name": "get_book_info",
                                "input": {"isbn": "0-7653-1178-X"},
                            }
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="toolu_bdrk_01BwXgYx99L8TRz2EsaQMcff",
                            name="get_book_info",
                            value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Here is the book information in the requested JSON format:

```json
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}
```

**Book Details & Recommendation:**

**Title:** Mistborn: The Final Empire
**Author:** Brandon Sanderson
**Pages:** 544
**Publication Year:** 2006

**Recommendation Score:** 9/10

**Why This Book is Highly Recommended:**

Mistborn: The Final Empire is the first book in Brandon Sanderson's acclaimed Mistborn trilogy and is widely considered one of the best fantasy novels of the 21st century. Here's why:

- **Compelling Magic System:** Sanderson is renowned for creating intricate, rule-based magic systems, and Mistborn features an innovative "allomancy" system that's both creative and internally consistent.

- **Strong Character Development:** The protagonist, Kel, experiences significant growth throughout the narrative, making her journey deeply engaging.

- **Plot Twists:** The book features several major plot revelations that recontextualize the entire story in a satisfying way.

- **World-Building:** The oppressive Final Empire setting is richly detailed and atmospheric, creating a compelling backdrop for the story.

- **Accessibility:** At 544 pages, it's substantial but not overwhelming, making it a great entry point for readers new to epic fantasy.

This book is perfect for fans of fantasy who appreciate innovative magic systems, complex characters, and intricate plots. Highly recommended for both seasoned fantasy readers and those looking to explore the genre!\
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
Here is the book information in the requested JSON format:

```json
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}
```

**Book Details & Recommendation:**

**Title:** Mistborn: The Final Empire
**Author:** Brandon Sanderson
**Pages:** 544
**Publication Year:** 2006

**Recommendation Score:** 9/10

**Why This Book is Highly Recommended:**

Mistborn: The Final Empire is the first book in Brandon Sanderson's acclaimed Mistborn trilogy and is widely considered one of the best fantasy novels of the 21st century. Here's why:

- **Compelling Magic System:** Sanderson is renowned for creating intricate, rule-based magic systems, and Mistborn features an innovative "allomancy" system that's both creative and internally consistent.

- **Strong Character Development:** The protagonist, Kel, experiences significant growth throughout the narrative, making her journey deeply engaging.

- **Plot Twists:** The book features several major plot revelations that recontextualize the entire story in a satisfying way.

- **World-Building:** The oppressive Final Empire setting is richly detailed and atmospheric, creating a compelling backdrop for the story.

- **Accessibility:** At 544 pages, it's substantial but not overwhelming, making it a great entry point for readers new to epic fantasy.

This book is perfect for fans of fantasy who appreciate innovative magic systems, complex characters, and intricate plots. Highly recommended for both seasoned fantasy readers and those looking to explore the genre!\
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
            "n_chunks": 121,
        }
    }
)
