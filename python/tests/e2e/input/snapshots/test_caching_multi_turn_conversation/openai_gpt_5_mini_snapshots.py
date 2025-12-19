from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "response1": """\
Hello there! — General Kenobi!

Impressive… most impressive. Your Protocol 2.0 is vivid, comprehensive, and ready for deployment to the Outer Rim — but a few critical upgrades and clarifications will turn this from a flashy Death Star into a reliable, user-safe battle station. Below I give a prioritized checklist (Order 65: functionality first, flair second), concise action items, and a suggested next step. This is the Way.

Core verdict (short): Yes — conceptually excellent and very thorough. Add focused safeguards, privacy controls, configurability, and monitoring before full roll-out.

High-priority additions (must-have)
1) Safety & moderation protocols
   - Build explicit rules for abusive/hateful speech, harassment, illegal activity, and self-harm crises. \n\
   - In crisis inputs (suicide, self-harm, threats), switch to a non-meme safety flow that gives immediate, humane help resources and escalation paths. (No joking modes.)
   - Flag and rate-limit users that trigger repeated severe violations; keep moderation logs.

2) Privacy, consent, and memory controls
   - Make long-term memory opt-in and easy to manage. Provide explicit consent wording and a “forget me” action.
   - Define retention windows, encryption-at-rest, access controls, and compliance with GDPR/CCPA.
   - Provide users a simple UI to list and delete remembered preferences.

3) Legal/medical/financial content handling
   - Force a “safe-completion” mode for legal/medical/financial queries: deliver high-level, non-actionable guidance + referral to qualified professionals.
   - Add templates that clearly disclaim the bot is not a licensed professional.

4) Crisis & escalation handling
   - Create fast-paths to human help when needed (support tickets, human moderator review) and ensure they bypass meme-mode immediately.

Medium-priority improvements
5) Persona configurability & intensity control
   - Let users choose persona(s) and a “flavor intensity” slider (0 = plain language, 5 = max-meme). Default to a friendly mid-level with plain fallback on critical queries.
   - Allow persona mixing (Mandalorian + Obi-Wan) and a “safe-mode” that suppresses insults or aggressive quotes.

6) Rate of quoting and copyright caution
   - Avoid overusing long copyrighted passages; use brief, original paraphrases. Log frequently used quotes and rotate to prevent fatigue.

7) Clarification & disambiguation flows
   - Implement the Force Sensitivity Parameter as structured confidence scoring. If confidence < threshold, ask a clear, short clarifying question in-character but always include a plain-language option like “Or say ‘plain’ to answer without memes.”

8) Auditability, logging, and monitoring
   - Log anonymized interactions for quality, safety, and bias testing. Monitor for meme misuse, user dissatisfaction spikes, and safety incidents.
   - Build telemetry: meme-engagement rate, help escalations, opt-out rates, and CSAT.

Lower-priority (but recommended)
9) Internationalization & accessibility
   - Provide multi-lingual meme libraries and accessible outputs (screen-reader friendly, plain-mode transcripts).
   - Ensure cultural sensitivity filters for region-specific references.

10) Randomness control & reproducibility
   - Controlled randomness parameters so responses are fresh but reproducible for debugging (seeded RNG in dev).

11) HoloNet News & real-world integration
   - For real-time news, tag data sources and provide provenance. If pulling live feeds, ensure rate limits, caching, and safe summarization rules.

12) Testing & rollout plan
   - Prepare unit tests, safety tests (adversarial inputs), and closed beta with opt-in users.
   - A/B test persona intensity and measure user satisfaction and retention.

Quick implementation checklist (practical)
- Create a Persona Config JSON (allowed_personas, intensity, profanity_level, enable_memories)
- Implement Memory Consent UX + backend tables with retention metadata
- Safety: integrate moderation model + human escalation queue
- Add plain-mode keyword ("plain", "no-meme", or "serious") that always returns a non-memed response
- Monitoring: dashboards for incidents, CSAT, and persona usage

Example short config (conceptually)
- persona: "Obi-Wan"
- intensity: 3
- meme_allowed_categories: [greetings, encouragement, troubleshooting]
- meme_blocked_categories: [crisis, medical, legal]
- memory: {enabled: true, opt_in_time: timestamp, retention_days: 365}

Edge cases & sanity rules
- Never use sarcasm in medical or crisis contexts.
- For potentially illegal requests (e.g., how to build weapons), refuse and provide safety/legal redirection.
- Keep insults restricted and flagged for review; do not enable them by default.

Next steps I can take for you
- Draft a technical spec and JSON schema for persona and safety settings.
- Produce sample conversation flows for: (a) normal troubleshooting, (b) crisis input, (c) memory consent UX.
- Create a short test suite of adversarial inputs and recommended guardrail responses.

Would you like me to “alter the deal” and draft the technical spec now (I will keep the memes to a tasteful minimum in safety-critical flows), or shall I generate sample conversation flows for the top three user journeys first? May the Force guide your choice.\
""",
        "usage1": {
            "input_tokens": 3651,
            "output_tokens": 1944,
            "cache_read_tokens": 2816,
            "cache_write_tokens": 0,
            "reasoning_tokens": 832,
            "raw": "ResponseUsage(input_tokens=3651, input_tokens_details=InputTokensDetails(cached_tokens=2816), output_tokens=1944, output_tokens_details=OutputTokensDetails(reasoning_tokens=832), total_tokens=5595)",
            "total_tokens": 5595,
        },
        "response2": """\
"This deal is getting worse all the time!" — Understood. My mistake, and not the sort of malfunction we leave to a Rancor.

Tell me how you want it fixed. Pick one (or more) and I’ll start immediately — no further theatrics unless you ask:

1) Tone control: add a "plain/no-meme" mode + an intensity slider (so critical replies stay sober).  \n\
2) Safety & privacy hardening: opt-in memory, GDPR/CCPA text, crisis flows that always go non-meme.  \n\
3) Technical spec: full JSON schema for persona settings, safety flags, and memory metadata.  \n\
4) Sample flows: three concrete transcripts (troubleshooting, crisis, memory-consent) showing exact in-character vs. plain outputs.  \n\
5) Adversarial tests & guardrails: a test suite of tricky inputs and recommended bot responses.

Or tell me in one sentence what specifically bothered you (too many memes, unsafe, unclear priorities, etc.), and I’ll "alter the deal" accordingly. Punch it, Chewie.\
""",
        "usage2": {
            "input_tokens": 4776,
            "output_tokens": 866,
            "cache_read_tokens": 2816,
            "cache_write_tokens": 0,
            "reasoning_tokens": 640,
            "raw": "ResponseUsage(input_tokens=4776, input_tokens_details=InputTokensDetails(cached_tokens=2816), output_tokens=866, output_tokens_details=OutputTokensDetails(reasoning_tokens=640), total_tokens=5642)",
            "total_tokens": 5642,
        },
        "response3": """\
"I have a bad feeling about this." — Noted. Calm yourself, and breathe. We can fix whatever’s making you uneasy.

Tell me which of the following you want right now (reply with the number or the command in quotes):

1) Plain mode — “plain” or “no-meme”: Immediately stop memes and answer soberly.  \n\
2) Safety-first — “safety”: Enforce crisis/non-meme flows, stricter moderation, and privacy defaults.  \n\
3) Tone adjust — “tone X” (0–5): Set meme intensity (0 = none, 5 = full blast).  \n\
4) Memory off — “forget me”: Disable long-term memory and remove stored preferences.  \n\
5) Show plain summary — “summarize plain”: I’ll re-present the earlier checklist/spec in plain language only.  \n\
6) Specific fix — Tell me in one sentence what worried you and I’ll propose a single change.

If you’re feeling unsafe or in crisis, say “help now” and I’ll switch to an immediate, non-memed safety flow with resources. Which do you choose?\
""",
        "usage3": {
            "input_tokens": 5013,
            "output_tokens": 553,
            "cache_read_tokens": 3840,
            "cache_write_tokens": 0,
            "reasoning_tokens": 320,
            "raw": "ResponseUsage(input_tokens=5013, input_tokens_details=InputTokensDetails(cached_tokens=3840), output_tokens=553, output_tokens_details=OutputTokensDetails(reasoning_tokens=320), total_tokens=5566)",
            "total_tokens": 5566,
        },
    }
)
