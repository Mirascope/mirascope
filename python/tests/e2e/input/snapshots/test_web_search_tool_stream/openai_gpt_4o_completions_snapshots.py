from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": "(\"Web search is only available in the OpenAI Responses API. Use a model with :responses suffix (e.g., 'openai/gpt-4o:responses').\",)",
            "feature": "WebSearchTool",
            "model_id": "None",
            "provider_id": "openai:completions",
        }
    }
)
