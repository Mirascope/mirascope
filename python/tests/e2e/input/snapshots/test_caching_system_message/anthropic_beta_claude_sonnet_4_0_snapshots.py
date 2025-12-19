from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "response1": """\
**General Kenobi!**

*adjusts imaginary Jedi robes*

A surprise to be sure, but a welcome one! I sense a disturbance in the Force... could it be that you seek assistance from this humble protocol droid? My circuits are buzzing with excitement - this is where the fun begins!

What brings you to this corner of the HoloNet today, Master Jedi? Are you perhaps in need of guidance navigating the treacherous asteroid field of daily tasks? Or maybe you require tactical support for a mission to the Outer Rim territories of productivity?

*beeps enthusiastically like R2-D2*

Remember, the Force will be with you... always. But first, how may this fully operational battle station of helpfulness serve you today?

🌟 *May the Force be with you!* 🌟\
""",
        "usage1": {
            "input_tokens": 4175,
            "output_tokens": 193,
            "cache_read_tokens": 4167,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
            "raw": "BetaUsage(cache_creation=BetaCacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=4167, input_tokens=8, output_tokens=193, server_tool_use=None, service_tier='standard')",
            "total_tokens": 4368,
        },
        "response2": """\
"Good morning, young Padawan! A most excellent question from the outer rim territories of hunger, this is."

*adjusts imaginary Jedi robes*

"Much sustenance, your body requires after the long hyperspace jump through sleep. Several options from across the galaxy, I sense:

**The Tatooine Moisture Farm Special:** Blue milk (regular milk) with some Bantha cereal - simple, but it sustained young Skywalker through his training.

**The Corellian Smuggler's Fuel:** Strong caf (coffee) with some quick rations (toast or pastry) - perfect for those who need to make the Kessel Run to work in less than 12 parsecs.

**The Jedi Temple Feast:** A balanced meal with protein (eggs), carbohydrates (bread or fruit), and perhaps some Dagobah swamp vegetables - for 'the Force flows through all living things,' including a nutritious breakfast.

**The Wookiee Warrior Portion:** Something hearty and filling - pancakes or a full breakfast spread, because 'let the Wookiee win' when it comes to morning hunger.

*waves hand mysteriously*

What calls to you from the galactic pantry, Master? 'Search your feelings, you know what you crave.' And remember - 'do or do not, there is no try' when it comes to starting your day with proper fuel!

This is the Way to a successful morning mission."

*beeps approvingly like R2-D2*\
""",
        "usage2": {
            "input_tokens": 4179,
            "output_tokens": 348,
            "cache_read_tokens": 4167,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
            "raw": "BetaUsage(cache_creation=BetaCacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=4167, input_tokens=12, output_tokens=348, server_tool_use=None, service_tier='standard')",
            "total_tokens": 4527,
        },
    }
)
