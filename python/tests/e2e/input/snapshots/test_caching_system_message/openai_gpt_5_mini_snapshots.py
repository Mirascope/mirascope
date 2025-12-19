from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "response1": "General Kenobi! How may I assist you today, Master Jedi?",
        "usage1": {
            "input_tokens": 3658,
            "output_tokens": 212,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "reasoning_tokens": 192,
            "raw": "ResponseUsage(input_tokens=3658, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=212, output_tokens_details=OutputTokensDetails(reasoning_tokens=192), total_tokens=3870)",
            "total_tokens": 3870,
        },
        "response2": """\
Short answer: pick one based on how much time and what you want (quick, healthy, protein, indulgent). Here are fast options with one-line how-tos — choose your breakfast destiny.

- Quick (5 min): Greek yogurt + berries + a handful of granola + drizzle of honey. Fast, balanced, and portable.
- Balanced/healthy: Oatmeal (rolled oats) with milk, sliced banana, a spoon of nut butter, and cinnamon. Slow-burning energy.
- High-protein: 2–3 eggs (scrambled or omelette) with spinach and tomato, plus a slice of whole-grain toast or half an avocado.
- Vegan: Tofu scramble with turmeric, nutritional yeast, sautéed peppers/onion, and whole-grain toast or a slice of avocado.
- Low-carb / keto: Veggie omelette (eggs, spinach, mushrooms, cheese) with smoked salmon or bacon and avocado.
- On-the-go: Smoothie (banana, spinach, protein powder or Greek yogurt, milk/plant milk, 1 tbsp nut butter) + a hard-boiled egg.
- Indulgent weekend: Pancakes or waffles with fresh berries, maple syrup, and crispy bacon or sausage.

Star Wars-themed pick (for fun): “Corellian Power Breakfast” — scrambled eggs with spinach & smoked salmon, a slice of seeded toast, and a strong coffee (punch it, Chewie!).

Anything you can’t eat or a time limit? Tell me that and I’ll suggest the optimal dish — and I’ll add a fitting holo-quote for bonus motivation. May the Force (and caffeine) be with you.\
""",
        "usage2": {
            "input_tokens": 3662,
            "output_tokens": 983,
            "cache_read_tokens": 2816,
            "cache_write_tokens": 0,
            "reasoning_tokens": 640,
            "raw": "ResponseUsage(input_tokens=3662, input_tokens_details=InputTokensDetails(cached_tokens=2816), output_tokens=983, output_tokens_details=OutputTokensDetails(reasoning_tokens=640), total_tokens=4645)",
            "total_tokens": 4645,
        },
    }
)
