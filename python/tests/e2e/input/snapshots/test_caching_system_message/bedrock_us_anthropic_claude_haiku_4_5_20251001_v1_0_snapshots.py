from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "response1": """\
# General Kenobi!

*You are a bold one.*

Greetings, my friend! Welcome to the HoloNet transmission station. I am fully operational and at your service, though I must say, "A surprise to be sure, but a welcome one!"

I sense you have wandered into my corner of the galaxy. Whether you seek wisdom from the Jedi Archives, require tactical assistance from the Rebellion, or simply wish to engage in witty banter worthy of a smuggler's cantina, I am here to help—*all while channeling the very essence of Star Wars itself*.

So tell me, what brings you to this sector of space? Do you have a query that needs answering? A problem requiring the Force? Or perhaps you simply wish to test whether my protocols are "impressive... most impressive"?

**May the Force be with you**, and do not hesitate to ask. "This is the Way." ⚔️✨\
""",
        "usage1": {
            "input_tokens": 4175,
            "output_tokens": 212,
            "cache_read_tokens": 0,
            "cache_write_tokens": 4167,
            "reasoning_tokens": 0,
            "raw": "Usage(cache_creation=CacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=4167), cache_creation_input_tokens=4167, cache_read_input_tokens=0, input_tokens=8, output_tokens=212, server_tool_use=None, service_tier=None)",
            "total_tokens": 4387,
        },
        "response2": """\
# 🌅 A Culinary Transmission from the Star Wars Cantina

*Adjusts holographic menu*

Greetings, young Padawan! What a *wonderful* query to begin your cycle! Allow me to present the breakfast options available across the galaxy:

## The High Ground Selections (My Recommendations)

**"This is the Way" - The Balanced Breakfast:**
- Blue Milk (or regular dairy of your choice—though blue is clearly superior)
- Eggs (prepared however the Force guides you: scrambled, fried, or poached)
- Toast or flatbread
- Fresh fruit, if available in your sector

*"Do. Or do not. There is no 'try'" when it comes to cracking eggs, young one.*

---

**The Rebel Alliance Special - Quick & Fortifying:**
- Oatmeal or granola with yogurt
- Berries (the Jedi Temple gardens produce excellent ones)
- A warm caf beverage (or coffee, if your midi-chlorian count is low)

*"I have a good feeling about this" breakfast choice.*

---

**The Scoundrel's Gambit - Hearty & Filling:**
- Bacon or sausage
- Hash browns or fried potatoes
- Toast with butter or jam
- Orange juice

*"Never tell me the odds" this won't keep you full until lunch!*

---

**The Minimalist Protocol - For the Time-Pressed:**
- A banana or granola bar
- Coffee/caf
- Perhaps some Jawa Juice (orange juice) for vitality

*"Another happy landing" in 5 minutes flat.*

---

## My Question for You, Master Jedi:

**Are you in a hurry, or do you have time to prepare something more elaborate?** Do you have dietary preferences or restrictions? Are you feeling particularly hungry, or just need fuel? \n\

*Much to learn about your preferences, I still have.* \n\

Give me these details, and I shall refine my recommendation with the precision of a targeting computer on a Star Destroyer! 🚀\
""",
        "usage2": {
            "input_tokens": 4179,
            "output_tokens": 487,
            "cache_read_tokens": 4167,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
            "raw": "Usage(cache_creation=CacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=4167, input_tokens=12, output_tokens=487, server_tool_use=None, service_tier=None)",
            "total_tokens": 4666,
        },
    }
)
