"""Taeglicher DNADiet-Tracker – Einstiegspunkt der GitHub Action.

Liest das Genotyp-Profil (oder ein Demo-Profil), berechnet Ranking, Supplemente
und Anpassungen, rotiert 'Gericht des Tages' + 'Fokus-Gen des Tages' deterministisch
nach Datum und schreibt Report + README-Dashboard + History.
"""
from __future__ import annotations

import argparse
import copy
import csv
import datetime as dt
import os

from . import panel as P
from . import report as R
from .analysis import build_analysis

ROOT = P.ROOT
REPORTS_DIR = os.path.join(ROOT, "reports")
DAILY_DIR = os.path.join(REPORTS_DIR, "daily")
HISTORY = os.path.join(REPORTS_DIR, "history.csv")


def _load_profile(explicit_path=None):
    """Gibt (profile, demo:bool) zurueck."""
    prof = P.load_profile(explicit_path)
    if prof:
        prof.setdefault("_demo", False)
        return prof, False
    demo = P.load_example_profile()
    demo["_demo"] = True
    return demo, True


def _pick_dish_of_day(ranking, day_ord):
    pool = [r for r in ranking if r["rank"] <= min(6, len(ranking))] or ranking
    return pool[day_ord % len(pool)]


def _pick_focus(analysis, day_ord):
    # Nur "spotlight"-faehige Befunde (keine LD-Proxy/bestaetigenden SNPs)
    cands = [f for f in analysis["notable_findings"] if f.get("spotlight", True)]
    if not cands:
        cands = [f for f in analysis["findings"]
                 if f.get("n_effect") is not None and f.get("spotlight", True)]
    if not cands:
        return None
    return cands[day_ord % len(cands)]


def _redact(analysis):
    a = copy.deepcopy(analysis)
    for f in a["findings"] + a["notable_findings"]:
        f["genotype_str"] = "•••"
    if a.get("apoe"):
        a["apoe"]["genotype_str"] = "•••"
    return a


def _read_history():
    if not os.path.exists(HISTORY):
        return []
    with open(HISTORY, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _append_history(row, fieldnames):
    exists = os.path.exists(HISTORY)
    os.makedirs(REPORTS_DIR, exist_ok=True)
    with open(HISTORY, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        if not exists:
            w.writeheader()
        w.writerow(row)


def run(date_str=None, profile_path=None, redact=False, quiet=False):
    if date_str is None:
        date_str = os.environ.get("DNADIET_DATE") or dt.date.today().isoformat()
    date_obj = dt.date.fromisoformat(date_str)
    day_ord = date_obj.toordinal()

    panel = P.load_panel()
    recipes = P.load_recipes()
    profile, demo = _load_profile(profile_path)

    analysis = build_analysis(panel, recipes, profile)
    analysis["profile_meta"]["demo"] = demo

    history = _read_history()
    streak = len({h["date"] for h in history} | {date_str})

    dish = _pick_dish_of_day(analysis["recipe_ranking"], day_ord)
    focus = _pick_focus(analysis, day_ord)

    render_src = _redact(analysis) if redact else analysis
    # dish/focus aus derselben (ggf. redaktierten) Quelle beziehen
    if redact and focus:
        focus = _pick_focus(render_src, day_ord)

    md = R.render_daily(render_src, date_str, dish, focus, streak=streak)

    os.makedirs(DAILY_DIR, exist_ok=True)
    daily_path = os.path.join(DAILY_DIR, f"{date_str}.md")
    with open(daily_path, "w", encoding="utf-8") as f:
        f.write(md)
    with open(os.path.join(REPORTS_DIR, "latest.md"), "w", encoding="utf-8") as f:
        f.write(md)

    # README-Dashboard aktualisieren
    readme_path = os.path.join(ROOT, "README.md")
    report_link = f"reports/daily/{date_str}.md"
    block = R.render_dashboard_block(render_src, date_str, dish, focus, report_link)
    try:
        with open(readme_path, "r", encoding="utf-8") as f:
            readme = f.read()
    except FileNotFoundError:
        readme = "# DNADiet\n"
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(R.update_readme(readme, block))

    # History
    _append_history({
        "date": date_str,
        "sample": analysis["profile_meta"].get("sample_id") or "",
        "demo": demo,
        "dish_of_day_id": dish["id"],
        "dish_of_day_title": dish["title"],
        "dish_of_day_fit": dish["fit"],
        "focus_gene": (focus or {}).get("gene", ""),
        "focus_rsid": (focus or {}).get("key", ""),
        "top1_title": analysis["recipe_ranking"][0]["title"],
    }, fieldnames=["date", "sample", "demo", "dish_of_day_id", "dish_of_day_title",
                   "dish_of_day_fit", "focus_gene", "focus_rsid", "top1_title"])

    if not quiet:
        print(f"[DNADiet] {date_str}  demo={demo}  "
              f"Gericht des Tages: {dish['title']} (Fit {dish['fit']})  "
              f"Fokus: {(focus or {}).get('gene','-')}")
        print(f"[DNADiet] Report: {daily_path}")
    return {"date": date_str, "demo": demo, "dish": dish, "focus": focus,
            "report_path": daily_path, "analysis": analysis}


def main(argv=None):
    ap = argparse.ArgumentParser(description="DNADiet taeglicher Tracker")
    ap.add_argument("--date", help="Datum ISO (YYYY-MM-DD), Standard: heute")
    ap.add_argument("--profile", help="Pfad zu profile.json (ueberschreibt Auto-Erkennung)")
    ap.add_argument("--redact", action="store_true",
                    help="Rohe Genotypen im Report maskieren (fuer oeffentliche Repos)")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)
    redact = args.redact or os.environ.get("DNADIET_REDACT") == "1"
    run(date_str=args.date, profile_path=args.profile, redact=redact, quiet=args.quiet)


if __name__ == "__main__":
    main()
