# SNP-Panel – Referenz

Automatisch erzeugt aus `data/snp_panel.json` (29 Varianten). Effekt-Allele auf GRCh38-Plus-Strang. Alle Richtungen wurden adversariell gegen etablierte Nutrigenomik-Literatur geprueft.

> ⚕️ Nur zu Informations-/Bildungszwecken – keine medizinische Beratung. Effekte einzelner Varianten sind meist klein und populationsabhaengig.

| rsID | Gen | Merkmal | Effekt-Allel | Konfidenz | Kernaussage |
| --- | --- | --- | --- | --- | --- |
| rs4988235 | MCM6/LCT | Laktosetoleranz (Laktasepersistenz) | G | hoch | G = ancestrale, adulte Laktase-Nicht-Persistenz (Laktoseintoleranz-Neigung); A = Laktasepersistenz. |
| rs182549 | MCM6/LCT | Laktosetoleranz (bestaetigend) | C | hoch | In starkem LD mit rs4988235; C = Nicht-Persistenz, T = Persistenz. |
| rs762551 | CYP1A2 | Koffein-Metabolismus | C | hoch | A-Allel = schneller Koffein-Metabolismus; C-Allel = langsamer Metabolismus und hoehere Koffein-Sensitivitaet. |
| rs1801133 | MTHFR (C677T) | Folatstoffwechsel / Homocystein | A | hoch | A (677T) senkt die MTHFR-Aktivitaet; AA ~30% Restaktivitaet, hoeheres Homocystein. |
| rs1801131 | MTHFR (A1298C) | Folatstoffwechsel (bestaetigend) | G | hoch | G (1298C) senkt die MTHFR-Aktivitaet milder; relevant v.a. als Compound-Heterozygotie mit C677T. |
| rs429358 | APOE | APOE-Genotyp (Teil 1) | C | hoch | C an rs429358 definiert (mit rs7412=C) das e4-Allel. e4 = Empfindlichkeit ggue. gesaettigtem Fett, hoeheres LDL/kardiovaskulaeres Risiko. |
| rs7412 | APOE | APOE-Genotyp (Teil 2) | T | hoch | T an rs7412 definiert (mit rs429358=T) das e2-Allel. |
| rs174537 | FADS1 | Omega-3-Umwandlung (ALA -> EPA/DHA) | T | hoch | G = effiziente Desaturase (gute ALA->EPA/DHA-Umwandlung); T = reduzierte Umwandlung. |
| rs174546 | FADS1 | Omega-3-Umwandlung (bestaetigend) | T | hoch | In starkem LD mit rs174537; T = reduzierte FADS1-Umwandlung. |
| rs1800562 | HFE (C282Y) | Eisenspeicherung (Haemochromatose) | A | hoch | A (C282Y) = Hauptrisikoallel fuer erhoehte Eisenspeicherung; AA = deutlich erhoehtes Haemochromatose-Risiko. |
| rs1799945 | HFE (H63D) | Eisenspeicherung (milder) | G | hoch | G (H63D) = milderes Eisenspeicher-Allel; relevant v.a. als Compound-Heterozygotie mit C282Y. |
| rs601338 | FUT2 | Sekretor-Status / B12 & Mikrobiom | A | mittel | A (W143X) = Nicht-Sekretor-Allel; AA = Nicht-Sekretor. Beeinflusst B12-Status und Darmmikrobiom (Richtung uneinheitlich). |
| rs7903146 | TCF7L2 | Blutzucker / Typ-2-Diabetes-Risiko | T | hoch | T = staerkstes haeufiges Risikoallel fuer Typ-2-Diabetes; profitiert von niedriger glykaemischer Last. |
| rs9939609 | FTO | Appetit / Adipositas-Neigung | A | hoch | A = Risikoallel fuer hoeheren Appetit/BMI; profitiert von proteinreicher, ballaststoffreicher, saettigender Kost. |
| rs1421085 | FTO (kausal) | Adipositas-Neigung (bestaetigend) | C | hoch | C = kausales Risikoallel (stoert ARID5B/Adipozyten-Braeunung); in LD mit rs9939609-A. |
| rs17782313 | MC4R | Appetit/Saettigung (bestaetigend) | C | mittel | C = Allel fuer hoeheren BMI/Appetit; verstaerkt das FTO-Bild. |
| rs2282679 | GC (Vitamin-D-Bindungsprotein) | Vitamin-D-Status | G | hoch | G = niedrigere 25(OH)D-Spiegel; bei sonnenarmer/pflanzlicher Kost relevant. |
| rs7501331 | BCO1 | Beta-Carotin -> Vitamin-A-Umwandlung | T | hoch | T = reduzierte Umwandlung von Beta-Carotin in aktives Vitamin A (Retinol). |
| rs12934922 | BCO1 | Beta-Carotin-Umwandlung (bestaetigend) | T | hoch | T = reduzierte BCO1-Umwandlung (bestaetigt rs7501331). |
| rs4880 | SOD2 | Mitochondrialer oxidativer Stress | T | mittel | T (Val16) veraendert den mitochondrialen Import der Superoxid-Dismutase; profitiert von antioxidantienreicher Kost. |
| rs713598 | TAS2R38 | Bitter-Geschmack (Kreuzbluetler) | C | hoch | C (Pro49) = Bitter-Schmecker (PAV); nimmt Bitterstoffe in Kreuzbluetlern staerker wahr. |
| rs2187668 | HLA-DQA1 (DQ2.5-Tag) | Zoeliakie-Suszeptibilitaet (genetisch) | T | hoch | T markiert das HLA-DQ2.5-Haplotyp – genetische Voraussetzung fuer Zoeliakie (Suszeptibilitaet, keine Diagnose). |
| rs671 | ALDH2 | Alkohol-Abbau (Flush) | A | hoch | A (*2) = defizitaere Aldehyddehydrogenase (Alkohol-Flush, Acetaldehyd-Akkumulation). |
| rs699 | AGT (M235T) | Salzsensitivitaet des Blutdrucks | G | mittel | G (235T/Thr) = hoehere Angiotensinogen-Spiegel; assoziiert mit salzsensitivem Blutdruck. |
| rs1801198 | TCN2 (P259R) | Vitamin-B12-Transport (Holo-Transcobalamin) | G | mittel | G (776G) senkt Holo-Transcobalamin (zellulaer verfuegbares B12); bei veganer Kost besonders relevant. |
| rs1805087 | MTR (A2756G) | B12-abhaengige Homocystein-Remethylierung | G | niedrig | MTR (Methioninsynthase) ist B12-abhaengig; das G-Allel kann die Homocystein-Remethylierung beeinflussen. Ergaenzt den MTHFR/Folat-Zyklus. |
| rs2236225 | MTHFD1 (R653Q) | Folat-/Cholin-Bedarf (Ein-Kohlenstoff-Stoffwechsel) | A | mittel | A (653Q) erhoeht bei knapper Zufuhr den Bedarf an Folat UND Cholin – auf veganer Kost (wenig Cholin) relevant. |
| rs7946 | PEMT (V175M) | Endogene Cholin-Synthese | T | mittel | T reduziert die endogene Phosphatidylcholin-Synthese; da Cholin auf veganer Kost knapp ist, steigt der Nahrungsbedarf. |
| rs10741657 | CYP2R1 | Vitamin-D-25-Hydroxylierung | A | mittel | CYP2R1 aktiviert Vitamin D in der Leber (25-Hydroxylierung); das A-Allel ist mit niedrigeren 25(OH)D-Spiegeln assoziiert (zweiter robuster D-Locus neben GC). |

