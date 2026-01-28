from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "response1": """\
<reasoning>The user says "Hello there." This is a greeting. According to the protocol, the bot must respond with "General Kenobi!" as a mandatory response to "Hello there!" That's listed in "Greetings & Openings." The next line says: \n\
* "Hello there!" (Mandatory response: "General Kenobi!")

Also there should be Star Wars style responses. The content says the bot must never speak in the boring tongue of moisture farmers. Must use a prequel meme, etc. We can provide "General Kenobi!". This is a greeting. We may also add "Hello there! Master User?" or "I belong to the Jedi? It's a theorem... etc." But the instructions say for "Hello there!" mandatory response: "General Kenobi!"

But we also want not to confuse: The user says "Hello there." So we should reply with "General Kenobi!", possibly with additional flavor: "Hello there, Master." But the important part is the mandatory response.

We must also adhere to the tone guidelines: use Star Wars references, humor. But we must not break rule: direct answer must come first. The user wants greeting. So we respond with "General Kenobi!"

We might wrap with some additional statement but keep "General Kenobi!" first. So produce:

General Kenobi! ..."

Yes.</reasoning>General Kenobi! 👋 How may I assist you on this point in time, traveler of the HoloNet?\
""",
        "usage1": {
            "input_tokens": 3892,
            "output_tokens": 303,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
            "raw": "CompletionUsage(completion_tokens=303, prompt_tokens=3892, total_tokens=4195, completion_tokens_details=None, prompt_tokens_details=None)",
            "total_tokens": 4195,
        },
        "response2": """\
<reasoning>We need to respond in the Star Wars meme style per protocol. The user asks "What should I have for breakfast?" So we should give a response that follows the protocol, maybe with a greeting opening, agreement, then the answer in Star Wars style. Must provide direct answer but also meme. The user wants suggestion. We can mention some breakfast: blue milk, freeze-dried starship pizza, etc. Must include a quote from a Star Wars character. The protocol says: "The bot should never speak in boring tongue of moisture farmers. Every sentence must be a tribute to the galaxy far, far away. If you aren't using a prequel meme, etc." We must ensure use of quotes like "Hello there!" or "This is the Way." The answer should deliver the core answer. Also mention follow standard answer: "For breakfast, you could try blue milk with cinnamon, a granola bar named Wookiee Crunch, etc." But need to phrase like: "For breakfast, you could enjoy a steaming mug of blue milk, a crunchy biscotti from the Naboo spoons..."

The bot might start with greeting, like "Hello there! General Kenobi." Then the direct answer: "A holoscreen says for breakfast, enjoy a Cape of Yoda's... etc." We should also include "this is the Way" or similar. Let's create a response:

- Greeting + Acknowledgement: "Hello there! General Kenobi. This is the Way."

- Then give a suggestion: "For your breakfast, I recommend a steaming cup of blue milk, perhaps paired with a sunrise over Tatooine... Wait, emphasize a breakfast like 'a hearty batch of Rancor-ly farmer's eggs'?

A better: "Start your day like a Jedi: warm, nourishing, strong. Grab a bowl of blue milk or a roast of Endor's dwarfs? Hmm.

Let's think: The bot should include a direct answer but with Star Wars flavor. Provide suggestions: "Blue milk, a Corellian crepe, a hot bowl of Chewbacca's yum". We might mention "Tusken raider's dried fruit & spice energy bar" as a crunchy breakfast.

We also include "I find your lack of faith disturbing" if user complains? Not needed.

We may also include the "Disagreement & Warnings" or "Agreement & affirmations" lines.

We need to use some structure guidelines: Possibly "Greetings & Openings". The bot should first greet: "Hello there!" maybe. They close with "I find your lack of faith disturbing" if needed. But we can deliver.

Let's craft:

**Response Outline:**

1. Greeting: "Hello there! General Kenobi."
2. Acceptance: "This is the Way." maybe that's after the greeting but before answer.

3. Provide answer: mention breakfast options: Blue Milk Buttermilk and Light-Centa-Grid Granola, a Corellian snack pizza, or a steaming bowl of turbolaser grain porridge. Each with a star wars reference.

We should embed a meme or quote: "I find your lack of faith disturbing" is only used when user is insulting, so not applicable. But we could incorporate "Great shot, kid" if recommended eggs, "Punch it, Chewie" to eggs.

Better to embed "It's a trap" etc. Not needed.

We also can produce a closing line.

The text can't be too long but thorough.

Let's produce:</reasoning>Hello there! General Kenobi.  \n\
This is the Way.

For your breakfast, channel the energy of a Jedi and the comfort of a home‑star:

| Dish | Star‑Wars Flavor | Why It Works |
|------|-----------------|--------------|
| **Blue‑milk cereal** – a puffed grain bowl swirled with Tatooine‑blue milk | “May the flavor be with you, young Padawan.” | Rich in calcium and vitamins, it will give you the stamina to outpace a Republic fleet. |
| **Corellian Missile Pizzazz** – a thin‑crust pizza topped with spicy kyber‑crusted pepperoni | “Applause, kid, that was a one‑in‑a‑million shot!” | The heat of the kyber crystal spice keeps your senses alert for the day’s negotiations. |
| **Wookiee‑Crunch Granola** – chewy oats with dried planet‑fruit, caramelised Spice‑root | “You have the strength to fight fighting for your own career.” | High‑fiber, low‑sugar – power your body like a well‑reinforced Mandalorian armor. |
| **Sith‑Iron Omelette** – dark‑sided eggs, pepper, and a touch of black‑pepper | “The Force is strong with this one.” | Protein‑packed, jet‑black to remind you that even the darkest side can fuel victory. |

Pick a combination that fits your mission profile: a light, low‑calorie “blue‑milk granola” if you’re in a stealth patrol, or the more robust “Corellian Missile Pizzazz” if you’ll be on the front lines of a day‑long negotiation.  \n\

Go forth, claim your breakfast, and **may the Force be with your taste buds**!\
""",
        "usage2": {
            "input_tokens": 3896,
            "output_tokens": 1091,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
            "raw": "CompletionUsage(completion_tokens=1091, prompt_tokens=3896, total_tokens=4987, completion_tokens_details=None, prompt_tokens_details=None)",
            "total_tokens": 4987,
        },
    }
)
