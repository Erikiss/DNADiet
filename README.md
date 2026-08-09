# 🧬🍽️ DNADiet

**Deine DNA trifft das Blueprint-Rezeptdossier.** Lade deine Genom-Daten in eine
Colab-Mappe, und ein **taeglicher GitHub-Tracker** wertet aus, welche der 14
Blueprint-Gerichte (Bryan Johnson) am besten zu deiner Genetik passen, welche
**Anpassungen** sich lohnen und welche **Supplemente** sinnvoll sind.

[![In Colab oeffnen](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Erikiss/DNADiet/blob/main/notebooks/DNADiet_Colab.ipynb)

👉 **Ein Klick genuegt:** Der Badge oeffnet die Mappe direkt aus GitHub im Browser. Zellen ausführen,
die 3 Dateien hochladen – am Ende schreibt das Notebook `genome/profile.json` **direkt zurueck ins Repo**
(kein lokales Git, nichts auf Drive). Der Tracker startet dann automatisch.

<!-- DNADIET:START -->
### 🧬 DNADiet – Tages-Dashboard (2026-08-09)

- **🥇 Gericht des Tages:** Chickpea Vegetable Frittata (Fit 98/100, Rang 2)
- **🔎 Fokus-Gen:** CYP1A2 (rs762551) – Genotyp `CC`
- **📊 Top-3 passende Gerichte:** Cauliflower Lentil Loaf (100), Chickpea Vegetable Frittata (98), Chickpea Stew (93)
- **💊 DNA-spezifische Supplement-Hinweise:** 5
- **📄 Vollstaendiger Report:** [reports/daily/2026-08-09.md](reports/daily/2026-08-09.md)

<!-- DNADIET:END -->

---

## So funktioniert's

```
Deine VCF/gVCF (Roh-DNA)                    3 Dateien:
      |  nur in Colab                        - M1CQRX41L...hc.gz          (Varianten)
      v                                       - M1CQRX41L...hc.vcf.gz.tbi  (Tabix-Index)
notebooks/DNADiet_Colab.ipynb  <----------- - M1CQRX41L...cram.crai       (CRAM-Index)
      |  extrahiert nur ~29 SNPs
      v
genome/profile.json  -->  Daily Tracker (GitHub Action)  -->  reports/ + Dashboard
```

1. **Colab-Mappe oeffnen** (Badge oben) → drei Dateien hochladen → es entsteht ein kleines
   `profile.json` (nur die ernaehrungsrelevanten SNPs, **kein** ganzes Genom).
2. **Profil ins Repo schreiben:** Die letzte Notebook-Zelle committet `genome/profile.json`
   **direkt ueber die GitHub-API** zurueck ins Repo – einmalig braucht sie dafuer einen
   fine-grained Token (*Contents: write*). *Alternativen:* lokal herunterladen und selbst
   committen, oder Secret `DNA_PROFILE_JSON` / Redaction `DNADIET_REDACT=1` (siehe [genome/README](genome/README.md)).
3. **Taeglich zuruecklehnen:** Der Tracker laeuft per Cron (06:00 UTC) und schreibt jeden Tag:
   - 🥇 **Gericht des Tages** (rotiert unter deinen Top-Treffern)
   - 🔎 **Fokus-Gen des Tages** (rotierendes Mini-Erklaerstueck)
   - 📊 **Ranking** aller 14 Gerichte nach genetischem Fit
   - 💊 **Supplement-Plan** (vegane Basis + DNA-spezifisch)
   - 🔧 **Konkrete Rezept-Anpassungen**

> Ohne hinterlegtes Profil laeuft der Tracker im **Demo-Modus** mit einem synthetischen
> Beispielprofil – so siehst du sofort, wie die Reports aussehen.
> Aktuelles Demo-Beispiel: [`reports/latest.md`](reports/latest.md).

## Was ausgewertet wird

Ein kuratierter Panel aus **29 gut etablierten, ernaehrungsrelevanten Varianten**
(Nutrigenomik), zugeschnitten auf die **rein pflanzliche** Blueprint-Kueche. Beispiele:

| Thema | Gene/Varianten | Was es fuer die Rezepte bedeutet |
|---|---|---|
| Omega-3-Umwandlung | **FADS1** (rs174537/46) | Schwachwandler brauchen Algenoel; ALA aus Lein/Chia/Walnuss reicht nicht |
| Fettstoffwechsel | **APOE** (rs429358/rs7412) | e4 → gesaettigtes Fett (Kokosmilch) meiden, marine Omega-3 betonen |
| Folat/Methylierung | **MTHFR, MTR, MTHFD1** | linsen-/kichererbsenreiche Gerichte + ggf. Methylfolat/B2 |
| Blutzucker | **TCF7L2** (rs7903146) | niedrig-glykaemisch (Cauliflower-/Chickpea-Rice) bevorzugen |
| Eisen | **HFE** (C282Y/H63D) | bei Ueberladungsrisiko eisenreiche Gerichte nicht mit Vitamin C pushen |
| Vitamin A | **BCO1** | schwache Beta-Carotin-Umwandlung → carotinoidreiche Gerichte + Fett |
| B12 / Vitamin D | **FUT2, TCN2, GC, CYP2R1** | vegane Basis-Supplemente genotypisch unterstrichen |
| Salz/Blutdruck | **AGT** (rs699) | salzsensitiv → Natrium moderat, Kalium betonen |
| Cholin | **PEMT, MTHFD1** | auf veganer Kost knapp → cholinreiche Zutaten |
| Geschmack | **TAS2R38** | Bitter-Schmecker: Kreuzbluetler roesten/abrunden |

Vollstaendige Liste inkl. Quellen: [`docs/SNP_PANEL.md`](docs/SNP_PANEL.md).

Die Effekt-Allel-Richtungen und die Rezept-Naehrstoff-Tags wurden mit einem
Multi-Agenten-Workflow **adversariell gegen die Literatur verifiziert**.

## Wie es technisch arbeitet

- **Extraktion (Colab, `dnadiet/vcf_profile.py`):** loest rsIDs autoritativ ueber
  **Ensembl** auf, liest Genotypen per **pysam/Tabix** (inkl. gVCF-Referenzbloecke),
  validiert das REF-Allel und faellt bei fehlendem Index auf einen Streaming-Parser zurueck.
  Der Build (GRCh38/37/T2T) wird aus dem VCF-Header erkannt.
- **Tracker (GitHub Action, `dnadiet/tracker.py`):** arbeitet nur auf `profile.json`
  (rsID + Genotyp) – **keine** Roh-DNA, **keine** Drittanbieter-Abhaengigkeiten.
- **Scoring (`dnadiet/analysis.py`):** zaehlt Effekt-Allele, berechnet den APOE-Diplotyp,
  wendet genotyp-abhaengige Diaet-Regeln auf die getaggten Rezepte an und erstellt
  Supplement-Plan + Anpassungen. Gericht/Fokus-Gen rotieren deterministisch nach Datum.

## Projektstruktur

```
notebooks/DNADiet_Colab.ipynb   Die Colab-Mappe (DNA hochladen -> profile.json)
dnadiet/                        Python-Paket (vcf_profile, analysis, report, tracker, panel)
data/snp_panel.json             Kuratierter, verifizierter SNP-Panel (29 Varianten)
data/recipes.json               14 Blueprint-Rezepte + Naehrstoff-Tags
genome/profile.example.json     Synthetisches Demo-Profil (keine echte Person)
reports/                        Taegliche Reports (vom Tracker erzeugt)
scripts/                        Generatoren (Panel, Notebook, Doku)
tests/                          pytest-Suite
.github/workflows/              daily-tracker.yml + tests.yml
```

## Entwicklung

```bash
python scripts/build_panel.py        # data/snp_panel.json neu erzeugen
python scripts/build_notebook.py     # Colab-Notebook neu erzeugen
python scripts/build_panel_doc.py    # docs/SNP_PANEL.md neu erzeugen
pytest -q                            # Tests
python -m dnadiet.tracker --date 2026-01-01   # Tracker lokal (Demo-Profil)
```

## Daten & Sichtbarkeit

Ob du das Repo **oeffentlich** (open source, wie in der Biohacking-Community ueblich) oder
privat betreibst, ist deine Entscheidung – DNADiet funktioniert in beiden Faellen. Standardmaessig
wird nur das kleine `genome/profile.json` (die ~29 Panel-SNPs) versioniert; die **rohen** DNA-Dateien
(Whole-Genome-VCF/CRAM) bleiben per `.gitignore` draussen – aus Groessengruenden (GitHubs 100-MB-Limit),
nicht aus Datenschutz. Wer die Rohdaten teilen will, nutzt Release-Assets / Git LFS / externes Hosting.

Falls du es doch privater moechtest: Secret-Modus (`DNA_PROFILE_JSON`) oder Redaction
(`DNADIET_REDACT=1`). Details: [`docs/PRIVACY.md`](docs/PRIVACY.md). (Genetische Daten einmal
oeffentlich gestellt lassen sich nicht mehr zurueckholen – das ist die einzige Ueberlegung wert.)

## Haftungsausschluss

Dieses Projekt dient ausschliesslich **Informations- und Bildungszwecken** und ist **keine
medizinische Beratung, Diagnose oder Therapieempfehlung**. Genvarianten sind nur ein Faktor
unter vielen; die Effekte einzelner Varianten sind meist klein und populationsabhaengig. Ein
positiver Gentest ist keine Diagnose. Bitte konsultiere vor Ernaehrungs- oder
Supplement-Aenderungen eine Aerztin/einen Arzt oder eine Ernaehrungsfachkraft.

Die Rezepte stammen aus dem *Blueprint*-Dossier von Bryan Johnson und sind Eigentum der
jeweiligen Rechteinhaber; sie werden hier nur zu privaten Auswertungszwecken referenziert.
