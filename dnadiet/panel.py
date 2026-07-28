"""Laden von Panel, Rezepten und Profil + kleine Genotyp-Helfer."""
from __future__ import annotations

import json
import os
from typing import Optional

# Repo-Wurzel relativ zu dieser Datei (dnadiet/panel.py -> ..)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
GENOME_DIR = os.path.join(ROOT, "genome")

LEVEL_ORD = {"none": 0, "low": 1, "medium": 2, "high": 3}
PRIORITY_ORD = {"hoch": 3, "mittel": 2, "niedrig": 1}


def _read_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_panel(path: Optional[str] = None) -> dict:
    """Laedt data/snp_panel.json."""
    return _read_json(path or os.path.join(DATA_DIR, "snp_panel.json"))


def load_recipes(path: Optional[str] = None) -> list:
    """Laedt data/recipes.json (getaggt) mit Fallback auf recipes_base.json."""
    if path:
        return _read_json(path)
    tagged = os.path.join(DATA_DIR, "recipes.json")
    if os.path.exists(tagged):
        return _read_json(tagged)
    return _read_json(os.path.join(DATA_DIR, "recipes_base.json"))


def load_profile(path: Optional[str] = None) -> Optional[dict]:
    """Laedt ein Genotyp-Profil. Reihenfolge, wenn path=None:
       1) $DNADIET_PROFILE  2) genome/profile.json  3) None (Demo)."""
    if path:
        return _read_json(path)
    env = os.environ.get("DNADIET_PROFILE")
    if env and os.path.exists(env):
        return _read_json(env)
    default = os.path.join(GENOME_DIR, "profile.json")
    if os.path.exists(default):
        return _read_json(default)
    return None


def load_example_profile() -> dict:
    """Synthetisches Beispielprofil fuer den Demo-Modus."""
    return _read_json(os.path.join(GENOME_DIR, "profile.example.json"))


# --------------------------------------------------------------------------
# Genotyp-Helfer. Profil-Allele sind Nukleotide auf dem Plus-Strang (GRCh38),
# genau wie die Effekt-Allele im Panel -> direktes Abzaehlen ist korrekt.
# --------------------------------------------------------------------------
def genotype_entry(profile: dict, rsid: str) -> Optional[dict]:
    if not profile:
        return None
    return (profile.get("genotypes") or {}).get(rsid)


def alleles_of(entry: Optional[dict]) -> Optional[list]:
    if not entry:
        return None
    al = entry.get("alleles")
    if al:
        return list(al)
    gt = entry.get("genotype")
    if gt and len(gt) == 2 and gt not in ("..", "--"):
        return [gt[0], gt[1]]
    return None


def count_effect_alleles(effect_allele: str, entry: Optional[dict]) -> Optional[int]:
    """Anzahl der Effekt-Allele (0..2); None, wenn kein Call vorliegt."""
    al = alleles_of(entry)
    if al is None:
        return None
    return sum(1 for a in al if a and a.upper() == effect_allele.upper())


def genotype_string(entry: Optional[dict]) -> str:
    al = alleles_of(entry)
    if not al:
        return "n/v"
    return "".join(al)
