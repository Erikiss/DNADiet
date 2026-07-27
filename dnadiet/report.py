"""Rendert den taeglichen Markdown-Report und den README-Dashboard-Block."""
from __future__ import annotations

from typing import Optional

DASHBOARD_START = "<!-- DNADIET:START -->"
DASHBOARD_END = "<!-- DNADIET:END -->"

DISCLAIMER = (
    "> **Hinweis:** Diese Auswertung dient ausschliesslich Informations- und "
    "Bildungszwecken und ist **keine medizinische Beratung, Diagnose oder "
    "Therapieempfehlung**. Genvarianten sind nur ein Faktor unter vielen; Effekte "
    "sind meist klein und populationsabhaengig. Vor Aenderungen an Ernaehrung oder "
    "Supplementen bitte aerztlichen/ernaehrungsmedizinischen Rat einholen. "
    "Ein positiver Gentest ist keine Diagnose."
)


def _table(headers, rows) -> str:
    out = ["| " + " | ".join(headers) + " |",
           "| " + " | ".join(["---"] * len(headers)) + " |"]
    for r in rows:
        out.append("| " + " | ".join(str(c) for c in r) + " |")
    return "\n".join(out)


def _fit_bar(fit: int) -> str:
    filled = round(fit / 10)
    return "█" * filled + "░" * (10 - filled)


def _driver_summary(drivers, positive=True, limit=2):
    picked = [d for d in drivers if d["positive"] == positive][:limit]
    return "; ".join(f"{d['gene']}: {d['rationale']}" for d in picked)


def render_daily(analysis: dict, date_str: str, dish_of_day: dict,
                 focus_finding: Optional[dict], streak: int = 1) -> str:
    meta = analysis["profile_meta"]
    ranking = analysis["recipe_ranking"]
    supps = analysis["supplements"]

    lines = []
    lines.append(f"# 🧬🍽️ DNADiet – Tagesreport {date_str}")
    lines.append("")
    if meta.get("demo"):
        lines.append("> ⚠️ **DEMO-MODUS** – es wurde noch kein persoenliches Profil hinterlegt. "
                     "Diese Auswertung nutzt ein **synthetisches Beispielprofil**. "
                     "Lade deine DNA im Colab-Notebook hoch und lege `genome/profile.json` ab, "
                     "um echte Ergebnisse zu erhalten.")
        lines.append("")
    sid = meta.get("sample_id") or "n/v"
    lines.append(f"*Profil:* `{sid}` · *Assembly:* {meta.get('assembly') or 'n/v'} · "
                 f"*Panel:* {meta.get('panel_snps')} SNPs · *Calls:* {meta.get('n_calls')} "
                 f"(davon {meta.get('n_low_confidence')} niedrige Konfidenz) · *Serie:* Tag {streak}")
    lines.append("")

    # --- Gericht des Tages ---
    lines.append("## 🥇 Gericht des Tages")
    lines.append("")
    lines.append(f"**{dish_of_day['title']}**  ·  genetischer Fit **{dish_of_day['fit']}/100** "
                 f"`{_fit_bar(dish_of_day['fit'])}`  ·  Rang {dish_of_day['rank']}/{len(ranking)}")
    lines.append("")
    pos = _driver_summary(dish_of_day["drivers"], positive=True)
    if pos:
        lines.append(f"*Warum es zu deiner Genetik passt:* {pos}")
        lines.append("")
    if dish_of_day["modifications"]:
        lines.append("*Feinschliff fuer dich:*")
        for m in dish_of_day["modifications"]:
            lines.append(f"- {m['text']}  _( {m['gene']} )_")
        lines.append("")

    # --- Fokus-Gen des Tages ---
    if focus_finding:
        lines.append("## 🔎 Fokus-Gen des Tages")
        lines.append("")
        lines.append(f"**{focus_finding['gene']}** ({focus_finding['key']}) – "
                     f"{focus_finding['trait']}")
        lines.append("")
        lines.append(f"- *Dein Genotyp:* `{focus_finding['genotype_str']}`")
        lines.append(f"- *Bedeutung:* {focus_finding['dosage_label']}")
        if focus_finding.get("effect_summary"):
            lines.append(f"- *Hintergrund:* {focus_finding['effect_summary']}")
        conf = focus_finding.get("confidence")
        if conf:
            lines.append(f"- *Evidenz-Konfidenz:* {conf}")
        lines.append("")

    # --- Ranking ---
    lines.append("## 📊 Gerichte-Ranking nach deiner Genetik")
    lines.append("")
    rows = []
    for r in ranking:
        why = _driver_summary(r["drivers"], positive=True, limit=1) or "–"
        watch = _driver_summary(r["drivers"], positive=False, limit=1) or "–"
        rows.append([r["rank"], r["title"][:46], f"{r['fit']}", _fit_bar(r["fit"]),
                     why[:60], watch[:60]])
    lines.append(_table(["#", "Gericht", "Fit", "", "Pluspunkt", "Achtung"], rows))
    lines.append("")

    # --- Genetische Befunde ---
    notable = analysis["notable_findings"]
    lines.append("## 🧬 Auffaellige genetische Befunde")
    lines.append("")
    if notable:
        rows = []
        for f in notable:
            rows.append([f["gene"], f["key"], f"`{f['genotype_str']}`",
                         f["dosage_label"][:80], f.get("confidence", "")])
        lines.append(_table(["Gen", "rsID", "Genotyp", "Interpretation", "Konfidenz"], rows))
    else:
        lines.append("_Keine auffaelligen Effekt-Allele im Panel – guenstiges Bild bzw. neutrale Genotypen._")
    lines.append("")

    # --- Supplemente ---
    lines.append("## 💊 Supplement-Empfehlungen")
    lines.append("")
    lines.append("**Basis (rein pflanzliche Kost, unabhaengig von der DNA):**")
    for s in supps["baseline"]:
        lines.append(f"- **{s['supplement']}** ({s['priority']}) – {s['rationale']}")
    lines.append("")
    if supps["dna"]:
        lines.append("**DNA-spezifisch (durch deine Varianten zusaetzlich unterstrichen):**")
        for s in supps["dna"]:
            genes = ", ".join(s["genes"])
            rat = " ".join(s["rationales"])
            lines.append(f"- **{s['supplement']}** ({s['priority']}) · _{genes}_ – {rat}")
        lines.append("")

    # --- Persoenliche Tipps ---
    if analysis["global_tips"]:
        lines.append("## 💡 Persoenliche Tipps")
        lines.append("")
        for t in analysis["global_tips"]:
            lines.append(f"- {t}")
        lines.append("")

    # --- Anpassungen der Top-Gerichte ---
    lines.append("## 🔧 Vorgeschlagene Rezept-Anpassungen (Top 5)")
    lines.append("")
    any_mod = False
    for r in ranking[:5]:
        if r["modifications"]:
            any_mod = True
            lines.append(f"**{r['rank']}. {r['title']}**")
            for m in r["modifications"]:
                lines.append(f"- {m['text']}  _( {m['gene']} )_")
            lines.append("")
    if not any_mod:
        lines.append("_Die Top-Gerichte passen bereits gut – keine Anpassungen noetig._")
        lines.append("")

    lines.append("---")
    lines.append(DISCLAIMER)
    lines.append("")
    lines.append(f"<sub>Automatisch erzeugt vom DNADiet-Tracker am {date_str}.</sub>")
    return "\n".join(lines)


