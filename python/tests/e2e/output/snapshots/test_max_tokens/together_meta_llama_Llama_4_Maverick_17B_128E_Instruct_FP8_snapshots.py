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
            "provider_id": "together",
            "model_id": "together/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
            "provider_model_name": "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
            "params": {"max_tokens": 50},
            "finish_reason": FinishReason.MAX_TOKENS,
            "messages": [
                UserMessage(content=[Text(text="List all U.S. states.")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Here are all 50 U.S. states, listed in alphabetical order:

1. Alabama (AL)
2. Alaska (AK)
3. Arizona (AZ)
4. Arkansas (AR)
5. California (CA)
6. Colorado (CO\
"""
                        )
                    ],
                    provider_id="together",
                    model_id="together/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
                    provider_model_name="meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
                    raw_message={
                        "role": "assistant",
                        "content": """\
Here are all 50 U.S. states, listed in alphabetical order:

1. Alabama (AL)
2. Alaska (AK)
3. Arizona (AZ)
4. Arkansas (AR)
5. California (CA)
6. Colorado (CO\
""",
                        "tool_calls": [],
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
            "provider_id": "together",
            "model_id": "together/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
            "provider_model_name": "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
            "params": {"max_tokens": 50},
            "finish_reason": FinishReason.MAX_TOKENS,
            "messages": [
                UserMessage(content=[Text(text="List all U.S. states.")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Here are all 50 U.S. states:

1. Alabama (AL)
2. Alaska (AK)
3. Arizona (AZ)
4. Arkansas (AR)
5. California (CA)
6. Colorado (CO)
7. Connecticut (\
"""
                        )
                    ],
                    provider_id="together",
                    model_id="together/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
                    provider_model_name="meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
                    raw_message={
                        "role": "assistant",
                        "content": """\
Here are all 50 U.S. states:

1. Alabama (AL)
2. Alaska (AK)
3. Arizona (AZ)
4. Arkansas (AR)
5. California (CA)
6. Colorado (CO)
7. Connecticut (\
""",
                        "tool_calls": [],
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
            "provider": "together",
            "model_id": "together/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
            "finish_reason": FinishReason.MAX_TOKENS,
            "messages": [
                UserMessage(content=[Text(text="List all U.S. states.")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Here is a list of all 50 U.S. states in alphabetical order:

1. Alabama (AL)
2. Alaska (AK)
3. Arizona (AZ)
4. Arkansas (AR)
5. California (CA)
6. Colorado (\
"""
                        )
                    ],
                    provider_id="together",
                    model_id="together/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
                    provider_model_name="meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
                    raw_message=None,
                ),
            ],
            "format": None,
            "tools": [],
            "n_chunks": 52,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider": "together",
            "model_id": "together/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
            "finish_reason": FinishReason.MAX_TOKENS,
            "messages": [
                UserMessage(content=[Text(text="List all U.S. states.")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Here is the list of all 50 U.S. states:

1. Alabama
2. Alaska
3. Arizona
4. Arkansas
5. California
6. Colorado
7. Connecticut
8. Delaware
9. Florida
10\
"""
                        )
                    ],
                    provider_id="together",
                    model_id="together/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
                    provider_model_name="meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
                    raw_message=None,
                ),
            ],
            "format": None,
            "tools": [],
            "n_chunks": 52,
        }
    }
)
