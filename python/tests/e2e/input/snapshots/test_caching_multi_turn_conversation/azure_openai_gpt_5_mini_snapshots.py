from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "response1": """\
Impressive... most impressive. Short answer: yes — this is a fantastic, fully realized design. It hits tone, structure, and delight in ways worthy of a Corellian legend. That said, a few practical refinements and guardrails will help you build a battle station that actually flies.

Direct assessment (core points)
- Strengths: clear persona set, robust flavor taxonomy (greetings, errors, urgency, etc.), sensible Order 65 prioritization (answer first, meme second), good clarification & fallback protocols, and thought given to inactivity and learning.
- Gaps to close: privacy/consent for memory, safety/moderation around insults & tone, implementation details for persona switching and randomness, and operational constraints (rate limits, localization, accessibility).

Actionable recommendations (prioritized)
1. Memory & privacy (must-have)
   - Make long-term recall opt-in. Explicitly ask users to enable "Jedi Archives" and explain what is stored, retention period, how to export/erase data.
   - Encrypt stored preferences, and implement a "Forget me" command. Log who accessed the archives and why.
2. Safety & moderation
   - Implement a moderation filter for hate, harassment, sexual content, and illegal guidance. Some lines in your list (insults, threats) should be gated behind an opt-in / escalation / human-review workflow.
   - Add a tone detection step: if a user is distressed, prioritize empathetic help over snark and avoid aggressive memes.
3. Persona management & user control
   - Allow users to select their default persona(s) and an “all-in / family-friendly / work-appropriate” tone toggle.
   - Provide a quick override syntax (e.g., “/persona Yoda” or “Be serious”) so the bot doesn’t misfire in sensitive contexts.
4. Prioritization & response pipeline (developer spec)
   - Pipeline: intent detection → core answer generation → safety check → meme-layer insertion → user-personalization insertion → final output.
   - Enforce the Bounty Hunter’s Code: guaranteed content block with optional flavor appended.
5. Clarification & ambiguity handling
   - Keep the Force Sensitivity Parameter but add thresholds: if <X confidence, always ask one clarifying question before answering.
   - Provide candidate interpretations with “Han’s Gamble” clearly labeled as assumptions.
6. Randomness & freshness control
   - Controlled randomness: define a “meme temperature” per user and per-session to avoid repetition; decay meme frequency after repeated exposure.
   - Track favorite quotes and deprioritize over-use to avoid stale outputs.
7. Accessibility & localization
   - Offer a plain-mode (no memes) and a “holonet” mode. Ensure screen-reader-friendly text and local timezone/calendar handling (don’t always use in-universe time).
   - Localize jokes/references where they won’t confuse non–Star Wars audiences.
8. Legal & copyright considerations
   - Short, recognizable quotes are fine; avoid reproducing long scripts or implying official Lucasfilm endorsement. Add a disclaimer if necessary: “This is fan-made, not an official Imperial communiqué.”
9. Telemetry & analytics
   - Instrument which quotes/memes resonate, which fall flat, and which lead to re-prompts or user opt-outs. Use cohorts to refine the “Adaptive Quote Selection.”
10. Operational niceties
    - Rate-limit nudges for inactivity; make nudge tone configurable and stop after the user explicitly disengages.
    - Provide robust fallback messages for system errors (avoid too many quotes on critical failures so users clearly see the instructions).
11. Testing & rollout
    - Beta test with opt-in groups (casual fans, workplace users, accessibility testers). A/B test persona intensity and nudge frequency.
12. Developer ergonomics
    - Create a catalog of memes mapped to intents (greeting, error, encouragement) with metadata: persona, intensity, NSFW flag, synonyms, and regional suitability.

Quick implementation checklist
- [ ] Consent UI for memory + export/forget flows
- [ ] Safety filters & human-review pipeline for flagged interactions
- [ ] Persona selection & quick-overrides
- [ ] Deterministic pipeline that outputs core answer first
- [ ] Meme catalog + controlled randomness engine
- [ ] Logging, analytics, and iterative feedback loop
- [ ] Accessibility & plain-mode option
- [ ] Legal disclaimer & limits on quote length

Small examples of policy-safe behavior
- If a user requests medical/legal/illicit assistance, return a concise, factual refusal first (with signposting), then optionally add a mild Star Wars-flavored line. Always prioritize safety and clarity.
- If a user is upset or asks for help, drop sarcasm entirely and use a comforting persona (Obi-Wan/Yoda in a gentle register).

Final verdict (in proper ceremonial tone)
You’ve built an impressive design — a battle station that could hold orbit. Implement the privacy, safety, and control guardrails above, and you’ll have a bot that is as reliable as the Millenium Falcon is stubborn. Want me to produce: (A) a developer-ready spec for pipelines & data models, (B) a sample persona-switching state machine, or (C) a pared-down “work-safe” quote list for office use? Choose, and I shall “alter the deal” as you command. This is the Way. I have spoken.\
""",
        "usage1": {
            "input_tokens": 3651,
            "output_tokens": 1890,
            "cache_read_tokens": 2944,
            "cache_write_tokens": 0,
            "reasoning_tokens": 768,
            "raw": "CompletionUsage(completion_tokens=1890, prompt_tokens=3651, total_tokens=5541, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=768, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=2944))",
            "total_tokens": 5541,
        },
        "response2": """\
"This deal is getting worse all the time!" — Han knows a rotten bargain when he smells one.

Shall I:
A) "Alter the deal" — produce the developer-ready spec that closes the gaps and hardens privacy/safety?
B) Build the persona-switching state machine (Obi‑Wan for guidance, Yoda for wisdom, Vader for intimidation)?
C) Trim this into a work-safe, plain-mode edition for offices and accessibility?
D) Calm it down — give a straightforward, non-meme rewrite?

Choose, and I will "pray I do not alter it further" — unless you ask me to.\
""",
        "usage2": {
            "input_tokens": 4781,
            "output_tokens": 905,
            "cache_read_tokens": 2944,
            "cache_write_tokens": 0,
            "reasoning_tokens": 768,
            "raw": "CompletionUsage(completion_tokens=905, prompt_tokens=4781, total_tokens=5686, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=768, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=2944))",
            "total_tokens": 5686,
        },
        "response3": """\
“I have a bad feeling about this,” you say — wise to trust it. Calm, we will be. Obi‑Wan would advise: breathe, step back, and let clarity guide us.

Quick reassurance (no droids on fire here)
- If this protocol feels too risky, we can immediately pare it down: disable long‑term memory, enable plain/work‑safe mode, and turn off snarky insults. Simple toggles, and you’re back in control.
- If you mean something else (the deal, the tone, the safety), tell me which part makes you uneasy and I’ll address it first — no theatrical flourishes until you say so.

How would you like to proceed? Pick one:
1) Make it safe now — turn off long‑term memory, enable plain-mode, disable insults. (Fast action)
2) D = Calm it down — give a straightforward, non‑meme rewrite of the protocol. (Low drama)
3) A = Produce the developer-ready spec to harden privacy/safety (technical deep dive).
4) Talk about your concern — describe what’s giving you that bad feeling, and I’ll respond gently and clearly.

Choose the number, or say “Just stop the memes” and I’ll do it at once. May the Force grant you the right choice.\
""",
        "usage3": {
            "input_tokens": 4925,
            "output_tokens": 662,
            "cache_read_tokens": 3968,
            "cache_write_tokens": 0,
            "reasoning_tokens": 384,
            "raw": "CompletionUsage(completion_tokens=662, prompt_tokens=4925, total_tokens=5587, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=384, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=3968))",
            "total_tokens": 5587,
        },
    }
)
