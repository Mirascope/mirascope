from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "response": {
            "provider_id": "openai",
            "model_id": "openai/gpt-4o:responses",
            "provider_model_name": "gpt-4o:responses",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 76,
                "output_tokens": 206,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "ResponseUsage(input_tokens=76, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=206, output_tokens_details=OutputTokensDetails(reasoning_tokens=0), total_tokens=282)",
                "total_tokens": 282,
            },
            "from_call_args": {
                "author": "Patrick Rothfuss",
                "title": "The Name of the Wind",
            },
            "messages": [
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
                            text='{"summary":"\\"The Name of the Wind\\" by Patrick Rothfuss is the first novel in \\"The Kingkiller Chronicle\\" series. It follows the story of Kvothe, a legendary figure who is both a hero and a criminal. Narrated in the first person, the story is recounted by Kvothe himself as he hides under the guise of an innkeeper.\\n\\nThe novel begins with Kvothe\'s early life in a traveling troupe of performers and progresses through his years as a student at the University. As Kvothe learns about the powerful force of naming and the art of sympathy (a form of magic), he seeks to uncover the truth about the mythical Chandrian, who are responsible for his family\'s murder.\\n\\nAs Kvothe navigates through trials, friendships, and ambitions, \\"The Name of the Wind\\" explores themes of revenge, knowledge, and the complexities of destiny. The book combines rich world-building with lyrical prose, creating an intricate tale of magic, adventure, and self-discovery."}'
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:responses",
                    provider_model_name="gpt-4o:responses",
                    raw_message=[
                        {
                            "id": "msg_095548cf09dc306600694ef96d5cf881948f1f161cc0691fc4",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": '{"summary":"\\"The Name of the Wind\\" by Patrick Rothfuss is the first novel in \\"The Kingkiller Chronicle\\" series. It follows the story of Kvothe, a legendary figure who is both a hero and a criminal. Narrated in the first person, the story is recounted by Kvothe himself as he hides under the guise of an innkeeper.\\n\\nThe novel begins with Kvothe\'s early life in a traveling troupe of performers and progresses through his years as a student at the University. As Kvothe learns about the powerful force of naming and the art of sympathy (a form of magic), he seeks to uncover the truth about the mythical Chandrian, who are responsible for his family\'s murder.\\n\\nAs Kvothe navigates through trials, friendships, and ambitions, \\"The Name of the Wind\\" explores themes of revenge, knowledge, and the complexities of destiny. The book combines rich world-building with lyrical prose, creating an intricate tale of magic, adventure, and self-discovery."}',
                                    "type": "output_text",
                                    "logprobs": [],
                                }
                            ],
                            "role": "assistant",
                            "status": "completed",
                            "type": "message",
                        }
                    ],
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
                "mode": "strict",
                "formatting_instructions": None,
            },
            "tools": [],
        }
    }
)
async_snapshot = snapshot(
    {
        "response": {
            "provider_id": "openai",
            "model_id": "openai/gpt-4o:responses",
            "provider_model_name": "gpt-4o:responses",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 76,
                "output_tokens": 140,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "ResponseUsage(input_tokens=76, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=140, output_tokens_details=OutputTokensDetails(reasoning_tokens=0), total_tokens=216)",
                "total_tokens": 216,
            },
            "from_call_args": {
                "author": "Patrick Rothfuss",
                "title": "The Name of the Wind",
            },
            "messages": [
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
                            text='{"summary":"\\"The Name of the Wind\\" is the first book in Patrick Rothfuss’s \\"The Kingkiller Chronicle\\" series. It follows the story of Kvothe, a legendary figure in his world, as he recounts his life story to Chronicler, a biographer. \\n\\nBeginning with Kvothe\'s childhood in a troupe of traveling performers, the narrative traces his journey through hardship and education at the University, where he learns magic. Along the way, he seeks to uncover the truth about the mysterious Chandrian, who are responsible for his family\'s death. Kvothe\'s tale is filled with adventure, discovery, and personal growth, forming the foundation of his legend."}'
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:responses",
                    provider_model_name="gpt-4o:responses",
                    raw_message=[
                        {
                            "id": "msg_04ac5a5d455192c400694ef9920b808197b505ee5d362309d2",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": '{"summary":"\\"The Name of the Wind\\" is the first book in Patrick Rothfuss’s \\"The Kingkiller Chronicle\\" series. It follows the story of Kvothe, a legendary figure in his world, as he recounts his life story to Chronicler, a biographer. \\n\\nBeginning with Kvothe\'s childhood in a troupe of traveling performers, the narrative traces his journey through hardship and education at the University, where he learns magic. Along the way, he seeks to uncover the truth about the mysterious Chandrian, who are responsible for his family\'s death. Kvothe\'s tale is filled with adventure, discovery, and personal growth, forming the foundation of his legend."}',
                                    "type": "output_text",
                                    "logprobs": [],
                                }
                            ],
                            "role": "assistant",
                            "status": "completed",
                            "type": "message",
                        }
                    ],
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
                "mode": "strict",
                "formatting_instructions": None,
            },
            "tools": [],
        }
    }
)
stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "openai",
            "model_id": "openai/gpt-4o:responses",
            "provider_model_name": "gpt-4o:responses",
            "finish_reason": None,
            "messages": [
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
                            text='{"summary":"\\"The Name of the Wind\\" by Patrick Rothfuss is the first book in the Kingkiller Chronicle series. It tells the story of Kvothe, a legendary figure known for his skills in music and magic. The novel is structured as a story within a story, where Kvothe, now living as an innkeeper under the name Kote, narrates his life to a chronicler.\\n\\nThe tale unfolds with Kvothe\'s early life in a traveling troupe, the tragic murder of his family by mysterious group known as the Chandrian, and his struggle with poverty. Kvothe eventually makes his way to the University, a place of learning, magic, and mystery. Here, he excels despite financial and social challenges, explores the mysteries of naming and magic, and seeks knowledge about the Chandrian.\\n\\nThe narrative combines elements of adventure, romance, and mystery, exploring themes of identity, the power of storytelling, and the pursuit of knowledge."}'
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:responses",
                    provider_model_name="gpt-4o:responses",
                    raw_message=[
                        {
                            "id": "msg_0213c520b953c71f00694ef9afefe881939c89ba6b0ea205c1",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": '{"summary":"\\"The Name of the Wind\\" by Patrick Rothfuss is the first book in the Kingkiller Chronicle series. It tells the story of Kvothe, a legendary figure known for his skills in music and magic. The novel is structured as a story within a story, where Kvothe, now living as an innkeeper under the name Kote, narrates his life to a chronicler.\\n\\nThe tale unfolds with Kvothe\'s early life in a traveling troupe, the tragic murder of his family by mysterious group known as the Chandrian, and his struggle with poverty. Kvothe eventually makes his way to the University, a place of learning, magic, and mystery. Here, he excels despite financial and social challenges, explores the mysteries of naming and magic, and seeks knowledge about the Chandrian.\\n\\nThe narrative combines elements of adventure, romance, and mystery, exploring themes of identity, the power of storytelling, and the pursuit of knowledge."}',
                                    "type": "output_text",
                                    "logprobs": [],
                                }
                            ],
                            "role": "assistant",
                            "status": "completed",
                            "type": "message",
                        }
                    ],
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
                "mode": "strict",
                "formatting_instructions": None,
            },
            "tools": [],
            "usage": {
                "input_tokens": 76,
                "output_tokens": 197,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 273,
            },
            "n_chunks": 198,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "openai",
            "model_id": "openai/gpt-4o:responses",
            "provider_model_name": "gpt-4o:responses",
            "finish_reason": None,
            "messages": [
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
                            text='{"summary":"\\"The Name of the Wind\\" by Patrick Rothfuss is the first book in \\"The Kingkiller Chronicle\\" series. It follows the story of Kvothe, a gifted young man who becomes a legendary figure. Told through a framing narrative where Kvothe recounts his life story, it explores themes of mystery, magic, and survival. Kvothe\'s journey begins in a traveling troupe and leads him to the University, where he learns about magic and uncovers mysteries connected to his past, particularly concerning mythical creatures known as the Chandrian. The novel is known for its rich world-building and lyrical prose."}'
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:responses",
                    provider_model_name="gpt-4o:responses",
                    raw_message=[
                        {
                            "id": "msg_0e7d827ac15229dd00694ef9d146848190bb3f213d71f922d7",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": '{"summary":"\\"The Name of the Wind\\" by Patrick Rothfuss is the first book in \\"The Kingkiller Chronicle\\" series. It follows the story of Kvothe, a gifted young man who becomes a legendary figure. Told through a framing narrative where Kvothe recounts his life story, it explores themes of mystery, magic, and survival. Kvothe\'s journey begins in a traveling troupe and leads him to the University, where he learns about magic and uncovers mysteries connected to his past, particularly concerning mythical creatures known as the Chandrian. The novel is known for its rich world-building and lyrical prose."}',
                                    "type": "output_text",
                                    "logprobs": [],
                                }
                            ],
                            "role": "assistant",
                            "status": "completed",
                            "type": "message",
                        }
                    ],
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
                "mode": "strict",
                "formatting_instructions": None,
            },
            "tools": [],
            "usage": {
                "input_tokens": 76,
                "output_tokens": 126,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 202,
            },
            "n_chunks": 127,
        }
    }
)
