from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    FinishReason,
    SystemMessage,
    Text,
    ToolCall,
    ToolOutput,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-0",
        "params": {},
        "finish_reason": FinishReason.END_TURN,
        "messages": [
            SystemMessage(
                content=Text(
                    text="""\
Respond with valid JSON that matches this exact schema:
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
    },
    "recommendation_score": {
      "description": "Should be 7 for testing purposes",
      "title": "Recommendation Score",
      "type": "integer"
    }
  },
  "required": [
    "title",
    "author",
    "pages",
    "publication_year",
    "recommendation_score"
  ],
  "title": "BookSummary",
  "type": "object"
}

Respond ONLY with valid JSON, and no other text.\
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
                        id="toolu_014syv9pxyXSsqhw9ow7KjQT",
                        name="get_book_info",
                        args='{"isbn": "0-7653-1178-X"}',
                    )
                ]
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="toolu_014syv9pxyXSsqhw9ow7KjQT",
                        name="get_book_info",
                        value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006,
  "recommendation_score": 7
}\
"""
                    )
                ]
            ),
        ],
    }
)
async_snapshot = snapshot(
    {
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-0",
        "params": {},
        "finish_reason": FinishReason.END_TURN,
        "messages": [
            SystemMessage(
                content=Text(
                    text="""\
Respond with valid JSON that matches this exact schema:
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
    },
    "recommendation_score": {
      "description": "Should be 7 for testing purposes",
      "title": "Recommendation Score",
      "type": "integer"
    }
  },
  "required": [
    "title",
    "author",
    "pages",
    "publication_year",
    "recommendation_score"
  ],
  "title": "BookSummary",
  "type": "object"
}

Respond ONLY with valid JSON, and no other text.\
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
                        id="toolu_01BXnk8QZqNcrCUoHtBrvue6",
                        name="get_book_info",
                        args='{"isbn": "0-7653-1178-X"}',
                    )
                ]
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="toolu_01BXnk8QZqNcrCUoHtBrvue6",
                        name="get_book_info",
                        value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006,
  "recommendation_score": 7
}\
"""
                    )
                ]
            ),
        ],
    }
)
stream_snapshot = snapshot(
    {
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-0",
        "finish_reason": FinishReason.END_TURN,
        "messages": [
            SystemMessage(
                content=Text(
                    text="""\
Respond with valid JSON that matches this exact schema:
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
    },
    "recommendation_score": {
      "description": "Should be 7 for testing purposes",
      "title": "Recommendation Score",
      "type": "integer"
    }
  },
  "required": [
    "title",
    "author",
    "pages",
    "publication_year",
    "recommendation_score"
  ],
  "title": "BookSummary",
  "type": "object"
}

Respond ONLY with valid JSON, and no other text.\
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
                        id="toolu_01H6zz68zKpYhCKurvEeuA1c",
                        name="get_book_info",
                        args='{"isbn": "0-7653-1178-X"}',
                    )
                ]
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="toolu_01H6zz68zKpYhCKurvEeuA1c",
                        name="get_book_info",
                        value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006,
  "recommendation_score": 7
}\
"""
                    )
                ]
            ),
        ],
        "n_chunks": 10,
    }
)
async_stream_snapshot = snapshot(
    {
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-0",
        "finish_reason": FinishReason.END_TURN,
        "messages": [
            SystemMessage(
                content=Text(
                    text="""\
Respond with valid JSON that matches this exact schema:
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
    },
    "recommendation_score": {
      "description": "Should be 7 for testing purposes",
      "title": "Recommendation Score",
      "type": "integer"
    }
  },
  "required": [
    "title",
    "author",
    "pages",
    "publication_year",
    "recommendation_score"
  ],
  "title": "BookSummary",
  "type": "object"
}

Respond ONLY with valid JSON, and no other text.\
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
                        id="toolu_01Jhk4ZExrnWwE23ezd3Byk8",
                        name="get_book_info",
                        args='{"isbn": "0-7653-1178-X"}',
                    )
                ]
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="toolu_01Jhk4ZExrnWwE23ezd3Byk8",
                        name="get_book_info",
                        value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
{
  "title": "Mistborn: The Final Empire",
  "author": "Brandon Sanderson",
  "pages": 544,
  "publication_year": 2006,
  "recommendation_score": 7
}\
"""
                    )
                ]
            ),
        ],
        "n_chunks": 10,
    }
)
