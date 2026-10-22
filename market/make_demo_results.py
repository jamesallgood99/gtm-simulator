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
    "product": "An AI-powered workplace safety platform for employers in high-injury industries. It uses existing site cameras to flag unsafe movements and hazards, turns them into coaching and safety reports, and shares the risk data with the employer's broker and carrier to support better workers' comp pricing at renewal.",
    "variants": [
        {"id": "A", "name": "Variant A", "headline": "Lower your workers' comp premium.",
         "message": "Lower your workers' comp premium. Our AI finds the risks driving your claims so you can bring your experience mod down before renewal.",
         "focus": "Cost and premium reduction"},
        {"id": "B", "name": "Variant B", "headline": "Fewer injuries. Fewer claims.",
         "message": "Fewer injuries. Fewer claims. AI watches for unsafe lifts, falls and near-misses on your existing cameras, so your safety team can coach before someone gets hurt.",
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
SURVEILLANCE = {"A": 0.2, "B": 1.0, "C": 0.45}

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

demo = {
    "generated_by": "heuristic",
    "note": "Demo data scored by a transparent heuristic in market/make_demo_results.py, not by a language model. Add a Claude API key to run live.",
    "campaign": CAMPAIGN,
    "sample_ids": [p["id"] for p in market["personas"]],
    "results": results,
    "stress": stress,
    "talk": talk,
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
