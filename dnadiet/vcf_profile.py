"""VCF/gVCF -> Genotyp-Profil an den Panel-SNPs. Wird im Colab-Notebook genutzt.

Bevorzugt pysam (schneller Tabix-Zugriff, gVCF-Bloecke, Multiallele). Ohne pysam
gibt es einen reinen Python-Fallback (ein Streaming-Durchlauf ueber die VCF).

Wichtig: Der taegliche Tracker braucht dieses Modul NICHT – er liest nur das
fertige profile.json. Koordinatengenauigkeit ist ausschliesslich hier relevant
und wird zweifach abgesichert: (1) autoritative rsID-Aufloesung ueber einen
coord_resolver (im Notebook: Ensembl), (2) REF-Allel-Abgleich gegen die VCF.
"""
from __future__ import annotations

import gzip
from typing import Callable, Optional

# chr1-Laengen zur Build-Erkennung
_CHR1_LEN = {248956422: "GRCh38", 249250621: "GRCh37", 248387328: "T2T-CHM13"}


class _NoUsableIndex(Exception):
    """Region-Fetch ohne funktionierenden Tabix-Index -> Stream-Fallback."""


def _norm_contig(chrom: str, available: set) -> Optional[str]:
    """Findet den passenden Contig-Namen (mit/ohne 'chr') in der VCF."""
    cands = [chrom, f"chr{chrom}", chrom.replace("chr", "")]
    if chrom in ("MT", "M"):
        cands += ["chrM", "MT", "M", "chrMT"]
    for c in cands:
        if c in available:
            return c
    return None


def detect_build_from_header(header_text: str) -> Optional[str]:
    """Erkennt den Build aus ##contig=<ID=chr1,length=...> oder ##reference."""
    for line in header_text.splitlines():
        if line.startswith("##contig") and ("ID=chr1," in line or "ID=1," in line):
            for tok in line.replace(">", "").split(","):
                if tok.startswith("length="):
                    try:
                        return _CHR1_LEN.get(int(tok.split("=")[1]))
                    except ValueError:
                        pass
        if line.startswith("##reference"):
            low = line.lower()
            if "38" in low or "hg38" in low:
                return "GRCh38"
            if "37" in low or "hg19" in low:
                return "GRCh37"
            if "chm13" in low or "t2t" in low:
                return "T2T-CHM13"
    return None


def _coords_for_snp(snp: dict, build: str, resolver: Optional[Callable]):
    """(chrom, pos, ref, alt) fuer einen SNP – Resolver hat Vorrang, sonst Panel-Fallback."""
    if resolver:
        r = resolver(snp["rsid"])
        if r:
            return r["chrom"], int(r["pos"]), r.get("ref"), r.get("alt")
    key = "grch37" if build == "GRCh37" else "grch38"
    c = snp.get(key)
    if not c:
        return None
    return str(c["chrom"]), int(c["pos"]), snp.get("ref"), snp.get("alt")


