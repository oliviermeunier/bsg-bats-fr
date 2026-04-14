"""End-to-end smoke test — runs BSG-BATS on the upstream example1.wav.

This test downloads the upstream BSG-BATS package from Zenodo the first
time it runs (~448 MB) and caches it locally. On subsequent runs the
cached copy is reused. The test asserts that the known expected species
for ``example1.wav`` is detected, matching the reference output shipped
by the upstream team in ``bsgbat/example_outfile``.
"""

from __future__ import annotations

from bsg_bats_fr.download import ensure_bsgbat
from bsg_bats_fr.infer import classify_wav
from bsg_bats_fr.sinp import to_sinp


def test_example1_barbastella_detected():
    bsgbat_dir = ensure_bsgbat()
    wav = bsgbat_dir / "data" / "example1.wav"
    assert wav.is_file(), f"missing example WAV: {wav}"

    result = classify_wav(wav)

    species = {d.species for d in result.detections}
    # Upstream reference output (bsgbat/example_outfile):
    # data/example1.wav\tBarbastella_barbastellus,3,Background,8
    assert "Barbastella_barbastellus" in species, (
        f"expected Barbastella_barbastellus in detections, got {species}"
    )


def test_sinp_payload_roundtrip():
    bsgbat_dir = ensure_bsgbat()
    wav = bsgbat_dir / "data" / "example1.wav"
    result = classify_wav(wav)

    payload = to_sinp(
        result,
        observer="ci-smoke-test",
        date_observation="2026-04-14T22:00:00+02:00",
        latitude=47.3220,
        longitude=5.0415,
    )

    assert payload["schemaVersion"] == "bsg-bats-fr/0.1.0"
    assert payload["observateur"] == "ci-smoke-test"
    assert payload["geometrie"]["type"] == "Point"
    assert payload["geometrie"]["coordinates"] == [5.0415, 47.3220]

    names = {occ["nomCite"] for occ in payload["occurrences"]}
    assert "Barbastella barbastellus" in names
    assert "Background" not in names  # excluded by default

    # All cd_nom must be null for now — this is the honest contract of the PoC.
    for occ in payload["occurrences"]:
        assert occ["cdNom"] is None
