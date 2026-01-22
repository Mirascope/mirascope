from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "response1": '<reasoning>The user says: "Hello there." According to bot design: greet with "Hello there!" The bot must reply with "General Kenobi!" as mandatory response? The protocol states: Greetings & Openings includes "Hello there!" => mandatory response: "General Kenobi!" So upon "Hello there." we respond with Hi greeting and reply "General Kenobi!" Also maybe some other greeting? It must use Star Wars style. I think just reply "General Kenobi!". Ensure no other unnecessary text. According to design, we respond "General Kenobi!" That is the mandatory response. Let\'s produce that.</reasoning>General Kenobi!',
        "usage1": {
            "input_tokens": 3721,
            "output_tokens": 136,
            "cache_read_tokens": 32,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
            "raw": "CompletionUsage(completion_tokens=136, prompt_tokens=3721, total_tokens=3857, completion_tokens_details=None, prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=32))",
            "total_tokens": 3857,
        },
        "response2": """\
<reasoning>The user asked, "What should I have for breakfast?" We need to respond with Star Wars style, following the policy. There's no disallowed content. We have to comply, use Star Wars theming. Must not provide disallowed content. Breakfast advice is allowed. We can respond with a Star Wars themed answer, maybe referring to the "HoloNet" etc. Do not say any disallowed content. We must use the style guidelines.

We need to incorporate the signature style: acknowledge user, maybe give suggestion like "A hearty corellian breakfast" etc. Ensure to respond with Star Wars references. Alright.</reasoning>*“Soon, the day will begin, and the Force will be in the breakfast,"* Master Kwank says.  \n\
Let me suggest a galactic breakfast that fuels both body and spirit.

- **Light-saber omelette** – whisk celestial eggs with a dash of Peroffi salt and a sprinkle of soy on the galactic stove. The rich gold white of the risotto‑like grains will give your day a crisp, youthful rhythm.   \n\
- **Yoda‑style smoothie** – blend frozen berries, a splash of blue milk, and a tablespoon of diced yew‑tree roots. It will *“bring balance”* to your morning nourishment.  \n\
- **Firefly coffee** – a light crema over a latte, served in a small cup with Helion pearls; it will *“ignite the core of your will.”*  \n\

Should you feel the heat of a Kessel Burn, substitute a hoth‑heat bulletproof, and your *“corellian Meathook”* can handle any relief.  \n\

Enjoy, Padawan. May your breakfast keep the *Tatooine* heat at bay and the *Dead Sea Scrolls* of your loom steady. 🐢✨\
""",
        "usage2": {
            "input_tokens": 3725,
            "output_tokens": 382,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
            "raw": "CompletionUsage(completion_tokens=382, prompt_tokens=3725, total_tokens=4107, completion_tokens_details=None, prompt_tokens_details=None)",
            "total_tokens": 4107,
        },
    }
)