## Vegane Basis-Supplemente (unabhaengig vom Genotyp)

*Ernaehrungsmuster:* rein pflanzlich (vegan), vollwertig, ballaststoffreich

- **Vitamin B12** (hoch) – Auf rein pflanzlicher Kost nicht verlaesslich zu decken – Supplementierung ist essenziell.
- **Vitamin D3 (Flechten) + K2** (hoch) – Kaum in pflanzlicher Nahrung enthalten; besonders bei wenig Sonnenlicht.
- **Algenoel (DHA/EPA)** (hoch) – Direkte marine Omega-3-Fettsaeuren fehlen in pflanzlicher Kost; ALA-Umwandlung ist begrenzt.
- **Jod (dosiert, z.B. Algen/jodiertes Salz)** (mittel) – Ohne Fisch/Milchprodukte haeufig knapp; Ueberdosierung (Kelp) jedoch vermeiden.
- **Selen (z.B. 1-2 Paranuesse) & Zink im Blick behalten** (niedrig) – Pflanzenkost kann grenzwertig sein; ueber Nahrung meist deckbar.

## Rezept-Naehrstoff-Tags

Level: `none < low < medium < high`. Diese Tags treiben das genetische Ranking.

- `saturated_fat` – Gesaettigte Fettsaeuren (Kokosmilch hoch, sonst niedrig)
- `sodium` – Natrium/Salz (Tamari, Salz, Ketchup)
- `glycemic_load` – Glykaemische Last (staerke-/zuckerreich vs. Cauliflower/Chickpea-Rice)
- `fiber` – Ballaststoffe
- `folate` – Folat (Linsen, Kichererbsen, Spinat, Bohnen)
- `iron_nonheme` – Nicht-Haem-Eisen (Huelsenfruechte, Spinat)
- `vitamin_c` – Vitamin C (Paprika, Zitrone, Tomate, Beeren) – steigert Eisenaufnahme
- `beta_carotene` – Provitamin-A-Carotinoide (Karotte, Suesskartoffel, Kuerbis, Spinat)
- `omega3_ala` – Pflanzliches ALA-Omega-3 (Lein, Chia, Walnuss, Hanf)
- `cruciferous` – Kreuzbluetler (Brokkoli, Kohl, Blumenkohl)
- `antioxidants` – Polyphenole/Antioxidantien (Beeren, Granatapfel, Kakao, Kraeuter, Oliven)
- `added_sugar` – Zugesetzter Zucker (Ahornsirup, Honig, Trockenfruechte, Ketchup)
- `purines` – Purine (Pilze, Huelsenfruechte)
- `oxalate` – Oxalat (Spinat, Suesskartoffel, Mandel)
- `legume_protein` – Huelsenfrucht-Protein (Linsen, Kichererbsen, Bohnen)
- `caffeine_theobromine` – Koffein/Theobromin (Kakao)
- `potassium` – Kalium (Huelsenfruechte, Suesskartoffel, Gruenzeug, Tomate) – Gegenspieler zu Natrium
- `choline` – Cholin (auf veganer Kost strukturell knapp; etwas in Huelsenfruechten, Kreuzbluetlern, Samen)
- `riboflavin_b2` – Riboflavin/B2 (Naehrhefe, Mandeln, Pilze, Gruenzeug) – Kofaktor der MTHFR
- `omega6_linoleic` – Omega-6-Linolsaeure (Samenoele, viele Nuesse) – hohes n-6:n-3 hemmt die FADS1-Umwandlung
- `gluten_free` (bool) – Von Natur aus glutenfrei (bei GF-Tamari/Gewuerzen)
- `dairy_free` (bool) – Milchfrei
- `contains_alcohol` (bool) – Enthaelt relevanten Alkohol (nur vernachlaessigbar in Essig)
- `b12_fortified` (bool) – Enthaelt potenziell mit B12 angereicherte Zutat (angereicherte Naehrhefe/Pflanzendrink)

