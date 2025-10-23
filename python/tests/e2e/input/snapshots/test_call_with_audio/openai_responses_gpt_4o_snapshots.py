from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": '(\'provider "openai:responses" does not support audio inputs. Try using "openai:completions" instead\',)',
            "feature": "audio input",
            "model_id": "None",
            "provider": "openai:responses",
        }
    }
)
