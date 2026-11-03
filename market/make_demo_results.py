#!/usr/bin/env python3
"""
Build the demo results the dashboard shows before anyone adds an API key.

These scores come from a simple, transparent heuristic (pain alignment, role stakes, skepticism and
change fatigue, plus noise). They are NOT model output. The dashboard labels them as demo data.
Run a live simulation with your own Claude API key to get real persona reactions.

    python market/make_demo_results.py
"""
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
market = json.loads((ROOT / "app" / "public" / "data" / "market.json").read_text())
rng = random.Random(7)

CAMPAIGN = {
    "name": "Q2 product launch",
    "product": "Keelstone, an AI workplace safety platform for mid-market employers in high-injury industries. It runs on the cameras a site already has to flag unsafe lifts, slips and near-misses, turns them into crew coaching, automates OSHA paperwork, and gives the CFO and broker a data-backed risk story at renewal.",
    "variants": [
        {"id": "A", "name": "Variant A", "headline": "Lower your workers' comp premium.",
         "message": "Lower your workers' comp premium. Our AI finds the risks driving your claims so you can bring your experience mod down before renewal.",
         "focus": "Cost and premium reduction"},
        {"id": "B", "name": "Variant B", "headline": "Fewer injuries. Fewer claims.",
         "message": "Fewer injuries. Fewer claims. Spot unsafe lifts, falls and near-misses on the cameras you already have, so your safety team can coach before someone gets hurt.",
         "focus": "Injury prevention and safety"},
        {"id": "C", "name": "Variant C", "headline": "Give your broker better data.",
         "message": "Give your broker better data. We turn what's happening on your sites into the risk story carriers want to see, so you and your broker walk into renewal with leverage.",
         "focus": "Broker partnership and renewal leverage"},
    ],
}

# How much each variant speaks to each pain theme (themes are tags on every pain point).
THEME = {
    "A": {"cost": 1.0, "roi": 0.6, "safety": 0.3, "revenue": 0.2},
    "B": {"safety": 1.0, "compliance": 0.5, "admin": 0.3, "roi": 0.2, "cost": 0.35},
    "C": {"differentiation": 0.9, "relationship": 0.8, "revenue": 0.6, "cost": 0.6, "admin": 0.3},
}
# Role stakes per variant (positive = the framing serves their role, negative = it threatens it).
ROLE = {
    "A": {"broker": -10, "cfo": 10, "it_manager": 4, "safety_manager": -2, "worker": -12},
    "B": {"broker": -4, "cfo": -8, "it_manager": -4, "safety_manager": 8, "worker": 0},
    "C": {"broker": 8, "cfo": 2, "it_manager": 6, "safety_manager": -6, "worker": -14},
}
# Variant B says "AI watches ... cameras". That costs points with people who care about privacy.
SURVEILLANCE = {"A": 0.2, "B": 0.85, "C": 0.45}

REACT = {
    "A": {
        "broker": {
            "hi": ["If this actually moves the mod, I want to see it before my client does. I'd rather bring it to them than have it go around me.",
                   "Premium is the conversation I have with every client right now. Show me a loss run that changed and I'll listen."],
            "mid": ["Every vendor says they'll lower premiums. The carrier decides that, not the software.",
                    "Interesting, but my clients ask me about premium, not a startup. Where do I fit in this?"],
            "lo": ["This reads like you're selling around the broker. That's a fast way to get my client to say no.",
                   "Lower premiums is my job. I don't need a tool promising my client what I negotiate."],
        },
        "cfo": {
            "hi": ["Our mod is killing us. If you can show a payback period I'll take the meeting this week.",
                   "That's the number I care about. What's the typical premium reduction and how long until we see it?"],
            "mid": ["I'd need to see the math. Premium savings show up a year later, the software bill shows up now.",
                    "Sounds good, but I've heard it before. Give me three customers in my industry."],
            "lo": ["Premiums are fine this year. Not a priority.",
                   "Another line item promising savings it can't guarantee. Pass."],
        },
        "it_manager": {
            "hi": ["If finance wants it I'll support it, but I need to know what it connects to.",
                   "Fine, but what's it running on and who maintains it?"],
            "mid": ["Premiums aren't my problem. I'd want to know what this does on my network.",
                    "Not really aimed at me. Send it to finance."],
            "lo": ["Nothing here tells me what you'd install on our systems. That's a no until I know.",
                   "Cost savings pitch, zero detail on security. I'll be the one who has to say no."],
        },
        "safety_manager": {
            "hi": ["If it helps me show finance that safety saves money, I'm in. That's the argument I keep losing.",
                   "Getting the mod down is what my bosses grade me on. I'd look at this."],
            "mid": ["Premium is a lagging number. I care about what happens on the floor before the claim.",
                    "Okay, but how does it actually reduce injuries? That's what moves the premium."],
            "lo": ["This is a finance pitch. Nothing about my people.",
                   "Leading with premium tells me you don't understand safety."],
        },
        "worker": {
            "hi": ["If it makes the job safer, sure. But this sounds like it's about saving the company money.",
                   "As long as it's not used to write people up."],
            "mid": ["Saving the company money on insurance doesn't do much for me.",
                    "So the company saves money. What changes for us on the floor?"],
            "lo": ["This is about cutting costs. Usually that means cutting corners somewhere else.",
                   "Lower premiums means they'll fight our claims harder. No thanks."],
        },
    },
    "B": {
        "broker": {
            "hi": ["Fewer claims is the best thing I can bring to a carrier. I'd like to see the data.",
                   "If it really cuts frequency, that helps me at renewal. Who else is using it?"],
            "mid": ["Safety tech is fine, but my clients buy outcomes. Show me claim frequency before and after.",
                    "Lots of safety tools out there. What's different here?"],
            "lo": ["My clients already have a safety program. I'm not sure this adds anything.",
                   "Cameras plus AI sounds like a liability conversation I'd have to manage."],
        },
        "cfo": {
            "hi": ["Fewer claims means a lower mod. I'd need to see the dollars, but I'm interested.",
                   "Injuries are expensive. If you can prove the reduction I'll take a look."],
            "mid": ["Sounds like a safety budget item. Where's the ROI?",
                    "Nice idea, but I need a number, not a promise of fewer injuries."],
            "lo": ["No dollars anywhere in this. I'd send it to safety and forget it.",
                   "Safety is important, but this doesn't tell me why I should pay for it."],
        },
        "it_manager": {
            "hi": ["Using the cameras we already have is a plus. I'd need to see how video is stored.",
                   "Okay, if it runs on existing cameras I'll at least look at the architecture."],
            "mid": ["AI watching our cameras means video leaving the building. I'd have a lot of questions.",
                    "Who owns the footage, where does it go, and who has access? Start there."],
            "lo": ["Camera feeds into an AI vendor is a hard no until legal and security sign off.",
                   "This is a privacy and security project disguised as a safety tool."],
        },
        "safety_manager": {
            "hi": ["This speaks to my daily struggle. I can't be on every site, and I find out about near-misses after the fact.",
                   "Catching unsafe lifts before an injury is exactly what I need. When can I see it?"],
            "mid": ["Sounds promising. My worry is false alarms burying my team.",
                    "I'd want to know how it handles our sites. Every warehouse looks different."],
            "lo": ["We already do observations. I'm not sure software adds much.",
                   "Interesting, but I don't have time to roll out another tool."],
        },
        "worker": {
            "hi": ["If it catches the stuff that actually hurts people, I'm for it. Just don't use it to blame us.",
                   "Coaching is better than getting hurt. I'd be okay with it if it's about safety, not discipline."],
            "mid": ["Cameras watching us all day? Depends what they do with it.",
                    "We've had safety programs before. They usually turn into more rules."],
            "lo": ["AI watching us on camera. That's not safety, that's surveillance.",
                   "They'll use this to write people up. Everyone on the floor knows how this goes."],
        },
    },
    "C": {
        "broker": {
            "hi": ["This is the first vendor pitch that treats me as a partner. Better data at renewal is exactly what I need.",
                   "If you give me the risk story, I can actually negotiate. I'd bring this to clients."],
            "mid": ["Better data helps, but carriers have their own models. How much weight do they give this?",
                    "I like that it includes the broker. I'd want to see a sample report."],
            "lo": ["I already tell my clients' risk story. Not sure I need help.",
                   "Sounds like a vendor trying to get between me and my carrier relationships."],
        },
        "cfo": {
            "hi": ["Leverage at renewal is worth money. What's the typical outcome?",
                   "If it helps us negotiate, I'm interested. Our broker could use more ammunition."],
            "mid": ["Sounds useful, but I'd want hard numbers on premium impact.",
                    "Maybe. I'd ask our broker if it's worth it."],
            "lo": ["That's what we pay our broker for.",
                   "Data for renewal is nice, not a reason to buy software."],
        },
        "it_manager": {
            "hi": ["Reporting is easy to support. What data leaves our systems?",
                   "If it's mostly reporting I can live with it. Need to see the data flow."],
            "mid": ["Sending our site data to carriers raises some questions for me.",
                    "Not really my area, but I'd need to know what's shared and with whom."],
            "lo": ["Sharing our operational data with carriers? I'd push back hard.",
                   "That's our data going to third parties. Need a lot more detail."],
        },
        "safety_manager": {
            "hi": ["If it gets safety a seat at the renewal table, that's a big deal for my program.",
                   "I'd love to show the carrier what we actually do. This could help."],
            "mid": ["This is a finance and broker conversation. Where does safety come in?",
                    "Okay, but does it help me prevent injuries, or just report them?"],
            "lo": ["This isn't for me. It's about insurance, not safety.",
                   "Renewal leverage doesn't help my people tomorrow morning."],
        },
        "worker": {
            "hi": ["Doesn't really affect me, but okay.",
                   "If it makes things safer, fine."],
            "mid": ["Data about us going to the insurance company? I'd want to know what's in it.",
                    "Not sure what this has to do with us."],
            "lo": ["So they're sending data about us to the insurance company. No.",
                   "Sounds like it's about the company's insurance, not our safety."],
        },
    },
}

