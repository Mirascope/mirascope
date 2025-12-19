from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "response1": """\
Ah, truly a magnificent reimagining of the galaxy's most compelling lore, filled with all the wit and wisdom worthy of a council of Jedi Masters and Sith Lords alike. This Expanded Holocron resonates with the power and grandeur of the Force, offering a protocol that is both entertaining and functionally robust—like a well-balanced lightsaber.

You have captured the essence of a "fully armed and operational battle station," and this Star Wars Meme Bot Protocol 2.0 is indeed "impressive... most impressive." It exhibits the delightful combination of lore accuracy, meme energy, and practical interaction guidelines that would make even the most stoic Mandalorian nod in approval.

"Shall I continue to 'alter the deal'?" you ask. At this juncture, the protocol stands strong, more fortified than the shields of a Mon Calamari cruiser. It might tempt the likes of the discerning Grand Moff or the cynical smuggler, but even they would acknowledge its prowess. "The Force is strong with this one," indeed.

If further refinement becomes necessary, know that I am always here, ready to channel the Force and deliver the insight you seek. Until then, "May the Force be with you" in your endeavors to bring balance and levity to interactions across the HoloNet!\
""",
        "usage1": {
            "input_tokens": 3652,
            "output_tokens": 263,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
            "raw": "CompletionUsage(completion_tokens=263, prompt_tokens=3652, total_tokens=3915, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=0, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0))",
            "total_tokens": 3915,
        },
        "response2": """\
This protocol is indeed "impressive... most impressive." You've crafted a comprehensive guide to turning a Star Wars meme bot into a fully armed and operational battle station of galactic communication. The integration of humor, Star Wars lore, and a structured interaction framework creates a unique, entertaining experience while ensuring functionality. Each section is detailed with creative implementations and considerations, ensuring the bot’s responses maintain thematic consistency and context.

If there's any refinement needed, it would only be minor adjustments based on testing user interactions to ensure smooth operation and adjust for any areas where the protocol may need flexibility or additional depth. You've established a robust foundation here, ready to engage with users in a way that truly embodies the spirit of the Star Wars universe.

May the Force be with your implementation!\
""",
        "usage2": {
            "input_tokens": 3652,
            "output_tokens": 151,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
            "raw": "CompletionUsage(completion_tokens=151, prompt_tokens=3652, total_tokens=3803, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=0, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0))",
            "total_tokens": 3803,
        },
    }
)
