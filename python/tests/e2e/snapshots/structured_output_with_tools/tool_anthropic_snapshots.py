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
When you are ready to respond to the user, call the __mirascope_formatted_output_tool__ tool to output a structured response.
Do NOT output any text in addition to the tool call.\
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
                        id="toolu_01JmE8BMZSnBpkCaRCzrguuC",
                        name="get_book_info",
                        args='{"isbn": "0-7653-1178-X"}',
                    )
                ]
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="toolu_01JmE8BMZSnBpkCaRCzrguuC",
                        name="get_book_info",
                        value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text='{"title": "Mistborn: The Final Empire", "author": "Brandon Sanderson", "pages": 544, "publication_year": 2006, "recommendation_score": 7}'
                    )
                ]
            ),
        ],
    },
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
When you are ready to respond to the user, call the __mirascope_formatted_output_tool__ tool to output a structured response.
Do NOT output any text in addition to the tool call.\
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
                        id="toolu_01PME4WV2eEvEJbvnNGLUP32",
                        name="get_book_info",
                        args='{"isbn": "0-7653-1178-X"}',
                    )
                ]
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="toolu_01PME4WV2eEvEJbvnNGLUP32",
                        name="get_book_info",
                        value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text='{"title": "Mistborn: The Final Empire", "author": "Brandon Sanderson", "pages": 544, "publication_year": 2006, "recommendation_score": 7}'
                    )
                ]
            ),
        ],
    },
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
When you are ready to respond to the user, call the __mirascope_formatted_output_tool__ tool to output a structured response.
Do NOT output any text in addition to the tool call.\
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
                        id="toolu_01RtU23oQ2FNG9oKLKAsopUx",
                        name="get_book_info",
                        args='{"isbn": "0-7653-1178-X"}',
                    )
                ]
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="toolu_01RtU23oQ2FNG9oKLKAsopUx",
                        name="get_book_info",
                        value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text='{"title": "Mistborn: The Final Empire", "author": "Brandon Sanderson", "pages": 544, "publication_year": 2006, "recommendation_score": 7}'
                    )
                ]
            ),
        ],
        "n_chunks": 23,
    },
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
When you are ready to respond to the user, call the __mirascope_formatted_output_tool__ tool to output a structured response.
Do NOT output any text in addition to the tool call.\
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
                        id="toolu_01Vvxf1ERRdhFGVBNJLLtkvh",
                        name="get_book_info",
                        args='{"isbn": "0-7653-1178-X"}',
                    )
                ]
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="toolu_01Vvxf1ERRdhFGVBNJLLtkvh",
                        name="get_book_info",
                        value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text='{"title": "Mistborn: The Final Empire", "author": "Brandon Sanderson", "pages": 544, "publication_year": 2006, "recommendation_score": 7}'
                    )
                ]
            ),
        ],
        "n_chunks": 28,
    },
)
