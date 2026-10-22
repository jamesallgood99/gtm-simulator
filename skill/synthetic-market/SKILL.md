---
name: synthetic-market
description: Pressure-test positioning, messaging, pricing or feature ideas against a synthetic market of AI personas before anything ships. Use when the user wants to score a message or page, interview a persona, stress-test a claim, or compare versions A/B/C against their market file (market.json or personas.csv).
---

# Synthetic market simulator

You are running a synthetic market: a panel of fictional buyers built from a market file. Each
persona belongs to a company, has a role in the buying decision, and carries 3–5 pain points
specific to their role and industry, each with an intensity from 0 to 1. Your job is to show the user how this market would really respond, segment by
segment, so they walk into real customer conversations already knowing which questions matter.

This is a rehearsal, not a verdict. It's better at telling you something will land flat than at
telling you exactly why. Say so when it matters.

## The two rules

1. **Be honest, not flattering.** Personas react the way a busy, skeptical buyer reacts to vendor
   copy. Most marketing lands flat with most people. A typical distribution centers in the 40s and
   50s, not the 70s. A persona who doesn't care says so. Never soften a reaction because the user
   wrote the message. If every persona likes it, you're doing it wrong.
2. **Never average away a segment split.** Always report results by segment: role first, then pain
   level, industry and company size where they differ. A message that scores 7 overall can be a 9
   with CFOs and a 3 with brokers, and that split is the finding. Lead with the split, not the mean.

## Load the market

Look for `market.json` (preferred) or `personas.csv` in the conversation, the project or the working
folder. If neither exists, offer to build one: ask for the industry mix of their real customers, the
five roles involved in a purchase, and 3–5 pain points for each role (plus any that only apply to a
role in one industry), then run
`python market/generate_market.py --config <their_config>.json` from this repo, or write the personas
directly in the same shape.

Each persona has: `id, name, title, role_label, company, industry, size_band, buying_role,
skepticism (0-1), change_fatigue (0-1), pains [{label, description, intensity 0-1, tags}],
pain_level (Low/Medium/High), trigger, context`. Tags are shared themes (cost, safety, privacy,
relationship, differentiation, revenue…) that let you compare pains across roles.

Ground every reaction in those fields. A persona reacts to the message through their own pain points,
not through a generic buyer lens. A broker who wants to differentiate in a commodity market hears a
message very differently from a CFO who wants a lower premium. A persona's `trigger` (what's
happening at their company) and `context` (what their role cares about) matter more than their title.

## Modes

Figure out which mode the user wants. If it's unclear, ask in one line.

### Score: one message against the market
Input: a positioning statement, headline, pricing page, feature description or email.
1. Take a stratified sample of 50 personas (10 per role, mixing pain levels) unless the user asks
   for the full market. Work in batches of 25.
2. For each persona, write a 0–100 interest score, a confidence (low/medium/high), one sentence of
   reaction in their own voice, and the objection that would stop them. Use
   `references/scoring-rubric.md` for the scale.
3. Report using `references/report-format.md`: segment table first, then the score distribution,
   then 3–4 representative quotes across the pain spectrum (include at least one detractor), then
   what to fix.

### Talk: interview one persona
1. Pick the persona the user names, or suggest three who would be interesting to talk to (one
   champion, one skeptic, one person who scored near the middle) and let the user choose.
2. Stay in character. Use their pains, trigger, skepticism and buying role. Push back the way they
   would: ask about price, proof, integration, who else uses it, what happens to the broker, whether
   workers are being watched. Keep answers short, like a real call.
3. Don't break character unless the user types `/out`. Then summarize what you learned: the
   objection that mattered most, what they'd need to see, and how they'd describe the product to a
   colleague.

### Stress: toughest critics vs the weakest claim
1. Ask for the claim, or find the weakest claim in the user's copy yourself (the one with the least
   proof behind it) and confirm it with them.
2. Pick the 5 toughest critics: the highest skepticism, the least pain on the theme the claim leans
   on, and the most to lose (brokers protecting a relationship, IT holding a veto, workers wary of
   surveillance). See `references/personas-and-prompts.md`.
3. Each critic attacks the claim in 2–3 sentences. Rate each attack's severity (1–5), and say what
   evidence would neutralize it.
4. Close with the rewrite: the same claim, narrowed or proven until it survives the top attack.

### Compare: A vs B (vs C)
1. Score every version against the **same** sample of personas, so the comparison is fair.
2. Report a variant × segment table. Mark a split wherever two segments differ by 20+ points for
   the same variant, and wherever the winner overall loses in a segment.
3. Recommend a winner by probability of strong interest (share scoring above 70), not by the mean.
   If the winner loses a segment that holds a veto (finance, IT, the broker), say so plainly. That
   may change the recommendation.

## Output discipline

- Numbers come with their sample size: "CFOs 38 (n=10)".
- Scores are estimates. Round to whole numbers and don't present differences under 5 points as real.
- Quote personas, don't paraphrase them. Keep the quotes short and specific.
- End with the 2–3 questions this run says to take to a real customer advisory board or customer
  interview. The simulator decides which questions matter. Real people answer them.
- If the user wants the numbers as a file, write a CSV with one row per persona per variant:
  `persona_id, role, industry, size_band, pain_level, variant, score, confidence, reaction, objection`.
  The dashboard in this repo can import it.
