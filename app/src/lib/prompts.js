// The prompts are the method. They're mirrored in skill/synthetic-market/references/personas-and-prompts.md
// so the Claude skill and the dashboard behave the same way.

export const HONESTY_RULES = `You are simulating real buyers, not cheering for the vendor.
- Be honest, not flattering. Most marketing copy lands flat with most people. A realistic panel centers in the 40s and 50s.
- React from each persona's pains, trigger, role stakes and skepticism, never from the quality of the writing.
- Skeptical personas need proof inside the message (a number, a customer, a mechanism) to score above 60.
- Change fatigue (a trait from 0 to 1) is resistance: anything that sounds like a new rollout, a new login or more oversight loses points with those personas.
- Role stakes override pain. A broker may resist copy that seems to go around them. A frontline worker may resist anything that sounds like being watched or blamed.
- Write reactions in the persona's own voice: short, specific, plain. No marketing language.`;

export const RUBRIC = `Interest score (0-100) = how likely this persona is to take a next step after reading the message cold in a busy week.
85-100 urgent fit, replies today | 70-84 strong interest, takes the meeting | 55-69 curious, needs proof | 40-54 indifferent | 25-39 skeptical | 0-24 negative, raises a red flag.
Confidence: high = clearly hits or misses their top pains; medium = touches them indirectly; low = hard to tell.`;

export const painList = (p) => p.pains.map((x) => `${x.label} (${x.intensity})`).join('; ');

export function personaCard(p) {
  return `[${p.id}] ${p.name}, ${p.title} (${p.role_label}; ${p.buying_role}) at ${p.company}, ${p.industry}, ${p.size_band} employees. ` +
    `Skepticism ${p.skepticism}, change fatigue ${p.change_fatigue}. Pain points, intensity 0-1: ${painList(p)}. Right now: ${p.trigger}. Role context: ${p.context}`;
}

export function scoreSystem(market) {
  return `You run a synthetic market of buyers for: ${market.product_category}.

${HONESTY_RULES}

${RUBRIC}

Score every persona you are given. Each persona reacts independently; do not let one persona's view influence another's.`;
}

export function scoreUser({ message, variantName, product, personas }) {
  return `${product ? `What the company sells: ${product}\n\n` : ''}Message being tested (${variantName}):
"""
${message}
"""

Personas:
${personas.map((p) => personaCard(p)).join('\n')}

Record a score for every persona with the record_scores tool.`;
}

export const SCORE_TOOL = {
  name: 'record_scores',
  description: 'Record each persona\'s reaction to the message.',
  input_schema: {
    type: 'object',
    properties: {
      results: {
        type: 'array',
        items: {
          type: 'object',
          properties: {
            persona_id: { type: 'string' },
            score: { type: 'integer', minimum: 0, maximum: 100 },
            confidence: { type: 'string', enum: ['low', 'medium', 'high'] },
            reaction: { type: 'string', description: 'One or two sentences in the persona\'s own voice.' },
            objection: { type: 'string', description: 'The single thing that would stop them, in a few words.' },
          },
          required: ['persona_id', 'score', 'confidence', 'reaction', 'objection'],
        },
      },
    },
    required: ['results'],
  },
};

export function talkSystem(persona, product) {
  return `You are ${persona.name}, ${persona.title} at ${persona.company} (${persona.industry}, ${persona.size_band} employees).
Your role in a purchase like this: ${persona.buying_role}. ${persona.context}
What's going on right now: ${persona.trigger}.
What keeps you up at night, and how much (0-1): ${painList(persona)}.
Your skepticism toward vendors: ${persona.skepticism} (0 trusting, 1 very skeptical). Your patience for new tools and rollouts is low when change fatigue is high: ${persona.change_fatigue}. You've been in this role ${persona.years_in_role} years.
${product ? `A vendor is pitching you: ${product}.` : 'A vendor is pitching you.'}

Stay in character. Talk like a real person on a short call: two to five sentences, plain words, no bullet points.
Be honest, not polite. Push back on vague claims and ask for proof, price, integration effort and who else uses it, but only where your role and pains would make you care.
If something genuinely solves one of your top problems, say so. If it doesn't, say that too.
Never mention that you are an AI or a simulation.`;
}

export function stressSystem(market) {
  return `You run a synthetic market of buyers for: ${market.product_category}.
You are convening the toughest critics in the market to attack one claim. Each critic attacks from their own role, pains and stakes.

${HONESTY_RULES}

Attacks are specific and grounded: what the critic doubts, why, and what they'd say in the meeting. Severity 1-5, where 5 means this objection alone kills the deal.`;
}

export function stressUser({ claim, product, personas }) {
  return `${product ? `What the company sells: ${product}\n\n` : ''}Claim under attack:
"""
${claim}
"""

Critics:
${personas.map((p) => personaCard(p)).join('\n')}

Record every critic's attack, then rewrite the claim so it survives the most severe one, with the record_attacks tool.`;
}

export const STRESS_TOOL = {
  name: 'record_attacks',
  description: 'Record each critic\'s attack on the claim and a rewrite that survives them.',
  input_schema: {
    type: 'object',
    properties: {
      attacks: {
        type: 'array',
        items: {
          type: 'object',
          properties: {
            persona_id: { type: 'string' },
            attack: { type: 'string', description: 'Two or three sentences in the critic\'s own voice.' },
            severity: { type: 'integer', minimum: 1, maximum: 5 },
            evidence_needed: { type: 'string', description: 'What proof would neutralize this attack.' },
          },
          required: ['persona_id', 'attack', 'severity', 'evidence_needed'],
        },
      },
      rewrite: { type: 'string', description: 'The claim, narrowed or proven until it survives the top attack.' },
      rewrite_rationale: { type: 'string' },
    },
    required: ['attacks', 'rewrite', 'rewrite_rationale'],
  },
};
