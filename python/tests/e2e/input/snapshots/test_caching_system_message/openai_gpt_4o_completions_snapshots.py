from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "response1": '"General Kenobi!" A surprise to be sure, but a welcome one. How may I assist you on your galactic journey today?',
        "usage1": {
            "input_tokens": 3659,
            "output_tokens": 28,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
            "raw": "CompletionUsage(completion_tokens=28, prompt_tokens=3659, total_tokens=3687, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=0, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0))",
            "total_tokens": 3687,
        },
        "response2": "\"Ah, the most important meal of the day, it is! Start your morning like a true Jedi with a nutritious breakfast that even Yoda would approve of. How about some Bantha blue milk pancakes with a side of roasted Porg eggs? They're sure to give you the energy of an entire squad of Clone Troopers! If you're feeling more like a scoundrel today, opt for a stack of Wookiee-approved Waffles with Kowakian monkey-lizard syrup. Punch it, Chewie, and remember: 'This is the Way' to start your day!\"",
        "usage2": {
            "input_tokens": 3663,
            "output_tokens": 117,
            "cache_read_tokens": 3584,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
            "raw": "CompletionUsage(completion_tokens=117, prompt_tokens=3663, total_tokens=3780, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=0, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=3584))",
            "total_tokens": 3780,
        },
    }
)
