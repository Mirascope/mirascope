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
            "model_id": "anthropic/claude-sonnet-4-5",
            "provider_model_name": "claude-sonnet-4-5",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 744,
                "output_tokens": 320,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "Usage(cache_creation=CacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=744, output_tokens=320, server_tool_use=None, service_tier='standard')",
                "total_tokens": 1064,
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
                            text='{"summary": "The Name of the Wind is the first book in The Kingkiller Chronicle trilogy. It follows Kvothe, a legendary figure who has become a humble innkeeper, as he recounts his life story to a chronicler. The narrative primarily takes place in Kvothe\'s past, beginning with his childhood as part of a traveling troupe of performers called the Edema Ruh. After his family and troupe are brutally murdered by the mysterious Chandrian\\u2014mythical beings from children\'s stories\\u2014young Kvothe is left orphaned and must survive on the streets. Driven by a desire for knowledge and revenge, he eventually gains admission to the University, a prestigious institution for studying sympathy (a magic system based on creating connections between objects) and other arts. At the University, Kvothe quickly becomes known for his exceptional talent in music, sympathy, and artificing, but also for his reckless behavior and ongoing feud with a wealthy fellow student. Throughout the story, he struggles with poverty, pursues forbidden knowledge about the Chandrian and the mysterious Amyr, and falls in love with Denna, an enigmatic woman who repeatedly enters and exits his life. The book weaves together themes of storytelling, loss, revenge, and the making of a legend, while maintaining a melancholic undertone as the present-day Kvothe seems diminished from his former glory."}'
                        )
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-5",
                    provider_model_name="claude-sonnet-4-5",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "id": "toolu_01RLXJEv2nNwf9Bg4kkhzHPP",
                                "input": {
                                    "summary": "The Name of the Wind is the first book in The Kingkiller Chronicle trilogy. It follows Kvothe, a legendary figure who has become a humble innkeeper, as he recounts his life story to a chronicler. The narrative primarily takes place in Kvothe's past, beginning with his childhood as part of a traveling troupe of performers called the Edema Ruh. After his family and troupe are brutally murdered by the mysterious Chandrian—mythical beings from children's stories—young Kvothe is left orphaned and must survive on the streets. Driven by a desire for knowledge and revenge, he eventually gains admission to the University, a prestigious institution for studying sympathy (a magic system based on creating connections between objects) and other arts. At the University, Kvothe quickly becomes known for his exceptional talent in music, sympathy, and artificing, but also for his reckless behavior and ongoing feud with a wealthy fellow student. Throughout the story, he struggles with poverty, pursues forbidden knowledge about the Chandrian and the mysterious Amyr, and falls in love with Denna, an enigmatic woman who repeatedly enters and exits his life. The book weaves together themes of storytelling, loss, revenge, and the making of a legend, while maintaining a melancholic undertone as the present-day Kvothe seems diminished from his former glory."
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
            "model_id": "anthropic/claude-sonnet-4-5",
            "provider_model_name": "claude-sonnet-4-5",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 744,
                "output_tokens": 289,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "Usage(cache_creation=CacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=744, output_tokens=289, server_tool_use=None, service_tier='standard')",
                "total_tokens": 1033,
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
                            text="{\"summary\": \"The Name of the Wind is the first book in Patrick Rothfuss's Kingkiller Chronicle trilogy. It follows Kvothe, a legendary figure who is now living in disguise as an innkeeper named Kote. The story is told primarily through Kvothe's own recounting of his past to a chronicler. Born into a traveling troupe of performers called the Edema Ruh, Kvothe's idyllic childhood is shattered when his entire troupe is slaughtered by the mysterious Chandrian, a group of legendary beings. Orphaned and driven by revenge, Kvothe struggles to survive on the streets before eventually gaining admission to the University, a prestigious school for magic and learning. There, despite his exceptional talents in sympathy (a form of magic) and music, he faces poverty, makes both friends and enemies, and begins his quest to uncover the truth about the Chandrian. The book weaves together themes of loss, ambition, love, and the power of storytelling, while establishing Kvothe as a complex protagonist whose legendary reputation contrasts with his current humble circumstances. The narrative sets up numerous mysteries about Kvothe's past and hints at the tragic events that led to his present situation.\"}"
                        )
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-5",
                    provider_model_name="claude-sonnet-4-5",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "id": "toolu_0168RhsneKPAKTorP4RXzAjn",
                                "input": {
                                    "summary": "The Name of the Wind is the first book in Patrick Rothfuss's Kingkiller Chronicle trilogy. It follows Kvothe, a legendary figure who is now living in disguise as an innkeeper named Kote. The story is told primarily through Kvothe's own recounting of his past to a chronicler. Born into a traveling troupe of performers called the Edema Ruh, Kvothe's idyllic childhood is shattered when his entire troupe is slaughtered by the mysterious Chandrian, a group of legendary beings. Orphaned and driven by revenge, Kvothe struggles to survive on the streets before eventually gaining admission to the University, a prestigious school for magic and learning. There, despite his exceptional talents in sympathy (a form of magic) and music, he faces poverty, makes both friends and enemies, and begins his quest to uncover the truth about the Chandrian. The book weaves together themes of loss, ambition, love, and the power of storytelling, while establishing Kvothe as a complex protagonist whose legendary reputation contrasts with his current humble circumstances. The narrative sets up numerous mysteries about Kvothe's past and hints at the tragic events that led to his present situation."
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
            "model_id": "anthropic/claude-sonnet-4-5",
            "provider_model_name": "claude-sonnet-4-5",
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
                            text='{"summary": "The Name of the Wind is the first book in Patrick Rothfuss\'s Kingkiller Chronicle trilogy. It follows Kvothe, a legendary figure who has become an innkeeper in hiding, as he recounts his life story to a chronicler. The narrative shifts between the present day at the Waystone Inn and Kvothe\'s past, beginning with his childhood as part of a traveling troupe of performers called the Edema Ruh. After his family and troupe are brutally murdered by the mysterious Chandrian—mythical beings of evil—young Kvothe survives alone and eventually makes his way to the city of Tarbean, where he lives as a street urchin for years. Driven by a desire for knowledge and revenge, he gains admission to the University, a prestigious school of magic and learning, at the remarkably young age of fifteen. At the University, Kvothe proves to be extraordinarily talented but struggles with poverty, makes both friends and enemies, and begins his study of sympathy (the magic system), naming, and the ancient art of shaping. Throughout the story, he searches for information about the Chandrian while dealing with his rivalry with a wealthy student named Ambrose and his complicated feelings for Denna, a mysterious woman he loves but can never quite reach. The book is notable for its beautiful prose, intricate world-building, and the frame narrative structure that creates mystery around what transformed the legendary Kvothe into a seemingly ordinary innkeeper."}'
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
                                "id": "toolu_01VQFHUYH3vG3aRGrGh72ywC",
                                "name": "__mirascope_formatted_output_tool__",
                                "input": {
                                    "summary": "The Name of the Wind is the first book in Patrick Rothfuss's Kingkiller Chronicle trilogy. It follows Kvothe, a legendary figure who has become an innkeeper in hiding, as he recounts his life story to a chronicler. The narrative shifts between the present day at the Waystone Inn and Kvothe's past, beginning with his childhood as part of a traveling troupe of performers called the Edema Ruh. After his family and troupe are brutally murdered by the mysterious Chandrian—mythical beings of evil—young Kvothe survives alone and eventually makes his way to the city of Tarbean, where he lives as a street urchin for years. Driven by a desire for knowledge and revenge, he gains admission to the University, a prestigious school of magic and learning, at the remarkably young age of fifteen. At the University, Kvothe proves to be extraordinarily talented but struggles with poverty, makes both friends and enemies, and begins his study of sympathy (the magic system), naming, and the ancient art of shaping. Throughout the story, he searches for information about the Chandrian while dealing with his rivalry with a wealthy student named Ambrose and his complicated feelings for Denna, a mysterious woman he loves but can never quite reach. The book is notable for its beautiful prose, intricate world-building, and the frame narrative structure that creates mystery around what transformed the legendary Kvothe into a seemingly ordinary innkeeper."
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
                "input_tokens": 744,
                "output_tokens": 340,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 1084,
            },
            "n_chunks": 218,
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
                            text='{"summary": "The Name of the Wind is the first book in Patrick Rothfuss\'s Kingkiller Chronicle trilogy. It follows Kvothe, a legendary figure who now lives in disguise as an innkeeper named Kote. The story is framed as Kvothe recounting his life to a chronicler over three days. In this first volume, Kvothe tells of his childhood as part of a traveling troupe of performers called the Edema Ruh, where he displayed remarkable talents in music and learning. His idyllic life is shattered when his entire troupe is massacred by the mysterious Chandrian, mythical beings of great power. Orphaned and driven by a desire for knowledge and revenge, Kvothe struggles to survive on the streets before eventually gaining admission to the University, a prestigious institution for learning sympathy (a form of magic), artificing, and other disciplines. At the University, he proves to be a prodigy but also makes dangerous enemies, struggles with poverty, and begins his search for information about the Chandrian. Throughout, he pursues Denna, a mysterious woman he loves but can never quite reach. The book blends coming-of-age themes with fantasy elements, exploring Kvothe\'s transformation from a traumatized child into a legendary figure, while leaving many mysteries unsolved for future volumes."}'
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
                                "id": "toolu_015w8yghAqjW8nkEoQo3hFjV",
                                "name": "__mirascope_formatted_output_tool__",
                                "input": {
                                    "summary": "The Name of the Wind is the first book in Patrick Rothfuss's Kingkiller Chronicle trilogy. It follows Kvothe, a legendary figure who now lives in disguise as an innkeeper named Kote. The story is framed as Kvothe recounting his life to a chronicler over three days. In this first volume, Kvothe tells of his childhood as part of a traveling troupe of performers called the Edema Ruh, where he displayed remarkable talents in music and learning. His idyllic life is shattered when his entire troupe is massacred by the mysterious Chandrian, mythical beings of great power. Orphaned and driven by a desire for knowledge and revenge, Kvothe struggles to survive on the streets before eventually gaining admission to the University, a prestigious institution for learning sympathy (a form of magic), artificing, and other disciplines. At the University, he proves to be a prodigy but also makes dangerous enemies, struggles with poverty, and begins his search for information about the Chandrian. Throughout, he pursues Denna, a mysterious woman he loves but can never quite reach. The book blends coming-of-age themes with fantasy elements, exploring Kvothe's transformation from a traumatized child into a legendary figure, while leaving many mysteries unsolved for future volumes."
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
                "input_tokens": 744,
                "output_tokens": 309,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 1053,
            },
            "n_chunks": 185,
        }
    }
)
