"""DNADiet – Nutrigenomik-Abgleich der Blueprint-Rezepte mit persoenlichen DNA-Daten.

Reihenfolge des Datenflusses:
  1. Colab-Notebook: VCF/gVCF hochladen -> vcf_profile.extract_profile() -> genome/profile.json
  2. Taeglicher Tracker (GitHub Action): profile.json + Panel + Rezepte
     -> analysis.build_analysis() -> report.render_daily() -> reports/

Der Tracker arbeitet ausschliesslich auf rsID + Genotyp; Koordinaten werden nur
bei der Extraktion im Notebook benoetigt.
"""

__version__ = "1.0.0"