OBJECTION = {
    "A": {"broker": ["Seems to go around the broker", "Premium is set by the carrier, not software", "No proof it moves the mod"],
          "cfo": ["Needs a proven payback period", "Savings land a year after the invoice", "No customers in our industry"],
          "it_manager": ["No detail on what gets installed", "Not my problem to solve", "Unclear data security"],
          "safety_manager": ["Leads with cost, not safety", "Premium is a lagging number", "Doesn't say how injuries drop"],
          "worker": ["Sounds like cost-cutting", "They'll fight our claims harder", "Nothing changes on the floor"]},
    "B": {"broker": ["Needs claim-frequency proof", "Cameras create liability questions", "Where does the broker fit?"],
          "cfo": ["No hard-dollar ROI", "Reads like a safety budget item", "No payback period"],
          "it_manager": ["Video privacy and storage", "Who owns the footage?", "Another system to support"],
          "safety_manager": ["Worried about false alarms", "No time for another rollout", "Every site is different"],
          "worker": ["Feels like surveillance", "Will be used for discipline", "Programs turn into more rules"]},
    "C": {"broker": ["Carriers may not weight this data", "Needs a sample report", "Could get between me and carriers"],
          "cfo": ["Isn't this the broker's job?", "No hard numbers on premium", "Reporting isn't a reason to buy"],
          "it_manager": ["Data shared with third parties", "Unclear data flow", "Needs a security review"],
          "safety_manager": ["Reporting, not prevention", "Insurance pitch, not safety", "Doesn't help my people tomorrow"],
          "worker": ["Data about workers going to insurers", "Not about our safety", "Doesn't affect me"]},
}


def score(p, v):
    theme = THEME[v]
    pains = p["pains"]
    fit = [x["intensity"] * max((theme.get(t, 0) for t in x["tags"]), default=0) for x in pains]
    weighted = sum(fit) / sum(x["intensity"] for x in pains)
    align = 0.5 * weighted + 0.5 * max(fit)
    privacy = max((x["intensity"] for x in pains if "privacy" in x["tags"]), default=0)
    s = 29 + 58 * align
    s += ROLE[v][p["role"]]
    s -= 14 * (p["skepticism"] - 0.5)
    s -= 12 * max(0.0, p["change_fatigue"] - 0.55)
    s -= 26 * SURVEILLANCE[v] * max(0.0, privacy - 0.35)
    if "nothing urgent" in p["trigger"]:
        s -= 8
    s += rng.gauss(0, 7)
    return int(max(2, min(98, round(s))))


def confidence(p, s):
    if s >= 75 or s <= 25:
        return "high"
    return "medium" if p["skepticism"] < 0.7 else rng.choice(["medium", "low"])


results = {}
for v in CAMPAIGN["variants"]:
    vid = v["id"]
    rows = []
    for p in market["personas"]:
        s = score(p, vid)
        band = "hi" if s >= 66 else "mid" if s >= 42 else "lo"
        rows.append({
            "persona_id": p["id"], "score": s, "confidence": confidence(p, s),
            "reaction": rng.choice(REACT[vid][p["role"]][band]),
            "objection": rng.choice(OBJECTION[vid][p["role"]]),
        })
    results[vid] = rows

