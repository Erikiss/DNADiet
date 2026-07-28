#!/usr/bin/env python3
"""Erzeugt docs/SNP_PANEL.md als lesbare Referenz aus data/snp_panel.json."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    panel = json.load(open(os.path.join(ROOT, "data", "snp_panel.json"), encoding="utf-8"))
    snps = panel["snps"]
    lines = []
    lines.append("# SNP-Panel – Referenz")
    lines.append("")
    lines.append(f"Automatisch erzeugt aus `data/snp_panel.json` ({len(snps)} Varianten). "
                 "Effekt-Allele auf GRCh38-Plus-Strang. Alle Richtungen wurden adversariell "
                 "gegen etablierte Nutrigenomik-Literatur geprueft.")
    lines.append("")
    lines.append("> ⚕️ Nur zu Informations-/Bildungszwecken – keine medizinische Beratung. "
                 "Effekte einzelner Varianten sind meist klein und populationsabhaengig.")
    lines.append("")
    lines.append("| rsID | Gen | Merkmal | Effekt-Allel | Konfidenz | Kernaussage |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for s in snps:
        summary = s.get("effect_summary", "").replace("|", "/")
        lines.append(f"| {s['rsid']} | {s['gene']} | {s['trait']} | "
                     f"{s['effect_allele']} | {s.get('confidence','')} | {summary} |")
    lines.append("")

    # Basis-Supplemente
    base = panel.get("diet_baseline", {})
    lines.append("## Vegane Basis-Supplemente (unabhaengig vom Genotyp)")
    lines.append("")
    lines.append(f"*Ernaehrungsmuster:* {base.get('diet_pattern','')}")
    lines.append("")
    for sup in base.get("supplements", []):
        lines.append(f"- **{sup['supplement']}** ({sup['priority']}) – {sup['rationale']}")
    lines.append("")

    # Tag-Vokabular
    tv = panel.get("tag_vocab", {})
    lines.append("## Rezept-Naehrstoff-Tags")
    lines.append("")
    lines.append("Level: `none < low < medium < high`. Diese Tags treiben das genetische Ranking.")
    lines.append("")
    for k, v in tv.get("tags", {}).items():
        lines.append(f"- `{k}` – {v}")
    for k, v in tv.get("booleans", {}).items():
        lines.append(f"- `{k}` (bool) – {v}")
    lines.append("")
    lines.append("## Quellen (Auswahl)")
    lines.append("")
    seen = []
    for s in snps:
        src = s.get("source", "")
        if src and src not in seen:
            seen.append(src)
            lines.append(f"- **{s['gene']}** ({s['rsid']}): {src}")
    lines.append("")

    out = os.path.join(ROOT, "docs", "SNP_PANEL.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("geschrieben:", out)


if __name__ == "__main__":
    main()
