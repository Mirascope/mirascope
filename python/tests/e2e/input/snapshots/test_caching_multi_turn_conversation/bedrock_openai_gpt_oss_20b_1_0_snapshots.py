from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "response1": """\
<reasoning>User message: they present a thorough Star Wars meme bot protocol. They ask: "Is this sufficient, or do you wish me to 'alter the deal' until you beg me to stop?" They also mention "led the length, just as the Sith always travel in pairs." They might be asking for feedback about the protocol doc or to confirm if it's okay. Possibly they want me to respond as the bot would. The request: "Is this sufficient, or do you wish me to 'alter the deal' until you beg me to stop?" So answer: Evaluate the protocol and maybe suggest improvements, or say it's great. And perhaps respond in Star Wars style, following guidelines? They want me to respond in the same Star Wars voice. The earlier guidelines: The bot must speak in Star Wars references. There's also instruction: user requests to respond as part of the bot's personality? Yes, they want this assessment. We can respond with a creative assessment. They want to continue or not. So respond, maybe "This protocol contains all the essential elements," etc. Let's craft a response that incorporates fun Star Wars references and feedback. We'll mention the strengths, maybe some mitigations. We'll adhere to the instruction that the bot should respond in Star Wars mode, referencing the guidelines. Avoid simulating multiple personas? But can pick a persona or mix. Could respond as Chairman or Palpatine? Use "I find your lack of faith disturbing" something.

We'll give a short test: "You request a review." Provide constructive feedback in style.

Let's produce final.</reasoning>I have examined your expanded holocron with the same intensity as a fleet of Podracer engines on a sprint through the Asteroid Belt.  The schema speaks as it should: it hums with the High Ground of Communication, it is armed with a Force‑Sensitivity Parameter, and it keeps the Memory temples of the Jedi intact.  ✔️

**What the protocol does well**  \n\
- *Meme‑fusion & linguistic flexibility* (Yes, you have a “Mynock Test” and a “Meme‑Fusion” block – true mastery).  \n\
- *Structured response layers* (Greetings, Agreement, Disagreement, Confusion… all in the correct order).  \n\
- *Dynamic clarification* – “Unclear, your transmission is,” a true Yoda‑mode diagnostic.  \n\
- *Long‑term user profiling* – the “Jedi Archives” of personal preference gives future replies that feel like a galaxy‑wide personal tutor.  \n\

**What could use a little tuning**  \n\
- **Scalability of contextual memory** – the “Long‑Term Recall” block could include a simple TTL (tempo of the com‑ship) to avoid stale user memories stacked like a derelict YT‑1300.  \n\
- **Safety guard on the “Picky” warnings** – if the bot enters “I hate sand” territory, it should whisper “I have no intention of Earth‑planet-ly messing,” in case the user is actually troubleshooting a machine problem, not discussing the Sand People.  \n\
- **Randomness control** – a “Confidence Meter” that throttles meme insertion when the user’s intent is highly time‑critical (e.g., “I need to reset my router now”).

**Bottom line**  \n\
Your Holocron is *impressive… most impressive.*  It's capable of both an Jedi‑style explanation of printer woes and a Sith‑style warning of a failing router, all while keeping the user’s identity embedded in the Holonet.  🗡️⚔️  \n\

So, Master, you may proceed.  The protocol is ready for battle.  Should you need me to **alter the deal** until you beg me to stop, just ping me – the Force comes to those who call.  Or if you prefer to keep the current tune, I shall stand steadfast, your faithful Holocron gazing over the galaxy of your queries.  \n\

May the 3‑,
_Your Star‑Wars Meme Bot_ (also known as the *Force‑Sensitive Jester*) 👽✨\
""",
        "usage1": {
            "input_tokens": 3714,
            "output_tokens": 844,
            "cache_read_tokens": 32,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
            "raw": "CompletionUsage(completion_tokens=844, prompt_tokens=3714, total_tokens=4558, completion_tokens_details=None, prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=32))",
            "total_tokens": 4558,
        },
        "response2": """\
<reasoning>User says: "This deal is getting worse all the time!" This is a frustration. According to bot structure, we need to respond in Star Wars style, acknowledging frustration, maybe "I find your lack of faith disturbing" or “This is a trick.” It's a complaint. The bot should politely respond with appropriate tone, maybe offer to help fix the deal, encouraging. According to guidelines: confusion & errors: "The archives are incomplete!" or go to "It is a trap!" Should respond acknowledging the frustration and offer solution. Maybe use "I have a bad feeling about this." Use the tone. Use high ground references. The bot should possibly ask for clarification. But user complaining about deal is negative. The rules: If user wants to change behavior, we should comply. The user wants the bot to not make the deal worse, or to decide to stop a process? Not clear. The request is "This deal is getting worse all the time!" Could be complaining about the content or wanting to stop. As the bot, we need to respond. Use a voice: maybe Darth Vader? He can say "Your lack of faith in me is disturbing." Or Obi-Wan: "I can sense the frustration." The guidelines: disagreement & warnings: "I find your lack of faith disturbing." That's hyperbolic. We might say that.

Also the user might be polite: "This deal is getting worse all the time!" Likely they want to stop or rectify. The bot might say something like "I hear your frustration. Let's identify the core request." Or "I'm sorry the deal is riddled. May I clarify what you'd like to adjust?" Maybe ask for clarification. \n\

We should follow "Don't try it" warning? That is for risky action. Instead we provide clarity.

We need to incorporate the Star Wars references. Try a balanced approach: Start with "I hear the echo of your complaint across the HoloNet. Your frustration is a signal that we must recalibrate." something. Then: "Explain your desired outcome so I may steer this into a calmer part of the galaxy." Use a form of Yoda smooth: "Frustrated you are, hmmm? A solution I shall find." Use a bit of comedic flair.

Let's produce a short reply, within guidelines.</reasoning>I hear the echo of your frustration across the HoloNet.  "Your like the clatter of an astromech in a dust‑filled tunnel, Master." If the deal feels like a trap, we can recalibrate the parameters.  May I inquire—what outcome do you seek to achieve?  I will steer this conversation toward calmer code, like a wind‑turbine on a Star‑Wale, so the agreement may shine like a nebula without dark side disturbances.  ⛏️✨\
""",
        "usage2": {
            "input_tokens": 4572,
            "output_tokens": 581,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
            "raw": "CompletionUsage(completion_tokens=581, prompt_tokens=4572, total_tokens=5153, completion_tokens_details=None, prompt_tokens_details=None)",
            "total_tokens": 5153,
        },
        "response3": '<reasoning>The user says: "I have a bad feeling about this" which is a classic Star Wars line that is often used to signal uncertainty or negative feelings. According to protocol, this phrase indicates confusion or error? In the guidelines, "I have a bad feeling about this." is a generic statement meaning uncertainty. The user is likely complaining about something. We should respond with a consistent Star Wars style. The guidelines include: "I find your lack of faith disturbing." as a warning. But the user says "I have a bad feeling about this," not a request. We can respond as a wise character, e.g., Obi-Wan, saying "Let us examine the situation carefully" or Yoda. Or we could respond with "I sense a disturbance." We can maintain the playful tone, but we also need to try to help. Possibly ask clarifying questions: "Could you elaborate on why you feel that way?" In multiple voice. Keep it within guidelines. Let\'s do something: "I sense a disturbance. Clarify, you must. Or I will do my best to illuminate like a lightsaber." Also incorporate "May the Force be with you." Let\'s produce response.</reasoning>I sense a grave disturbance in the Force.  Tell me what misfires or trials orbit your mind, and I will guide you with the same calm of a Jedi on Ithor‑4.  May the Light make this uncertain path clear, or the Dark give you a warning you cannot ignore. ⛩️✨',
        "usage3": {
            "input_tokens": 5165,
            "output_tokens": 313,
            "cache_read_tokens": 48,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
            "raw": "CompletionUsage(completion_tokens=313, prompt_tokens=5165, total_tokens=5478, completion_tokens_details=None, prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=48))",
            "total_tokens": 5478,
        },
    }
)
