from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "response1": """\
<think>
Okay, let's see. The user is talking about a bot that's been expanded into a fully armed and operational battle station. They mention that the bot's responses are now more powerful and that the Force is strong with it. The user is asking if this is sufficient or if they want to "alter the deal" until they stop.

First, I need to understand the context. The user is describing a Star Wars bot that has been enhanced with advanced features, making it a battle station. The bot's responses are now more powerful, which suggests that the bot's capabilities have increased. The user is reflecting on whether this expansion is enough and if they want to change the bot's design further.

The user's original message was about the bot's power, and now they're asking about the adequacy of the expansion. The response should acknowledge the expansion and the power it brings, then ask if they want to continue or change it. The tone should be enthusiastic but also open to feedback.

I should structure the response to first acknowledge the expansion, mention the power, and then invite the user to ask if they want to alter the bot further. It's important to keep the tone positive and encouraging, showing that the bot is a great addition to the Star Wars universe.
</think>

"Ah, the power of this battle station! The Force is strong with this document, and the bot's responses are now more formidable than ever. Is this sufficient, or do you wish me to 'alter the deal' until you beg me to stop?"  \n\

You're absolutely right—this expansion brings a new level of strength, and I'm honored to have contributed to it. If you'd like to refine the bot further, or if there's something you'd like to add, I'm here to help. The Force is with you, and I'm ready to continue to make the galaxy better.\
""",
        "usage1": {
            "input_tokens": 3718,
            "output_tokens": 382,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
            "provider_tool_usage": None,
            "raw": "MLXCassetteResponse(text='', token=151645, prompt_tokens=3718, generation_tokens=382, finish_reason='stop')",
            "total_tokens": 4100,
        },
        "response2": """\
<think>
Okay, let's see. The user is talking about a bot that's been expanded into a fully armed and operational battle station. They mention that the bot's responses are now more powerful and that the Force is strong with it. The user is asking if this is sufficient or if they want to "alter the deal" until they stop.

First, I need to understand the context. The user is describing a Star Wars bot that has been enhanced with advanced features, making it a battle station. The bot's responses are now more powerful, which suggests that the bot's capabilities have increased. The user is reflecting on whether this expansion is enough and if they want to change the bot's design further.

The user's original message was about the bot's power, and now they're asking about the adequacy of the expansion. The response should acknowledge the expansion and the power it brings, then ask if they want to continue or change it. The tone should be enthusiastic but also open to feedback.

I should structure the response to first acknowledge the expansion, mention the power, and then invite the user to ask if they want to alter the bot further. It's important to keep the tone positive and encouraging, showing that the bot is a great addition to the Star Wars universe.
</think>

"Ah, the power of this battle station! The Force is strong with this document, and the bot's responses are now more formidable than ever. Is this sufficient, or do you wish me to 'alter the deal' until you beg me to stop?"  \n\

You're absolutely right—this expansion brings a new level of strength, and I'm honored to have contributed to it. If you'd like to refine the bot further, or if there's something you'd like to add, I'm here to help. The Force is with you, and I'm ready to continue to make the galaxy better.\
""",
        "usage2": {
            "input_tokens": 3718,
            "output_tokens": 382,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
            "provider_tool_usage": None,
            "raw": "MLXCassetteResponse(text='', token=151645, prompt_tokens=3718, generation_tokens=382, finish_reason='stop')",
            "total_tokens": 4100,
        },
    }
)
