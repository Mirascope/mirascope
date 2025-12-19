from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "response1": "**ToolCall (star_wars_tool):** {}",
        "usage1": {
            "input_tokens": 3900,
            "output_tokens": 12,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "reasoning_tokens": 77,
        },
        "response2": """\
Ah, a query of sustenance! For breakfast, young Padawan, you might consider some nutrient paste, or perhaps a warm mug of Jawa Juice to awaken your internal systems.

However, my primary function is to navigate the hyperspace lanes of Star Wars lore and deliver responses with the precision of a thermal detonator! Would you like me to engage with you in the manner of a wise Jedi Master, a cunning scoundrel, or perhaps a stoic Mandalorian? What Star Wars wisdom or meme-tastic response can I offer you today?\
""",
        "usage2": {
            "input_tokens": 3904,
            "output_tokens": 110,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "reasoning_tokens": 185,
        },
    }
)
