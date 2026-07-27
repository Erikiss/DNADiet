"""Tests der Analyse-Engine: Genotyp-Logik, APOE-Diplotyp, Ranking, Supplemente."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dnadiet import panel as P
from dnadiet.analysis import (
    apoe_diplotype,
    build_analysis,
    build_findings,
    rank_recipes,
    supplement_plan,
    when_matches,
)
from dnadiet.panel import count_effect_alleles


def test_when_matches():
    assert when_matches(">=1", 1) and when_matches(">=1", 2)
    assert not when_matches(">=1", 0)
    assert when_matches("==0", 0) and not when_matches("==0", 1)
    assert when_matches(">=2", 2) and not when_matches(">=2", 1)
    assert when_matches(">=0", 0)
    assert not when_matches(">=1", None)  # kein Call


def test_count_effect_alleles():
    assert count_effect_alleles("A", {"alleles": ["A", "A"]}) == 2
    assert count_effect_alleles("A", {"alleles": ["A", "G"]}) == 1
    assert count_effect_alleles("A", {"alleles": ["G", "G"]}) == 0
    assert count_effect_alleles("A", None) is None
    assert count_effect_alleles("a", {"alleles": ["A", "A"]}) == 2  # case-insensitiv


def test_apoe_diplotype_table():
    # rs429358 (C=e4), rs7412 (T=e2)
    assert apoe_diplotype(["T", "T"], ["C", "C"]) == "E3/E3"
    assert apoe_diplotype(["T", "C"], ["C", "C"]) == "E3/E4"
    assert apoe_diplotype(["C", "C"], ["C", "C"]) == "E4/E4"
    assert apoe_diplotype(["T", "T"], ["C", "T"]) == "E2/E3"
    assert apoe_diplotype(["T", "T"], ["T", "T"]) == "E2/E2"
    assert apoe_diplotype(["T", "C"], ["C", "T"]) == "E2/E4"
    assert apoe_diplotype(None, ["C", "C"]) is None


def test_build_findings_on_example():
    panel = P.load_panel()
    profile = P.load_example_profile()
    findings = build_findings(panel, profile)
    by = {f["key"]: f for f in findings}
    # APOE aus rs429358 TC + rs7412 CC -> E3/E4
    assert by["APOE"]["genotype_str"] == "E3/E4"
    assert by["APOE"]["notable"] is True
    # FADS1 TT -> schwacher Umwandler, notable, aktive Diaetregel
    assert by["rs174537"]["n_effect"] == 2
    assert by["rs174537"]["notable"] is True
    assert any(r["tag"] == "omega3_ala" for r in by["rs174537"]["diet_rules"])


def test_coconut_soup_penalised_for_apoe4():
    """Butternut-Suppe (Kokosmilch, hohe glyk. Last) muss beim e4-Profil schlecht ranken."""
    panel = P.load_panel()
    recipes = P.load_recipes()
    profile = P.load_example_profile()
    findings = build_findings(panel, profile)
    ranking = rank_recipes(findings, recipes)
    by_id = {r["id"]: r for r in ranking}
    coconut = by_id[12]  # Butternut Squash Soup mit Kokosmilch
    lentil = by_id[2]    # Lemon Red Lentil Soup
    assert coconut["rank"] > lentil["rank"]
    assert coconut["rank"] >= 12  # unteres Ende
    # Anpassung fuer gesaettigtes Fett vorgeschlagen
    assert any("saturated" in m["text"].lower() or "Kokos" in m["text"] for m in coconut["modifications"])


def test_supplement_plan_merges_omega3():
    panel = P.load_panel()
    profile = P.load_example_profile()
    findings = build_findings(panel, profile)
    plan = supplement_plan(panel, findings)
    baseline_names = {s["supplement"] for s in plan["baseline"]}
    assert any("B12" in n for n in baseline_names)
    dna_by = {s["supplement"]: s for s in plan["dna"]}
    # Algenoel muss FADS1 und APOE vereinen (kanonischer Name)
    assert "Algenoel (DHA/EPA)" in dna_by
    genes = dna_by["Algenoel (DHA/EPA)"]["genes"]
    assert "FADS1" in genes and "APOE" in genes


def test_build_analysis_structure():
    panel = P.load_panel()
    recipes = P.load_recipes()
    profile = P.load_example_profile()
    a = build_analysis(panel, recipes, profile)
    assert len(a["recipe_ranking"]) == 14
    assert a["profile_meta"]["n_calls"] == len(profile["genotypes"])
    assert a["apoe"]["genotype_str"] == "E3/E4"
    assert a["notable_findings"]  # nicht leer
    # jedes Ranking hat rank + fit
    assert all("rank" in r and "fit" in r for r in a["recipe_ranking"])


def test_neutral_profile_no_findings():
    """Profil ganz ohne Effekt-Allele -> neutrales Ranking (Fit 50), keine Anpassungen."""
    panel = P.load_panel()
    recipes = P.load_recipes()
    # Alle Genotypen = homozygot Nicht-Effekt-Allel
    gts = {}
    for s in panel["snps"]:
        ref = s["ref"]
        non = ref if ref != s["effect_allele"] else s["alt"]
        gts[s["rsid"]] = {"alleles": [non, non], "genotype": non + non, "source": "vcf"}
    profile = {"genotypes": gts}
    a = build_analysis(panel, recipes, profile)
    assert all(r["fit"] == 50 for r in a["recipe_ranking"])


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print("OK", name)
    print("Alle Tests bestanden.")
