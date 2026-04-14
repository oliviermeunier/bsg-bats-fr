"""Minimal SINP-compatible JSON serializer.

SINP (Système d'Information sur la Nature et les Paysages) is the French
national biodiversity data standard. Its ``Occurrences de taxons`` schema
defines the canonical fields for a single observation record.

This module emits a **minimal** SINP-compatible payload carrying only the
fields that can be derived directly from a BSG-BATS classification plus
the acquisition metadata passed in by the caller. It is intentionally a
seed: a production ingestion pipeline will need to add deployment
metadata (device type, microphone, gain settings…), validate cd_nom
values against a live TaxRef snapshot, and handle observer identity
according to the source SINP platform.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from .infer import InferenceResult
from .taxref import lookup as taxref_lookup


def to_sinp(
    result: InferenceResult,
    *,
    observer: str,
    date_observation: str,
    latitude: float | None = None,
    longitude: float | None = None,
    device: str = "AudioMoth",
    exclude_background: bool = True,
) -> dict[str, Any]:
    """Convert an ``InferenceResult`` into a minimal SINP JSON payload.

    ``date_observation`` must be an ISO-8601 string (e.g. ``2026-04-14T22:15:00+02:00``).
    Coordinates, when provided, are in WGS84 decimal degrees.

    The payload intentionally carries ``cd_nom: null`` for every species
    until the TaxRef mapping has been validated — see :mod:`bsg_bats_fr.taxref`.
    """
    try:
        datetime.fromisoformat(date_observation)
    except ValueError as exc:
        raise ValueError(
            f"date_observation must be ISO-8601 (got {date_observation!r})"
        ) from exc

    geom: dict[str, Any] | None = None
    if latitude is not None and longitude is not None:
        geom = {
            "type": "Point",
            "coordinates": [longitude, latitude],
            "crs": "EPSG:4326",
        }

    occurrences: list[dict[str, Any]] = []
    for det in result.detections:
        if exclude_background and det.species == "Background":
            continue
        taxref = taxref_lookup(det.species)
        occurrences.append(
            {
                "nomCite": taxref["scientific_name"],
                "cdNom": taxref["cd_nom"],
                "nomCiteNotes": taxref["notes"],
                "nombreDetections": det.count,
                "segmentsDetectes": det.segments,
                "methode": "acoustic classifier",
                "sourceModele": f"BSG-BATS {result.model}",
            }
        )

    return {
        "schemaVersion": "bsg-bats-fr/0.1.0",
        "notesCompatibiliteSinp": (
            "Seed SINP payload — cdNom values are intentionally null until a "
            "French chiropterologist validates the TaxRef mapping. Do NOT ingest "
            "this payload into a production SINP / GBIF / GeoNature pipeline "
            "as-is."
        ),
        "observateur": observer,
        "dateObservation": date_observation,
        "geometrie": geom,
        "dispositif": device,
        "fichierSource": result.wav_path,
        "modele": {
            "nom": "BSG-BATS",
            "version": result.model,
            "fichierEspeces": result.species_file,
            "seuilLogit": result.logit_threshold,
            "nSegments": result.n_segments,
        },
        "occurrences": occurrences,
    }
