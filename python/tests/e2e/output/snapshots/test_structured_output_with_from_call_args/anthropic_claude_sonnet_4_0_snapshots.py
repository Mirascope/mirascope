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
            "provider_id": "anthropic",
            "model_id": "anthropic/claude-sonnet-4-0",
            "provider_model_name": "claude-sonnet-4-0",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 427,
                "output_tokens": 257,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "Usage(cache_creation=CacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=427, output_tokens=257, server_tool_use=None, service_tier='standard')",
                "total_tokens": 684,
            },
            "from_call_args": {
                "author": "Patrick Rothfuss",
                "title": "The Name of the Wind",
            },
            "messages": [
                SystemMessage(
                    content=Text(
                        text="Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output."
                    )
                ),
                UserMessage(
                    content=[
                        Text(
                            text="Summarize the book The Name of the Wind by Patrick Rothfuss."
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text='{"summary": "The Name of the Wind is the first book in Patrick Rothfuss\'s Kingkiller Chronicle series. It follows Kvothe, a legendary figure who is now living in hiding as an innkeeper named Kote. The story is framed as Kvothe telling his life story to a chronicler over three days. The book covers Kvothe\'s childhood as part of a traveling troupe of performers called the Edema Ruh, the tragic murder of his family by mysterious beings called the Chandrian, and his subsequent years living as a street orphan in the city of Tarbean. Eventually, Kvothe gains admission to the University, a prestigious institution for learning sympathy (a form of magic), where he studies under masters while struggling with poverty and making both allies and enemies. Throughout his journey, Kvothe demonstrates exceptional musical talent, quick wit, and growing magical abilities, while being driven by his quest for knowledge about the Chandrian and his desire to learn the name of the wind - a form of naming magic that represents true understanding and power over the fundamental forces of the world."}'
                        )
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "id": "toolu_01XeoDFcXb9j3dsa3drJwbMP",
                                "input": {
                                    "summary": "The Name of the Wind is the first book in Patrick Rothfuss's Kingkiller Chronicle series. It follows Kvothe, a legendary figure who is now living in hiding as an innkeeper named Kote. The story is framed as Kvothe telling his life story to a chronicler over three days. The book covers Kvothe's childhood as part of a traveling troupe of performers called the Edema Ruh, the tragic murder of his family by mysterious beings called the Chandrian, and his subsequent years living as a street orphan in the city of Tarbean. Eventually, Kvothe gains admission to the University, a prestigious institution for learning sympathy (a form of magic), where he studies under masters while struggling with poverty and making both allies and enemies. Throughout his journey, Kvothe demonstrates exceptional musical talent, quick wit, and growing magical abilities, while being driven by his quest for knowledge about the Chandrian and his desire to learn the name of the wind - a form of naming magic that represents true understanding and power over the fundamental forces of the world."
                                },
                                "name": "__mirascope_formatted_output_tool__",
                                "type": "tool_use",
                            }
                        ],
                    },
                ),
            ],
            "format": {
                "name": "Book",
                "description": "A book with title, author, and summary.",
                "schema": {
                    "description": "A book with title, author, and summary.",
                    "properties": {"summary": {"title": "Summary", "type": "string"}},
                    "required": ["summary"],
                    "title": "Book",
                    "type": "object",
                },
                "mode": "tool",
                "formatting_instructions": "Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output.",
            },
            "tools": [],
        }
    }
)
async_snapshot = snapshot(
    {
        "response": {
            "provider_id": "anthropic",
            "model_id": "anthropic/claude-sonnet-4-0",
            "provider_model_name": "claude-sonnet-4-0",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 427,
                "output_tokens": 273,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "Usage(cache_creation=CacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=427, output_tokens=273, server_tool_use=None, service_tier='standard')",
                "total_tokens": 700,
            },
            "from_call_args": {
                "author": "Patrick Rothfuss",
                "title": "The Name of the Wind",
            },
            "messages": [
                SystemMessage(
                    content=Text(
                        text="Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output."
                    )
                ),
                UserMessage(
                    content=[
                        Text(
                            text="Summarize the book The Name of the Wind by Patrick Rothfuss."
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text='{"summary": "The Name of the Wind is the first book in Patrick Rothfuss\'s Kingkiller Chronicle series. It tells the story of Kvothe, a legendary figure who has become a simple innkeeper in hiding. The narrative is framed as Kvothe recounting his life story to a chronicler over three days. The book covers Kvothe\'s childhood as part of a traveling troupe of performers called the Edema Ruh, the tragic murder of his family by mysterious beings called the Chandrian, and his subsequent years as a street orphan in the city of Tarbean. The story follows his eventual admission to the University, a prestigious institution for learning magic and other disciplines, where he studies sympathy (a form of magic), naming (the ability to know the true names of things), and artificery. Throughout his time at the University, Kvothe struggles with poverty, makes both friends and enemies, and begins his quest for knowledge about the Chandrian to avenge his family. The book is renowned for its beautiful prose, intricate magic system, and rich world-building, establishing Kvothe as both a gifted student and a figure of growing legend."}'
                        )
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "id": "toolu_015VDLotgxy3Bpj8y5VBDxpZ",
                                "input": {
                                    "summary": "The Name of the Wind is the first book in Patrick Rothfuss's Kingkiller Chronicle series. It tells the story of Kvothe, a legendary figure who has become a simple innkeeper in hiding. The narrative is framed as Kvothe recounting his life story to a chronicler over three days. The book covers Kvothe's childhood as part of a traveling troupe of performers called the Edema Ruh, the tragic murder of his family by mysterious beings called the Chandrian, and his subsequent years as a street orphan in the city of Tarbean. The story follows his eventual admission to the University, a prestigious institution for learning magic and other disciplines, where he studies sympathy (a form of magic), naming (the ability to know the true names of things), and artificery. Throughout his time at the University, Kvothe struggles with poverty, makes both friends and enemies, and begins his quest for knowledge about the Chandrian to avenge his family. The book is renowned for its beautiful prose, intricate magic system, and rich world-building, establishing Kvothe as both a gifted student and a figure of growing legend."
                                },
                                "name": "__mirascope_formatted_output_tool__",
                                "type": "tool_use",
                            }
                        ],
                    },
                ),
            ],
            "format": {
                "name": "Book",
                "description": "A book with title, author, and summary.",
                "schema": {
                    "description": "A book with title, author, and summary.",
                    "properties": {"summary": {"title": "Summary", "type": "string"}},
                    "required": ["summary"],
                    "title": "Book",
                    "type": "object",
                },
                "mode": "tool",
                "formatting_instructions": "Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output.",
            },
            "tools": [],
        }
    }
)
stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "anthropic",
            "model_id": "anthropic/claude-sonnet-4-0",
            "provider_model_name": "claude-sonnet-4-0",
            "finish_reason": None,
            "messages": [
                SystemMessage(
                    content=Text(
                        text="Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output."
                    )
                ),
                UserMessage(
                    content=[
                        Text(
                            text="Summarize the book The Name of the Wind by Patrick Rothfuss."
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text='{"summary": "The Name of the Wind is the first book in Patrick Rothfuss\'s Kingkiller Chronicle trilogy. It follows Kvothe, a legendary figure who is now living in hiding as an innkeeper named Kote. The story is framed as Kvothe telling his life story to a chronicler over three days. The book covers Kvothe\'s childhood as part of a traveling troupe of performers called the Edema Ruh, the tragic murder of his family by mysterious beings called the Chandrian, and his subsequent life as a street orphan. The narrative then follows his time at the University, where he studies sympathy (a form of magic), struggles with poverty, and begins his education in naming - the art of understanding the true nature of things. Throughout, Kvothe searches for information about the Chandrian to avenge his family\'s death. The book establishes Kvothe as a brilliant but often reckless young man with extraordinary talents in music, magic, and learning, while building a rich fantasy world with detailed magic systems and mythology."}'
                        )
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "tool_use",
                                "id": "toolu_011Q5K5obvvinC6GNC9nWAXs",
                                "name": "__mirascope_formatted_output_tool__",
                                "input": {
                                    "summary": "The Name of the Wind is the first book in Patrick Rothfuss's Kingkiller Chronicle trilogy. It follows Kvothe, a legendary figure who is now living in hiding as an innkeeper named Kote. The story is framed as Kvothe telling his life story to a chronicler over three days. The book covers Kvothe's childhood as part of a traveling troupe of performers called the Edema Ruh, the tragic murder of his family by mysterious beings called the Chandrian, and his subsequent life as a street orphan. The narrative then follows his time at the University, where he studies sympathy (a form of magic), struggles with poverty, and begins his education in naming - the art of understanding the true nature of things. Throughout, Kvothe searches for information about the Chandrian to avenge his family's death. The book establishes Kvothe as a brilliant but often reckless young man with extraordinary talents in music, magic, and learning, while building a rich fantasy world with detailed magic systems and mythology."
                                },
                            }
                        ],
                    },
                ),
            ],
            "format": {
                "name": "Book",
                "description": "A book with title, author, and summary.",
                "schema": {
                    "description": "A book with title, author, and summary.",
                    "properties": {"summary": {"title": "Summary", "type": "string"}},
                    "required": ["summary"],
                    "title": "Book",
                    "type": "object",
                },
                "mode": "tool",
                "formatting_instructions": "Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output.",
            },
            "tools": [],
            "usage": {
                "input_tokens": 427,
                "output_tokens": 250,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 677,
            },
            "n_chunks": 146,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "anthropic",
            "model_id": "anthropic/claude-sonnet-4-0",
            "provider_model_name": "claude-sonnet-4-0",
            "finish_reason": None,
            "messages": [
                SystemMessage(
                    content=Text(
                        text="Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output."
                    )
                ),
                UserMessage(
                    content=[
                        Text(
                            text="Summarize the book The Name of the Wind by Patrick Rothfuss."
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text='{"summary": "The Name of the Wind is the first book in Patrick Rothfuss\'s Kingkiller Chronicle trilogy. It follows Kvothe, a legendary figure who recounts his life story to a chronicler. The tale begins with Kvothe\'s childhood as part of a traveling troupe of performers called the Edema Ruh. After his family is brutally murdered by mysterious beings called the Chandrian, young Kvothe becomes an orphan living on the streets. Driven by a desire for knowledge and revenge, he eventually gains admission to the University, a prestigious institution where students learn sympathy (a form of magic), alchemy, and other scholarly pursuits. At the University, Kvothe proves to be exceptionally talented but also impulsive and proud, leading to conflicts with wealthy student Ambrose and gaining the attention of various masters. The story alternates between Kvothe\'s past adventures and the present day, where he has become an innkeeper in hiding, seemingly having lost his legendary powers. The book explores themes of storytelling, the power of names and music, love, loss, and the difference between legend and reality."}'
                        )
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "tool_use",
                                "id": "toolu_011pcPz33XZnrbwjSfDSZPXE",
                                "name": "__mirascope_formatted_output_tool__",
                                "input": {
                                    "summary": "The Name of the Wind is the first book in Patrick Rothfuss's Kingkiller Chronicle trilogy. It follows Kvothe, a legendary figure who recounts his life story to a chronicler. The tale begins with Kvothe's childhood as part of a traveling troupe of performers called the Edema Ruh. After his family is brutally murdered by mysterious beings called the Chandrian, young Kvothe becomes an orphan living on the streets. Driven by a desire for knowledge and revenge, he eventually gains admission to the University, a prestigious institution where students learn sympathy (a form of magic), alchemy, and other scholarly pursuits. At the University, Kvothe proves to be exceptionally talented but also impulsive and proud, leading to conflicts with wealthy student Ambrose and gaining the attention of various masters. The story alternates between Kvothe's past adventures and the present day, where he has become an innkeeper in hiding, seemingly having lost his legendary powers. The book explores themes of storytelling, the power of names and music, love, loss, and the difference between legend and reality."
                                },
                            }
                        ],
                    },
                ),
            ],
            "format": {
                "name": "Book",
                "description": "A book with title, author, and summary.",
                "schema": {
                    "description": "A book with title, author, and summary.",
                    "properties": {"summary": {"title": "Summary", "type": "string"}},
                    "required": ["summary"],
                    "title": "Book",
                    "type": "object",
                },
                "mode": "tool",
                "formatting_instructions": "Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output.",
            },
            "tools": [],
            "usage": {
                "input_tokens": 427,
                "output_tokens": 265,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 692,
            },
            "n_chunks": 160,
        }
    }
)
