"""Kern-Engine: Genotyp + Panel + Rezepte -> Ranking, Supplemente, Anpassungen.

Arbeitet ausschliesslich auf rsID + Genotyp (keine Koordinaten noetig).
"""
from __future__ import annotations

from typing import Optional

from .panel import (
    LEVEL_ORD,
    PRIORITY_ORD,
    alleles_of,
    count_effect_alleles,
    genotype_entry,
    genotype_string,
)

# --------------------------------------------------------------------------
# Vorschlaege fuer Rezept-Anpassungen, wenn ein Gericht bei einer aktiven
# genetischen Regel ungünstig abschneidet. Schluessel: (tag, prefer).
# --------------------------------------------------------------------------
MOD_TEMPLATES = {
    ("saturated_fat", "low"): "Gesaettigtes Fett senken: Kokosmilch durch ungesuesste Soja-/Hafermilch ersetzen, Oelmenge reduzieren.",
    ("added_sugar", "low"): "Zugesetzten Zucker weglassen oder halbieren (Ahornsirup, Honig, gesuesste Cranberries; Ketchup ohne Zucker).",
    ("glycemic_load", "low"): "Glykaemische Last senken: staerkereiche Anteile (z.B. Suesskartoffel) reduzieren, mehr nicht-staerkiges Gemuese/Blattgruen; Cauliflower-/Chickpea-Rice bevorzugen.",
    ("iron_nonheme", "low"): "Eisenaufnahme bremsen: eisenreiche Huelsenfruechte moderat portionieren und Vitamin-C-Quellen zeitlich trennen; Kaffee/Tee zur Mahlzeit hemmt die Aufnahme.",
    ("vitamin_c", "low"): "Vitamin-C-reiche Zutaten nicht gezielt mit den eisenreichsten Komponenten kombinieren (nur bei HFE-Eisenueberladung relevant).",
    ("caffeine_theobromine", "low"): "Kakao/Koffein reduzieren oder frueher am Tag geniessen.",
    ("folate", "high"): "Folat erhoehen: eine Portion Linsen, Kichererbsen oder Spinat ergaenzen.",
    ("omega3_ala", "high"): "Pflanzliches Omega-3 ergaenzen: 1 EL gemahlenen Leinsamen/Chia oder Walnuesse zufuegen (zusaetzlich Algenoel fuer EPA/DHA).",
    ("beta_carotene", "high"): "Mehr Carotinoide: Karotte/Suesskartoffel/Kuerbis/rote Paprika ergaenzen – mit etwas Oel fuer bessere Aufnahme.",
    ("fiber", "high"): "Ballaststoffe erhoehen: Huelsenfruechte, Gemuese oder Samen ergaenzen.",
    ("legume_protein", "high"): "Saettigendes Protein: eine Portion Linsen/Kichererbsen/Bohnen zufuegen.",
    ("antioxidants", "high"): "Antioxidantien erhoehen: Beeren, Granatapfel, frische Kraeuter oder etwas Kakao ergaenzen.",
}


def when_matches(cond: str, n: Optional[int]) -> bool:
    """Prueft Bedingungen wie '>=1', '>=2', '==0', '==1', '==2' gegen n."""
    if n is None:
        return False
    cond = cond.strip()
    for op in (">=", "<=", "==", ">", "<"):
        if cond.startswith(op):
            val = int(cond[len(op):])
            if op == ">=":
                return n >= val
            if op == "<=":
                return n <= val
            if op == "==":
                return n == val
            if op == ">":
                return n > val
            if op == "<":
                return n < val
    return False


# --------------------------------------------------------------------------
# APOE: Diplotyp aus rs429358 (ref T / alt C) + rs7412 (ref C / alt T).
# --------------------------------------------------------------------------
_APOE_TABLE = {
    (0, 0): "E3/E3",
    (0, 1): "E2/E3",
    (0, 2): "E2/E2",
    (1, 0): "E3/E4",
    (2, 0): "E4/E4",
    (1, 1): "E2/E4",
    (2, 1): "E1/E4 (selten)",
    (1, 2): "E1/E2 (selten)",
    (2, 2): "E1/E1 (selten)",
}


def apoe_diplotype(al429: Optional[list], al7412: Optional[list]) -> Optional[str]:
    if not al429 or not al7412:
        return None
    c = sum(1 for a in al429 if a and a.upper() == "C")
    t = sum(1 for a in al7412 if a and a.upper() == "T")
    return _APOE_TABLE.get((c, t), "unklar")