## Quellen (Auswahl)

- **MCM6/LCT** (rs4988235): Enattah 2002; gut etabliert
- **MCM6/LCT** (rs182549): LD-Proxy zu rs4988235
- **CYP1A2** (rs762551): Cornelis 2006
- **MTHFR (C677T)** (rs1801133): Frosst 1995; gut etabliert
- **MTHFR (A1298C)** (rs1801131): Weisberg 1998
- **APOE** (rs429358): APOE-Isoformen, etabliert
- **FADS1** (rs174537): Ameur 2012; Schaeffer 2006
- **FADS1** (rs174546): LD-Proxy zu rs174537
- **HFE (C282Y)** (rs1800562): Feder 1996; gut etabliert
- **HFE (H63D)** (rs1799945): Feder 1996
- **FUT2** (rs601338): Hazra 2008 (Richtung uneinheitlich)
- **TCF7L2** (rs7903146): Grant 2006; gut etabliert
- **FTO** (rs9939609): Frayling 2007
- **FTO (kausal)** (rs1421085): Claussnitzer 2015
- **MC4R** (rs17782313): Loos 2008
- **GC (Vitamin-D-Bindungsprotein)** (rs2282679): Wang 2010 (GWAS Vitamin D)
- **BCO1** (rs7501331): Leung 2009
- **SOD2** (rs4880): Sutton 2003
- **TAS2R38** (rs713598): Kim 2003
- **HLA-DQA1 (DQ2.5-Tag)** (rs2187668): Monsuur 2008 (DQ2.5-Tag)
- **ALDH2** (rs671): gut etabliert (v.a. ostasiatische Populationen)
- **AGT (M235T)** (rs699): Sethi 2003 (Richtung nutrigenetisch vertretbar)
- **TCN2 (P259R)** (rs1801198): Namour 2001
- **MTR (A2756G)** (rs1805087): Harmon 1999 (Richtung in der Literatur uneinheitlich)
- **MTHFD1 (R653Q)** (rs2236225): Brody 2002
- **PEMT (V175M)** (rs7946): da Costa 2006
