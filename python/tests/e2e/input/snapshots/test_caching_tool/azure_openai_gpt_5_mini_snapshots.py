from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "response1": "General Kenobi! How can I assist you today?",
        "usage1": {
            "input_tokens": 3779,
            "output_tokens": 213,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "reasoning_tokens": 192,
            "raw": "CompletionUsage(completion_tokens=213, prompt_tokens=3779, total_tokens=3992, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=192, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0))",
            "total_tokens": 3992,
        },
        "response2": """\
Great question — I can tailor a pick to your time, diet, and cravings. Short list of good choices by need (plus quick recipes):

If you want something fast
- Greek yogurt + fruit + a handful of nuts or granola — high protein, <5 minutes.

If you need long-lasting fullness (high-protein)
- Veggie omelette: 2–3 eggs, chopped spinach/tomato/onion, a little cheese — cook 5–8 minutes.

If you want something you can prep ahead
- Overnight oats: 1/2 cup rolled oats + 1/2–1 cup milk (dairy or plant) + 1 tbsp chia or yogurt + 1 tsp sweetener + fruit. Refrigerate overnight.

If you want portable/quick energy
- Smoothie: 1 banana + 1 cup berries + a handful of spinach + 1 scoop protein or 2 tbsp nut butter + 1 cup milk or water. Blend.

If you prefer savory + trendy
- Avocado toast with an egg: mash 1/2 avocado with lemon, salt, pepper, spread on toast, top with a fried/poached egg and chili flakes.

If you’re vegan or gluten-free
- Chia pudding: 3 tbsp chia + 1 cup milk + sweetener, stir and chill 30+ minutes (ideally overnight). Top with fruit and nuts.

If you want low-carb
- Cottage cheese or ricotta bowl with cucumber, cherry tomatoes, olive oil, salt, pepper, and herbs — or a spinach+feta omelette.

If it’s a weekend treat
- Pancakes or French toast with fruit and yogurt — make from scratch or boost store batter with mashed banana and berries.

Quick tips
- Protein + fiber + healthy fat keeps you full longer.
- Carbs are fine in the morning if you need quick energy (exercise, busy morning).
- If you tell me how much time you have, any dietary restrictions, and whether you want sweet or savory, I’ll pick one and give a 3–5 minute step-by-step. Which do you prefer?\
""",
        "usage2": {
            "input_tokens": 3783,
            "output_tokens": 892,
            "cache_read_tokens": 2688,
            "cache_write_tokens": 0,
            "reasoning_tokens": 448,
            "raw": "CompletionUsage(completion_tokens=892, prompt_tokens=3783, total_tokens=4675, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=448, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=2688))",
            "total_tokens": 4675,
        },
    }
)
