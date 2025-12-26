from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "response": {
            "provider_id": "google",
            "model_id": "google/gemini-2.5-flash",
            "provider_model_name": "gemini-2.5-flash",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 15,
                "output_tokens": 258,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 79,
                "raw": """\
cache_tokens_details=None cached_content_token_count=None candidates_token_count=179 candidates_tokens_details=None prompt_token_count=15 prompt_tokens_details=[ModalityTokenCount(
  modality=<MediaModality.TEXT: 'TEXT'>,
  token_count=15
)] thoughts_token_count=79 tool_use_prompt_token_count=None tool_use_prompt_tokens_details=None total_token_count=273 traffic_type=None\
""",
                "total_tokens": 273,
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
                            text='{"summary":"The Name of the Wind, by Patrick Rothfuss, is the first book in The Kingkiller Chronicle series. It tells the story of Kvothe, a legendary figure, as he recounts his past to a chronicler named Devan Lochees, known as Chronicler. The narrative unfolds through Kvothe\'s own words, detailing his childhood as an orphaned Edema Ruh (traveling performer), his time on the streets of Tarbean, and his remarkable journey to the University, where he seeks knowledge and revenge. He learns magic, fights mythical creatures, and navigates complex social and political landscapes, all while searching for the truth behind the Chandrian, the beings responsible for his family\'s murder. The story is a rich tapestry of adventure, magic, romance, and mystery, building the legend of Kvothe as a hero, a villain, and everything in between."}'
                        )
                    ],
                    provider_id="google",
                    model_id="google/gemini-2.5-flash",
                    provider_model_name="gemini-2.5-flash",
                    raw_message={
                        "parts": [
                            {
                                "function_call": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": '{"summary":"The Name of the Wind, by Patrick Rothfuss, is the first book in The Kingkiller Chronicle series. It tells the story of Kvothe, a legendary figure, as he recounts his past to a chronicler named Devan Lochees, known as Chronicler. The narrative unfolds through Kvothe\'s own words, detailing his childhood as an orphaned Edema Ruh (traveling performer), his time on the streets of Tarbean, and his remarkable journey to the University, where he seeks knowledge and revenge. He learns magic, fights mythical creatures, and navigates complex social and political landscapes, all while searching for the truth behind the Chandrian, the beings responsible for his family\'s murder. The story is a rich tapestry of adventure, magic, romance, and mystery, building the legend of Kvothe as a hero, a villain, and everything in between."}',
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            }
                        ],
                        "role": "model",
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
            "provider_id": "google",
            "model_id": "google/gemini-2.5-flash",
            "provider_model_name": "gemini-2.5-flash",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 15,
                "output_tokens": 210,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 57,
                "raw": """\
cache_tokens_details=None cached_content_token_count=None candidates_token_count=153 candidates_tokens_details=None prompt_token_count=15 prompt_tokens_details=[ModalityTokenCount(
  modality=<MediaModality.TEXT: 'TEXT'>,
  token_count=15
)] thoughts_token_count=57 tool_use_prompt_token_count=None tool_use_prompt_tokens_details=None total_token_count=225 traffic_type=None\
""",
                "total_tokens": 225,
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
                            text='{"summary":"The Name of the Wind tells the story of Kvothe, a legendary figure, as he recounts his early life to a chronicler named Devan Lochees, also known as Chronicler. Living as an innkeeper in a remote village under a new identity, Kvothe begins to share the true tale of his upbringing in a troupe of traveling performers, his orphaned years in the streets of Tarbean, and his eventual enrollment in the prestigious University. The narrative explores his struggles with poverty, his brilliant but rebellious academic pursuits, his encounters with mythical creatures, and the tragic mystery surrounding the Chandrian, who murdered his family. It is the first-person account of how he became the infamous wizard, duelist, and legend known by many names."}'
                        )
                    ],
                    provider_id="google",
                    model_id="google/gemini-2.5-flash",
                    provider_model_name="gemini-2.5-flash",
                    raw_message={
                        "parts": [
                            {
                                "function_call": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": '{"summary":"The Name of the Wind tells the story of Kvothe, a legendary figure, as he recounts his early life to a chronicler named Devan Lochees, also known as Chronicler. Living as an innkeeper in a remote village under a new identity, Kvothe begins to share the true tale of his upbringing in a troupe of traveling performers, his orphaned years in the streets of Tarbean, and his eventual enrollment in the prestigious University. The narrative explores his struggles with poverty, his brilliant but rebellious academic pursuits, his encounters with mythical creatures, and the tragic mystery surrounding the Chandrian, who murdered his family. It is the first-person account of how he became the infamous wizard, duelist, and legend known by many names."}',
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            }
                        ],
                        "role": "model",
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
            "provider_id": "google",
            "model_id": "google/gemini-2.5-flash",
            "provider_model_name": "gemini-2.5-flash",
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
                            text='{"summary":"The Name of the Wind by Patrick Rothfuss tells the story of Kvothe, a legendary figure, as he recounts his early life to a chronicler named Devan Lochees. The narrative follows Kvothe from his childhood as an orphaned arcanist traveling with a troupe of actors, through the tragic loss of his family to a mythical group called the Chandrian, and his subsequent years as a street urchin in the city of Tarbean. He eventually gains admission to the prestigious University, a center of learning and magic, where he navigates academic challenges, financial struggles, and intense rivalries, all while pursuing knowledge and seeking answers about the Chandrian and the mysterious beings known as the Amyr."}'
                        )
                    ],
                    provider_id="google",
                    model_id="google/gemini-2.5-flash",
                    provider_model_name="gemini-2.5-flash",
                    raw_message={
                        "parts": [
                            {
                                "function_call": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": '{"summary":"The Name of the Wind by Patrick Rothfuss tells the story of Kvothe, a legendary figure, as he recounts his early life to a chronicler named Devan Lochees',
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                            {
                                "function_call": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": ". The narrative follows Kvothe from his childhood as an orphaned arcanist traveling with a troupe of actors, through the tragic loss of his family to a mythical group called the Chandrian, and his subsequent years as a street urchin in the",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                            {
                                "function_call": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": " city of Tarbean. He eventually gains admission to the prestigious University, a center of learning and magic, where he navigates academic challenges, financial struggles, and intense rivalries, all while pursuing knowledge and seeking answers about the Chandrian and",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                            {
                                "function_call": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": ' the mysterious beings known as the Amyr."}',
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                        ],
                        "role": "model",
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
                "mode": "strict",
                "formatting_instructions": None,
            },
            "tools": [],
            "usage": {
                "input_tokens": 15,
                "output_tokens": 145,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 38,
                "raw": "None",
                "total_tokens": 160,
            },
            "n_chunks": 6,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "google",
            "model_id": "google/gemini-2.5-flash",
            "provider_model_name": "gemini-2.5-flash",
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
                            text='{"summary":"The Name of the Wind by Patrick Rothfuss tells the story of Kvothe, a legendary figure, as he recounts his early life to a chronicler. The narrative primarily focuses on his childhood in a troupe of traveling performers, his subsequent orphanhood and survival on the streets of Tarbean, and his audacious admission to the University to study arcanum. Through his adventures, Kvothe hones his skills in magic, music, and wit, makes both friends and enemies, and begins his quest to uncover the truth behind the mythical Chandrian, who are responsible for the death of his family."}'
                        )
                    ],
                    provider_id="google",
                    model_id="google/gemini-2.5-flash",
                    provider_model_name="gemini-2.5-flash",
                    raw_message={
                        "parts": [
                            {
                                "function_call": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": '{"summary":"The Name of the Wind by Patrick Rothfuss tells the story of Kvothe, a legendary figure, as he recounts his early life to a chronicler. The narrative primarily focuses',
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                            {
                                "function_call": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": " on his childhood in a troupe of traveling performers, his subsequent orphanhood and survival on the streets of Tarbean, and his audacious admission to the University to study arcanum. Through his adventures, Kvothe hones his skills in magic",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                            {
                                "function_call": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": ', music, and wit, makes both friends and enemies, and begins his quest to uncover the truth behind the mythical Chandrian, who are responsible for the death of his family."}',
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                        ],
                        "role": "model",
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
                "mode": "strict",
                "formatting_instructions": None,
            },
            "tools": [],
            "usage": {
                "input_tokens": 15,
                "output_tokens": 123,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 55,
                "raw": "None",
                "total_tokens": 138,
            },
            "n_chunks": 5,
        }
    }
)
