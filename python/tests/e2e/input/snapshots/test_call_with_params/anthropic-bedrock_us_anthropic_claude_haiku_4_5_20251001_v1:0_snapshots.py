from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "exception": {
            "type": "BadRequestError",
            "args": "(\"Error code: 400 - {'message': '`temperature` and `top_p` cannot both be specified for this model. Please use only one.'}\",)",
            "body": "{'message': '`temperature` and `top_p` cannot both be specified for this model. Please use only one.'}",
            "message": "Error code: 400 - {'message': '`temperature` and `top_p` cannot both be specified for this model. Please use only one.'}",
            "request": "<Request('POST', 'https://bedrock-runtime.us-east-1.amazonaws.com/model/us.anthropic.claude-haiku-4-5-20251001-v1:0/invoke')>",
            "request_id": "None",
            "response": "<Response [400 Bad Request]>",
            "status_code": "400",
        },
        "logging": ["Skipping unsupported parameter: seed=42 (provider: anthropic)"],
    }
)
