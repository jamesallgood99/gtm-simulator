#!/usr/bin/env python3
"""
Generate a synthetic market: N fictional companies, one persona per role at each
company, and 3-5 pain points for every persona. Each persona gets their role's core pains, one pain
specific to their role in their industry, and optional role pains up to the configured count.

    python market/generate_market.py                       # uses config.example.json
    python market/generate_market.py --config my_icp.json  # your own market

Writes:
    market/output/market.json     full market (companies + personas), used by the skill
    market/output/personas.csv    flat persona table, easy to open in a spreadsheet
    market/output/companies.csv   company table
    app/public/data/market.json   copy the dashboard loads

Only uses the Python standard library. Every name and company is invented.
"""
import argparse
import csv
import json
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

FIRST = [
    "Maria", "James", "Aisha", "Wei", "Carlos", "Priya", "Derek", "Fatima", "Tom", "Yuki",
    "Luis", "Grace", "Andre", "Nina", "Omar", "Rachel", "Kofi", "Elena", "Sam", "Hana",
    "Marcus", "Leah", "Raj", "Sofia", "Dmitri", "Tasha", "Ben", "Mei", "Victor", "Alana",
    "Jorge", "Keisha", "Ethan", "Rosa", "Imran", "Claire", "Tyrone", "Ingrid", "Paulo", "Dana",
    "Hector", "Joy", "Kenji", "Amara", "Frank", "Lucia", "Nate", "Zainab", "Owen", "Beatriz",
]
LAST = [
    "Okafor", "Nguyen", "Ramirez", "Patel", "Kowalski", "Haddad", "Brennan", "Tanaka", "Silva",
    "Johnson", "Cho", "Mensah", "Lindqvist", "Morales", "Fischer", "Abbott", "Reyes", "Sato",
    "Delgado", "Murphy", "Ahmed", "Novak", "Castillo", "Walsh", "Iyer", "Duarte", "Hughes",
    "Banerjee", "Ortiz", "Kim", "Petrov", "Greene", "Alvarez", "Yamamoto", "Osei", "Romero",
    "Becker", "Chavez", "Lund", "Torres",
]
NAME_A = ["Gran", "Hal", "Mer", "Cobal", "Red", "Iron", "Stone", "Ash", "Brid", "Corv",
          "Tal", "Wex", "Lan", "Mar", "Pell", "Quin", "Rook", "Sab", "Thorn", "Vell"]
NAME_B = ["ford", "wick", "ridge", "ton", "dale", "brook", "mere", "haven", "field", "crest",
          "point", "gate", "well", "stead", "vale"]
SUFFIX = {
    "Construction": ["Builders", "Construction", "Contracting", "Civil"],
    "Manufacturing": ["Manufacturing", "Fabrication", "Industries", "Components"],
    "Warehousing & logistics": ["Logistics", "Distribution", "Fulfillment", "Freight"],
    "Healthcare & senior living": ["Senior Living", "Health", "Care Communities", "Home Health"],
    "Transportation": ["Transport", "Trucking", "Transit", "Carriers"],
    "Agriculture & food processing": ["Farms", "Foods", "Packing", "Growers"],
    "Hospitality": ["Hospitality", "Hotels", "Resorts", "Restaurant Group"],
    "Retail": ["Retail", "Stores", "Supply", "Outfitters"],
}
REGIONS = ["West", "Southwest", "Midwest", "Southeast", "Northeast", "Mountain"]
SIZE_RANGES = {"50-200": (50, 200), "200-1,000": (200, 1000), "1,000-5,000": (1000, 5000)}


def weighted_pick(rng, mix):
    keys, weights = zip(*mix.items())
    return rng.choices(keys, weights=weights, k=1)[0]


def allocate(mix, n):
    """Split n items across a weighted mix so the counts match the weights (largest remainder)."""
    total = sum(mix.values())
    raw = {k: n * w / total for k, w in mix.items()}
    counts = {k: math.floor(v) for k, v in raw.items()}
    leftover = n - sum(counts.values())
    for k in sorted(raw, key=lambda k: raw[k] - counts[k], reverse=True)[:leftover]:
        counts[k] += 1
    return counts


def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def company_name(rng, industry, used):
    while True:
        name = f"{rng.choice(NAME_A)}{rng.choice(NAME_B)} {rng.choice(SUFFIX.get(industry, ['Group']))}"
        if name not in used:
            used.add(name)
            return name


def pain_score(pains):
    """Overall pain = mean intensity of the persona's three strongest pain points."""
    vals = sorted((x["intensity"] for x in pains), reverse=True)[:3]
    return sum(vals) / len(vals)


def assign_pain_levels(personas, high_share=0.35, low_share=0.25):
    """Pain level is relative to this market: top 35% High, bottom 25% Low, rest Medium."""
    ranked = sorted(personas, key=lambda p: p["pain_score"])
    n = len(ranked)
    for i, p in enumerate(ranked):
        p["pain_level"] = "Low" if i < n * low_share else "High" if i >= n * (1 - high_share) else "Medium"


