"""Tests des VCF/gVCF-Parsers: pysam-Pfad, gVCF-Bloecke, Streaming-Fallback."""
import gzip
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dnadiet import panel as P
from dnadiet.vcf_profile import detect_build_from_header, extract_profile

HEADER = """##fileformat=VCFv4.2
##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">
##FORMAT=<ID=GQ,Number=1,Type=Integer,Description="GQ">
##FORMAT=<ID=DP,Number=1,Type=Integer,Description="DP">
##INFO=<ID=END,Number=1,Type=Integer,Description="END">
##contig=<ID=chr1,length=248956422>
##contig=<ID=chr2,length=242193529>
##contig=<ID=chr10,length=133797422>
#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tSAMPLE
"""


def _panel_by_id():
    return {s["rsid"]: s for s in P.load_panel()["snps"]}


def _vcf_lines():
    by = _panel_by_id()
    lines = HEADER
    for rsid, gt in [("rs1801133", "0/1"), ("rs7903146", "1/1"), ("rs4988235", "0/1")]:
        s = by[rsid]
        c = s["grch38"]
        lines += f"chr{c['chrom']}\t{c['pos']}\t.\t{s['ref']}\t{s['alt']}\t50\tPASS\t.\tGT:GQ:DP\t{gt}:99:30\n"
    return lines


def test_detect_build():
    assert detect_build_from_header(HEADER) == "GRCh38"
    h37 = HEADER.replace("248956422", "249250621")
    assert detect_build_from_header(h37) == "GRCh37"


def test_stream_fallback(tmp_path):
    """Reine gzip-Datei -> Streaming-Parser (kein pysam-Index noetig)."""
    path = tmp_path / "sample.vcf.gz"
    with gzip.open(path, "wt") as f:
        f.write(_vcf_lines())
    panel = P.load_panel()
    prof = extract_profile(str(path), panel, assume_ref_if_missing=True)
    g = prof["genotypes"]
    assert g["rs1801133"]["genotype"] == "GA"
    assert g["rs7903146"]["genotype"] == "TT"
    assert g["rs4988235"]["genotype"] == "GA"
    # nicht vorhandene Position -> assumed-ref, niedrige Konfidenz
    assert g["rs671"]["source"] == "assumed-ref"
    assert g["rs671"]["confidence"] == "niedrig"


def test_pysam_path_and_gvcf(tmp_path):
    try:
        import pysam
    except ImportError:
        return  # in CI ohne pysam uebersprungen
    by = _panel_by_id()
    plain = tmp_path / "s.vcf"
    lines = _vcf_lines()
    # gVCF-Referenzblock ueber rs9939609
    s = by["rs9939609"]; c = s["grch38"]
    lines += f"chr{c['chrom']}\t{c['pos']-4}\t.\t{s['ref']}\t<NON_REF>\t.\t.\tEND={c['pos']+4}\tGT:DP\t0/0:22\n"
    # chr16-Contig ergaenzen
    lines = lines.replace("##contig=<ID=chr10,length=133797422>\n",
                          "##contig=<ID=chr10,length=133797422>\n##contig=<ID=chr16,length=90338345>\n")
    plain.write_text(lines)
    gz = str(plain) + ".gz"
    pysam.tabix_compress(str(plain), gz, force=True)
    pysam.tabix_index(gz, preset="vcf", force=True)

    prof = extract_profile(gz, P.load_panel(), assume_ref_if_missing=True)
    assert prof["engine"] == "pysam"
    g = prof["genotypes"]
    assert g["rs1801133"]["genotype"] == "GA"
    # gVCF-Block -> hom-ref
    assert g["rs9939609"]["source"] == "gvcf-ref"
    assert g["rs9939609"]["genotype"] == s["ref"] * 2


def test_resolver_overrides_coords(tmp_path):
    """coord_resolver (simuliert Ensembl) hat Vorrang vor Panel-Fallback."""
    path = tmp_path / "s.vcf.gz"
    with gzip.open(path, "wt") as f:
        f.write(_vcf_lines())
    panel = P.load_panel()
    by = _panel_by_id()
    resolver = lambda rsid: (
        {"chrom": by[rsid]["grch38"]["chrom"], "pos": by[rsid]["grch38"]["pos"],
         "ref": by[rsid]["ref"], "alt": by[rsid]["alt"]} if rsid in by else None)
    prof = extract_profile(str(path), panel, coord_resolver=resolver, assume_ref_if_missing=True)
    assert prof["assembly"] == "GRCh38"
    assert prof["genotypes"]["rs1801133"]["genotype"] == "GA"


if __name__ == "__main__":
    import tempfile
    import pathlib
    test_detect_build()
    print("OK test_detect_build")
    for fn in (test_stream_fallback, test_pysam_path_and_gvcf, test_resolver_overrides_coords):
        with tempfile.TemporaryDirectory() as d:
            fn(pathlib.Path(d))
            print("OK", fn.__name__)
    print("Alle Tests bestanden.")