def _apoe_finding(profile: dict) -> Optional[dict]:
    e429 = genotype_entry(profile, "rs429358")
    e7412 = genotype_entry(profile, "rs7412")
    al429 = alleles_of(e429)
    al7412 = alleles_of(e7412)
    dip = apoe_diplotype(al429, al7412)
    if dip is None:
        return None
    n_e4 = dip.count("4")
    n_e2 = dip.count("2")
    diet_rules: list = []
    supp_rules: list = []
    exp_rules: list = []
    if n_e4 >= 1:
        label = ("APOE-e4-Traeger: erhoehte Empfindlichkeit gegenueber gesaettigtem Fett, "
                 "tendenziell hoeheres LDL/kardiovaskulaeres Risiko.")
        diet_rules = [
            {"when": ">=0", "tag": "saturated_fat", "prefer": "low", "weight": 3,
             "rationale": "APOE-e4 reagiert unguenstig auf gesaettigtes Fett – Kokosmilch & Co. gering halten."},
            {"when": ">=0", "tag": "antioxidants", "prefer": "high", "weight": 1,
             "rationale": "Polyphenolreiche, mediterran gepraegte Kost ist bei e4 guenstig."},
            {"when": ">=0", "tag": "fiber", "prefer": "high", "weight": 1,
             "rationale": "Ballaststoffe unterstuetzen ein guenstiges Lipidprofil."},
        ]
        supp_rules = [
            {"when": ">=0", "supplement": "Algenoel (DHA/EPA)", "priority": "hoch",
             "rationale": "Marine Omega-3 wirken kardioprotektiv – bei e4 besonders sinnvoll.", "diet_context": ["vegan"]},
        ]
        exp_rules = [
            {"when": ">=0", "tip": "APOE-e4: gesaettigte Fette (Kokosmilch, viel Oel) bewusst niedrig halten, "
                                   "Schwerpunkt auf ungesaettigte Fette (Oliven, Nuesse, Algenoel)."},
        ]
    elif n_e2 >= 1:
        label = ("APOE-e2-Traeger: meist guenstigeres LDL, aber Neigung zu hoeheren Triglyzeriden; "
                 "raffinierte Kohlenhydrate/Zucker eher gering halten.")
        diet_rules = [
            {"when": ">=0", "tag": "glycemic_load", "prefer": "low", "weight": 1,
             "rationale": "Bei e2 profitieren Triglyzeride von niedriger glykaemischer Last."},
            {"when": ">=0", "tag": "added_sugar", "prefer": "low", "weight": 1,
             "rationale": "Zugesetzten Zucker gering halten (Triglyzeride)."},
        ]
    else:
        label = "APOE-e3/e3: haeufigster Genotyp, neutrale Fettstoffwechsel-Antwort."

    return {
        "key": "APOE",
        "gene": "APOE",
        "trait": "APOE-Isoform (Fettstoffwechsel)",
        "category": "lipide",
        "spotlight": True,
        "genotype_str": dip,
        "n_effect": n_e4,
        "dosage_label": label,
        "notable": (n_e4 >= 1 or n_e2 >= 1),
        "confidence": "hoch",
        "effect_summary": "APOE bestimmt die Reaktion auf Nahrungsfette; e4 = fett-/cholesterinsensitiv, e2 = triglyzeridsensitiv.",
        "diet_rules": diet_rules,
        "supplement_rules": supp_rules,
        "experience_rules": exp_rules,
    }


# --------------------------------------------------------------------------
# Findings aus dem Panel bauen (Regeln bereits nach Genotyp gefiltert).
# --------------------------------------------------------------------------
def build_findings(panel: dict, profile: dict) -> list:
    findings = []
    for snp in panel.get("snps", []):
        if snp.get("apoe_component"):
            continue  # in _apoe_finding zusammengefasst
        rsid = snp["rsid"]
        entry = genotype_entry(profile, rsid)
        n = count_effect_alleles(snp["effect_allele"], entry)
        gt = genotype_string(entry)
        dosage_label = snp.get("dosage", {}).get(str(n)) if n is not None else "kein Call in der VCF"
        active_diet = [r for r in snp.get("diet_rules", []) if when_matches(r["when"], n)]
        active_supp = [r for r in snp.get("supplement_rules", []) if when_matches(r["when"], n)]
        active_exp = [r for r in snp.get("experience_rules", []) if when_matches(r["when"], n)]
        findings.append({
            "key": rsid,
            "gene": snp["gene"],
            "trait": snp["trait"],
            "category": snp.get("category", ""),
            "spotlight": snp.get("spotlight", True),
            "genotype_str": gt,
            "n_effect": n,
            "effect_allele": snp["effect_allele"],
            "dosage_label": dosage_label,
            "notable": (n is not None and n >= 1),
            "confidence": snp.get("confidence", ""),
            "effect_summary": snp.get("effect_summary", ""),
            "call_source": (entry or {}).get("source"),
            "call_confidence": (entry or {}).get("confidence"),
            "diet_rules": active_diet,
            "supplement_rules": active_supp,
            "experience_rules": active_exp,
        })

    apoe = _apoe_finding(profile)
    if apoe:
        findings.append(apoe)
    return findings


