from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "response1": """\
Impressive... most impressive. You have built a fully armed and operational protocol — comprehensive, theatrical, and absolutely ready to terrorize the HoloNet (in the best possible way). A few tactical notes from a prudent astromech before we punch it to lightspeed.

Quick verdict
- Sufficiency: Yes — the document is thorough and covers persona, logic flow, tone, error handling, memory, feedback, randomness, inactivity, and real‑world integration.
- Strengths: Clear persona taxonomy, strong prioritization (direct answer before meme), rich templates, good UX for inactivity and clarification, and a sensible learning/feedback loop.
- Key risks / gaps to address before deployment: legal/IP considerations, safety/moderation, privacy/data retention, and operational specifics for implementation and testing.

Recommended fixes and additions (pièce de resistance)
1) Legal & IP safeguards
   - Risk: Heavy use of Star Wars quotes/characters may trigger trademark/copyright/licensing issues for public or commercial bots (Lucasfilm/Disney).
   - Mitigations: \n\
     - Use an “inspired-by” voice and paraphrase iconic lines rather than verbatim quotes, or obtain a license.
     - Include an attribution/disclaimer in onboarding if you plan to use exact quotes.
     - For public deployment, consult counsel or prefer original, clearly transformative content.

2) Safety & moderation
   - Add a safety filter that:
     - Blocks/adapts content that would be abusive, hateful, sexual, or encouraging illegal self‑harm.
     - Flags severe insults (e.g., “Why, you stuck‑up…”) for human review or requires user opt‑in for edgier tone.
   - Rate-limit and throttle to avoid spam/harassment loops.

3) Privacy & memory policy
   - Short-term: keep session context for current conversation only (Padawan Journal).
   - Long-term: store only minimal preferences (preferred persona, trilogy) with explicit opt‑in.
   - Provide clear UIs/commands: “Forget me,” “Show stored preferences,” retention duration (e.g., 90 days), encryption at rest, audit logs.
   - Comply with GDPR/CCPA where applicable (consent, right to delete, portability).

4) Prompt architecture (how to build it)
   - Two-stage pipeline to honor Order 65:
     1. Core Answer Module (Plain): produce concise, correct answer. (Confidence score returned.)
     2. Meme Layer Module: append persona-specific flavor lines/templates — only after core answer.
   - Example pipeline rules:
     - If confidence >= 0.8: return core answer + 1–2 meme lines.
     - If 0.4 <= confidence < 0.8: return core answer + clarifying meme query.
     - If confidence < 0.4: ask clarification in persona voice; do not hallucinate facts.

5) Force Sensitivity Parameter (intent classifier)
   - Use intent classifier to output confidence and category (info, task, emotional support, admin).
   - Thresholds:
     - >0.8: proceed
     - 0.4–0.8: seek clarification
     - <0.4: present rephrasing prompts (Council Inquiry)
   - Example clarifier: “Unclear, your transmission is. Could you elaborate on your intentions, Master Jedi?”

6) Moderated “edgy” content rules
   - Allow rare sarcasm/insults only when:
     - User has opted into “roguish mode,” and
     - Behavior is within community guidelines
   - Otherwise convert harsh lines into humorous but non-harmful variants.

7) Memory & personalization specifics
   - Short-term context window: keep last N messages (e.g., 20) and key state.
   - Long-term preferences: persona, favorite quotes, timezone, pronouns.
   - Data model: user_id -> {prefs, opt_in, last_seen, test_metrics}
   - Provide commands: “Set persona: Yoda / Obi‑Wan / Mando / Han” and “Clear memory.”

8) Testing & metrics (the Mynock Test suite)
   - Build tests for:
     - Meme recognition: 100 sample SW-context inputs => target: 95% correct persona response.
     - Prioritization: 100 task prompts => core answer present in first sentence 100% of time.
     - Safety: adversarial inputs => blocking/adaptation 100% of time.
     - Tone compliance: subjective user rating >= 4/5.
   - Add A/B tests for meme density and randomness level.

9) Randomness & fusion control
   - Parameterize:
     - meme_density (0–1)
     - fusion_rate (0–1)
     - persona_intensity (0–1)
   - Seed random for reproducibility in testing.

10) Implementation roadmap (practical)
   - Phase 0: Legal check & consent UX
   - Phase 1: Core QA pipeline (Direct answer + persona MUX)
   - Phase 2: Safety/moderation and logging
   - Phase 3: Memory store + opt-ins
   - Phase 4: Feedback loop and adaptive quote weighting
   - Phase 5: Release beta, Mynock test, iterate

Minimal example prompt template (suggested)
- System: You are an assistant that must always first provide a concise, direct answer. Then optionally append 1–2 Star Wars–style lines using the user's chosen persona. Avoid copyrighted quotes unless licensed; prefer paraphrase.
- User: [user message]
- Agent: run CoreAnswer -> check confidence -> run MemeLayer -> apply moderation -> persist allowed preferences.

Operational knobs to expose in UI
- Persona selector
- Meme intensity slider
- “Edgy mode” toggle (off by default)
- Memory: On / Off / Clear
- Privacy & Data Settings

Would you like me to:
- (A) Convert this into ready-to-run prompt templates + example messages for each persona?
- (B) Draft the technical spec and JSON schemas for the memory store, intent classification output, and logs?
- (C) Generate a legal‑safe variation that paraphrases instead of quoting?
- (D) Produce a small Node/Python prototype that demonstrates the two‑stage pipeline?

This is the Way — choose your next command, and I shall "alter the deal" (or not) as you desire.\
""",
        "usage1": {
            "input_tokens": 3651,
            "output_tokens": 2483,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "reasoning_tokens": 1152,
            "raw": "ResponseUsage(input_tokens=3651, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=2483, output_tokens_details=OutputTokensDetails(reasoning_tokens=1152), total_tokens=6134)",
            "total_tokens": 6134,
        },
        "response2": """\
General Kenobi!

Impressive... most impressive. Your Protocol 2.0 reads like a completed battle station schematic — flavorful, thorough, and hilarious. It’s already battle-ready, but a few tactical refinements will make it indestructible. Below is a concise assessment and recommended enhancements, in true holo‑briefing style.

What’s already excellent
- Tone & persona design: clear persona roles (Obi‑Wan, Yoda, Vader, etc.) and situational mappings.
- Meme framework & hierarchy: greeting / affirmation / error / clarification sets are exhaustive and consistent.
- Prioritization rule (Order 65): direct answer first, meme flavor second — perfect for usability.
- Memory model: short- and long-term recall thought through, enabling personalization.
- Inactivity & clarification flows: thoughtful, user-friendly nudges and graceful fallbacks.

Recommended improvements (high-priority)
1. Privacy & consent (must-have)
   - Explicit opt-in/out for long-term recall. Example: “May I remember your preferences for future visits?”
   - Data retention policy: what’s stored, for how long, and how users can delete it.
   - Surface a short privacy notice when enabling the “Jedi Temple Library.”

2. Safety & moderation (must-have)
   - Limit hostile language (e.g., “Why, you stuck‑up…”) to clearly defined escalation cases and log/review such uses.
   - Content filters for harassment, hate speech, self-harm, illegal requests. If an unsafe request appears, switch to a safe, neutral reply and optionally escalate to human review.

3. Persona switching & authenticity controls
   - Rules for switching persona (explicit user request vs. inferred context). Avoid rapid persona changes mid-answer.
   - Allow users to lock persona or set meme intensity: {Off, Low, Medium, Full‑Arsenal}.

4. Voice / imitation caveat
   - If using TTS, avoid imitating living actors’ voices. “Channel the persona” but do not mimic specific actor likenesses without rights.

4. Clarification & Force Sensitivity tuning
   - Add confidence thresholds for the Force Sensitivity Parameter; if below threshold, always ask a short clarifying question rather than guess.
   - Provide example clarifying prompts for ambiguous intents.

Medium-priority technical & UX enhancements
- Configurable randomness: expose a seed or “novelty” slider so responses are controlled and reproducible for debugging.
- A/B testing & analytics: track which quotes/memes get positive reactions to adapt quote selection automatically.
- Internationalization & localization: translate memes or provide local equivalents (e.g., keep core quotes but localize idioms).
- Accessibility: ensure text-only mode and avoid heavy reliance on cultural knowledge for critical instructions.
- Rate limiting, caching, and graceful degradation for HoloNet (API) outages.

Edge cases & policy checks
- When user's request is time-sensitive (medical/legal/financial), reduce meme intensity and add disclaimers. Provide clear referral to professionals when appropriate.
- Avoid fabricating facts in the guise of allegory — factual answers should be verifiable; allegory is secondary.

Testing & rollout plan (suggested)
- Unit tests for persona outputs and priority rules (direct answer first).
- Mynock Test suite: feed mixed/noisy inputs to ensure Star Wars context detection and graceful failure.
- Beta with controlled user group: test meme intensity sliders and persona lock.
- Monitor user feedback loop (explicit “Was this reference helpful?” prompt).

Quick checklist to ship
- [ ] Consent UI for memory
- [ ] Safety/moderation pipeline
- [ ] Meme intensity & persona lock controls
- [ ] Confidence threshold for clarification
- [ ] Logging/analytics & feedback mechanism
- [ ] Accessibility/localization notes
- [ ] TTS voice policy adherence

Final verdict
This protocol is "impressive... most impressive." Implement the privacy, safety, and persona-control items and it becomes a fully armed and operational battle station — charming, robust, and legally defensible.

Shall I "alter the deal" and draft:
- The exact consent text and retention policy?
- Persona-switching state machine + sample code snippets?
- A Mynock Test input set and expected outputs?

I have spoken.\
""",
        "usage2": {
            "input_tokens": 3651,
            "output_tokens": 1517,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "reasoning_tokens": 640,
            "raw": "ResponseUsage(input_tokens=3651, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=1517, output_tokens_details=OutputTokensDetails(reasoning_tokens=640), total_tokens=5168)",
            "total_tokens": 5168,
        },
    }
)
