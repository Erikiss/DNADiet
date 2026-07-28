#!/usr/bin/env python3
"""Erzeugt notebooks/DNADiet_Colab.ipynb – die Colab-Mappe zum Hochladen der DNA."""
import json
import os


def md(*lines):
    return {"cell_type": "markdown", "metadata": {}, "source": _src(lines)}


def code(*lines):
    return {"cell_type": "code", "metadata": {}, "execution_count": None,
            "outputs": [], "source": _src(lines)}


def _src(lines):
    text = "\n".join(lines)
    parts = text.split("\n")
    return [p + "\n" for p in parts[:-1]] + [parts[-1]]


cells = []

cells.append(md(
    "# 🧬🍽️ DNADiet – deine DNA trifft die Blueprint-Rezepte",
    "",
    "Diese Colab-Mappe wertet **deine persoenlichen DNA-Daten** aus und gleicht sie mit dem",
    "**Blueprint-Rezeptdossier** (14 rein pflanzliche Gerichte von Bryan Johnson) ab.",
    "",
    "**Du laedst genau diese drei Dateien hoch:**",
    "",
    "| Datei | Rolle |",
    "|---|---|",
    "| `M1CQRX41L.mm2.sortdup.bqsr.hc.gz` | **Varianten (VCF/gVCF)** – die eigentlichen Genotypen |",
    "| `M1CQRX41L.mm2.sortdup.bqsr.hc.vcf.gz.tbi` | Tabix-Index (schneller Zugriff) |",
    "| `M1CQRX41L.mm2.sortdup.bqsr.cram.crai` | CRAM-Index (nur informativ, nicht zwingend noetig) |",
    "",
    "**Ergebnis:** ein kleines `profile.json` (nur ~29 ernaehrungsrelevante SNPs, **kein** ganzes Genom),",
    "das du ins Repo legst, damit der **taegliche GitHub-Tracker** daraus Reports erstellt.",
    "",
    "> ℹ️ **Daten:** Deine Roh-DNA bleibt in dieser Colab-Sitzung; ins Repo kommt nur das",
    "> kleine Genotyp-Profil (~29 SNPs). Ob du dein Repo oeffentlich oder privat betreibst,",
    "> ist deine Entscheidung (siehe letzter Abschnitt).",
    "",
    "> ⚕️ **Kein medizinischer Rat.** Nur zu Informations-/Bildungszwecken. Genvarianten sind",
    "> nur ein Faktor; Effekte sind meist klein. Aenderungen bitte mit Arzt/Ernaehrungsfachkraft besprechen.",
))

cells.append(md("## 0) Abhaengigkeiten & Code laden"))
cells.append(code(
    "# pysam (VCF/gVCF/Tabix) + requests (Ensembl-Koordinaten)",
    "!pip -q install pysam requests",
))
cells.append(code(
    "# DNADiet-Code + Daten (Panel & Rezepte) aus dem Repo holen",
    "REPO_URL = 'https://github.com/erikiss/dnadiet.git'  # ggf. auf dein Repo anpassen",
    "BRANCH   = 'main'                                     # bzw. dein Branch",
    "",
    "import os, sys, subprocess",
    "if not os.path.isdir('/content/dnadiet_repo'):",
    "    subprocess.run(['git','clone','--depth','1','-b',BRANCH,REPO_URL,'/content/dnadiet_repo'], check=True)",
    "sys.path.insert(0, '/content/dnadiet_repo')",
    "os.chdir('/content/dnadiet_repo')",
    "",
    "from dnadiet import panel as P",
    "from dnadiet.vcf_profile import extract_profile",
    "from dnadiet.analysis import build_analysis",
    "from dnadiet import report as Rep",
    "PANEL = P.load_panel()",
    "RECIPES = P.load_recipes()",
    "print(f'Panel geladen: {len(PANEL[\"snps\"])} SNPs, {len(RECIPES)} Rezepte.')",
))

cells.append(md(
    "## 1) Die drei Dateien hochladen",
    "",
    "Klicke auf **Durchsuchen** und waehle alle drei Dateien gleichzeitig aus.",
    "(Es reicht zwingend die `...hc.gz`; Index-Dateien beschleunigen nur.)",
))
cells.append(code(
    "from google.colab import files",
    "uploaded = files.upload()",
    "uploaded_names = list(uploaded.keys())",
    "print('Hochgeladen:', uploaded_names)",
))

