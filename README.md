# bsg-bats-fr

**French-ecosystem integration layer for [BSG-BATS](https://zenodo.org/records/15495676), the open-source European bat acoustic classifier published by Meramo et al. (2026).**

> ⚠️ **This repository is the public proof-of-concept (PoC) that accompanies an NLnet NGI Zero Commons Fund proposal submitted in May 2026.** It is a *seed* — not a final tool. The goal is to make a single, verifiable claim: **the author can take the published BSG-BATS model, run it end-to-end on a WAV file, and emit a French-biodiversity-standard payload, with CI proof.**
>
> Nothing more is claimed by this repository. The rest — lightweight desktop GUI, extension of the model to missing French *Myotis* species, phonic-group classification, GeoNature integration — is described in the NLnet proposal and is deliberately *not* implemented here.

[![CI](https://github.com/oliviermeunier/bsg-bats-fr/actions/workflows/ci.yml/badge.svg)](https://github.com/oliviermeunier/bsg-bats-fr/actions/workflows/ci.yml)
[![License: EUPL 1.2](https://img.shields.io/badge/License-EUPL_1.2-blue.svg)](./LICENSE)

## What this does

Given a WAV recording of bat echolocation calls (typically from an
[AudioMoth](https://www.openacousticdevices.info/audiomoth) or similar ultrasonic
device), `bsg-bats-fr`:

1. **Downloads and verifies** the upstream BSG-BATS package (`bsgbat.zip`,
   ~448 MB) from [Zenodo record 15495676](https://zenodo.org/records/15495676)
   on first use, and caches it locally in `~/.cache/bsg-bats-fr/`. MD5 is
   checked against the published value.
2. **Runs inference** using the upstream ensemble model (`model_v0.21_r1.pt`
   by default) without retraining, quantization, or modification. The upstream
   `supervised.py` and `data384.py` modules are imported verbatim via
   `sys.path` injection — no vendoring, no divergence.
3. **Serializes the detections** into a JSON payload that follows a minimal,
   SINP-compatible schema — the French national biodiversity data standard.
   Observer, ISO-8601 date, WGS84 coordinates and recording device are all
   carried as first-class fields.

The result is written to stdout or to a file, and can be inspected by hand,
fed into a GeoNature ingestion pipeline, or diffed against previous runs.

## What this does *not* do (yet)

- No training, fine-tuning, or extension of the BSG-BATS model.
- No coverage of the missing common French *Myotis* species
  (*M. mystacinus*, *M. brandtii*, *M. nattereri*, *M. bechsteinii*,
  *M. emarginatus*, *M. myotis*, *M. blythii*) — those are listed as
  next steps in the upstream paper and are the subject of the NLnet proposal.
- No phonic-group classification.
- No desktop GUI.
- No validated TaxRef `cdNom` mapping — **every `cdNom` is currently `null`**
  on purpose, pending review by a French chiropterologist. The Latin
  binomial is authoritative. See
  [`bsg_bats_fr/taxref.py`](./bsg_bats_fr/taxref.py) for the full statement.
- No direct GeoNature database write.

If any of these matter to you *now*, this is not the right tool yet — please
track the NLnet proposal.

## Why this exists

The BSG-BATS authors (Meramo, Somervuo, Rannisto, Ovaskainen, Lilley at SLU
Uppsala and the University of Helsinki) published in 2026 a state-of-the-art
CNN classifier for 21 European bat species, trained against a large annotated
dataset from the LIFEPLAN ERC Synergy programme. The model is
benchmark-competitive, open-source, and directly runnable on a laptop CPU.

However, in their *Next steps* section the paper explicitly lists three
unresolved practical gaps:

1. The Python-only interface is not usable by non-coder field naturalists.
2. Several common French *Myotis* species are not yet in the training set.
3. Phonic-group workflows (essential in French protocols) are future work.

This PoC — and, beyond it, the [NLnet proposal](https://github.com/oliviermeunier/bsg-bats-fr) —
is positioned as a **French-ecosystem integration layer** that addresses these
gaps from the French end, in explicit coordination with the upstream BSG-BATS
team. It is *not* a fork. It is *not* a competitor. It is a companion.

## Install

```bash
git clone https://github.com/oliviermeunier/bsg-bats-fr.git
cd bsg-bats-fr
pip install -e .
```

Python ≥3.10 is required. PyTorch CPU is sufficient — no GPU is needed.
On first run, ~448 MB will be downloaded from Zenodo and cached under
`~/.cache/bsg-bats-fr/`.

## Usage

```bash
bsg-bats-fr path/to/recording.wav \
  --observer "Jean Dupont" \
  --date "2026-04-14T22:15:00+02:00" \
  --lat 47.3220 \
  --lon 5.0415 \
  --device "AudioMoth 1.2.0" \
  --output recording.sinp.json
```

Output (truncated):

```json
{
  "schemaVersion": "bsg-bats-fr/0.1.0",
  "observateur": "Jean Dupont",
  "dateObservation": "2026-04-14T22:15:00+02:00",
  "geometrie": { "type": "Point", "coordinates": [5.0415, 47.322], "crs": "EPSG:4326" },
  "dispositif": "AudioMoth 1.2.0",
  "modele": { "nom": "BSG-BATS", "version": "model_v0.21_r1.pt", "nSegments": 42, "seuilLogit": 0.0 },
  "occurrences": [
    {
      "nomCite": "Barbastella barbastellus",
      "cdNom": null,
      "nombreDetections": 3,
      "segmentsDetectes": [5, 8, 12],
      "methode": "acoustic classifier",
      "sourceModele": "BSG-BATS model_v0.21_r1.pt"
    }
  ]
}
```

Pass `--raw` to emit the untransformed inference result instead of the SINP
payload.

## Tests

```bash
pip install pytest
pytest -v tests/
```

The smoke test runs the full pipeline against the upstream `example1.wav`
(shipped inside `bsgbat.zip`) and asserts that *Barbastella barbastellus* is
detected, matching the reference output in `bsgbat/example_outfile`. The
test also validates the SINP serializer.

The smoke test is executed on every push in
[`.github/workflows/ci.yml`](./.github/workflows/ci.yml). The CI badge at
the top of this README is the canonical proof that the PoC runs end-to-end.

## Acknowledgements

- **BSG-BATS team** — Katarina Meramo, Panu Somervuo, Juho Rannisto, Otso
  Ovaskainen, Thomas M. Lilley (SLU Uppsala, University of Helsinki).
  The model, the annotated dataset, and the paper are theirs. This PoC is
  built on top of their work in explicit coordination.
- **LIFEPLAN** — ERC Synergy programme for the European biodiversity
  monitoring infrastructure that produced the training data.
- **Vigie-Chiro / MNHN** — historical French bat acoustic monitoring network
  (Yves Bas and colleagues) that this project coordinates with rather than
  competes against.

## License

EUPL-1.2 — see [LICENSE](./LICENSE). The upstream BSG-BATS code is
downloaded at runtime from Zenodo and retains its original license; this
repository does not redistribute upstream artifacts.

## Citation

If you use this tool, please cite the upstream paper first:

> Meramo, K., Somervuo, P., Rannisto, J., Ovaskainen, O., & Lilley, T. M.
> (2026). *BSG-BATS: An open-source data annotation portal and classifier
> for European bat vocalizations.* Methods in Ecology and Evolution.
> https://doi.org/10.1111/2041-210x.70220