# --------------------------------------------------------------------------
# pysam-Pfad
# --------------------------------------------------------------------------
def _extract_pysam(vcf_path, snps, build, resolver, assume_ref):
    import pysam

    vf = pysam.VariantFile(vcf_path)
    samples = list(vf.header.samples)
    if not samples:
        raise ValueError("VCF enthaelt keine Sample-Spalte (keine Genotypen).")
    sample = samples[0]
    available = set(vf.header.contigs)
    genotypes = {}
    warnings = []
    probed_ok = False  # mind. ein Region-Fetch war erfolgreich

    for snp in snps:
        rsid = snp["rsid"]
        coords = _coords_for_snp(snp, build, resolver)
        if not coords:
            genotypes[rsid] = {"alleles": None, "genotype": None, "source": "no-coords",
                               "confidence": "niedrig"}
            continue
        chrom, pos, exp_ref, _ = coords
        contig = _norm_contig(chrom, available)
        if contig is None:
            genotypes[rsid] = {"alleles": None, "genotype": None, "source": "no-contig",
                               "confidence": "niedrig"}
            continue

        variant_rec = None
        block_rec = None
        try:
            for rec in vf.fetch(contig, max(0, pos - 1), pos):
                real_alts = [a for a in (rec.alts or ()) if a not in ("<NON_REF>", "<*>")]
                if rec.pos == pos and real_alts:
                    variant_rec = rec
                    break
                if rec.start < pos <= rec.stop:  # gVCF-Referenzblock
                    block_rec = rec
            probed_ok = True
        except (ValueError, OSError) as e:
            # Scheitert schon der erste Region-Fetch -> kein nutzbarer Index.
            if not probed_ok:
                raise _NoUsableIndex(str(e))
            warnings.append(f"{rsid}: fetch fehlgeschlagen ({e})")

        if variant_rec is not None:
            rec = variant_rec
            gt = rec.samples[sample].get("GT")
            if gt is None or all(a is None for a in gt):
                genotypes[rsid] = {"alleles": None, "genotype": None, "source": "no-call",
                                   "confidence": "niedrig"}
                continue
            allele_map = list(rec.alleles)  # index 0 = ref
            nucs = []
            for idx in gt:
                if idx is None:
                    nucs.append(None)
                else:
                    a = allele_map[idx]
                    nucs.append(rec.ref if a in ("<NON_REF>", "<*>") else a)
            gq = rec.samples[sample].get("GQ")
            dp = rec.samples[sample].get("DP")
            ref_ok = (exp_ref is None) or (rec.ref and rec.ref[0].upper() == exp_ref.upper())
            if not ref_ok:
                warnings.append(f"{rsid}: REF {rec.ref} != erwartet {exp_ref} (Build/Strang pruefen)")
            genotypes[rsid] = {
                "alleles": [n for n in nucs if n is not None] or None,
                "genotype": "".join(n for n in nucs if n) if any(nucs) else None,
                "source": "vcf", "confidence": "hoch" if ref_ok else "niedrig",
                "gq": int(gq) if isinstance(gq, (int, float)) else None,
                "dp": int(dp) if isinstance(dp, (int, float)) else None,
                "pos": pos, "contig": contig,
            }
        elif block_rec is not None:
            gt = block_rec.samples[sample].get("GT")
            dp = block_rec.samples[sample].get("DP")
            hom_ref = gt is not None and all((a == 0) for a in gt if a is not None)
            if hom_ref and exp_ref:
                genotypes[rsid] = {
                    "alleles": [exp_ref, exp_ref], "genotype": exp_ref + exp_ref,
                    "source": "gvcf-ref", "confidence": "hoch" if (dp or 0) else "mittel",
                    "dp": int(dp) if isinstance(dp, (int, float)) else None,
                    "pos": pos, "contig": contig,
                }
            else:
                genotypes[rsid] = {"alleles": None, "genotype": None, "source": "gvcf-uncalled",
                                   "confidence": "niedrig", "pos": pos, "contig": contig}
        else:
            if assume_ref and exp_ref:
                genotypes[rsid] = {
                    "alleles": [exp_ref, exp_ref], "genotype": exp_ref + exp_ref,
                    "source": "assumed-ref", "confidence": "niedrig", "pos": pos, "contig": contig,
                }
            else:
                genotypes[rsid] = {"alleles": None, "genotype": None, "source": "absent",
                                   "confidence": "niedrig", "pos": pos, "contig": contig}
    return genotypes, warnings, sample


# --------------------------------------------------------------------------
# Reiner Python-Fallback (ein Streaming-Durchlauf; ohne Index langsamer)
# --------------------------------------------------------------------------
def _open_text(path):
    if str(path).endswith(".gz"):
        return gzip.open(path, "rt")
    return open(path, "rt")


