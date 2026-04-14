"""Run BSG-BATS inference on a WAV file and return structured detections.

This is a thin wrapper over the upstream BSG-BATS ``classify.py`` script.
It does NOT retrain, quantize, or alter the model — it only:

1. Ensures the upstream package is downloaded and extracted (via download.py)
2. Injects the upstream ``code/`` directory into ``sys.path`` so its modules
   (``supervised``, ``data384``) can be imported
3. Runs the inference loop from ``supervised.classify1_cpu``
4. Emits a typed Python dict that can be serialized to JSON / SINP
"""

from __future__ import annotations

import importlib
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import torch

from .download import ensure_bsgbat

LOGIT_THRESHOLD = 0.0
DEFAULT_MODEL = "model_v0.21_r1.pt"
SPECIES_FILE = "species21bg"


@dataclass
class Detection:
    species: str
    count: int
    segments: list[int] = field(default_factory=list)


@dataclass
class InferenceResult:
    wav_path: str
    model: str
    species_file: str
    logit_threshold: float
    n_segments: int
    detections: list[Detection]

    def to_dict(self) -> dict[str, Any]:
        return {
            "wav_path": self.wav_path,
            "model": self.model,
            "species_file": self.species_file,
            "logit_threshold": self.logit_threshold,
            "n_segments": self.n_segments,
            "detections": [
                {"species": d.species, "count": d.count, "segments": d.segments}
                for d in self.detections
            ],
        }


def _load_upstream(bsgbat_dir: Path):
    code_dir = str(bsgbat_dir / "code")
    if code_dir not in sys.path:
        sys.path.insert(0, code_dir)
    supervised = importlib.import_module("supervised")
    data384 = importlib.import_module("data384")
    return supervised, data384


def classify_wav(
    wav_path: str | Path,
    model_filename: str = DEFAULT_MODEL,
    logit_threshold: float = LOGIT_THRESHOLD,
) -> InferenceResult:
    """Run a single WAV file through BSG-BATS and return structured detections."""
    wav_path = Path(wav_path)
    if not wav_path.is_file():
        raise FileNotFoundError(wav_path)

    bsgbat_dir = ensure_bsgbat()
    supervised, data384 = _load_upstream(bsgbat_dir)

    species_path = bsgbat_dir / "models" / SPECIES_FILE
    model_path = bsgbat_dir / "models" / model_filename

    species = data384.read_filelist(str(species_path))
    nspecies = len(species)

    device = torch.device("cpu")
    model = supervised.Net(nclasses=nspecies)
    model.load_state_dict(torch.load(str(model_path), map_location=device))
    model.eval()

    dat = data384.wav2spectrograms(str(wav_path))
    logits = supervised.classify1_cpu(dat, model, nspecies)

    detections: list[Detection] = []
    for i in range(nspecies):
        above = np.where(logits[:, i] > logit_threshold)[0]
        if above.size > 0:
            detections.append(
                Detection(
                    species=species[i],
                    count=int(above.size),
                    segments=[int(x) for x in above.tolist()],
                )
            )

    return InferenceResult(
        wav_path=str(wav_path),
        model=model_filename,
        species_file=SPECIES_FILE,
        logit_threshold=logit_threshold,
        n_segments=int(logits.shape[0]),
        detections=detections,
    )
