# `genome/` – dein persoenliches Genotyp-Profil

Hier lebt **`profile.json`** – das kleine, aus deiner DNA extrahierte Genotyp-Profil,
das der taegliche Tracker auswertet.

## Was ist `profile.json`?

Es enthaelt **ausschliesslich die ~29 ernaehrungsrelevanten SNPs** aus `data/snp_panel.json`
– **kein** vollstaendiges Genom, keine Rohdaten. Erzeugt wird es im
[Colab-Notebook](../notebooks/DNADiet_Colab.ipynb) aus deiner hochgeladenen VCF/gVCF.

`profile.example.json` ist ein **synthetisches Beispielprofil** (keine echte Person),
das der Tracker im Demo-Modus nutzt, solange kein echtes Profil vorhanden ist.

## Profil aktivieren

### Am einfachsten · direkt aus dem Colab-Notebook
Die letzte Zelle der [Colab-Mappe](../notebooks/DNADiet_Colab.ipynb) schreibt `genome/profile.json`
per GitHub-API **direkt ins Repo** – kein lokales Git noetig. Einmalig braucht sie einen
fine-grained Token mit *Contents: Read and write*.

### Alternativ · Datei lokal committen
Einfach ins Repo legen und committen:

```bash
git add genome/profile.json
git commit -m "Mein DNADiet-Profil"
git push
```

Ab dann nutzt der taegliche Tracker deine echten Daten. Ob das Repo oeffentlich oder
privat ist, bleibt dir ueberlassen.

### Optional · GitHub-Secret (nichts Genetisches im Repo-Baum)
Wer das Profil lieber nicht versioniert: Repo → *Settings → Secrets and variables →
Actions → New repository secret*
- **Name:** `DNA_PROFILE_JSON`
- **Wert:** kompletter Inhalt von `profile.json`

Der Workflow schreibt das Profil dann nur temporaer auf den Runner (nie ins Repo).

## Hinweise

- Die taeglichen Reports enthalten interpretierte Genotypen (z.B. „rs1801133: AG").
  Willst du die rohen Genotypen im committeten Report maskieren, setze die Repo-Variable
  **`DNADIET_REDACT=1`** – dann werden sie zu `•••`.
- **Rohe** DNA-Dateien (`*.vcf.gz`, `*.hc.gz`, `*.cram`, `*.crai`, `*.tbi`, …) sind per
  `.gitignore` ausgeschlossen – aus Groessengruenden (mehrere GB, GitHubs 100-MB-Limit),
  nicht aus Datenschutz. Das kleine `profile.json` wird ganz normal versioniert.

## Format (Kurzreferenz)

```json
{
  "schema_version": 1,
  "sample_id": "M1CQRX41L",
  "assembly": "GRCh38",
  "genotypes": {
    "rs1801133": {"alleles": ["A","G"], "genotype": "AG", "source": "vcf", "confidence": "hoch"}
  }
}
```

`source`: `vcf` (Variante gecallt) · `gvcf-ref` (Referenzblock, hom-ref bestaetigt) ·
`assumed-ref` (Position fehlt in reiner VCF → als hom-ref angenommen, niedrige Konfidenz).
