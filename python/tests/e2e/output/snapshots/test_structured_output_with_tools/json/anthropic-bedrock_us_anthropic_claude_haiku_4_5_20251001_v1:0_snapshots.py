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
                        id="toolu_bdrk_01WkrVv7daF1uNS7qciX2hjf",
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
                            "id": "toolu_bdrk_01WkrVv7daF1uNS7qciX2hjf",
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
                        id="toolu_bdrk_01WkrVv7daF1uNS7qciX2hjf",
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

**Additional Recommendation:**

**Book:** Mistborn: The Final Empire
**Recommendation Score:** 9/10

**Why I recommend it:**
- **Engaging World-Building**: Brandon Sanderson is renowned for his intricate magic systems, and this book features the innovative "Mistborn" system with unique powers based on ingesting metals
- **Compelling Story**: The novel combines epic fantasy with a heist narrative, following Vin, a street orphan who discovers she's a Mistborn with extraordinary powers
- **Character Development**: Strong character arcs with a diverse cast that evolves throughout the 544-page journey
- **Page-Turner**: Despite its substantial length, it's highly engaging and difficult to put down
- **Series Potential**: The first in a trilogy, it sets up an excellent foundation for continued reading
- **Critical Acclaim**: Widely praised by fantasy readers and won multiple awards

**Best For:** Readers who enjoy epic fantasy, magic systems, character-driven narratives, and don't mind longer books with complex world-building.\
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
Based on the book information retrieved, here's the detailed information:

```json
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}
```

**Additional Recommendation:**

**Book:** Mistborn: The Final Empire
**Recommendation Score:** 9/10

**Why I recommend it:**
- **Engaging World-Building**: Brandon Sanderson is renowned for his intricate magic systems, and this book features the innovative "Mistborn" system with unique powers based on ingesting metals
- **Compelling Story**: The novel combines epic fantasy with a heist narrative, following Vin, a street orphan who discovers she's a Mistborn with extraordinary powers
- **Character Development**: Strong character arcs with a diverse cast that evolves throughout the 544-page journey
- **Page-Turner**: Despite its substantial length, it's highly engaging and difficult to put down
- **Series Potential**: The first in a trilogy, it sets up an excellent foundation for continued reading
- **Critical Acclaim**: Widely praised by fantasy readers and won multiple awards

**Best For:** Readers who enjoy epic fantasy, magic systems, character-driven narratives, and don't mind longer books with complex world-building.\
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
)
async_snapshot = snapshot(
    {
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
                        id="toolu_bdrk_01RQq6gj1vRtN5DvKV7vhEpm",
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
                            "id": "toolu_bdrk_01RQq6gj1vRtN5DvKV7vhEpm",
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
                        id="toolu_bdrk_01RQq6gj1vRtN5DvKV7vhEpm",
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

**Book Information:**
- **Title:** Mistborn: The Final Empire
- **Author:** Brandon Sanderson
- **Pages:** 544
- **Publication Year:** 2006

**Recommendation Score: 8.5/10** ⭐

**Why This Book is Recommended:**

1. **Exceptional World-Building** - Sanderson creates an intricate fantasy world with a unique magic system based on metal ingestion (Allomancy), which is innovative and well-developed.

2. **Compelling Story** - The narrative follows Vin, a street urchin who discovers her powers and becomes entangled in a rebellion against an immortal tyrant. The plot is engaging with excellent pacing.

3. **Strong Character Development** - Vin's character arc is particularly powerful, showing her growth from a frightened orphan to a confident hero.

4. **Perfect for Fantasy Lovers** - Whether you're new to fantasy or a seasoned reader, this book offers something special. It's the first in an acclaimed trilogy.

5. **Well-Written Prose** - Sanderson's writing is clear, immersive, and maintains excellent momentum throughout the 544 pages.

**Best For:** Fantasy enthusiasts, readers who enjoy magic systems with clear rules, and those seeking epic tales with strong female protagonists.\
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
```json
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}
```

**Book Information:**
- **Title:** Mistborn: The Final Empire
- **Author:** Brandon Sanderson
- **Pages:** 544
- **Publication Year:** 2006

**Recommendation Score: 8.5/10** ⭐

**Why This Book is Recommended:**

1. **Exceptional World-Building** - Sanderson creates an intricate fantasy world with a unique magic system based on metal ingestion (Allomancy), which is innovative and well-developed.

2. **Compelling Story** - The narrative follows Vin, a street urchin who discovers her powers and becomes entangled in a rebellion against an immortal tyrant. The plot is engaging with excellent pacing.

3. **Strong Character Development** - Vin's character arc is particularly powerful, showing her growth from a frightened orphan to a confident hero.

4. **Perfect for Fantasy Lovers** - Whether you're new to fantasy or a seasoned reader, this book offers something special. It's the first in an acclaimed trilogy.

5. **Well-Written Prose** - Sanderson's writing is clear, immersive, and maintains excellent momentum throughout the 544 pages.

**Best For:** Fantasy enthusiasts, readers who enjoy magic systems with clear rules, and those seeking epic tales with strong female protagonists.\
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
)
stream_snapshot = snapshot(
    {
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
                        id="toolu_bdrk_01P9h7S6MgaYCKf9DbtBmQv7",
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
                            "id": "toolu_bdrk_01P9h7S6MgaYCKf9DbtBmQv7",
                            "name": "get_book_info",
                            "input": {"isbn": "0-7653-1178-X"},
                        }
                    ],
                },
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="toolu_bdrk_01P9h7S6MgaYCKf9DbtBmQv7",
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

