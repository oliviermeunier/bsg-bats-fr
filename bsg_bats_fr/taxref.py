"""Mapping between BSG-BATS species labels and French TaxRef identifiers.

TaxRef is the French national taxonomic reference maintained by MNHN / PatriNat.
Each species has a stable ``cdNom`` integer identifier used as the primary key
in the French biodiversity data standard SINP.

**Status**: this mapping is a *placeholder* for the PoC. It is NOT yet validated
against the current TaxRef version. A French chiropterologist must review every
row before the outputs of this tool are ingested into any production SINP / GBIF
/ GeoNature pipeline.

All ``cd_nom`` values are set to ``None`` until that review happens. The JSON
output of the PoC therefore carries the Latin binomial (authoritative) and an
explicit ``cd_nom: null``, which is honest and non-breaking.
"""

from __future__ import annotations

from typing import TypedDict


class TaxRefEntry(TypedDict):
    scientific_name: str
    cd_nom: int | None
    notes: str | None


BSG_BATS_TO_TAXREF: dict[str, TaxRefEntry] = {
    "Barbastella_barbastellus": {
        "scientific_name": "Barbastella barbastellus",
        "cd_nom": None,
        "notes": None,
    },
    "Eptesicus_nilssonii": {
        "scientific_name": "Eptesicus nilssonii",
        "cd_nom": None,
        "notes": None,
    },
    "Eptesicus_serotinus": {
        "scientific_name": "Eptesicus serotinus",
        "cd_nom": None,
        "notes": None,
    },
    "Hypsugo_savii": {
        "scientific_name": "Hypsugo savii",
        "cd_nom": None,
        "notes": None,
    },
    "Miniopterus_schreibersii": {
        "scientific_name": "Miniopterus schreibersii",
        "cd_nom": None,
        "notes": None,
    },
    "Myotis_alcathoe": {
        "scientific_name": "Myotis alcathoe",
        "cd_nom": None,
        "notes": None,
    },
    "Myotis_crypticus": {
        "scientific_name": "Myotis crypticus",
        "cd_nom": None,
        "notes": "recently described (Ruedi et al. 2019); check TaxRef v17+ coverage",
    },
    "Myotis_daubentonii": {
        "scientific_name": "Myotis daubentonii",
        "cd_nom": None,
        "notes": None,
    },
    "Nyctalus_leisleri": {
        "scientific_name": "Nyctalus leisleri",
        "cd_nom": None,
        "notes": None,
    },
    "Nyctalus_noctula": {
        "scientific_name": "Nyctalus noctula",
        "cd_nom": None,
        "notes": None,
    },
    "Pipistrellus_kuhlii": {
        "scientific_name": "Pipistrellus kuhlii",
        "cd_nom": None,
        "notes": None,
    },
    "Pipistrellus_nathusii": {
        "scientific_name": "Pipistrellus nathusii",
        "cd_nom": None,
        "notes": None,
    },
    "Pipistrellus_pipistrellus": {
        "scientific_name": "Pipistrellus pipistrellus",
        "cd_nom": None,
        "notes": None,
    },
    "Pipistrellus_pygmaeus": {
        "scientific_name": "Pipistrellus pygmaeus",
        "cd_nom": None,
        "notes": None,
    },
    "Plecotus_auritus": {
        "scientific_name": "Plecotus auritus",
        "cd_nom": None,
        "notes": None,
    },
    "Plecotus_austriacus": {
        "scientific_name": "Plecotus austriacus",
        "cd_nom": None,
        "notes": None,
    },
    "Rhinolophus_euryale": {
        "scientific_name": "Rhinolophus euryale",
        "cd_nom": None,
        "notes": None,
    },
    "Rhinolophus_ferrumequinum": {
        "scientific_name": "Rhinolophus ferrumequinum",
        "cd_nom": None,
        "notes": None,
    },
    "Rhinolophus_hipposideros": {
        "scientific_name": "Rhinolophus hipposideros",
        "cd_nom": None,
        "notes": None,
    },
    "Tadarida_teniotis": {
        "scientific_name": "Tadarida teniotis",
        "cd_nom": None,
        "notes": None,
    },
    "Vespertilio_murinus": {
        "scientific_name": "Vespertilio murinus",
        "cd_nom": None,
        "notes": None,
    },
    "Background": {
        "scientific_name": "Background",
        "cd_nom": None,
        "notes": "non-bat class — never ingested as an observation",
    },
}


def lookup(label: str) -> TaxRefEntry:
    """Look up a BSG-BATS species label, returning a safe fallback entry."""
    entry = BSG_BATS_TO_TAXREF.get(label)
    if entry is not None:
        return entry
    return {
        "scientific_name": label.replace("_", " "),
        "cd_nom": None,
        "notes": "unknown BSG-BATS label — mapping missing",
    }