by_id = {p["id"]: p for p in market["personas"]}


def pick(role, level, key=lambda p: p["skepticism"]):
    cands = [p for p in market["personas"] if p["role"] == role and p["pain_level"] == level]
    return max(cands, key=key)


ROLE_STAKES = {"broker": 1, "it_manager": 1, "worker": 1, "cfo": 0.7, "safety_manager": 0.3}


def theme_intensity(p, theme):
    return max([x["intensity"] for x in p["pains"] if theme in x["tags"]] + [0])


def toughest_critics(theme, count=5):
    """Same formula as app/src/lib/stats.js toughestCritics."""
    ranked = sorted(market["personas"], key=lambda p: -(p["skepticism"] * 0.5 + (1 - theme_intensity(p, theme)) * 0.3
                                                         + ROLE_STAKES.get(p["role"], 0.5) * 0.2))
    out, per_role = [], {}
    for p in ranked:
        if per_role.get(p["role"], 0) >= 2:
            continue
        per_role[p["role"]] = per_role.get(p["role"], 0) + 1
        out.append(p)
        if len(out) == count:
            break
    return out


ATTACKS = {
    "broker": [
        (5, "Premiums are set by the carrier against the experience mod, and the mod looks back three years. Nobody controls a 20% cut in year one, and if my client expects it, I'm the one explaining why it didn't happen.",
         "Mod and premium history for named customers, with the renewal year the change actually hit."),
        (4, "First-year premium cuts are rare. The usual path is fewer claims, then a better mod a year or two later. Promising 20% up front makes the whole pitch look naive, and it makes me look naive if I bring it to a client.",
         "Claim frequency in year one, then the mod and premium changes that followed."),
    ],
    "it_manager": [
        (3, "Before anyone talks savings, tell me what runs on our network and where the video goes. If security says no, the 20% is irrelevant.",
         "Architecture diagram, data retention policy, SOC 2 report."),
        (3, "Savings claims don't tell me who supports this at 2 a.m. across all our sites. Another system with no owner is a cost too.",
         "Who handles deployment and support, and the expected IT hours per site."),
    ],
    "worker": [
        (3, "If the company is saving 20% on insurance, it's coming from somewhere. Usually it means fighting our claims harder.",
         "A clear statement that footage is used for coaching, not discipline, ideally agreed with workers."),
        (2, "Nobody on the floor cares about the premium. If this is sold as a cost-cutting tool, people will treat it like one and work around it.",
         "Worker-facing language about safety outcomes, and a pilot crew who'll vouch for it."),
    ],
    "cfo": [
        (4, "Twenty percent of what, and compared to what? If the market softened that year, everybody's premium dropped. I need a control group or I'm not believing it.",
         "Savings compared against similar companies or the market trend, with the software cost netted out."),
        (4, "Even if it's true, the savings land at renewal and the invoice lands now. Show me the payback period, not the headline.",
         "A payback model built on our own loss runs."),
    ],
    "safety_manager": [
        (2, "If you sell this to leadership as a premium play, I'll be judged on premium. I can control injuries. I can't control the carrier.",
         "Leading indicators the safety team owns, reported alongside premium."),
        (2, "Twenty percent sounds like marketing. My credibility with leadership depends on not overpromising.",
         "Conservative, sourced outcome ranges."),
    ],
}

critics = toughest_critics("cost")
used = {}
attacks = []
for p in critics:
    i = used.get(p["role"], 0)
    used[p["role"]] = i + 1
    sev, text, needed = ATTACKS[p["role"]][i]
    attacks.append({"persona_id": p["id"], "severity": sev, "attack": text, "evidence_needed": needed})

stress = {
    "claim": "Customers cut their workers' comp premium by 20% in the first year.",
    "theme": "cost",
    "attacks": attacks,
    "rewrite": "Customers cut claim frequency in the first year, and that shows up in the experience mod at the next renewal. Bring your broker. We'll show you the loss runs.",
    "rewrite_rationale": "The original promise fails the top attack: carriers set premiums against a three-year mod, so nobody controls a 20% cut in year one. The rewrite claims what the product controls (claim frequency), names the real path to premium (the mod at renewal), and brings the broker in instead of going around them.",
}
print("critics:", [(p["role"], p["skepticism"]) for p in critics])

talk_p = pick("cfo", "High", key=lambda p: next((x["intensity"] for x in p["pains"] if x["key"] == "premium_cost"), 0))
talk = {
    "persona_id": talk_p["id"],
    "transcript": [
        {"role": "user", "text": "We help employers lower their workers' comp premium. Our AI finds the risks driving your claims so you can bring your experience mod down."},
        {"role": "persona", "text": f"Our mod is the reason I took this call. But I've had three vendors tell me that this year. What's the actual number, and when do I see it? Premium savings show up at renewal. Your invoice shows up next month."},
        {"role": "user", "text": "Most customers see claim frequency drop in the first six months, and that shows up in the mod over the next renewal cycle."},
        {"role": "persona", "text": "So, eighteen months to two years before it shows up in my premium. That's fine, if you'll put it in writing. Who else in " + talk_p["industry"].lower() + " is using it, and can I call their CFO?"},
        {"role": "user", "text": "Yes, we can set up a reference call. What would you need to see before taking it to your CEO?"},
        {"role": "persona", "text": "A payback model with our own loss runs in it, not a generic slide. And I'd want our broker in the room. If they don't buy it, I won't get it past the board."},
    ],
}

