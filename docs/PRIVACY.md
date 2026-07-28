# Daten, Sichtbarkeit & Sicherheit

DNADiet verarbeitet **genetische Daten**. Wie offen du damit umgehst, entscheidest du selbst:
Ein **oeffentliches** Repo (open source, wie in der Biohacking-/Blueprint-Community ueblich)
funktioniert genauso wie ein privates. Dieses Dokument beschreibt beide Wege und die
technischen Standardeinstellungen.

## Datenfluss

```
Deine VCF/gVCF (Roh-DNA)
        │   nur in der Colab-Sitzung
        ▼
Colab-Notebook  ──►  profile.json  (nur ~29 SNPs, kein ganzes Genom)
        │
        ▼
GitHub (privat)  ──►  Daily Tracker  ──►  reports/  +  README-Dashboard
```

## Prinzipien

1. **Roh-DNA bleibt draussen – aus Groessengruenden.** VCF/gVCF/CRAM sind oft mehrere GB
   und ueberschreiten GitHubs 100-MB-Limit; `.gitignore` haelt sie daher aus dem Repo
   (`*.vcf.gz`, `*.hc.gz`, `*.cram`, `*.crai`, `*.tbi` u.a.). Wer die Rohdaten dennoch
   oeffentlich teilen will, nutzt Release-Assets / Git LFS / externes Hosting.
2. **Datensparsamkeit.** `profile.json` enthaelt ausschliesslich die Panel-SNPs, die fuer
   die Ernaehrungsauswertung gebraucht werden – kein ganzes Genom.
3. **Committen ist der Standard.** `genome/profile.json` wird ganz normal versioniert
   (`git add genome/profile.json`).
4. **Secret-Alternative.** Wer nichts Genetisches im Repo-Baum will, hinterlegt das Profil
   als Repo-Secret `DNA_PROFILE_JSON`.
5. **Redaction.** Repo-Variable `DNADIET_REDACT=1` maskiert rohe Genotypen in den
   committeten Reports.

## Gut zu wissen

- Oeffentlich vs. privat ist deine Wahl – beide Modi werden unterstuetzt.
- Einmal oeffentlich gestellte genetische Daten lassen sich praktisch nicht mehr
  zurueckholen; das ist die einzige Ueberlegung wert.
- Interpretierte Genotypen stehen in den Reports; mit `DNADIET_REDACT=1` bleiben sie maskiert.

## Kein medizinischer Rat

Alle Ausgaben dienen nur Informations-/Bildungszwecken und ersetzen keine aerztliche oder
ernaehrungsmedizinische Beratung. Ein positiver Gentest ist keine Diagnose.