def render_dashboard_block(analysis: dict, date_str: str, dish_of_day: dict,
                           focus_finding: Optional[dict], report_link: str) -> str:
    meta = analysis["profile_meta"]
    ranking = analysis["recipe_ranking"]
    demo = " · ⚠️ DEMO" if meta.get("demo") else ""
    lines = [DASHBOARD_START]
    lines.append(f"### 🧬 DNADiet – Tages-Dashboard ({date_str}{demo})")
    lines.append("")
    lines.append(f"- **🥇 Gericht des Tages:** {dish_of_day['title']} "
                 f"(Fit {dish_of_day['fit']}/100, Rang {dish_of_day['rank']})")
    if focus_finding:
        lines.append(f"- **🔎 Fokus-Gen:** {focus_finding['gene']} ({focus_finding['key']}) – "
                     f"Genotyp `{focus_finding['genotype_str']}`")
    top3 = ", ".join(f"{r['title']} ({r['fit']})" for r in ranking[:3])
    lines.append(f"- **📊 Top-3 passende Gerichte:** {top3}")
    n_dna = len(analysis["supplements"]["dna"])
    lines.append(f"- **💊 DNA-spezifische Supplement-Hinweise:** {n_dna}")
    lines.append(f"- **📄 Vollstaendiger Report:** [{report_link}]({report_link})")
    lines.append("")
    lines.append(DASHBOARD_END)
    return "\n".join(lines)


def update_readme(readme_text: str, block: str) -> str:
    """Ersetzt den Dashboard-Block im README (oder haengt ihn an)."""
    if DASHBOARD_START in readme_text and DASHBOARD_END in readme_text:
        pre = readme_text.split(DASHBOARD_START)[0]
        post = readme_text.split(DASHBOARD_END, 1)[1]
        return pre + block + post
    sep = "" if readme_text.endswith("\n") else "\n"
    return readme_text + sep + "\n" + block + "\n"