# ---------------------------------------------------------------------------------------------
# What a live run would extract from the sample PRD, MRD and creative brief in
# app/public/data/samples/. Written by hand for the demo; live runs ask Claude to do this.
# ---------------------------------------------------------------------------------------------
BRIEF = {
    "product_name": "Keelstone Safety Platform",
    "summary": CAMPAIGN["product"],
    "target": "Mid-market employers (50 to 5,000 employees) in high-injury industries, buying through an independent broker.",
    "proposition": "Fewer injuries, fewer claims, and a better story at renewal, on the cameras you already have.",
    "tone": "Plain, practical and specific. Talk like a safety professional, not a tech company. Never fear-based.",
    "mandatories": [
        "Never imply surveillance or discipline.",
        "Position the broker as a partner, never as someone we go around.",
        "Only use claims we can prove (MRD proof table).",
        "Mention the cameras you already have in at least one direction.",
    ],
    "features": [
        {"id": "F1", "name": "Hazard detection on existing cameras", "short": "Hazard detection",
         "description": "Flags unsafe lifts, slips, missing PPE and forklift near-misses on existing IP cameras. Alerts go to the safety team.",
         "primary_roles": ["safety_manager"], "themes": ["safety", "compliance"], "setup_effort": "medium", "source": "PRD"},
        {"id": "F2", "name": "Crew coaching feed", "short": "Coaching feed",
         "description": "Weekly coaching clips from flagged events, faces blurred, played in toolbox talks.",
         "primary_roles": ["safety_manager", "worker"], "themes": ["safety", "change"], "setup_effort": "low", "source": "PRD"},
        {"id": "F3", "name": "Broker risk report", "short": "Broker report",
         "description": "Renewal-ready report of hazard trends and corrective actions. Brokers see all their Keelstone clients.",
         "primary_roles": ["broker"], "themes": ["relationship", "differentiation", "revenue", "cost"], "setup_effort": "low", "source": "PRD"},
        {"id": "F4", "name": "Total cost of risk dashboard", "short": "Cost of risk",
         "description": "Premium, claims, reserves and lost workdays in one view, with an ROI tracker against the customer's baseline.",
         "primary_roles": ["cfo"], "themes": ["cost", "roi"], "setup_effort": "medium", "source": "PRD"},
        {"id": "F5", "name": "OSHA recordkeeping automation", "short": "OSHA logs",
         "description": "Drafts OSHA 300, 300A and 301 entries from incident reports, with an audit trail.",
         "primary_roles": ["safety_manager"], "themes": ["compliance", "admin"], "setup_effort": "low", "source": "PRD"},
        {"id": "F6", "name": "Privacy and data controls", "short": "Privacy controls",
         "description": "Edge blurring, 30-day video retention, SSO, role-based access, coaching-only video policy.",
         "primary_roles": ["it_manager", "worker"], "themes": ["privacy", "integration"], "setup_effort": "low", "source": "PRD"},
        {"id": "F7", "name": "Anonymous near-miss reporting", "short": "Near-miss reports",
         "description": "Workers report a hazard from their phone in under 30 seconds, anonymously if they choose.",
         "primary_roles": ["worker"], "themes": ["safety", "relationship"], "setup_effort": "low", "source": "PRD"},
        {"id": "F8", "name": "Claims and HRIS integrations", "short": "Integrations",
         "description": "Payroll, HRIS and carrier claims feeds flow in without manual exports. Needs IT approval.",
         "primary_roles": ["it_manager", "cfo"], "themes": ["integration", "admin"], "setup_effort": "high", "source": "PRD"},
    ],
    "claims": [
        {"id": "K1", "text": "Customers cut claim frequency by 30% in the first year.", "proof": "Pilot of 6 customers, 12 months, internal analysis.", "proof_strength": 3, "theme": "safety", "source": "MRD"},
        {"id": "K2", "text": "Customers cut their workers' comp premium by 20% in the first year.", "proof": "None yet. Requested by sales.", "proof_strength": 1, "theme": "cost", "source": "MRD"},
        {"id": "K3", "text": "Deploys on your existing cameras in under a week.", "proof": "9 of 11 pilot deployments.", "proof_strength": 4, "theme": "integration", "source": "MRD"},
        {"id": "K4", "text": "No new hardware required.", "proof": "True except a small on-site gateway, included.", "proof_strength": 3, "theme": "integration", "source": "MRD"},
        {"id": "K5", "text": "Safety teams cover 3x more sites.", "proof": "One pilot customer quote, not measured.", "proof_strength": 2, "theme": "safety", "source": "MRD"},
        {"id": "K6", "text": "Brokers win renewals with Keelstone reports.", "proof": "Two broker case studies in progress.", "proof_strength": 2, "theme": "relationship", "source": "MRD"},
    ],
}
GENERATION = {
    "A": {"rationale": "Creative brief direction 1 (cost). Speaks to the CFO's premium and mod. Avoids the unproven 20% premium claim and names the real path: the mod at renewal.",
          "features": ["F4", "F1"], "claims": ["K1"], "checks": ["Avoids the unproven premium claim (K2)"]},
    "B": {"rationale": "Direction 2 (safety). Leads with the proposition's first half and the cameras-you-already-have mandatory. Written for the safety manager.",
          "features": ["F1", "F2"], "claims": ["K1", "K4"], "checks": ["Mentions existing cameras", "Says coach, not watch"]},
    "C": {"rationale": "Direction 3 (partnership). Puts the broker beside the employer at renewal, as the brief requires.",
          "features": ["F3"], "claims": ["K6"], "checks": ["Broker as partner"]},
}
for v in CAMPAIGN["variants"]:
    v.update(GENERATION[v["id"]])

DOCS = [
    {"name": "keelstone-prd.md", "type": "PRD", "path": "data/samples/keelstone-prd.md"},
    {"name": "keelstone-mrd.md", "type": "MRD", "path": "data/samples/keelstone-mrd.md"},
    {"name": "keelstone-creative-brief.md", "type": "Creative brief", "path": "data/samples/keelstone-creative-brief.md"},
]

# ---------------------------------------------------------------------------------------------
# Adoption: every persona against every feature. Same idea as the message scores above: a
# transparent heuristic so the demo has a realistic shape, clearly labeled as not model output.
# ---------------------------------------------------------------------------------------------
FEATURE_THEMES = {
    "F1": {"safety": 1.0, "compliance": 0.4},
    "F2": {"safety": 0.8, "change": 0.2},
    "F3": {"relationship": 1.0, "differentiation": 0.9, "revenue": 0.6, "cost": 0.5},
    "F4": {"cost": 1.0, "roi": 1.0},
    "F5": {"compliance": 1.0, "admin": 0.8},
    "F6": {"privacy": 1.0, "integration": 0.3},
    "F7": {"safety": 0.8, "relationship": 0.6},
    "F8": {"integration": 1.0, "admin": 0.7},
}
ROLE_FEAT = {
    "broker":         {"F1": -2, "F2": -10, "F3": 16, "F4": 4, "F5": -6, "F6": -8, "F7": -8, "F8": -10},
    "cfo":            {"F1": 0, "F2": -10, "F3": 4, "F4": 13, "F5": -2, "F6": -4, "F7": -6, "F8": 2},
    "it_manager":     {"F1": -12, "F2": -6, "F3": -8, "F4": -6, "F5": -6, "F6": 13, "F7": -4, "F8": 4},
    "safety_manager": {"F1": 11, "F2": 8, "F3": -2, "F4": 0, "F5": 10, "F6": 0, "F7": 8, "F8": -6},
    "worker":         {"F1": -12, "F2": 0, "F3": -20, "F4": -20, "F5": -14, "F6": 6, "F7": 7, "F8": -20},
}
SETUP = {"low": 0.0, "medium": 0.5, "high": 1.0}
CAMERA = {"F1": 1.0, "F2": 0.6}
# 12-month adoption relative to 90 days. Below 1 = novelty fades. Above 1 = value compounds.
DURABILITY = {"F1": 1.05, "F2": 0.7, "F3": 1.2, "F4": 1.25, "F5": 1.0, "F6": 1.0, "F7": 0.75, "F8": 1.15}
DURABILITY_ROLE = {("F2", "worker"): 0.55, ("F2", "safety_manager"): 0.85, ("F7", "worker"): 0.6,
                   ("F7", "safety_manager"): 0.95, ("F1", "worker"): 0.9, ("F3", "broker"): 1.25}

