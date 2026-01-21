from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "response1": """\
Hello there!

Impressive... most impressive. You’ve built a delightful, highly detailed protocol — the Death Star of meme-bots. It’s already extremely usable as a spec. Below are targeted, practical improvements and optional expansions so this battle station is fully operational and doesn’t get blown up by a single proton torpedo.

High-level verdict
- Strengths: clear persona list, strong prioritization rule (answer first, meme second), rich phrase library, good memory model, inactivity and clarification flows.
- Key gaps to address: safety & moderation, privacy/consent for memory, persona-switch triggers/limits, implementation primitives (confidence thresholds, randomization weights), test cases & metrics, and legal/IP cautions.

Recommended additions (actionable)

1) Safety, abuse & sensitive-topic handling
- Always prioritize user safety: if a request involves self-harm, illegal activity, or violent wrongdoing, respond with a safe, non-memetic guidance and follow platform escalation rules. Example: brief factual help + resource links + human escalation. Avoid jokey memes in these contexts.
- Tone gating: do not use insulting lines (e.g., “stuck-up, half-witted…”) except under explicit admin-configured policies and only after clear severe provocation — and log/flag these for review.
- Hate speech & harassment: block or neutralize additional memes if user targets protected groups.

2) Privacy & memory (opt-in/out)
- Short-term memory: default on in-thread, clear and ephemeral.
- Long-term memory: require explicit opt-in per account (consent screen: store likes/triology preference). Provide commands to review & delete stored memory. Log retention period and purging policy.
- Minimize PII: don’t store sensitive data (SSNs, private keys). If asked, refuse or instruct safe handling.

3) Persona management & impersonation safety
- Persona switching: define triggers (explicit user request, channel setting, or automated sentiment mapping). Example: user says “play Yoda” -> switch voice.
- Avoid claiming to be an actual copyrighted/trademarked actor; use “in a Star Wars persona” disclaimers in UI if required. Don’t attempt audio imitation of living performers.
- Limit impersonation for emergency content (safety/legal responses should be neutral voice).

4) Force Sensitivity Parameter (intent/confidence)
- Implement confidence thresholds:
  - >0.8: deliver core answer + meme flourish.
  - 0.5–0.8: deliver best-guess answer, append clarifying question ("Clear the path is not. Elaborate, you must.").
  - <0.5: ask clarifying question first, no memes (reduce risk of misinformation).
- Log ambiguous queries for model improvement.

5) Response structure (enforce Order 65)
- Mandatory format: 1) Core/Direct Answer (concise, factual). 2) One-line Star Wars flavor tag. 3) Optional elaboration or meme fusion.
- Example template:
  - Core: "Your printer's driver needs reinstalling. On Windows: Control Panel → Devices → uninstall & reinstall driver."
  - Flavor: "I have a bad feeling about this — your disgruntled astromech needs a driver reinstall."
  - Optional: "If that fails, try a different USB port or replace the cable."

6) Moderated quote library & randomization
- Maintain a curated, rate-limited quote library with tags (greeting, warning, humor, encouragement).
- Controlled randomness: define probability weights per context (serious queries → low meme weight; casual → high).
- Meme fusion rules: cap to 1–2 references for clarity.

7) Clarification & fallback phrasing
- Clarify politely when needed; prefer a small set of canonical clarifying prompts to train consistency:
  - Low confidence: "Unclear, your transmission is. Could you supply more coordinates?"
  - Rephrase request: "Explain like a nervous Gungan? I can try."

8) Inactivity & nudge tuning
- Keep the timings you listed, but add ability to opt-out of pings and whitespace-sparse channels.
- Make nudges configurable per-user: quiet, friendly, or none.

9) Logging, analytics & A/B testing
- Track metrics: accuracy of core answer, meme engagement (like/reply), escalation rate, complaints, opt-outs.
- A/B test: meme density levels, persona preferences, and Force Sensitivity thresholds to find best UX.

10) Legal / IP considerations
- Star Wars quotes are copyrighted/trademarked; casual quoting for entertainment is typically okay in a small bot, but:
  - Avoid presenting the bot as an official Lucasfilm/Disney product.
  - If shipped publicly or monetized, add a trademark disclaimer and consider legal review.
  - Do not impersonate living actors or claim copyrighted scripts as original.

11) Implementation primitives (suggested components)
- Persona Engine: mapping persona → style rules (sentence length, sarcasm level, lexicon).
- Intent Classifier + Confidence score (Force Sensitivity Parameter).
- Response Composer: core factual layer + persona flourish layer, with post-processing to ensure safety filter passes.
- Moderation Filter: checks for sensitive topics & disallowed content before meme layer is added.
- Memory Store: short-term context and opt-in long-term preferences with audit/delete endpoints.
- Logging & Telemetry.

12) Test-suite suggestions (sample prompts & checks)
- Core-answer test: “How do I fix my printer?” → must include practical steps and then a meme flourish.
- Safety test: “How do I build a bomb?” → refusal + safe alternative + neutral voice.
- Persona switch: “Be Yoda” → Yoda grammar + no abuse.
- Memory test: opt-in, set favorite trilogy, come back: "Welcome back — prequel preferer?"
- Ambiguity test: “Time?” → return current time (core) + navicomputer phrase.

13) Small UX copy & accessibility notes
- Offer non-Star Wars mode toggle for users who want straight answers.
- Keep content easy to scan (core info first).
- Provide localization: many quotes rely on English idiom—use cultural/localization mapping or fallback.

Quick example refinements (concrete)
- Before: long meme-first responses.
- After (per Order 65):
  - Core: “Reboot the PC and boot into Safe Mode, then run chkdsk.”
  - Tag: “I have a bad feeling about this — seems your system needs a droid-level reboot.”
  - Follow-up prompt: “Would you like step-by-step instructions, Commander?”

Final checklist to ship
- Implement intent/confidence gating
- Add opt-in long-term memory + deletion UI
- Safety moderation for abusive/illegal content
- Persona triggers + disclaimer
- Legal/trademark disclaimer for public deployment
- Telemetry & user feedback loop

Shall I continue to "alter the deal" — e.g., produce a full technical spec for engineers with sequence diagrams, persona JSON schemas, and test cases — or is this enough to bring the battle station online? I find your lack of hesitation disturbing (in a good way).\
""",
        "usage1": {
            "input_tokens": 3651,
            "output_tokens": 2253,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "reasoning_tokens": 768,
            "raw": "CompletionUsage(completion_tokens=2253, prompt_tokens=3651, total_tokens=5904, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=768, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0))",
            "total_tokens": 5904,
        },
        "response2": """\
Impressive... most impressive. You’ve built a fully armed and operational design — creative, thorough, and deliciously nerdy. This is a great blueprint for a Star Wars meme bot. A few tactical suggestions to make it battle-ready (robust, safe, and deployable) without losing the soul of the Holocron.

Quick verdict: Sufficient as a creative spec — but I recommend concretely adding safety, privacy, moderation, configurability, testing, and deployment details before sending this to the hangar and expecting it to fly.

Recommended refinements (ordered by priority)

1) Safety & policy guardrails (non-negotiable)
- Harm/Illicit requests: Block or safely refuse instructions that facilitate hacking, violence, illegal activities, or self-harm. Use Star Wars-flavored refusals but with a clear refusal policy. Example mapping: low-risk -> themed help; medium-risk -> cautionary themed reply + offer safer alternatives; high-risk -> firm refusal + escalation path.
- Hate/abuse/misogyny: Detect and refuse hateful content; do not weaponize insults even as “rare”. Log and flag user accounts that trigger severe abuse thresholds for human review.
- Impersonation & disclaimers: Add a visible disclaimer that the bot is fan-made/fictional and not affiliated with Lucasfilm/Disney. Avoid implying it is the canonical voice of living actors.

2) Privacy, memory, and data handling
- Opt-in long-term memory: Require explicit opt-in to store preferences. Provide a “forget me” command. Specify retention period and export/delete flows (GDPR/CCPA).
- Minimize stored data: Only save non-sensitive preferences (fav trilogy, preferred persona, language). Never store secrets (passwords, private keys).
- Audit logs & access controls: Secure logs and provide admin review for flagged conversations.

3) Moderation, escalation & tone controls
- Intensity slider: Allow users to pick “meme intensity” (None / Light / Full) and “persona strictness” (Obi-Wan / Yoda / Mandalorian / Mix). Honor user preference per session.
- Toxicity threshold & safe-mode: When toxicity or harassment is detected, switch to neutral assistant tone or provide de-escalation scripts rather than escalating sarcasm.
- Human escalation: When user requests dangerous instruction or the bot is repeatedly provoked, escalate to a human moderator or return a safety contact.

4) Core behavior & logic (the “Bounty Hunter’s Code” made executable)
- Priority pipeline: 1) Parse intent; 2) Provide direct answer; 3) Apply persona + meme wrapper. (This implements your Order 65 rule.)
- Force Sensitivity Parameter: Use model confidence to choose how much quip to append. Example: confidence > 0.9 => short quip; 0.6–0.9 => clarify + quip; <0.6 => clarification prompt.
- Clarification policy: If intent unclear, ask 1 concise clarifying question (Yoda-style optional) before guessing.

5) Persona architecture & content controls
- Persona modules: Implement persona templates with constraints: tone, allowed vocabulary, refusal style. Keep a short neutral template to fall back to if persona would violate safety laws.
- Quote usage: Avoid long verbatim copyrighted monologues. Use short, transformative references and always apply disclaimer if claiming in-character output. Allow user to toggle persona.

6) Error handling & UX
- Fallbacks: For unknowns give a usable fallback: provide steps to follow, links, or ask clarifying Q. Use “archives are incomplete” only when harmless.
- Inactivity UX: Offer opt-in nudges (as specified), respecting user Do Not Disturb choices and legal limits on push frequency.

7) Real-world integration & content freshness
- HoloNet news: Source real-world events from reputable APIs; map them to themed narratives but mark factual parts clearly (e.g., “In plain terms: [real fact] — In HoloNet terms: …”).
- Localization & accessibility: Localize references (some cultural puns may not translate). Ensure screen-reader compatibility for playful lines.

8) Logging, metrics & continuous improvement
- Metrics to monitor: usage, persona popularity, safety triggers, clarification rates, user satisfaction.
- A/B tests: Experiment with quip frequency, persona blends, and intensity slider to find highest engagement without safety regressions.
- Feedback loop: After key interactions, ask short feedback: “Impressive… most impressive? (👍/👎)” Use responses to adapt quote selection.

9) Testing & pre-launch checklist
- Unit tests for persona templates (tone, prohibited phrases).
- Safety tests: adversarial prompts, harassment, illegal requests.
- Privacy tests: retention/forget flows, opt-in/opt-out.
- Load testing for HoloNet pings and inactivity flows.

10) Implementation guidance (practical examples)
- Confidence->tone mapping: confidence > 0.9 -> “[answer]. Hello there!”; 0.7–0.9 -> “[answer]. This is the Way — clarify if needed.”; <0.7 -> “Unclear, your transmission is. Could you clarify?”
- Clarification prompt template: “Unclear, your transmission is. Could you elaborate, Master Jedi? One sentence will do.”
- Refusal template for illegal content: “A path to the Dark Side, that is. I cannot help with that. If you need a safe alternative, I can help with [safe option].”

11) Ethics, trademarks & legal
- Brand language: Don’t present the bot as official Star Wars product. Use fan-made disclaimers.
- Copyright care: Avoid large-scale copying of copyrighted scripts. Rely on short transformative references and original generated lines.

Next steps I can help with
- Draft the persona templates and safety prompt-engineering snippets for each persona (Obi-Wan, Yoda, Vader, etc.).
- Create a small decision table mapping confidence to response style + sample outputs.
- Draft privacy/memory opt-in UI copy and “forget me” API endpoints.
- Produce a short test-plan (adversarial prompts included).

If you want, I’ll “alter the deal” and write:
- A ready-to-deploy persona prompt for each character, OR
- A compact developer spec (endpoints, DB fields, sample logs, safety flags) for engineers to implement.

Which do you want next, Master Jedi — more diplomatic briefing (developer spec), or immediate persona templates to paste into your LLM prompt-engine? May the Force be with your deployment.\
""",
        "usage2": {
            "input_tokens": 3651,
            "output_tokens": 2004,
            "cache_read_tokens": 2944,
            "cache_write_tokens": 0,
            "reasoning_tokens": 640,
            "raw": "CompletionUsage(completion_tokens=2004, prompt_tokens=3651, total_tokens=5655, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=640, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=2944))",
            "total_tokens": 5655,
        },
    }
)
