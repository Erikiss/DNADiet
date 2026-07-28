# Datenschutz & Sicherheit

DNADiet verarbeitet **genetische Daten** – die sensibelste Kategorie personenbezogener
Daten. Dieses Projekt ist so gebaut, dass so wenig wie moeglich davon das Repo erreicht.

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

1. **Roh-DNA bleibt lokal.** VCF/gVCF/CRAM werden nur im Colab-Notebook gelesen und nie
   ins Repo geladen. `.gitignore` blockiert `*.vcf.gz`, `*.hc.gz`, `*.cram`, `*.crai`,
   `*.tbi` u.a.
2. **Datensparsamkeit.** `profile.json` enthaelt ausschliesslich die Panel-SNPs, die fuer
   die Ernaehrungsauswertung gebraucht werden.
3. **Explizites Committen.** `genome/profile.json` ist per `.gitignore` gesperrt und muss
   bewusst mit `git add -f` hinzugefuegt werden.
4. **Secret-Alternative.** Statt der Datei kann das Profil als Repo-Secret
   `DNA_PROFILE_JSON` hinterlegt werden – dann liegt nichts Genetisches im Repo-Baum.
5. **Redaction.** Repo-Variable `DNADIET_REDACT=1` maskiert rohe Genotypen in den
   committeten Reports.

## Empfehlungen

- **Privates Repository verwenden.** Auch interpretierte Genotypen sind sensibel.
- Zugriffsrechte des Repos eng halten.
- Bei Weitergabe/Teilen der Reports an die interpretierten Genotypen denken (oder Redaction nutzen).

## Kein medizinischer Rat

Alle Ausgaben dienen nur Informations-/Bildungszwecken und ersetzen keine aerztliche oder
ernaehrungsmedizinische Beratung. Ein positiver Gentest ist keine Diagnose.
