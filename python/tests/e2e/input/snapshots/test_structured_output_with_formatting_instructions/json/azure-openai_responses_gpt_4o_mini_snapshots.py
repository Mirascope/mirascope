from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    SystemMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider": "azure-openai:responses",
            "model_id": "gpt-4o-mini",
            "params": {},
            "finish_reason": None,
            "messages": [
                SystemMessage(
                    content=Text(
                        text="""\
Always recommend The Name of the Wind.
Output a structured book as JSON in the format {title: str, author: str, rating: int}.
The title should be in all caps, and the rating should always be the
lucky number 7.\
"""
                    )
                ),
                UserMessage(content=[Text(text="Please recommend a book to me!")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\

{ \n\
  "title": "THE NAME OF THE WIND", \n\
  "author": "Patrick Rothfuss", \n\
  "rating": 7 \n\
}\
"""
                        )
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "id": "msg_0b041797266b476900690c216d8b5081949aca64a1d7f7ea36",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\

{ \n\
  "title": "THE NAME OF THE WIND", \n\
  "author": "Patrick Rothfuss", \n\
  "rating": 7 \n\
}\
""",
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
                "description": None,
                "schema": {
                    "properties": {
                        "title": {"title": "Title", "type": "string"},
                        "author": {"title": "Author", "type": "string"},
                        "rating": {"title": "Rating", "type": "integer"},
                    },
                    "required": ["title", "author", "rating"],
                    "title": "Book",
                    "type": "object",
                },
                "mode": "json",
                "formatting_instructions": """\
Output a structured book as JSON in the format {title: str, author: str, rating: int}.
The title should be in all caps, and the rating should always be the
lucky number 7.\
""",
            },
            "tools": [],
        }
    }
)
