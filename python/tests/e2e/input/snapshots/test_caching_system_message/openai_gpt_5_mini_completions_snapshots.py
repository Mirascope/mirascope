from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "response1": """\
General Kenobi!

How can this humble astromech assist you across the HoloNet today?\
""",
        "usage1": {
            "input_tokens": 3658,
            "output_tokens": 221,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "reasoning_tokens": 192,
            "raw": "CompletionUsage(completion_tokens=221, prompt_tokens=3658, total_tokens=3879, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=192, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0))",
            "total_tokens": 3879,
        },
        "response2": """\
The Force is hungry. Choose your breakfast based on time, mood, and allegiance:

- Quick and balanced (5 min): Greek yogurt + granola + mixed berries — protein, crunch, and fiber. "Punch it, Chewie!"
- Hearty & energizing (10–12 min): Scrambled eggs with spinach and feta on whole-grain toast — simple, filling, and keeps you focused.
- On the go (2–3 min prep): Banana + natural peanut butter on whole-grain bread or a protein bar and coffee — portable and reliable.
- Low-carb / Keto (5–8 min): Omelette with cheese, mushrooms, and avocado — satiating, low carbs.
- Vegan / Make-ahead: Overnight oats with almond milk, chia seeds, maple, and berries — prep tonight, eat like a Jedi tomorrow.
- Smoothie (5 min): Banana + spinach + protein powder or Greek yogurt + frozen berries + a splash of milk — sip while briefing the fleet.
- Treat-yourself (20–30 min): Pancakes or French toast with fresh fruit — for the morning that deserves applause. "Great shot, kid, that was one in a million!"

Which path calls to you? Any dietary restrictions, time limits, or ingredients on your ship manifest I should account for?\
""",
        "usage2": {
            "input_tokens": 3662,
            "output_tokens": 529,
            "cache_read_tokens": 2816,
            "cache_write_tokens": 0,
            "reasoning_tokens": 256,
            "raw": "CompletionUsage(completion_tokens=529, prompt_tokens=3662, total_tokens=4191, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=256, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=2816))",
            "total_tokens": 4191,
        },
    }
)
