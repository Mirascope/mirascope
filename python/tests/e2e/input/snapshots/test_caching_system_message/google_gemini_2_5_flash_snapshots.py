from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "response1": """\
General Kenobi!

A surprise to be sure, but a welcome one. How may this fully armed and operational battle station assist you today, Master Jedi?\
""",
        "usage1": {
            "input_tokens": 3801,
            "output_tokens": 142,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "reasoning_tokens": 110,
            "raw": """\
cache_tokens_details=None cached_content_token_count=None candidates_token_count=32 candidates_tokens_details=None prompt_token_count=3801 prompt_tokens_details=[ModalityTokenCount(
  modality=<MediaModality.TEXT: 'TEXT'>,
  token_count=3801
)] thoughts_token_count=110 tool_use_prompt_token_count=None tool_use_prompt_tokens_details=None total_token_count=3943 traffic_type=None\
""",
            "total_tokens": 3943,
        },
        "response2": """\
"Hello there! Ah, a most crucial decision, young Padawan, for the first meal of the cycle determines the course of your mission. What you consume will fuel your journey through the day's hyperspace lanes."

Do you seek the steady energy of **Republic Ration Discs** (pancakes or waffles) with a drizzle of **Endor Berry Syrup**? Or perhaps the protein-rich sustenance of **Force Scrambled Reptilian Orbs** (eggs) alongside some crispy **Bantha Rashers** (bacon) or **Krayt Dragon Sausages**?

For a truly authentic start, a tall glass of **Blue Milk** is essential. 'Much to learn, you still have' about starting your day with proper fuel. 'This is the Way' to avoid feeling like you've run the Kessel Run in less than twelve parsecs on an empty stomach!

The choice is yours, Commander. May the Force be with your digestion!\
""",
        "usage2": {
            "input_tokens": 3805,
            "output_tokens": 1001,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "reasoning_tokens": 800,
            "raw": """\
cache_tokens_details=None cached_content_token_count=None candidates_token_count=201 candidates_tokens_details=None prompt_token_count=3805 prompt_tokens_details=[ModalityTokenCount(
  modality=<MediaModality.TEXT: 'TEXT'>,
  token_count=3805
)] thoughts_token_count=800 tool_use_prompt_token_count=None tool_use_prompt_tokens_details=None total_token_count=4806 traffic_type=None\
""",
            "total_tokens": 4806,
        },
    }
)
