from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "response1": "General Kenobi! How can I assist you today?",
        "usage1": {
            "input_tokens": 3697,
            "output_tokens": 145,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "reasoning_tokens": 128,
            "raw": "ResponseUsage(input_tokens=3697, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=145, output_tokens_details=OutputTokensDetails(reasoning_tokens=128), total_tokens=3842)",
            "total_tokens": 3842,
        },
        "response2": """\
Great — I can help. Any dietary restrictions, ingredients you have, or time constraints? If not, here are quick, tasty options by how much time you have and by goal.

If you have 5 minutes (grab-and-go)
- Greek yogurt + berries + a drizzle of honey and granola — protein + fiber.
- Whole-grain toast with peanut/almond butter and banana slices.
- 2 hard-boiled eggs + an apple.

If you have ~15 minutes (fast but cooked)
- Avocado toast topped with a poached or fried egg and a squeeze of lemon.
- Smoothie: spinach, frozen banana, protein powder or Greek yogurt, a tablespoon of nut butter, and milk/water.
- Veggie omelet or scrambled eggs with tomatoes, spinach, and feta.

If you have ~30 minutes (sit-down, more filling)
- Oatmeal cooked with milk, topped with nuts, cinnamon, and fruit (or make overnight oats the night before).
- Breakfast burrito: scrambled eggs or tofu, black beans, salsa, avocado in a whole-wheat tortilla.
- Savory grain bowl: quinoa, roasted veggies, a soft-boiled egg, and a tahini drizzle.

If you’re aiming for specific goals
- Weight loss: high-protein, moderate-fiber (eggs + veg, Greek yogurt + berries).
- Muscle gain: more carbs + protein (oatmeal with protein powder or eggs + whole-grain toast).
- Low-carb: omelet or tofu scramble with veggies and avocado.

One simple balanced pick (15 minutes)
- Avocado toast + egg: 1 slice whole-grain toast, 1/2 avocado mashed with salt/pepper/lemon, top with a fried or poached egg, and add chili flakes or cherry tomatoes. Protein + healthy fat + fiber.

Tell me what you have in the fridge or your goal/mood and I’ll give a specific recipe.\
""",
        "usage2": {
            "input_tokens": 3701,
            "output_tokens": 658,
            "cache_read_tokens": 3584,
            "cache_write_tokens": 0,
            "reasoning_tokens": 256,
            "raw": "ResponseUsage(input_tokens=3701, input_tokens_details=InputTokensDetails(cached_tokens=3584), output_tokens=658, output_tokens_details=OutputTokensDetails(reasoning_tokens=256), total_tokens=4359)",
            "total_tokens": 4359,
        },
    }
)