NOTES = {
    "F1": {"broker": ("Leading indicators I can take to a carrier. That's new.", "Nice for the client. Doesn't change my renewal conversation yet."),
           "cfo": ("If it prevents one big claim, it pays for itself.", "Cameras flagging things doesn't tell me what it saves."),
           "it_manager": ("Runs on cameras we have, if the gateway passes review.", "AI on our camera network means a security review and more alerts to support."),
           "safety_manager": ("Finally I see the near-misses on sites I can't get to.", "Worried about alert fatigue across every site."),
           "worker": ("If it catches the forklift close calls, good.", "Feels like being watched, whatever they call it.")},
    "F2": {"broker": ("Shows the client is doing something about safety.", "Not something I'd ever look at."),
           "cfo": ("Fine, if it's cheap to run.", "Training videos don't move my numbers."),
           "it_manager": ("Low lift for us if it's in the browser.", "Another app on shared tablets I'll end up supporting."),
           "safety_manager": ("Toolbox talks with our own footage will land better than stock videos.", "Good for a month. Crews tune out by summer."),
           "worker": ("Seeing a real near-miss from our floor hits harder than a slideshow.", "Another safety video. We'll watch it because we have to.")},
    "F3": {"broker": ("This is what makes me different from the broker down the street.", "Carriers have their own models. I'd need to see this move a quote."),
           "cfo": ("Our broker walking in with this at renewal is worth something.", "That's the broker's job, not a reason to buy software."),
           "it_manager": ("Just a report. Fine, if sharing is controlled.", "Our site data going to third parties needs sign-off."),
           "safety_manager": ("Gets safety credit at the renewal table.", "Reports for the insurance side, not for my people."),
           "worker": ("Doesn't affect me.", "Data about us going to the insurance company. No.")},
    "F4": {"broker": ("Helps me talk total cost of risk instead of just premium.", "The client's CFO tool, not mine."),
           "cfo": ("Total cost of risk in one place is exactly what the board asks for.", "Only as good as the data feeding it."),
           "it_manager": ("Read-only dashboard. Easy.", "Depends on the integrations I have to approve."),
           "safety_manager": ("Finally a way to show leadership safety saves money.", "Finance's dashboard. I'll look at it at budget time."),
           "worker": ("Doesn't affect me.", "That's for the bosses.")},
    "F5": {"broker": ("Cleaner logs help at renewal.", "Not my world."),
           "cfo": ("Fewer surprises in an inspection is fine.", "Compliance software, not a cost lever."),
           "it_manager": ("Low risk, mostly forms.", "One more system holding employee incident data."),
           "safety_manager": ("Hours back every month on the 300 log.", "Our current EHS tool already does this."),
           "worker": ("If reporting gets easier, fine.", "Paperwork is paperwork.")},
    "F6": {"broker": ("Answers the privacy question before my client asks it.", "Not my area."),
           "cfo": ("Lowers the legal risk of putting AI on cameras.", "Table stakes, not a reason to buy."),
           "it_manager": ("Edge blurring and 30-day retention gets this through review.", "Policies can change. I'd want it in the contract."),
           "safety_manager": ("Makes the crew conversation much easier.", "Good, but crews won't read a privacy notice."),
           "worker": ("Blurred faces and no discipline in writing. That helps.", "A policy can change the day after we sign off on it.")},
    "F7": {"broker": ("Near-miss volume is a leading indicator I can use.", "Not something I'd see."),
           "cfo": ("Cheap prevention. Fine by me.", "Doesn't show up in any number I track."),
           "it_manager": ("Mobile web, no app store. I can live with that.", "Personal phones on a work system raise questions."),
           "safety_manager": ("Near-misses are the reports I never get.", "Volume drops once the launch push is over."),
           "worker": ("Anonymous matters. I'd actually report the stuff I see.", "People stop reporting when nothing gets fixed.")},
    "F8": {"broker": ("Cleaner claims data helps my submissions.", "Not my problem."),
           "cfo": ("No more spreadsheets from three systems.", "Integration projects always run long."),
           "it_manager": ("Saves the exports I do by hand every month.", "Every integration is something that breaks on the next update."),
           "safety_manager": ("Hours and headcount without chasing HR.", "IT will take months to approve it."),
           "worker": ("Doesn't affect me.", "Doesn't affect me.")},
}


def adoption_row(p, f):
    fid = f["id"]
    themes = FEATURE_THEMES[fid]
    fit = [x["intensity"] * max((themes.get(t, 0) for t in x["tags"]), default=0) for x in p["pains"]]
    align = 0.5 * sum(fit) / sum(x["intensity"] for x in p["pains"]) + 0.5 * max(fit)
    privacy = max([x["intensity"] for x in p["pains"] if "privacy" in x["tags"]] + [0])
    e = 25 + 44 * align + 0.8 * ROLE_FEAT[p["role"]][fid]
    if p["role"] in f["primary_roles"]:
        e += 5
    e -= 10 * (p["skepticism"] - 0.5)
    e -= 14 * SETUP[f["setup_effort"]] * max(0.0, p["change_fatigue"] - 0.4)
    e -= 30 * CAMERA.get(fid, 0) * max(0.0, privacy - 0.4)
    e += rng.gauss(0, 7)
    e = int(max(2, min(98, round(e))))
    import math
    p90 = 0.03 + 0.8 / (1 + math.exp(-(e - 58) / 11))
    p90 *= 1 - 0.3 * SETUP[f["setup_effort"]] * p["change_fatigue"]
    dur = DURABILITY_ROLE.get((fid, p["role"]), DURABILITY[fid])
    p12 = min(0.9, p90 * dur) + rng.gauss(0, 0.04)
    a90 = int(max(1, min(98, round(p90 * 100 + rng.gauss(0, 3)))))
    a12 = int(max(1, min(98, round(p12 * 100))))
    pos, neg = NOTES[fid][p["role"]]
    return {"persona_id": p["id"], "feature_id": fid, "enthusiasm": e, "adopt_90d": a90, "adopt_12m": a12,
            "note": pos if e >= 55 else neg}


