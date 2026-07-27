# `genome/` – dein persoenliches Genotyp-Profil

Hier lebt **`profile.json`** – das kleine, aus deiner DNA extrahierte Genotyp-Profil,
das der taegliche Tracker auswertet.

## Was ist `profile.json`?

Es enthaelt **ausschliesslich die ~29 ernaehrungsrelevanten SNPs** aus `data/snp_panel.json`
– **kein** vollstaendiges Genom, keine Rohdaten. Erzeugt wird es im
[Colab-Notebook](../notebooks/DNADiet_Colab.ipynb) aus deiner hochgeladenen VCF/gVCF.

`profile.example.json` ist ein **synthetisches Beispielprofil** (keine echte Person),
das der Tracker im Demo-Modus nutzt, solange kein echtes Profil vorhanden ist.

## Profil aktivieren – zwei Wege

### Weg A · Datei committen (privates Repo!)
`genome/profile.json` steht bewusst in `.gitignore`, damit nichts versehentlich
oeffentlich wird. Zum Aktivieren explizit hinzufuegen:

```bash
git add -f genome/profile.json
git commit -m "Mein DNADiet-Profil"
git push
```

### Weg B · GitHub-Secret (nichts Genetisches im Repo-Baum)
Repo → *Settings → Secrets and variables → Actions → New repository secret*
- **Name:** `DNA_PROFILE_JSON`
- **Wert:** kompletter Inhalt von `profile.json`

Der Workflow schreibt das Profil dann nur temporaer auf den Runner (nie ins Repo).

## Datenschutz-Hinweise

- **Nutze ein privates Repository.** Die taeglichen Reports enthalten interpretierte
  Genotypen (z.B. „rs1801133: AG").
- Willst du auch in den committeten Reports keine rohen Genotypen sehen, setze die
  Repo-Variable **`DNADIET_REDACT=1`** – dann werden Genotypen zu `•••` maskiert.
- Roh-DNA-Dateien (`*.vcf.gz`, `*.hc.gz`, `*.cram`, `*.crai`, `*.tbi`, …) sind in
  `.gitignore` gesperrt und sollten **nie** committet werden.

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