**Book Summary & Recommendation:**

**Mistborn: The Final Empire** is an epic fantasy novel by Brandon Sanderson, first published in 2006. This is the first book in the acclaimed Mistborn trilogy.

**Key Details:**
- **Title:** Mistborn: The Final Empire
- **Author:** Brandon Sanderson
- **Pages:** 544
- **Publication Year:** 2006

**About the Book:**
Mistborn is a groundbreaking fantasy novel set in a sprawling world ruled by an immortal tyrant called the Lord Ruler. The story follows Vin, a street orphan who discovers she possesses extraordinary magical abilities called "Allomancy" - the power to ingest metals and use them to grant superhuman abilities. Vin is recruited into a crew attempting to overthrow the oppressive Lord Ruler in an ambitious heist-fantasy hybrid narrative.

**Recommendation Score: 9/10**

**Why I Recommend It:**
- ✅ Unique magic system that's intricate and well-thought-out
- ✅ Compelling protagonist with great character development
- ✅ Excellent blend of fantasy, heist, and political intrigue
- ✅ Fast-paced and hard to put down
- ✅ Well-written by one of today's most prolific fantasy authors
- ✅ Great starting point for Brandon Sanderson's works
- ⚠️ The 544 pages might be lengthy for some casual readers, but it doesn't feel slow

**Perfect For:** Fantasy fans, especially those who enjoy intricate magic systems, character-driven stories, and epic world-building.\
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
```json
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006
}
```

**Book Summary & Recommendation:**

**Mistborn: The Final Empire** is an epic fantasy novel by Brandon Sanderson, first published in 2006. This is the first book in the acclaimed Mistborn trilogy.

**Key Details:**
- **Title:** Mistborn: The Final Empire
- **Author:** Brandon Sanderson
- **Pages:** 544
- **Publication Year:** 2006

**About the Book:**
Mistborn is a groundbreaking fantasy novel set in a sprawling world ruled by an immortal tyrant called the Lord Ruler. The story follows Vin, a street orphan who discovers she possesses extraordinary magical abilities called "Allomancy" - the power to ingest metals and use them to grant superhuman abilities. Vin is recruited into a crew attempting to overthrow the oppressive Lord Ruler in an ambitious heist-fantasy hybrid narrative.

**Recommendation Score: 9/10**

**Why I Recommend It:**
- ✅ Unique magic system that's intricate and well-thought-out
- ✅ Compelling protagonist with great character development
- ✅ Excellent blend of fantasy, heist, and political intrigue
- ✅ Fast-paced and hard to put down
- ✅ Well-written by one of today's most prolific fantasy authors
- ✅ Great starting point for Brandon Sanderson's works
- ⚠️ The 544 pages might be lengthy for some casual readers, but it doesn't feel slow

**Perfect For:** Fantasy fans, especially those who enjoy intricate magic systems, character-driven stories, and epic world-building.\
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
        "n_chunks": 127,
    }
)
async_stream_snapshot = snapshot(
    {
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
                    Text(text="I'll look up the book information for you."),
                    ToolCall(
                        id="toolu_bdrk_01NtaA4fNN18GrU1osAH7wJc",
                        name="get_book_info",
                        args='{"isbn": "0-7653-1178-X"}',
                    ),
                ],
                provider="anthropic-bedrock",
                model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                raw_message={
                    "role": "assistant",
                    "content": [
                        {
                            "type": "text",
                            "text": "I'll look up the book information for you.",
                        },
                        {
                            "type": "tool_use",
                            "id": "toolu_bdrk_01NtaA4fNN18GrU1osAH7wJc",
                            "name": "get_book_info",
                            "input": {"isbn": "0-7653-1178-X"},
                        },
                    ],
                },
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="toolu_bdrk_01NtaA4fNN18GrU1osAH7wJc",
                        name="get_book_info",
                        value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
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
1. **Exceptional World-Building:** Sanderson creates a richly detailed fantasy world with a unique magic system based on metal ingestion
2. **Compelling Characters:** The protagonist Vin's journey from slavery to self-discovery is engaging and emotionally resonant
3. **Page-Turner Plot:** Despite being 544 pages, it's highly readable with great pacing and multiple plot twists
4. **Strong Fandom:** This is the first book in the Mistborn series and has built a devoted following
5. **Accessible Fantasy:** While complex, it's more approachable than many epic fantasy novels

**Best for:** Readers who enjoy fantasy with intricate magic systems, strong character development, and an intriguing rebellion narrative. Perfect for fans of Brandon Sanderson or fantasy epics in general.

The only reason I'm not giving it a 10/10 is that the beginning can feel a bit slow for some readers, but it's absolutely worth pushing through!\
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
1. **Exceptional World-Building:** Sanderson creates a richly detailed fantasy world with a unique magic system based on metal ingestion
2. **Compelling Characters:** The protagonist Vin's journey from slavery to self-discovery is engaging and emotionally resonant
3. **Page-Turner Plot:** Despite being 544 pages, it's highly readable with great pacing and multiple plot twists
4. **Strong Fandom:** This is the first book in the Mistborn series and has built a devoted following
5. **Accessible Fantasy:** While complex, it's more approachable than many epic fantasy novels

**Best for:** Readers who enjoy fantasy with intricate magic systems, strong character development, and an intriguing rebellion narrative. Perfect for fans of Brandon Sanderson or fantasy epics in general.

The only reason I'm not giving it a 10/10 is that the beginning can feel a bit slow for some readers, but it's absolutely worth pushing through!\
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
        "n_chunks": 88,
    }
)