cells.append(md("## 2) VCF finden & (falls moeglich) Index bereitstellen"))
cells.append(code(
    "import shutil, pysam",
    "",
    "# Die Variantendatei ist die .gz, die KEIN Index ist:",
    "vcf = None",
    "for f in uploaded_names:",
    "    if f.endswith(('.tbi','.crai','.csi','.bai')):",
    "        continue",
    "    if f.endswith('.gz'):",
    "        vcf = f",
    "if vcf is None:",
    "    raise SystemExit('Keine VCF/gVCF (.gz) gefunden – bitte die ...hc.gz hochladen.')",
    "print('Variantendatei:', vcf)",
    "",
    "# Vorhandenen Tabix-Index passend benennen (Namens-Mismatch .hc.gz vs .hc.vcf.gz ausgleichen)",
    "tbis = [f for f in uploaded_names if f.endswith('.tbi')]",
    "target = vcf + '.tbi'",
    "if not os.path.exists(target) and tbis:",
    "    try:",
    "        shutil.copy(tbis[0], target)",
    "        print(f'Index {tbis[0]} -> {target} kopiert.')",
    "    except Exception as e:",
    "        print('Index-Kopie nicht moeglich:', e)",
    "",
    "# Index testen; scheitert er, wird spaeter automatisch der Streaming-Parser genutzt.",
    "index_status = 'kein Index'",
    "try:",
    "    vf = pysam.VariantFile(vcf)",
    "    c0 = list(vf.header.contigs)[0]",
    "    next(vf.fetch(c0, 0, 1), None)",
    "    index_status = 'Index OK'",
    "except Exception:",
    "    try:",
    "        pysam.tabix_index(vcf, preset='vcf', force=True)",
    "        index_status = 'neu indexiert'",
    "    except Exception as e:",
    "        index_status = f'kein nutzbarer Index ({e}) -> Streaming-Fallback'",
    "print('Index-Status:', index_status)",
))

cells.append(md(
    "## 3) rsID → GRCh38-Koordinaten (autoritativ ueber Ensembl)",
    "",
    "Statt fest verdrahteter Koordinaten fragen wir die **authoritativen** GRCh38-Positionen",
    "live bei Ensembl ab. Faellt Ensembl aus, werden die im Repo hinterlegten Fallback-Koordinaten",
    "genutzt und zusaetzlich das REF-Allel gegen die VCF geprueft.",
))
cells.append(code(
    "import requests, json as _json",
    "",
    "def ensembl_coords(rsids, assembly='GRCh38'):",
    "    server = 'https://rest.ensembl.org'",
    "    coord = {}",
    "    for i in range(0, len(rsids), 150):",
    "        chunk = rsids[i:i+150]",
    "        try:",
    "            r = requests.post(server + '/variation/homo_sapiens',",
    "                              headers={'Content-Type':'application/json','Accept':'application/json'},",
    "                              data=_json.dumps({'ids': chunk}), timeout=60)",
    "            if r.status_code != 200:",
    "                continue",
    "            for rsid, info in r.json().items():",
    "                for m in (info.get('mappings') or []):",
    "                    if m.get('assembly_name') == assembly:",
    "                        al = (m.get('allele_string') or '').split('/')",
    "                        coord[rsid] = {'chrom': str(m.get('seq_region_name')),",
    "                                       'pos': int(m.get('start')),",
    "                                       'ref': al[0] if al else None,",
    "                                       'alt': al[1] if len(al) > 1 else None}",
    "                        break",
    "        except Exception as e:",
    "            print('Ensembl-Batch-Fehler:', e)",
    "    return coord",
    "",
    "rsids = [s['rsid'] for s in PANEL['snps']]",
    "coord_map = ensembl_coords(rsids)",
    "print(f'Ensembl aufgeloest: {len(coord_map)}/{len(rsids)} SNPs.')",
    "resolver = (lambda rsid: coord_map.get(rsid)) if coord_map else None",
))

