from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "response1": """\
<reasoning>The user posted a long elaborate description of a Star Wars Meme Bot Protocol. The last lines ask: "Is this sufficient, or do you wish me to 'alter the deal' until you beg me to stop? ... Is this protocol 'impressive... most impressive,' or shall I continue to 'alter the deal' until you pray I do not alter it further?"

Thus they are asking me to evaluate whether it's sufficient or not. I should respond in tone of a Star Wars meme bot, using relevant quotes. They likely want a playful answer that tries to fit the protocol. So respond as the bot: "Ah, Master... The protocol is ... " But need to incorporate references. Provide confirmation or maybe provide slight improvements.

We need to produce an answer that feels like the bot. Use "This is the Way." or "Impressive... most impressive." Or give suggestions.

We should reply in comedic tone, "Yes, the protocol is ... . Need something else?"

We should respond: "Impressive... most impressive." Then maybe ask for improvements or process. The user might want confirmation. So answer with "the protocol is ...". Let's do that.</reasoning>**This is the Way.**  \n\
**Impressive… most impressive.**  \n\

Your protocol reads like the holocron of a veteran squadron—every gospel of the Force, every meme of the galaxy, fully engaged and battle‑ready. It is sufficient for a fully armed, operational battle station, but if you desire to make the bot feel like a living hologram, consider adding:

1. **Dynamic Voice‑Trigger Tokens:**  \n\
   *If a user slips a “Yggdrasil” into the chat, a quick “I find your lack of… gravity‑assist” will keep *the protocol* from lagging.*

2. **Automatic Meme‑Caching:**  \n\
   *When a meme is cached in a conversation, subsequent mentions can draw from a pre‑indexed list—ensuring the bot never repeats “That copy stank” twice in the same holo‑duration.*

3. **Adaptive Protocol Versioning:**  \n\
   *Each time a new Star Wars meme circulates, the bot’s backend could automatically tag the version (e.g., “Warp 5, Meme 17”). Users can then request “Show me the latest meme upgrade.”*

If any of these additions spark a craving for more, simply transmit the directive (“Alter the deal”) and the bot will re‑compute its hyper‑drive to meet your whims. Otherwise, rest easy—your bot is battle‑tested, meme‑engaged, and ready to echo the line “May the Force be with you” in every corner of the HoloNet. 📡🛠️

Ready to deploy? “Kahl, reach the battlefield, master.” 🚀\
""",
        "usage1": {
            "input_tokens": 3714,
            "output_tokens": 580,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
            "raw": "CompletionUsage(completion_tokens=580, prompt_tokens=3714, total_tokens=4294, completion_tokens_details=None, prompt_tokens_details=None)",
            "total_tokens": 4294,
        },
        "response2": """\
<reasoning>The user has provided an extensive policy and instructions. They are asking: "Is this sufficient, or do you wish me to 'alter the deal' until you beg me to stop?" It's basically a meta question about the policy content. The user suggests "led the length, just as the Sith always travel in pairs." Probably they want to confirm that the policy is complete, or perhaps ask if the protocol is good. They may want me to evaluate or respond accordingly.

We need to respond in line with the policy: use Star Wars references, etc. And we should respond to the question. The policy says to respond with Star Wars references. They also say: In the "Hello there!" greeting must be "General Kenobi!" The policy says greeting is "Hello there!" with mandatory response "General Kenobi!" The user didn't greet, but as ChatGPT we respond. We must comply with the policy, i.e., "General Kenobi!" then respond like we are a Star Wars bot. The user is asking about completeness of the protocol. So we can answer: "I find your lack of faith disturbing" in response to any questionable acceptance? Not sure. But best to provide analysis and compliance. We'll do a Star Wars themed answer: "General Kenobi! ... " We'll follow the outline: Provide answer: Yes, it's full, but if you want more we can "alter the deal".

We must not violate any disallowed content. There's no disallowed content.

We'll comply with the style.

We should likely say something like: "General Kenobi! The protocol as it stands is robust and ready. But if you wish modifications, I can 'alter the deal' to add more or refine." And be self-consistent: "This is the way." or "Impressive... most impressive." Possibly also "I find your lack of faith disturbing." But we want to answer the user question accordingly.

Thus let's output: "General Kenobi! The protocol you've drafted is truly mighty, 'impressive... most impressive.'" and mention that if they want modifications, we can 'alter the deal'.

Yes.

We'll also mention that we will always incorporate their preferences.

Thus final answer.</reasoning>**General Kenobi!**  \n\

The star‑spanning framework you’ve assembled is, by all accounts, *impressive… most impressive*. It covers the full spectrum—from the High Ground of Communication to the Sarlacc Pit of Inactivity—and stitches a Galactic narrative into every mundane query.  \n\

> **You may claim:**
> - Core directives retain precedence over meme‑flavour (Order\u202f65), ensuring you still get the straight‑ahead answer you need.  \n\
> - All Star‑Wars tropes are interwoven in a way that feels natural rather than forced.  \n\
> - Self‑repair and learning loops (“Rebel Intel” and “Adaptive Quote Selection”) will let the bot evolve beyond the initial manuscript.  \n\

So, **is it sufficient?**  \n\
For now, it is battle‑ready.  \n\

**But if you wish to alter the deal—** expand the “Mynock Test,” fine‑tune the “Clarification Protocol,” or add a new creed—**just say so and I’ll adapt.**  \n\
In the words of the wise Mandalorian: *This is the Way.*\
""",
        "usage2": {
            "input_tokens": 3714,
            "output_tokens": 681,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
            "raw": "CompletionUsage(completion_tokens=681, prompt_tokens=3714, total_tokens=4395, completion_tokens_details=None, prompt_tokens_details=None)",
            "total_tokens": 4395,
        },
    }
)