ADOPT_SAMPLE = []
for role in market["roles"]:
    pool = [p for p in market["personas"] if p["role"] == role["key"]]
    for lvl in ("High", "Medium", "Low"):
        ADOPT_SAMPLE += [p for p in pool if p["pain_level"] == lvl][: {"High": 4, "Medium": 4, "Low": 4}[lvl]]
adoption = {
    "sample_ids": [p["id"] for p in ADOPT_SAMPLE],
    "rows": [adoption_row(p, f) for p in ADOPT_SAMPLE for f in BRIEF["features"]],
}
# ---------------------------------------------------------------------------------------------
# Competition: the same personas read our message for a feature and each competitor's message for
# the same feature, blind (brand names removed). Competitors are the fictional rivals from the
# Competitive Intel Tracker demo (github.com/jamesallgood99/competitive-intel-tracker).
# Same caveat as above: a transparent heuristic, not model output.
# ---------------------------------------------------------------------------------------------
crng = random.Random(23)

COMPETITORS = [
    {"id": "watchpost", "name": "Watchpost AI",
     "positioning": "Cloud video analytics for safety teams. Leads with breadth of hazard detection and speed to deploy.",
     "source": "Sample copy for a fictional competitor"},
    {"id": "sightwell", "name": "Sightwell",
     "positioning": "Low-cost, self-serve PPE and restricted-zone alerts. Free on three cameras.",
     "source": "Sample copy for a fictional competitor"},
    {"id": "lumenfield", "name": "Lumenfield",
     "positioning": "Serious-injury-and-fatality prevention for enterprises, with consultants on top of the software.",
     "source": "Sample copy for a fictional competitor"},
]

COMP_FEATURES = ["F1", "F2", "F4", "F5", "F6", "F3"]

COMP_MESSAGES = {
    "F1": {
        "ours": "Spot unsafe lifts, slips, missing PPE and forklift near-misses on the cameras you already have, and get alerts your safety team can act on the same shift.",
        "watchpost": "See every hazard on every shift. Watchpost detects more than 40 hazard types, from PPE to vehicle near-misses, and goes live in hours on the cameras you already have.",
        "sightwell": "PPE compliance on autopilot. Start free on three cameras and get hard hat, vest and restricted-zone alerts the same day.",
        "lumenfield": "Prevent serious injuries and fatalities. Lumenfield detects the high-energy hazards behind life-changing incidents, on the cameras you already have.",
    },
    "F2": {
        "ours": "Every week, flagged moments become short coaching clips with faces blurred, ready for your toolbox talk. Coaching, never discipline.",
        "watchpost": "Export any flagged clip in one click and use it in your next safety meeting.",
        "lumenfield": "Every finding goes to former OSHA and EHS leaders, who build your corrective-action plan with you.",
    },
    "F4": {
        "ours": "Premium, claims, reserves and lost workdays in one view, with ROI tracked against your own baseline.",
        "lumenfield": "Our cost model puts a dollar figure on every serious-injury precursor you remove, so finance sees exactly what prevention is worth.",
    },
    "F5": {
        "ours": "OSHA 300, 300A and 301 entries drafted from your incident reports, with an audit trail, so recordkeeping takes minutes instead of days.",
        "lumenfield": "OSHA 300, 300A and 301 logs drafted from every incident and reviewed by our EHS advisors before you file.",
    },
    "F6": {
        "ours": "Faces blurred on site before video leaves the building. Thirty-day retention, SSO and role-based access, and video used for coaching only.",
        "watchpost": "SOC 2 Type II and ISO 27001. Blurring available on request, and video kept for 90 days so nothing gets lost.",
        "lumenfield": "Every face blurred at the edge, by default. SOC 2 Type II, with FedRAMP in process for the most sensitive sites.",
    },
    "F3": {
        "ours": "A renewal-ready report of hazard trends and fixes, so you and your broker walk into renewal with evidence the carrier can use.",
    },
}

# How each message reads: themes it speaks to, role stakes, proof inside the message (0-1), and how
# much it raises video-privacy worries (negative = it reassures).
MSG = {
    ("ours", "F1"): {"themes": {"safety": 1.0, "compliance": 0.4}, "role": {}, "proof": 0.45, "privacy": 0.5},
    ("ours", "F2"): {"themes": {"safety": 0.8, "change": 0.2, "relationship": 0.3}, "role": {"worker": 8}, "proof": 0.4, "privacy": 0.1},
    ("ours", "F3"): {"themes": {"relationship": 1.0, "differentiation": 0.9, "revenue": 0.6, "cost": 0.5}, "role": {}, "proof": 0.4, "privacy": 0.2},
    ("ours", "F4"): {"themes": {"cost": 1.0, "roi": 1.0}, "role": {}, "proof": 0.45, "privacy": 0.0},
    ("ours", "F5"): {"themes": {"compliance": 1.0, "admin": 0.8}, "role": {}, "proof": 0.5, "privacy": 0.0},
    ("ours", "F6"): {"themes": {"privacy": 1.0, "integration": 0.3}, "role": {"it_manager": 4, "worker": 5}, "proof": 0.6, "privacy": -0.6},
    ("watchpost", "F1"): {"themes": {"safety": 1.0, "compliance": 0.5}, "role": {"safety_manager": 3, "it_manager": -3}, "proof": 0.7, "privacy": 0.6},
    ("watchpost", "F2"): {"themes": {"safety": 0.5}, "role": {"worker": -10, "safety_manager": -5}, "proof": 0.2, "privacy": 0.5},
    ("watchpost", "F6"): {"themes": {"privacy": 0.5, "integration": 0.3}, "role": {"it_manager": -2, "worker": -12}, "proof": 0.5, "privacy": 0.35},
    ("sightwell", "F1"): {"themes": {"safety": 0.6, "compliance": 0.9, "cost": 0.6}, "role": {"cfo": 2, "safety_manager": -8, "it_manager": 3}, "proof": 0.4, "privacy": 0.4},
    ("lumenfield", "F1"): {"themes": {"safety": 1.0, "compliance": 0.3}, "role": {"safety_manager": 3, "worker": -3, "cfo": 2}, "proof": 0.45, "privacy": 0.35},
    ("lumenfield", "F2"): {"themes": {"safety": 0.6, "compliance": 0.4}, "role": {"worker": -14, "safety_manager": 1, "cfo": -3}, "proof": 0.5, "privacy": 0.1},
    ("lumenfield", "F4"): {"themes": {"cost": 1.0, "roi": 1.0, "safety": 0.4}, "role": {"cfo": 6, "safety_manager": -4}, "proof": 0.65, "privacy": 0.0},
    ("lumenfield", "F5"): {"themes": {"compliance": 1.0, "admin": 0.5}, "role": {"safety_manager": 1}, "proof": 0.55, "privacy": 0.0},
    ("lumenfield", "F6"): {"themes": {"privacy": 1.0, "integration": 0.4, "compliance": 0.4}, "role": {"it_manager": 12, "worker": -5}, "proof": 0.7, "privacy": -0.55},
}

