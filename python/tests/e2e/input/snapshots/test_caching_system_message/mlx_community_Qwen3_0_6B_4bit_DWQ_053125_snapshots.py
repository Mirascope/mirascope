from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "response1": """\
<think>
Okay, the user just said "Hello there." I need to respond appropriately. Let me start by acknowledging their greeting. Since the user is a new user, I should make it friendly and open. Maybe add a playful tone to keep it engaging.

I should check if there's any specific context I need to consider. The previous interaction was about the expanded protocol, so maybe the user is looking for a response that ties back to that. But since they just said "Hello there," I don't need to go into that. \n\

I should keep the response simple and positive. Maybe something like "Hello, and welcome to the Star Wars Meme Bot Protocol 2.0!" That sounds good. Let me make sure it's in the right tone and doesn't sound forced. Also, check if there's any other details the user might want, but as far as I can tell, this is the most appropriate response.
</think>

Hello, and welcome to the Star Wars Meme Bot Protocol 2.0!\
""",
        "usage1": {
            "input_tokens": 3726,
            "output_tokens": 208,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
            "raw": "MLXCassetteResponse(text='', token=151645, prompt_tokens=3726, generation_tokens=208, finish_reason='stop')",
            "total_tokens": 3934,
        },
        "response2": """\
<think>
Okay, the user is asking, "What should I have for breakfast?" I need to respond in a way that's helpful and in line with the bot's capabilities. Let me think about the previous interactions. The bot has a variety of responses, so I should pick one that's appropriate.

The bot's responses include things like a coffee, a snack, or a meal. Since the user is asking about breakfast, maybe a light snack like a banana or a fruit would be good. But I should make sure it's in the context of the bot's role. The bot's responses are about Star Wars, so maybe a snack that's a bit more in line with that.

Wait, the user's question is straightforward. The bot can respond with a simple answer. Let me check the previous examples. In the "Droid's Protocol" section, there's a "Coffee" option. That seems like a good choice. It's a common breakfast item and fits the Star Wars theme.

So, the response should be something like, "I have a coffee for breakfast!" or "A light snack, like a banana, for your energy." But since the bot's responses are in the context of the protocol, maybe a more specific answer. The previous example had a banana, so maybe that's a good choice.

I should also consider if the user might have a specific preference, but since there's no input, the bot can offer a general answer. Let me make sure the response is friendly and in line with the bot's tone. The bot uses phrases like "I have a bad feeling about this" when there's a problem, so maybe a slightly more positive response.

So, the final answer would be a simple, positive breakfast recommendation. Let me put that into the response format.
</think>

"Ah, a light snack, like a banana, for your energy!"\
""",
        "usage2": {
            "input_tokens": 3730,
            "output_tokens": 382,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
            "raw": "MLXCassetteResponse(text='', token=151645, prompt_tokens=3730, generation_tokens=382, finish_reason='stop')",
            "total_tokens": 4112,
        },
    }
)
