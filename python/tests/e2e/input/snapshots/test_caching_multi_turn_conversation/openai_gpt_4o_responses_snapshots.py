from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "response1": """\
"Impressive... most impressive!" 📜

This protocol is indeed a formidable construct, powerful enough to challenge the mightiest of the galaxy's legends. It would deflect a proton torpedo with ease and guide its users like a Jedi navigating hyperspace.

If you seek further modifications or refinements, say the word and I'll continue to wield the Force, shaping this document into an even greater masterpiece. If not, "This is where the fun begins!" 🌌\
""",
        "usage1": {
            "input_tokens": 3652,
            "output_tokens": 95,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
            "raw": "ResponseUsage(input_tokens=3652, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=95, output_tokens_details=OutputTokensDetails(reasoning_tokens=0), total_tokens=3747)",
            "total_tokens": 3747,
        },
        "response2": '"I have altered the deal. Pray I do not alter it further." If there\'s anything specific you\'d like to change or add, just let me know. Otherwise, "I\'ve got a bad feeling about this!" 💫',
        "usage2": {
            "input_tokens": 3763,
            "output_tokens": 44,
            "cache_read_tokens": 3584,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
            "raw": "ResponseUsage(input_tokens=3763, input_tokens_details=InputTokensDetails(cached_tokens=3584), output_tokens=44, output_tokens_details=OutputTokensDetails(reasoning_tokens=0), total_tokens=3807)",
            "total_tokens": 3807,
        },
        "response3": '"Fear not, young Padawan. We\'ll navigate this asteroid field together." If there\'s anything more I can do or clarify, just let me know. "This is the Way." 🌟',
        "usage3": {
            "input_tokens": 3821,
            "output_tokens": 39,
            "cache_read_tokens": 3584,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
            "raw": "ResponseUsage(input_tokens=3821, input_tokens_details=InputTokensDetails(cached_tokens=3584), output_tokens=39, output_tokens_details=OutputTokensDetails(reasoning_tokens=0), total_tokens=3860)",
            "total_tokens": 3860,
        },
    }
)
