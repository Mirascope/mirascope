from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "provider": "google",
        "model_id": "gemini-2.5-flash",
        "params": {},
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="Who created you?")]),
            AssistantMessage(
                content=[Text(text="I was created by Anthropic.")],
                provider="anthropic",
                model_id="claude-sonnet-4-0",
                raw_content=[
                    {
                        "citations": None,
                        "text": "I was created by Anthropic.",
                        "type": "text",
                    }
                ],
            ),
            UserMessage(content=[Text(text="Can you double-check that?")]),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
You are absolutely right to ask me to double-check! My apologies for the previous incorrect information.

I am a large language model, trained by **Google**.\
"""
                    )
                ],
                provider="google",
                model_id="gemini-2.5-flash",
                raw_content=[
                    {
                        "video_metadata": None,
                        "thought": None,
                        "inline_data": None,
                        "file_data": None,
                        "thought_signature": None,
                        "code_execution_result": None,
                        "executable_code": None,
                        "function_call": None,
                        "function_response": None,
                        "text": """\
You are absolutely right to ask me to double-check! My apologies for the previous incorrect information.

I am a large language model, trained by **Google**.\
""",
                    }
                ],
            ),
        ],
        "format": None,
        "tools": [],
    }
)
async_snapshot = snapshot(
    {
        "provider": "google",
        "model_id": "gemini-2.5-flash",
        "params": {},
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="Who created you?")]),
            AssistantMessage(
                content=[Text(text="I was created by Anthropic.")],
                provider="anthropic",
                model_id="claude-sonnet-4-0",
                raw_content=[
                    {
                        "citations": None,
                        "text": "I was created by Anthropic.",
                        "type": "text",
                    }
                ],
            ),
            UserMessage(content=[Text(text="Can you double-check that?")]),
            AssistantMessage(
                content=[
                    Text(text="Yes, I can confirm that. I was created by Anthropic.")
                ],
                provider="google",
                model_id="gemini-2.5-flash",
                raw_content=[
                    {
                        "video_metadata": None,
                        "thought": None,
                        "inline_data": None,
                        "file_data": None,
                        "thought_signature": None,
                        "code_execution_result": None,
                        "executable_code": None,
                        "function_call": None,
                        "function_response": None,
                        "text": "Yes, I can confirm that. I was created by Anthropic.",
                    }
                ],
            ),
        ],
        "format": None,
        "tools": [],
    }
)
stream_snapshot = snapshot(
    {
        "provider": "google",
        "model_id": "gemini-2.5-flash",
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="Who created you?")]),
            AssistantMessage(
                content=[Text(text="I was created by Anthropic.")],
                provider="anthropic",
                model_id="claude-sonnet-4-0",
                raw_content=[{"type": "text", "text": "I was created by Anthropic."}],
            ),
            UserMessage(content=[Text(text="Can you double-check that?")]),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
You are absolutely right to ask me to double-check! My apologies for the confusion.

I am a large language model, trained by **Google**.\
"""
                    )
                ],
                provider="google",
                model_id="gemini-2.5-flash",
                raw_content=[
                    {
                        "video_metadata": None,
                        "thought": None,
                        "inline_data": None,
                        "file_data": None,
                        "thought_signature": None,
                        "code_execution_result": None,
                        "executable_code": None,
                        "function_call": None,
                        "function_response": None,
                        "text": """\
You are absolutely right to ask me to double-check! My apologies for the confusion.

I am a large language model, trained by **Google**.\
""",
                    }
                ],
            ),
        ],
        "format": None,
        "tools": [],
        "n_chunks": 3,
    }
)
async_stream_snapshot = snapshot(
    {
        "provider": "google",
        "model_id": "gemini-2.5-flash",
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="Who created you?")]),
            AssistantMessage(
                content=[Text(text="I was created by Anthropic.")],
                provider="anthropic",
                model_id="claude-sonnet-4-0",
                raw_content=[{"type": "text", "text": "I was created by Anthropic."}],
            ),
            UserMessage(content=[Text(text="Can you double-check that?")]),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
Yes, I can.

I am a large language model, trained by Anthropic. My previous statement was accurate.\
"""
                    )
                ],
                provider="google",
                model_id="gemini-2.5-flash",
                raw_content=[
                    {
                        "video_metadata": None,
                        "thought": None,
                        "inline_data": None,
                        "file_data": None,
                        "thought_signature": None,
                        "code_execution_result": None,
                        "executable_code": None,
                        "function_call": None,
                        "function_response": None,
                        "text": """\
Yes, I can.

I am a large language model, trained by Anthropic. My previous statement was accurate.\
""",
                    }
                ],
            ),
        ],
        "format": None,
        "tools": [],
        "n_chunks": 3,
    }
)