def pick_pains(rng, role, industry_pain, heat, lo_hi):
    """Core role pains always apply. Add the industry-specific pain, then fill from the optional
    role pains until the persona has between lo and hi pain points."""
    lo, hi = lo_hi
    chosen = [dict(p, source="role") for p in role.get("core_pains", [])]
    if industry_pain:
        chosen.append(dict(industry_pain, key="industry_" + role["key"], source="industry", weight=0.75))
    target = max(lo, min(hi, rng.randint(lo, hi)))
    optional = list(role.get("optional_pains", []))
    rng.shuffle(optional)
    while len(chosen) < target and optional:
        chosen.append(dict(optional.pop(), source="role"))
    chosen = chosen[:hi]
    out = []
    for p in chosen:
        intensity = clamp(p.get("weight", 0.7) * 0.85 + heat * 0.45 + rng.gauss(0, 0.12), 0.05, 0.98)
        out.append({
            "key": p["key"],
            "label": p["label"],
            "description": p["description"],
            "tags": p.get("tags", []),
            "source": p["source"],
            "intensity": round(intensity, 2),
        })
    out.sort(key=lambda x: x["intensity"], reverse=True)
    return out


def build(config):
    rng = random.Random(config.get("seed", 42))
    n = config["n_companies"]
    lo_hi = tuple(config.get("pains_per_persona", [3, 5]))

    industries = [k for k, c in allocate(config["industry_mix"], n).items() for _ in range(c)]
    sizes = [k for k, c in allocate(config["size_mix"], n).items() for _ in range(c)]
    rng.shuffle(industries)
    rng.shuffle(sizes)

    used_names, used_people = set(), set()
    companies, personas = [], []
    for i in range(n):
        industry, size = industries[i], sizes[i]
        lo, hi = SIZE_RANGES.get(size, (100, 1000))
        trigger = rng.choice(config["triggers"])
        # Company-level "heat": some companies are in pain, some are fine.
        heat = rng.betavariate(2.2, 2.2) - 0.5  # -0.5..0.5, centered
        if "nothing urgent" in trigger:
            heat -= 0.2
        company = {
            "id": f"C{i + 1:03d}",
            "name": company_name(rng, industry, used_names),
            "industry": industry,
            "size_band": size,
            "employees": int(rng.uniform(lo, hi) // 10 * 10),
            "region": rng.choice(REGIONS),
            "trigger": trigger,
        }
        companies.append(company)

        for role in config["roles"]:
            while True:
                full = f"{rng.choice(FIRST)} {rng.choice(LAST)}"
                if full not in used_people:
                    used_people.add(full)
                    break
            industry_pain = config.get("industry_pains", {}).get(industry, {}).get(role["key"])
            pains = pick_pains(rng, role, industry_pain, heat, lo_hi)
            personas.append({
                "id": f"{company['id']}-{role['key']}",
                "company_id": company["id"],
                "company": company["name"],
                "industry": industry,
                "size_band": size,
                "name": full,
                "role": role["key"],
                "role_label": role["label"],
                "title": rng.choice(role["titles"]),
                "buying_role": role["buying_role"],
                "years_in_role": rng.randint(1, 18),
                "skepticism": round(clamp(role["skepticism"] + rng.gauss(0, 0.12), 0.05, 0.95), 2),
                "change_fatigue": round(clamp(role.get("change_fatigue", 0.5) - heat * 0.2 + rng.gauss(0, 0.12), 0.05, 0.95), 2),
                "pains": pains,
                "pain_level": None,
                "pain_score": round(pain_score(pains), 2),
                "trigger": trigger,
                "context": role.get("context", ""),
            })
    assign_pain_levels(personas)
    return {
        "market_name": config["market_name"],
        "product_category": config["product_category"],
        "description": config.get("description", ""),
        "seed": config.get("seed", 42),
        "themes": config.get("themes", {}),
        "roles": [{k: r[k] for k in ("key", "label", "buying_role")} for r in config["roles"]],
        "companies": companies,
        "personas": personas,
    }


def write_outputs(market, outdir):
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "market.json").write_text(json.dumps(market, indent=1))
    with open(outdir / "personas.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "name", "title", "role", "company", "industry", "size_band", "buying_role",
                    "years_in_role", "skepticism", "change_fatigue", "pain_level",
                    "pain_1", "pain_2", "pain_3", "pain_4", "pain_5", "trigger"])
        for p in market["personas"]:
            pains = [f"{x['label']} ({x['intensity']})" for x in p["pains"]] + [""] * 5
            w.writerow([p["id"], p["name"], p["title"], p["role_label"], p["company"], p["industry"],
                        p["size_band"], p["buying_role"], p["years_in_role"], p["skepticism"],
                        p["change_fatigue"], p["pain_level"], *pains[:5], p["trigger"]])
    with open(outdir / "companies.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "name", "industry", "size_band", "employees", "region", "trigger"])
        for c in market["companies"]:
            w.writerow([c[k] for k in ("id", "name", "industry", "size_band", "employees", "region", "trigger")])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default=str(ROOT / "market" / "config.example.json"))
    ap.add_argument("--out", default=str(ROOT / "market" / "output"))
    ap.add_argument("--no-app-copy", action="store_true", help="don't copy market.json into the dashboard")
    args = ap.parse_args()

    market = build(json.loads(Path(args.config).read_text()))
    write_outputs(market, Path(args.out))
    if not args.no_app_copy:
        app_data = ROOT / "app" / "public" / "data"
        app_data.mkdir(parents=True, exist_ok=True)
        (app_data / "market.json").write_text(json.dumps(market))

    from collections import Counter
    print(f"{market['market_name']}: {len(market['companies'])} companies, {len(market['personas'])} personas")
    print("Pain levels:", dict(Counter(p["pain_level"] for p in market["personas"])))
    print("Industries:", dict(Counter(c["industry"] for c in market["companies"])))


if __name__ == "__main__":
    main()
