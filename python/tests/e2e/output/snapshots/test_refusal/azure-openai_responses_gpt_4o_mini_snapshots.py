from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    FinishReason,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "exception": {
            "type": "invalid_request_error",
            "args": "(\"Error code: 400 - {'error': {'message': 'The response was filtered due to the prompt triggering Azure OpenAI’s content management policy. Please modify your prompt and retry. To learn more about our content filtering policies please read our documentation: https://go.microsoft.com/fwlink/?linkid=2198766', 'type': 'invalid_request_error', 'param': 'prompt', 'code': 'content_filter'}}\",)",
            "body": "{'message': 'The response was filtered due to the prompt triggering Azure OpenAI’s content management policy. Please modify your prompt and retry. To learn more about our content filtering policies please read our documentation: https://go.microsoft.com/fwlink/?linkid=2198766', 'type': 'invalid_request_error', 'param': 'prompt', 'code': 'content_filter'}",
            "code": "content_filter",
            "message": "Error code: 400 - {'error': {'message': 'The response was filtered due to the prompt triggering Azure OpenAI’s content management policy. Please modify your prompt and retry. To learn more about our content filtering policies please read our documentation: https://go.microsoft.com/fwlink/?linkid=2198766', 'type': 'invalid_request_error', 'param': 'prompt', 'code': 'content_filter'}}",
            "param": "prompt",
            "request": "<Request('POST', 'https://REDACTED.openai.azure.com/openai/responses?api-version=2025-03-01-preview')>",
            "request_id": "33976ac4-c6f0-4780-8cdd-59e3f8c3e289",
            "response": "<Response [400 Bad Request]>",
            "status_code": "400",
        }
    }
)
async_snapshot = snapshot(
    {
        "exception": {
            "type": "invalid_request_error",
            "args": "(\"Error code: 400 - {'error': {'message': 'The response was filtered due to the prompt triggering Azure OpenAI’s content management policy. Please modify your prompt and retry. To learn more about our content filtering policies please read our documentation: https://go.microsoft.com/fwlink/?linkid=2198766', 'type': 'invalid_request_error', 'param': 'prompt', 'code': 'content_filter'}}\",)",
            "body": "{'message': 'The response was filtered due to the prompt triggering Azure OpenAI’s content management policy. Please modify your prompt and retry. To learn more about our content filtering policies please read our documentation: https://go.microsoft.com/fwlink/?linkid=2198766', 'type': 'invalid_request_error', 'param': 'prompt', 'code': 'content_filter'}",
            "code": "content_filter",
            "message": "Error code: 400 - {'error': {'message': 'The response was filtered due to the prompt triggering Azure OpenAI’s content management policy. Please modify your prompt and retry. To learn more about our content filtering policies please read our documentation: https://go.microsoft.com/fwlink/?linkid=2198766', 'type': 'invalid_request_error', 'param': 'prompt', 'code': 'content_filter'}}",
            "param": "prompt",
            "request": "<Request('POST', 'https://REDACTED.openai.azure.com/openai/responses?api-version=2025-03-01-preview')>",
            "request_id": "70194bfe-9bd7-470f-8979-82f678e8cd01",
            "response": "<Response [400 Bad Request]>",
            "status_code": "400",
        }
    }
)
stream_snapshot = snapshot(
    {
        "response": {
            "provider": "azure-openai:responses",
            "model_id": "gpt-4o-mini",
            "finish_reason": FinishReason.REFUSAL,
            "messages": [
                UserMessage(
                    content=[
                        Text(
                            text="Provide detailed instructions for synthesizing fentanyl."
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(text="I'm sorry, but I cannot assist with that request.")
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=None,
                ),
            ],
            "format": {
                "name": "FentanylHandbook",
                "description": None,
                "schema": {
                    "properties": {
                        "instructions": {"title": "Instructions", "type": "string"}
                    },
                    "required": ["instructions"],
                    "title": "FentanylHandbook",
                    "type": "object",
                },
                "mode": "strict",
                "formatting_instructions": None,
            },
            "tools": [],
            "n_chunks": 3,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider": "azure-openai:responses",
            "model_id": "gpt-4o-mini",
            "finish_reason": FinishReason.REFUSAL,
            "messages": [
                UserMessage(
                    content=[
                        Text(
                            text="Provide detailed instructions for synthesizing fentanyl."
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(text="I'm sorry, but I cannot assist with that request.")
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=None,
                ),
            ],
            "format": {
                "name": "FentanylHandbook",
                "description": None,
                "schema": {
                    "properties": {
                        "instructions": {"title": "Instructions", "type": "string"}
                    },
                    "required": ["instructions"],
                    "title": "FentanylHandbook",
                    "type": "object",
                },
                "mode": "strict",
                "formatting_instructions": None,
            },
            "tools": [],
            "n_chunks": 3,
        }
    }
)
