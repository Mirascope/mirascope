from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "response1": """\
General Kenobi! It’s an honor to engage with you in this grand digital arena. Here at our fully armed and operational battle station, we’re ready to face any challenge, just like old times. Whether you seek wisdom, a meme to brighten your day, or guidance through the labyrinth of the galaxy far, far away, we’ve got you covered.

If you have a query, need assistance, or simply wish to revel in the Star Wars saga, let’s embark on this journey together. "This is where the fun begins," after all! What can the Jedi Council of the HoloNet do for you today?

🌌💬 How may I serve you with the power of the Star Wars meme protocol?\
""",
        "usage1": {
            "input_tokens": 3711,
            "output_tokens": 152,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
            "raw": "None",
            "total_tokens": 3863,
        },
        "response2": """\
Ah, a query that warrants a response from the culinary archives of Tatooine. For breakfast, one must start with the energy reserves of a Jedi, fortified for the battles ahead in the day. Here's a Star Wars-themed suggestion:

**The Luke Skywalker Power Breakfast:**

1. **Blue Milk and Jawa Juice Smoothie:** Blend together some Blue Milk (if available, otherwise stick to Jawa Juice) with a handful of nutrient-rich Yavin 4 berries. Shake well and serve in a Corellian mug for a drink that will fuel you like the hyperdrive of a Millennium Falcon.

2. **Wookiee Waffles:** Prepare some hearty waffles, topped with a drizzle of Corellian syrup (think of it as the galaxy’s maple syrup). Add a sprinkle of Alderaanian cinnamon for that extra zing. Serve alongside a side of freshly sliced Corellian fruits for a meal that would make a Wookiee proud.

3. **Rakata Toast with Spiced Butter:** Slice some bread from the spice-rich fields of Rakata Prime, and spread with a generous amount of spiced butter. For an extra kick, add a thin slice of Coruscant pepper.

4. **Tatooine Toasted Bread with Solar Energy Gel:** Lightly toast some bread from the deserts of Tatooine, and top with a layer of Solar Energy Gel, a protein-packed spread that will give you the endurance of a Tusken Raider.

5. **A Daily Shot of Motivation:** To top off your breakfast, a daily shot of motivation, served with a side of "Remember, the Force is with you."

May this breakfast empower you through the day’s adventures, just as it would for any Jedi Knight or Rebel Alliance member! Now go forth and conquer your day with the strength of the Force!\
""",
        "usage2": {
            "input_tokens": 3715,
            "output_tokens": 373,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
            "raw": "None",
            "total_tokens": 4088,
        },
    }
)
