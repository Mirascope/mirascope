from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "response1": "General Kenobi! This is where the fun begins. How might I assist you on this fine galactic day?",
        "usage1": {
            "input_tokens": 3698,
            "output_tokens": 24,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
            "raw": "CompletionUsage(completion_tokens=24, prompt_tokens=3698, total_tokens=3722, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=0, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0))",
            "total_tokens": 3722,
        },
        "response2": """\
Ah, breakfast! The most important meal of the day. A Jedi would tell you this is indeed the first battle to conquer. "Obi-Wan has taught you well" if you start with something balanced. Consider this:

1. **Blue Milk Smoothie**: A concoction fit for a Jedi! Blend some blue milk (or regular milk), bananas, and your favorite berries. The Force is strong with this one!

2. **Scrambled Porg Eggs**: Packed with protein, you could whip them up with a bit of cheese and vegetables. "Impressive... most impressive," when starting your day right.

3. **Corellian Toast**: Known to us as French toast. Top it with some fresh fruits and a drizzle of syrup. "This is where the fun begins!"

4. **Yoda Green Omelette**: Spinach, some herbs, and maybe a touch of pesto to give it that Yoda hue. "Much to learn, you still have" in cooking, but this is a wise choice.

5. **Wookiee Oats**: Simple oatmeal with honey, nuts, and sliced fruits. Breakfast to rival a Wookiee's strength!

“Choose wisely, and may the Force be with your breakfast!”\
""",
        "usage2": {
            "input_tokens": 3702,
            "output_tokens": 257,
            "cache_read_tokens": 3584,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
            "raw": "CompletionUsage(completion_tokens=257, prompt_tokens=3702, total_tokens=3959, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=0, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=3584))",
            "total_tokens": 3959,
        },
    }
)
