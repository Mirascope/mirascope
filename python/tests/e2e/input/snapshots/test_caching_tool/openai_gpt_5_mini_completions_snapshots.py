from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "response1": "General Kenobi! How can I assist you today?",
        "usage1": {
            "input_tokens": 3779,
            "output_tokens": 148,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "reasoning_tokens": 128,
            "raw": "CompletionUsage(completion_tokens=148, prompt_tokens=3779, total_tokens=3927, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=128, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0))",
            "total_tokens": 3927,
        },
        "response2": """\
Nice — I can help. A couple quick clarifying questions that will let me tailor suggestions: any dietary restrictions (vegetarian, vegan, gluten-free, allergies)? How much time do you have (5, 15, 30+ minutes)? Want something light, filling, or indulgent?

Meanwhile, here are tasty options by category — pick one that fits your time and goal:

Quick (5–10 minutes)
- Smoothie: frozen banana + handful of berries + scoop protein or Greek yogurt + milk or plant milk + a spoonful peanut butter. Blend — drinkable and fast.
- Avocado toast with egg: smash half an avocado on whole-grain toast, sprinkle salt/pepper/chili flakes, top with a fried/poached egg.
- Greek yogurt parfait: plain Greek yogurt, granola, honey, and sliced fruit.

Balanced & Filling (10–20 minutes)
- Veggie omelette or scrambled eggs: 2–3 eggs, spinach, tomato, mushrooms, cheese. Quick, high-protein, satiating.
- Breakfast burrito: scrambled eggs or tofu scramble, black beans, salsa, avocado in a tortilla. Make-ahead option: wrap and freeze.

Make-ahead / Low-effort for busy mornings
- Overnight oats: oats + milk + chia + sweetener + fruit, refrigerated overnight. Eat cold or warmed.
- Chia pudding: chia seeds + milk + sweetener, set overnight; top with fruit/nuts.

Comfort / Indulgent (20–30+ minutes)
- Pancakes or waffles: classic or oat flour pancakes; top with fruit and a little maple syrup.
- Shakshuka: eggs poached in spicy tomato sauce — flavorful and great with crusty bread.

Special diets
- Low-carb / Keto: scrambled eggs with spinach, avocado, and smoked salmon.
- Vegan: tofu scramble or smoothie bowl with plant protein and seeds.

Drinks
- Coffee or tea (if you drink it), plus a water glass to hydrate.
- Green smoothie or fresh juice if you want extra greens.

Tell me your restrictions and how much time you have and I’ll give one tailored recipe with exact ingredients and steps. Which sounds good?\
""",
        "usage2": {
            "input_tokens": 3783,
            "output_tokens": 649,
            "cache_read_tokens": 3712,
            "cache_write_tokens": 0,
            "reasoning_tokens": 192,
            "raw": "CompletionUsage(completion_tokens=649, prompt_tokens=3783, total_tokens=4432, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=192, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=3712))",
            "total_tokens": 4432,
        },
    }
)
