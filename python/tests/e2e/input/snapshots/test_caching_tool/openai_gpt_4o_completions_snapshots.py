from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "response1": "General Kenobi! This is where the fun begins. How may I assist you in this galaxy far, far away today?",
        "usage1": {
            "input_tokens": 3698,
            "output_tokens": 26,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
            "provider_tool_usage": None,
            "raw": "CompletionUsage(completion_tokens=26, prompt_tokens=3698, total_tokens=3724, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=0, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0))",
            "total_tokens": 3724,
        },
        "response2": "\"For breakfast, the choice is yours. But remember, 'A Jedi must have the deepest commitment, the most serious mind.' Start your day with something that gives you the energy of a podracer and the calm of a Jedi Knight meditating. Perhaps eggs with a side of fruits from Dagobah, or blue milk and a protein bantha steak. This is the Way to a great start!\"",
        "usage2": {
            "input_tokens": 3702,
            "output_tokens": 81,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
            "provider_tool_usage": None,
            "raw": "CompletionUsage(completion_tokens=81, prompt_tokens=3702, total_tokens=3783, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=0, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0))",
            "total_tokens": 3783,
        },
    }
)