# --------------------------------------------------------------------------
# Rezept-Bewertung.
# --------------------------------------------------------------------------
def _score_recipe(recipe: dict, active_rules: list):
    tags = recipe.get("tags", {})
    bools = recipe.get("booleans", {})
    score = 0.0
    drivers = []
    for r in active_rules:
        tag = r["tag"]
        prefer = r["prefer"]
        w = float(r.get("weight", 1))
        if prefer in ("low", "high"):
            v = LEVEL_ORD.get(tags.get(tag, "none"), 0)
            centered = (v - 1.5) / 1.5  # none->-1 .. high->+1
            s = centered if prefer == "high" else -centered
            contrib = w * s
        else:  # boolean, prefer True
            contrib = w * (0.5 if bool(bools.get(tag, False)) else -0.5)
        score += contrib
        if abs(contrib) >= 0.5:
            drivers.append({
                "gene": r.get("_gene", ""), "key": r.get("_key", ""),
                "tag": tag, "prefer": prefer, "contrib": round(contrib, 2),
                "positive": contrib > 0, "rationale": r.get("rationale", ""),
            })
    drivers.sort(key=lambda d: -abs(d["contrib"]))
    return score, drivers


def _modifications(recipe: dict, active_rules: list) -> list:
    tags = recipe.get("tags", {})
    mods = []
    seen = set()
    for r in active_rules:
        tag, prefer = r["tag"], r["prefer"]
        if prefer not in ("low", "high"):
            continue
        v = LEVEL_ORD.get(tags.get(tag, "none"), 0)
        adverse = (prefer == "low" and v >= 2) or (prefer == "high" and v <= 1)
        if not adverse:
            continue
        tmpl = MOD_TEMPLATES.get((tag, prefer))
        if tmpl and tmpl not in seen:
            seen.add(tmpl)
            mods.append({"text": tmpl, "gene": r.get("_gene", "")})
    return mods


def rank_recipes(findings: list, recipes: list) -> list:
    active_rules = []
    for f in findings:
        for r in f.get("diet_rules", []):
            rr = dict(r)
            rr["_gene"] = f["gene"]
            rr["_key"] = f["key"]
            active_rules.append(rr)

    rows = []
    for rec in recipes:
        score, drivers = _score_recipe(rec, active_rules)
        mods = _modifications(rec, active_rules)
        rows.append({
            "id": rec["id"], "title": rec["title"], "score": score,
            "drivers": drivers, "modifications": mods,
            "tags": rec.get("tags", {}), "booleans": rec.get("booleans", {}),
        })

    scores = [r["score"] for r in rows]
    lo, hi = (min(scores), max(scores)) if scores else (0, 0)
    for r in rows:
        if hi > lo:
            r["fit"] = round(100 * (r["score"] - lo) / (hi - lo))
        else:
            r["fit"] = 50  # keine genotypbedingten Praeferenzen -> neutral
    rows.sort(key=lambda r: (-r["score"], r["id"]))
    for i, r in enumerate(rows, 1):
        r["rank"] = i
    return rows


# --------------------------------------------------------------------------
# Supplement-Plan: Basis (vegan) + DNA-spezifisch.
# --------------------------------------------------------------------------
def supplement_plan(panel: dict, findings: list) -> dict:
    baseline = list(panel.get("diet_baseline", {}).get("supplements", []))

    dna_map: dict = {}
    for f in findings:
        for r in f.get("supplement_rules", []):
            name = r["supplement"]
            entry = dna_map.setdefault(name, {
                "supplement": name, "priority": r.get("priority", "mittel"),
                "genes": [], "rationales": [],
            })
            if PRIORITY_ORD.get(r.get("priority", "mittel"), 2) > PRIORITY_ORD.get(entry["priority"], 2):
                entry["priority"] = r["priority"]
            if f["gene"] not in entry["genes"]:
                entry["genes"].append(f["gene"])
            if r.get("rationale") and r["rationale"] not in entry["rationales"]:
                entry["rationales"].append(r["rationale"])

    dna = sorted(dna_map.values(),
                 key=lambda e: (-PRIORITY_ORD.get(e["priority"], 2), e["supplement"]))
    return {"baseline": baseline, "dna": dna}


# --------------------------------------------------------------------------
# Gesamtanalyse.
# --------------------------------------------------------------------------
def build_analysis(panel: dict, recipes: list, profile: dict) -> dict:
    findings = build_findings(panel, profile)
    ranking = rank_recipes(findings, recipes)
    supplements = supplement_plan(panel, findings)

    global_tips = []
    for f in findings:
        for r in f.get("experience_rules", []):
            tip = r.get("tip")
            if tip and tip not in global_tips:
                global_tips.append(tip)

    notable = [f for f in findings if f.get("notable")]

    genotypes = (profile or {}).get("genotypes", {})
    n_calls = sum(1 for v in genotypes.values() if alleles_of(v))
    n_low = sum(1 for v in genotypes.values()
                if (v.get("confidence") == "niedrig" or v.get("source") == "assumed-ref"))

    apoe = next((f for f in findings if f["key"] == "APOE"), None)

    return {
        "profile_meta": {
            "sample_id": (profile or {}).get("sample_id"),
            "assembly": (profile or {}).get("assembly"),
            "source": (profile or {}).get("source"),
            "demo": bool((profile or {}).get("_demo")),
            "panel_snps": len(panel.get("snps", [])),
            "n_calls": n_calls,
            "n_low_confidence": n_low,
        },
        "findings": findings,
        "notable_findings": notable,
        "recipe_ranking": ranking,
        "supplements": supplements,
        "global_tips": global_tips,
        "apoe": apoe,
    }