cells.append(md("## 4) Genotyp-Profil extrahieren"))
cells.append(code(
    "sample_guess = vcf.split('.')[0]  # z.B. 'M1CQRX41L'",
    "profile = extract_profile(vcf, PANEL, coord_resolver=resolver, sample_id=sample_guess)",
    "",
    "gts = profile['genotypes']",
    "n_called = sum(1 for g in gts.values() if g.get('alleles'))",
    "print(f\"Sample: {profile['sample_id']} | Assembly: {profile['assembly']} | Engine: {profile['engine']}\")",
    "print(f'Genotypen bestimmt: {n_called}/{len(gts)}')",
    "if profile.get('warnings'):",
    "    print('\\nHinweise:')",
    "    for w in profile['warnings'][:15]:",
    "        print('  -', w)",
    "",
    "print('\\nrsID        Gen                         Genotyp  Quelle')",
    "byid = {s['rsid']: s for s in PANEL['snps']}",
    "for rsid, g in gts.items():",
    "    s = byid[rsid]",
    "    print(f\"{rsid:11s} {s['gene'][:26]:26s} {str(g.get('genotype')):7s}  {g.get('source')}\")",
))

cells.append(md("## 5) Auswertung ansehen (Ranking, Supplemente, Anpassungen)"))
cells.append(code(
    "from IPython.display import Markdown, display",
    "import datetime as _dt",
    "",
    "analysis = build_analysis(PANEL, RECIPES, profile)",
    "today = _dt.date.today().isoformat()",
    "",
    "# Gericht des Tages + Fokus-Gen wie im taeglichen Tracker",
    "from dnadiet.tracker import _pick_dish_of_day, _pick_focus",
    "day_ord = _dt.date.today().toordinal()",
    "dish = _pick_dish_of_day(analysis['recipe_ranking'], day_ord)",
    "focus = _pick_focus(analysis, day_ord)",
    "md_report = Rep.render_daily(analysis, today, dish, focus, streak=1)",
    "display(Markdown(md_report))",
))

cells.append(md(
    "## 6) Profil speichern & herunterladen",
    "",
    "Das `profile.json` enthaelt **nur** die ~29 Panel-Genotypen – kein vollstaendiges Genom.",
))
cells.append(code(
    "import json as _json",
    "with open('profile.json', 'w', encoding='utf-8') as f:",
    "    _json.dump(profile, f, ensure_ascii=False, indent=2)",
    "print('Gespeichert: profile.json (' + str(len(profile['genotypes'])) + ' Genotypen)')",
    "from google.colab import files as _f",
    "_f.download('profile.json')",
))

cells.append(md(
    "## 7) Taeglichen Tracker aktivieren",
    "",
    "Damit der **taegliche GitHub-Tracker** deine echten Daten nutzt:",
    "",
    "### Standard – Datei committen",
    "1. Lege `profile.json` unter `genome/profile.json` im Repo ab.",
    "2. Committen:",
    "   ```bash",
    "   git add genome/profile.json",
    "   git commit -m 'Mein DNADiet-Profil'",
    "   git push",
    "   ```",
    "3. Der Workflow **DNADiet Daily Tracker** laeuft taeglich (oder manuell ueber *Actions → Run workflow*)",
    "   und schreibt Reports nach `reports/` sowie ein Dashboard ins `README.md`.",
    "",
    "> Ob dein Repo oeffentlich oder privat ist, bleibt dir ueberlassen. Die rohen DNA-Dateien",
    "> gehoeren wegen ihrer Groesse ohnehin nicht ins Git – nur das kleine `profile.json`.",
    "",
    "### Optional – Profil als GitHub-Secret (nichts Genetisches im Repo-Baum)",
    "1. Repo → *Settings → Secrets and variables → Actions → New repository secret*.",
    "2. Name: `DNA_PROFILE_JSON`, Wert: kompletter Inhalt von `profile.json`.",
    "3. Optional Variable `DNADIET_REDACT=1` setzen, um rohe Genotypen in den committeten Reports zu maskieren.",
    "",
    "Fertig – ab dann bekommst du taeglich *Gericht des Tages*, *Fokus-Gen*, ein genetisches",
    "Rezept-Ranking, Supplement-Empfehlungen und konkrete Rezept-Anpassungen. 🎉",
))

nb = {
    "cells": cells,
    "metadata": {
        "colab": {"provenance": [], "name": "DNADiet_Colab.ipynb"},
        "kernelspec": {"name": "python3", "display_name": "Python 3"},
        "language_info": {"name": "python"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = os.path.join(root, "notebooks", "DNADiet_Colab.ipynb")
with open(out, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)
print("geschrieben:", out, "-", len(cells), "Zellen")
