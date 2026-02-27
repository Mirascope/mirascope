from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "response1": """\
<think>
Okay, the user just said "Hello there." I need to respond appropriately. Let me start by acknowledging their greeting. Since the user is a new user, I should make it friendly and open. Maybe add a playful tone to keep it light.

I should check if there's a specific response expected. The previous message was about the expanded protocol, so maybe the user is looking for a continuation of that. But since they just said "Hello there," I should respond in a way that's engaging and not too technical.

Let me think of a good opening line. Something like "Hello, young Padawan!" to keep it in line with the Star Wars context. Also, maybe add a bit of a nod to the previous interactions, like mentioning the HoloNet or the Jedi Archives, to show I'm connecting.

I should make sure the response is concise and not too long. Let me draft a few options and pick one that fits best. Maybe start with a greeting and then a brief explanation of the bot's capabilities, keeping it simple and positive.

Wait, the user might be testing if I can respond in a way that's not too technical. So, keeping it light and playful is key. Let me check the previous messages to ensure consistency. The user's last message was about the expanded protocol, so the response should align with that.

Okay, putting it all together: "Hello, young Padawan! The HoloNet is here, and the Jedi Archives are ready to help. What's your first question?" That way, it's engaging and keeps the conversation going.
</think>

Hello, young Padawan! The HoloNet is here, and the Jedi Archives are ready to help. What's your first question?\
""",
        "usage1": {
            "input_tokens": 3726,
            "output_tokens": 353,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
            "provider_tool_usage": None,
            "raw": "MLXCassetteResponse(text='', token=151645, prompt_tokens=3726, generation_tokens=353, finish_reason='stop')",
            "total_tokens": 4079,
        },
        "response2": """\
<think>
Okay, the user is asking, "What should I have for breakfast?" I need to respond in a way that's helpful and in line with the bot's capabilities. Let me think about the previous interactions. The bot has a variety of responses, so I should pick one that's appropriate.

The bot's responses include things like a coffee, a snack, or a meal. Since the user is asking about breakfast, maybe a light snack like a banana or a fruit. But I should make sure it's in the context of the bot's role. The bot's responses are about Star Wars, so maybe a snack that's a reference to the Force or a meme.

Wait, the user's question is straightforward. The bot can respond with a simple answer. Let me check the previous examples. In the "Droid's Protocol" section, there's a "Coffee" option. That seems like a good choice. It's a common breakfast item and ties into the Force.

So, the response should be something like, "I have a coffee for breakfast!" or "A light snack, like a banana, for your energy." But since the user is asking for breakfast, maybe a snack that's a reference to the Force. The bot's response should be in Star Wars context, so maybe "A snack that's a reference to the Force, like a banana or a fruit." But the user might prefer a more direct answer.

Alternatively, the bot could mention a specific item, like a "fruit bowl" or "a snack that's a reference to the Force." But the user might not be looking for that. The bot's responses are about the bot's actions, so maybe a simple answer. Let me go with "A light snack, like a banana, for your energy!" That's clear and in line with the bot's role.
</think>

"Ah, a light snack, like a banana, for your energy!"\
""",
        "usage2": {
            "input_tokens": 3730,
            "output_tokens": 393,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
            "provider_tool_usage": None,
            "raw": "MLXCassetteResponse(text='', token=151645, prompt_tokens=3730, generation_tokens=393, finish_reason='stop')",
            "total_tokens": 4123,
        },
    }
)