def _extract_stream(vcf_path, snps, build, resolver, assume_ref):
    # Zielpositionen sammeln: (contig_normalisiert_ohne_chr, pos) -> snp
    targets = {}
    exp_ref = {}
    for snp in snps:
        coords = _coords_for_snp(snp, build, resolver)
        if coords:
            chrom, pos, er, _ = coords
            targets[(chrom.replace("chr", ""), pos)] = snp["rsid"]
            exp_ref[snp["rsid"]] = er
    found = {}
    sample = None
    with _open_text(vcf_path) as fh:
        for line in fh:
            if line.startswith("##"):
                continue
            if line.startswith("#CHROM"):
                cols = line.rstrip("\n").split("\t")
                sample = cols[9] if len(cols) > 9 else None
                continue
            cols = line.rstrip("\n").split("\t")
            if len(cols) < 10:
                continue
            chrom = cols[0].replace("chr", "")
            try:
                pos = int(cols[1])
            except ValueError:
                continue
            key = (chrom, pos)
            if key not in targets:
                continue
            rsid = targets[key]
            ref, alts = cols[3], cols[4].split(",")
            alleles = [ref] + [a for a in alts if a not in ("<NON_REF>", "<*>", ".")]
            fmt = cols[8].split(":")
            vals = cols[9].split(":")
            fd = dict(zip(fmt, vals))
            gt = fd.get("GT", "./.")
            idxs = gt.replace("|", "/").split("/")
            nucs = []
            for i in idxs:
                if i in (".", ""):
                    nucs.append(None)
                else:
                    j = int(i)
                    nucs.append(alleles[j] if j < len(alleles) else None)
            er = exp_ref.get(rsid)
            ref_ok = (er is None) or (ref[:1].upper() == er.upper())
            found[rsid] = {
                "alleles": [n for n in nucs if n] or None,
                "genotype": "".join(n for n in nucs if n) if any(nucs) else None,
                "source": "vcf", "confidence": "hoch" if ref_ok else "niedrig",
                "pos": pos, "contig": cols[0],
            }
    genotypes = {}
    warnings = []
    for snp in snps:
        rsid = snp["rsid"]
        if rsid in found:
            genotypes[rsid] = found[rsid]
        else:
            coords = _coords_for_snp(snp, build, resolver)
            er = coords[2] if coords else None
            if assume_ref and er:
                genotypes[rsid] = {"alleles": [er, er], "genotype": er + er,
                                   "source": "assumed-ref", "confidence": "niedrig"}
            else:
                genotypes[rsid] = {"alleles": None, "genotype": None, "source": "absent",
                                   "confidence": "niedrig"}
    return genotypes, warnings, sample


# --------------------------------------------------------------------------
# Oeffentliche API
# --------------------------------------------------------------------------
def extract_profile(vcf_path: str, panel: dict, coord_resolver: Optional[Callable] = None,
                    build: Optional[str] = None, sample_id: Optional[str] = None,
                    assume_ref_if_missing: bool = True) -> dict:
    """Extrahiert ein Genotyp-Profil an allen Panel-SNPs.

    vcf_path        : Pfad zur (b)gzip-komprimierten VCF/gVCF (.vcf.gz / .hc.gz).
    panel           : geladenes snp_panel.json (dict mit 'snps').
    coord_resolver  : optional callable(rsid)->{'chrom','pos','ref','alt'} (Ensembl im Notebook).
    build           : 'GRCh38'/'GRCh37'/... ; wird sonst aus dem Header erkannt.
    assume_ref_if_missing : fehlende Position in einer reinen VCF als hom-ref annehmen.
    """
    snps = panel.get("snps", [])

    # Build erkennen (nur, wenn kein Resolver autoritative Koordinaten liefert)
    if build is None:
        try:
            with _open_text(vcf_path) as fh:
                head = []
                for line in fh:
                    if not line.startswith("#"):
                        break
                    head.append(line)
                    if len(head) > 5000:
                        break
            build = detect_build_from_header("".join(head)) or "GRCh38"
        except Exception:
            build = "GRCh38"

    engine = "pysam"
    try:
        import pysam  # noqa: F401
    except ImportError:
        pysam = None
    if pysam is not None:
        try:
            genotypes, warnings, sample = _extract_pysam(
                vcf_path, snps, build, coord_resolver, assume_ref_if_missing)
        except _NoUsableIndex:
            genotypes, warnings, sample = _extract_stream(
                vcf_path, snps, build, coord_resolver, assume_ref_if_missing)
            engine = "stream-fallback (kein Tabix-Index)"
            warnings.append("Kein nutzbarer Tabix-Index – Streaming-Parser genutzt (langsamer, aber korrekt).")
        except (ValueError, OSError, NotImplementedError, RuntimeError) as e:
            # z.B. reine gzip- statt bgzf-Kompression
            genotypes, warnings, sample = _extract_stream(
                vcf_path, snps, build, coord_resolver, assume_ref_if_missing)
            engine = "stream-fallback"
            warnings.append(f"pysam-Oeffnung fehlgeschlagen ({e}) – Streaming-Parser genutzt.")
    else:
        genotypes, warnings, sample = _extract_stream(
            vcf_path, snps, build, coord_resolver, assume_ref_if_missing)
        engine = "stream"

    return {
        "schema_version": 1,
        "sample_id": sample_id or sample,
        "assembly": "GRCh38" if coord_resolver else build,
        "engine": engine,
        "panel_rsids": [s["rsid"] for s in snps],
        "warnings": warnings,
        "genotypes": genotypes,
    }
