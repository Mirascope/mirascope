from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "response1": """\
**General Kenobi!** \n\

*adjusts imaginary Jedi robes with digital precision*

A surprise to be sure, but a welcome one! You have successfully initiated contact with this fully operational protocol droid. I sense a disturbance in the Force... or perhaps it's just the anticipation of an epic conversation ahead.

*mechanical whirring sounds in binary*

What brings you to this remote sector of the HoloNet, Master Jedi? Are you perhaps seeking guidance from the Jedi Archives? Technical assistance with your starship's hyperdrive? Or maybe you're just here to discuss the finer points of why the high ground is always the tactical advantage?

This is where the fun begins! How may this humble astromech... er, *protocol* droid assist you today?

*awaits transmission with the patience of Obi-Wan and the enthusiasm of R2-D2*\
""",
        "usage1": {
            "input_tokens": 4175,
            "output_tokens": 204,
            "cache_read_tokens": 0,
            "cache_write_tokens": 4167,
            "reasoning_tokens": 0,
            "raw": "Usage(cache_creation=CacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=4167), cache_creation_input_tokens=4167, cache_read_input_tokens=0, input_tokens=8, output_tokens=204, server_tool_use=None, service_tier='standard')",
            "total_tokens": 4379,
        },
        "response2": """\
*adjusts imaginary protocol droid posture*

"Hello there!" A breakfast consultation, I see! \n\

The morning meal is crucial, young Padawan - as Master Yoda would say, "Strong with hunger, you are. Feed you, we must." \n\

Consider these options from across the galaxy:

🥛 **Blue Milk and Bantha Cereal** - A classic Tatooine sunrise meal. Simple, nutritious, and it won't leave you feeling like you're stuck in the Sarlacc Pit by mid-morning.

🍳 **Nerf Scramble** (scrambled eggs) - "This is the Way" to start your day with protein. Perhaps with some crispy dewback strips (bacon) on the side?

🥞 **Jawa Juice and Power Coupling Cakes** (pancakes) - Sweet fuel for your hyperdrive engines! Stack them high like the spires of Coruscant.

🍞 **Moisture Farmer's Toast** - Simple but effective. Add some blue butter and Naboo berry jam for a taste that's "impressive... most impressive."

Remember: "Do or do not, there is no try" - so whatever you choose, commit to it fully! And as Han Solo would say about a good breakfast, "Never tell me the odds" of it keeping you satisfied until the next meal.

*beeps approvingly*

What sounds good to your taste sensors, Commander? The Force will guide your decision... but so will your refrigerator's current inventory levels.\
""",
        "usage2": {
            "input_tokens": 4179,
            "output_tokens": 350,
            "cache_read_tokens": 4167,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
            "raw": "Usage(cache_creation=CacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=4167, input_tokens=12, output_tokens=350, server_tool_use=None, service_tier='standard')",
            "total_tokens": 4529,
        },
    }
)
