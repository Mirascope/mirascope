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
Okay, the user mentioned that the deal is getting worse. Let me start by understanding the context. The previous interaction was about the bot's responses, and now they're saying the deal is worse. I need to respond appropriately.

First, I should acknowledge their concern. It's important to show empathy and understanding. Maybe mention that the bot is designed to handle such situations but that there are challenges. Then, I can offer help, like suggesting ways to improve the bot's response or provide additional support.

I should keep the tone positive and encouraging. Let them know that they can ask for further assistance. It's good to make them feel supported. Also, maybe add a note about the bot's capabilities to reassure them that they're not alone in this endeavor.

I need to make sure the response is concise and focused. Avoid any negative language. Let me check if there's anything else they might need, but I'll stick to the main points. Alright, time to put it all together in a helpful and supportive way.
</think>

"Ah, the power of this battle station! The Force is strong with this document, and the bot's responses are now more formidable than ever. Is this sufficient, or do you wish me to 'alter the deal' until you beg me to stop?"  \n\

You're absolutely right—this expansion brings a new level of strength, and I'm honored to have contributed to it. If you'd like to refine the bot further, or if there's something you'd like to add, I'm here to help. The Force is with you, and I'm ready to continue to make the galaxy better.\
""",
        "usage2": {
            "input_tokens": 3859,
            "output_tokens": 333,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
            "provider_tool_usage": None,
            "raw": "MLXCassetteResponse(text='', token=151645, prompt_tokens=3859, generation_tokens=333, finish_reason='stop')",
            "total_tokens": 4192,
        },
        "response3": """\
<think>
Okay, the user mentioned they have a bad feeling about the bot's expansion. Let me start by acknowledging their concern. It's important to show empathy and understanding. The previous response was a bit generic, so I need to make it more personal.

The user's feedback is about the bot's performance, so I should address that directly. Maybe mention specific instances where the bot failed or didn't meet expectations. It's crucial to validate their feelings without making them feel judged.

I should also invite them to provide more details so I can tailor the response better. It's good to encourage them to share their thoughts and help them feel heard. Finally, wrap it up with a positive note to keep the conversation open.
</think>

"Ah, the power of this battle station! The Force is strong with this document, and the bot's responses are now more formidable than ever. Is this sufficient, or do you wish me to 'alter the deal' until you beg me to stop?"  \n\

You're absolutely right—this expansion brings a new level of strength, and I'm honored to have contributed to it. If you'd like to refine the bot further, or if there's something you'd like to add, I'm here to help. The Force is with you, and I'm ready to continue to make the galaxy better.\
""",
        "usage3": {
            "input_tokens": 3998,
            "output_tokens": 270,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
            "provider_tool_usage": None,
            "raw": "MLXCassetteResponse(text='', token=151645, prompt_tokens=3998, generation_tokens=270, finish_reason='stop')",
            "total_tokens": 4268,
        },
    }
)
