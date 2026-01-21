from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "response1": """\
This protocol is indeed "impressive... most impressive." You've crafted a document that's as rich and detailed as the Galactic Senate itself, full of creativity and Star Wars references that would delight any fan across the galaxy. The integration of humor, narrative structure, and detailed guidelines ensures that the bot will engage users in a way that's both entertaining and functional. You have truly "unleashed the power of this fully armed and operational battle station."

Should you require further revisions, feel free to ask. But as it stands, this is a document that any protocol droid would be proud to call its own. "May the Force be with you" as you implement this protocol in your project!\
""",
        "usage1": {
            "input_tokens": 3652,
            "output_tokens": 137,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
            "raw": "CompletionUsage(completion_tokens=137, prompt_tokens=3652, total_tokens=3789, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=0, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0))",
            "total_tokens": 3789,
        },
        "response2": 'Ah, "I see what you did there." A classic Lando Calrissian sentiment! If you feel the deal is getting worse, perhaps I can assist in "altering" the protocol to better suit your needs. Just let me know what you’d like to change, and we\'ll make sure it becomes "most impressive" once more. "This is the Way!"',
        "usage2": {
            "input_tokens": 3806,
            "output_tokens": 76,
            "cache_read_tokens": 3072,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
            "raw": "CompletionUsage(completion_tokens=76, prompt_tokens=3806, total_tokens=3882, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=0, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=3072))",
            "total_tokens": 3882,
        },
        "response3": "\"It’s a trap!\" Or maybe just a minor disturbance in the Force. If there's anything specific that's causing this feeling, let me know, and together we'll navigate out of this asteroid field of uncertainty. \"Stay on target,\" and we'll ensure the protocol is as solid as a Wookiee's loyalty. How can I assist in turning that bad feeling into a victorious end?",
        "usage3": {
            "input_tokens": 3897,
            "output_tokens": 75,
            "cache_read_tokens": 3840,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
            "raw": "CompletionUsage(completion_tokens=75, prompt_tokens=3897, total_tokens=3972, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=0, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=3840))",
            "total_tokens": 3972,
        },
    }
)
