from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "response1": "General Kenobi! How may I assist you today, Master Jedi?",
        "usage1": {
            "input_tokens": 3658,
            "output_tokens": 280,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "reasoning_tokens": 256,
            "raw": "CompletionUsage(completion_tokens=280, prompt_tokens=3658, total_tokens=3938, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=256, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0))",
            "total_tokens": 3938,
        },
        "response2": """\
Hello there!

Short answer: pick based on time and goals — here are quick, tasty options depending on what you need right now.

1) Quick & Energizing (5 minutes)
- Greek yogurt parfait: Greek yogurt + honey + granola + berries. Protein and fuel for the morning. "Punch it, Chewie!"

2) Protein-Packed (10–12 minutes)
- Veggie omelette or scrambled eggs with spinach, tomatoes, and feta. Keeps you full and focused. Great if you need brainpower for the day.

3) On-the-Go (2 minutes)
- Banana with nut butter and a handful of nuts, or a ready-made protein smoothie (banana, protein powder, milk/plant milk, spinach). Fast and portable.

4) Low-Carb / Keto Friendly (5–10 minutes)
- Avocado + smoked salmon or eggs cooked in butter or olive oil. Satisfying, low-carb, and flavorful.

5) Comfort / Weekend Treat (20–30 minutes)
- Pancakes or French toast with fruit and a drizzle of maple syrup. Save this for when you have time to enjoy it.

6) Light & Refreshing (5 minutes)
- Green smoothie: spinach + frozen mango/banana + Greek yogurt or protein powder + water/almond milk. Easy digestion and vitamins.

How to pick: if you’re short on time — go Quick or On-the-Go. If you need to stay full longer — Protein-Packed. Feeling indulgent? Comfort.

Which direction suits you — speedy, hearty, light, or treat? Tell me any food preferences or allergies, and I’ll tailor the perfect menu. May the Force be with your breakfast.\
""",
        "usage2": {
            "input_tokens": 3662,
            "output_tokens": 863,
            "cache_read_tokens": 2944,
            "cache_write_tokens": 0,
            "reasoning_tokens": 512,
            "raw": "CompletionUsage(completion_tokens=863, prompt_tokens=3662, total_tokens=4525, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=512, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=2944))",
            "total_tokens": 4525,
        },
    }
)