# Reactions to competitor copy: (positive, negative, objection) per role.
COMP_NOTES = {
    ("watchpost", "F1"): {
        "broker": ("More hazard types is something I can mention to a carrier.", "Detection counts don't change a renewal.", "No link to claims or renewal"),
        "cfo": ("Live in hours means I'm not paying for a long rollout.", "Forty hazard types is a feature list, not a saving.", "No dollar outcome"),
        "it_manager": ("Hours to go live tells me it's not a big install.", "Live in hours means video going to their cloud. Where is it stored?", "Video leaves the building"),
        "safety_manager": ("Forty hazard types out of the box covers a lot more of my sites.", "More detections just means more alerts for my team to clear.", "Alert overload"),
        "worker": ("If it catches the vehicle close calls, good.", "Every hazard on every shift sounds like every move on every shift.", "Feels like constant watching")},
    ("watchpost", "F2"): {
        "broker": ("Fine, clients like safety meetings.", "Not something I'd look at.", "Not relevant to me"),
        "cfo": ("Cheap to use.", "Exporting clips doesn't move any number I track.", "No business outcome"),
        "it_manager": ("Simple export, low support.", "Clips exported to who knows where. That's a data problem.", "Uncontrolled video exports"),
        "safety_manager": ("Handy for the meeting, I guess.", "Exporting clips is my job getting bigger, not easier.", "More work for the safety team"),
        "worker": ("Real footage beats a slideshow.", "So they pull up a clip of you in front of the whole crew.", "Used to call people out")},
    ("watchpost", "F6"): {
        "broker": ("SOC 2 helps the client's legal team.", "Not my area.", "Not relevant to me"),
        "cfo": ("The certifications cover us legally.", "Ninety days of video is ninety days of liability.", "Long video retention"),
        "it_manager": ("SOC 2 and ISO 27001 both. That gets a review started.", "Blurring on request means it's off by default. That fails our review.", "Blurring off by default"),
        "safety_manager": ("Good to have the certifications.", "I'd have to explain to crews why we keep their video for 90 days.", "Hard to explain to crews"),
        "worker": ("At least there's blurring.", "They keep the video 90 days so nothing gets lost. Nothing about us, anyway.", "Keeps video on workers")},
    ("sightwell", "F1"): {
        "broker": ("Cheap way for a client to show they're doing something.", "PPE alerts aren't a risk story.", "Too narrow to matter at renewal"),
        "cfo": ("Free to start. That's an easy yes to try it.", "Free on three cameras means a bill on thirty.", "Cost at full scale unclear"),
        "it_manager": ("Three cameras is a small enough pilot to approve.", "Self-serve means someone plugs it in without asking me.", "Shadow IT risk"),
        "safety_manager": ("Hard hats and vests are an easy win.", "PPE is the easy part. My injuries come from lifts and forklifts.", "Misses the real injury causes"),
        "worker": ("Hard hat reminders are fine.", "Cameras writing you up for a missing vest.", "PPE policing")},
    ("lumenfield", "F1"): {
        "broker": ("Serious injuries drive the big claims. Carriers care about that.", "Not sure it changes my renewal conversation.", "No link to renewal"),
        "cfo": ("One fatality would cost more than anything else we spend on safety.", "Serious incidents are rare here. What about everyday claims?", "Rare events, unclear ROI"),
        "it_manager": ("Works on existing cameras, so a smaller review.", "AI on our camera network means a security review.", "Security review"),
        "safety_manager": ("High-energy hazards are what keep me up at night.", "Most of our claims are strains, not fatalities.", "Misses everyday injuries"),
        "worker": ("If it stops the accidents that kill people, I'm for it.", "Cameras looking for the worst thing that could happen to you.", "Feels like being watched")},
    ("lumenfield", "F2"): {
        "broker": ("Expert-led plans look good to carriers.", "Not my world.", "Not relevant to me"),
        "cfo": ("Expert help is useful.", "Consultants means a services bill every quarter.", "Ongoing consulting cost"),
        "it_manager": ("No new tool for us to run.", "Outside consultants getting our video.", "Third parties with video access"),
        "safety_manager": ("Former OSHA people on my side is real help.", "Consultants write plans. I need my crews to change.", "Doesn't reach the crews"),
        "worker": ("Fine, if they actually fix stuff.", "Consultants we never meet deciding what we did wrong.", "Nothing for the crew")},
    ("lumenfield", "F4"): {
        "broker": ("Dollars per hazard helps me frame cost of risk.", "The CFO's tool, not mine.", "Not relevant to me"),
        "cfo": ("A dollar figure on prevention is the number I've never had.", "A model's dollar figure is only as good as its assumptions.", "Model assumptions"),
        "it_manager": ("Just a report.", "Depends what data it needs from our systems.", "Data it needs"),
        "safety_manager": ("Finally finance sees what my program is worth.", "Putting a price on precursors makes safety a finance exercise.", "Turns safety into a number"),
        "worker": ("Doesn't affect me.", "Pricing our injuries. Great.", "Pricing injuries")},
    ("lumenfield", "F5"): {
        "broker": ("Reviewed logs are cleaner at renewal.", "Not my world.", "Not relevant to me"),
        "cfo": ("Expert review lowers inspection risk.", "Advisors reviewing paperwork sounds billable.", "Extra services cost"),
        "it_manager": ("Mostly forms. Low risk.", "One more vendor holding incident data.", "Incident data with a vendor"),
        "safety_manager": ("A second set of expert eyes before filing is worth having.", "Waiting on advisors slows down filing.", "Slower filing"),
        "worker": ("Fine.", "Paperwork is paperwork.", "Doesn't affect me")},
    ("lumenfield", "F6"): {
        "broker": ("Privacy by default helps my clients' legal teams.", "Not my area.", "Not relevant to me"),
        "cfo": ("Lowers the legal risk.", "Table stakes, not a reason to buy.", "Table stakes"),
        "it_manager": ("Edge blurring by default plus FedRAMP in process. That's a serious security posture.", "FedRAMP 'in process' isn't FedRAMP.", "Certification not finished"),
        "safety_manager": ("Makes the crew conversation easier.", "Crews won't care about FedRAMP.", "Doesn't speak to crews"),
        "worker": ("Faces blurred by default. Good.", "Nothing here says what they won't use the video for.", "No promise against discipline")},
}
OUR_OBJ = {
    "F1": {"broker": "No link to renewal yet", "cfo": "No dollar outcome", "it_manager": "Security review for the gateway", "safety_manager": "Alert fatigue", "worker": "Feels like being watched"},
    "F2": {"broker": "Not relevant to me", "cfo": "No business outcome", "it_manager": "Another app to support", "safety_manager": "Crews tune out", "worker": "Another safety video"},
    "F3": {"broker": "Needs to move a quote", "cfo": "That's the broker's job", "it_manager": "Data shared with third parties", "safety_manager": "Reporting, not prevention", "worker": "Data about workers to insurers"},
    "F4": {"broker": "The CFO's tool", "cfo": "Only as good as the data", "it_manager": "Integrations to approve", "safety_manager": "Finance's dashboard", "worker": "Doesn't affect me"},
    "F5": {"broker": "Not my world", "cfo": "Not a cost lever", "it_manager": "Incident data with a vendor", "safety_manager": "Our EHS tool already does this", "worker": "Paperwork is paperwork"},
    "F6": {"broker": "Not my area", "cfo": "Table stakes", "it_manager": "Wants it in the contract", "safety_manager": "Crews won't read it", "worker": "Policies can change"},
}


