from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    SystemMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "provider": "anthropic-bedrock",
        "model_id": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
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
```json
{
  "title": "THE NAME OF THE WIND",
  "author": "Patrick Rothfuss",
  "rating": 7
}
```

I highly recommend this book! It's an epic fantasy novel that follows Kvothe, a legendary figure, as he recounts his extraordinary life story. The prose is beautifully written, the magic system is creative and well-developed, and the world-building is immersive. It's the first book in *The Kingkiller Chronicle* series and is perfect if you enjoy character-driven narratives with mystery and adventure.\
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
  "title": "THE NAME OF THE WIND",
  "author": "Patrick Rothfuss",
  "rating": 7
}
```

I highly recommend this book! It's an epic fantasy novel that follows Kvothe, a legendary figure, as he recounts his extraordinary life story. The prose is beautifully written, the magic system is creative and well-developed, and the world-building is immersive. It's the first book in *The Kingkiller Chronicle* series and is perfect if you enjoy character-driven narratives with mystery and adventure.\
""",
                            "type": "text",
                        }
                    ],
                },
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
)
