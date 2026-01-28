from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    FinishReason,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "response": {
            "provider_id": "bedrock",
            "model_id": "bedrock/openai.gpt-oss-20b-1:0",
            "provider_model_name": "openai.gpt-oss-20b-1:0",
            "params": {"max_tokens": 50},
            "finish_reason": FinishReason.MAX_TOKENS,
            "usage": {
                "input_tokens": 76,
                "output_tokens": 50,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "CompletionUsage(completion_tokens=50, prompt_tokens=76, total_tokens=126, completion_tokens_details=None, prompt_tokens_details=None)",
                "total_tokens": 126,
            },
            "messages": [
                UserMessage(content=[Text(text="List all U.S. states.")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="<reasoning>User wants a list of all US states. Provide a list. Should be accurate: 50 states. Provide in alphabetical order or typical listing. Perhaps include state abbreviations. No extra content? Should be concise. Provide answer.</reasoning>"
                        )
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/openai.gpt-oss-20b-1:0",
                    provider_model_name="openai.gpt-oss-20b-1:0",
                    raw_message={
                        "content": "<reasoning>User wants a list of all US states. Provide a list. Should be accurate: 50 states. Provide in alphabetical order or typical listing. Perhaps include state abbreviations. No extra content? Should be concise. Provide answer.</reasoning>",
                        "role": "assistant",
                    },
                ),
            ],
            "format": None,
            "tools": [],
        }
    }
)
async_snapshot = snapshot(
    {
        "response": {
            "provider_id": "bedrock",
            "model_id": "bedrock/openai.gpt-oss-20b-1:0",
            "provider_model_name": "openai.gpt-oss-20b-1:0",
            "params": {"max_tokens": 50},
            "finish_reason": FinishReason.MAX_TOKENS,
            "usage": {
                "input_tokens": 76,
                "output_tokens": 50,
                "cache_read_tokens": 48,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "CompletionUsage(completion_tokens=50, prompt_tokens=76, total_tokens=126, completion_tokens_details=None, prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=48))",
                "total_tokens": 126,
            },
            "messages": [
                UserMessage(content=[Text(text="List all U.S. states.")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
<reasoning>User: "List all U.S. states." There's no special instruction, so just give list of 50 U.S. states.

We should comply and provide a list of all 50 states alphabetically or similar. Provide as final</reasoning>\
"""
                        )
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/openai.gpt-oss-20b-1:0",
                    provider_model_name="openai.gpt-oss-20b-1:0",
                    raw_message={
                        "content": """\
<reasoning>User: "List all U.S. states." There's no special instruction, so just give list of 50 U.S. states.

We should comply and provide a list of all 50 states alphabetically or similar. Provide as final</reasoning>\
""",
                        "role": "assistant",
                    },
                ),
            ],
            "format": None,
            "tools": [],
        }
    }
)
stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "bedrock",
            "model_id": "bedrock/openai.gpt-oss-20b-1:0",
            "provider_model_name": "openai.gpt-oss-20b-1:0",
            "finish_reason": FinishReason.MAX_TOKENS,
            "messages": [
                UserMessage(content=[Text(text="List all U.S. states.")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="<reasoning>We need to list all US states. The user asked for a list of all states. We'll provide a list. Probably alphabetically. Include the 50 states. We should ensure we include all. Also mention that DC is not a</reasoning>"
                        )
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/openai.gpt-oss-20b-1:0",
                    provider_model_name="openai.gpt-oss-20b-1:0",
                    raw_message=None,
                ),
            ],
            "format": None,
            "tools": [],
            "usage": {
                "input_tokens": 76,
                "output_tokens": 50,
                "cache_read_tokens": 48,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 126,
            },
            "n_chunks": 3,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "bedrock",
            "model_id": "bedrock/openai.gpt-oss-20b-1:0",
            "provider_model_name": "openai.gpt-oss-20b-1:0",
            "finish_reason": FinishReason.MAX_TOKENS,
            "messages": [
                UserMessage(content=[Text(text="List all U.S. states.")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="<reasoning>The user wants a list of all U.S. states. Provide full list: 50 states. They probably want them alphabetically. Provide with numbers. That is straightforward.</reasoning>**The 50 United\u202f"
                        )
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/openai.gpt-oss-20b-1:0",
                    provider_model_name="openai.gpt-oss-20b-1:0",
                    raw_message=None,
                ),
            ],
            "format": None,
            "tools": [],
            "usage": {
                "input_tokens": 76,
                "output_tokens": 50,
                "cache_read_tokens": 48,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 126,
            },
            "n_chunks": 4,
        }
    }
)