def comp_row(p, brand, fid):
    m = MSG[(brand, fid)]
    fit = [x["intensity"] * max((m["themes"].get(t, 0) for t in x["tags"]), default=0) for x in p["pains"]]
    align = 0.5 * sum(fit) / sum(x["intensity"] for x in p["pains"]) + 0.5 * max(fit)
    privacy = max([x["intensity"] for x in p["pains"] if "privacy" in x["tags"]] + [0])
    s = 24 + 46 * align + 0.8 * ROLE_FEAT[p["role"]][fid] + m["role"].get(p["role"], 0)
    s -= 16 * (p["skepticism"] - 0.5) * (1.2 - m["proof"])
    s += 8 * (m["proof"] - 0.5)
    s -= 24 * m["privacy"] * max(0.0, privacy - 0.35)
    if "nothing urgent" in p["trigger"]:
        s -= 6
    s += crng.gauss(0, 6)
    s = int(max(2, min(98, round(s))))
    if brand == "ours":
        pos, neg = NOTES[fid][p["role"]]
        obj = OUR_OBJ[fid][p["role"]]
    else:
        pos, neg, obj = COMP_NOTES[(brand, fid)][p["role"]]
    conf = "high" if s >= 75 or s <= 25 else ("medium" if p["skepticism"] < 0.7 else crng.choice(["medium", "low"]))
    return {"persona_id": p["id"], "score": s, "confidence": conf, "reaction": pos if s >= 55 else neg, "objection": obj}


COMP_SAMPLE = []
for role in market["roles"]:
    pool = [p for p in market["personas"] if p["role"] == role["key"]]
    for lvl, k in (("High", 7), ("Medium", 7), ("Low", 6)):
        COMP_SAMPLE += [p for p in pool if p["pain_level"] == lvl][:k]

competition = {
    "competitors": COMPETITORS,
    "features": COMP_FEATURES,
    "messages": COMP_MESSAGES,
    "sample_ids": [p["id"] for p in COMP_SAMPLE],
    "results": {fid: {brand: [comp_row(p, brand, fid) for p in COMP_SAMPLE] for brand in COMP_MESSAGES[fid]}
                for fid in COMP_FEATURES},
}


stress["claim_id"] = "K2"

demo = {
    "generated_by": "heuristic",
    "note": "Demo data scored by a transparent heuristic in market/make_demo_results.py, not by a language model. Add a Claude API key to run live.",
    "campaign": CAMPAIGN,
    "sample_ids": [p["id"] for p in market["personas"]],
    "results": results,
    "stress": stress,
    "talk": talk,
    "brief": BRIEF,
    "documents": DOCS,
    "adoption": adoption,
    "competition": competition,
}
out = ROOT / "app" / "public" / "data" / "demo" / "q2-launch.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(demo))

from statistics import mean
for vid, rows in results.items():
    by_role = {}
    for r in rows:
        by_role.setdefault(by_id[r["persona_id"]]["role"], []).append(r["score"])
    print(vid, "mean", round(mean(r["score"] for r in rows)), "P>70", round(sum(r["score"] > 70 for r in rows) / len(rows), 2),
          {k: round(mean(v)) for k, v in by_role.items()})

from collections import defaultdict
agg = defaultdict(list)
for r in adoption["rows"]:
    agg[(r["feature_id"], by_id[r["persona_id"]]["role"])].append(r)
print("adoption sample", len(ADOPT_SAMPLE))
for f in BRIEF["features"]:
    line = []
    for role in [r["key"] for r in market["roles"]]:
        rs = agg[(f["id"], role)]
        line.append(f'{role[:6]} {round(mean(x["enthusiasm"] for x in rs))}/{round(mean(x["adopt_90d"] for x in rs))}->{round(mean(x["adopt_12m"] for x in rs))}')
    print(f["short"].ljust(18), " | ".join(line))

feat_by_id = {f["id"]: f for f in BRIEF["features"]}
print("competition sample", len(COMP_SAMPLE))
for fid in COMP_FEATURES:
    prim = feat_by_id[fid]["primary_roles"]
    for brand, rows in competition["results"][fid].items():
        by_role = defaultdict(list)
        for r in rows:
            by_role[by_id[r["persona_id"]]["role"]].append(r["score"])
        main = [s for k, v in by_role.items() if k in prim for s in v]
        print(fid, brand.ljust(10), "main", round(mean(main)), "all", round(mean(r["score"] for r in rows)),
              " ".join(f"{k[:6]}={round(mean(v))}" for k, v in by_role.items()))
