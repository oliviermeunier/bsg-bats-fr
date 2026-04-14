"""Download and cache the upstream BSG-BATS package from Zenodo."""

from __future__ import annotations

import hashlib
import os
import urllib.request
import zipfile
from pathlib import Path

ZENODO_URL = "https://zenodo.org/records/15495676/files/bsgbat.zip?download=1"
ZIP_MD5 = "2c61c47394941d6429600fd7089058b7"
ZIP_NAME = "bsgbat.zip"


def default_cache_dir() -> Path:
    base = os.environ.get("BSG_BATS_FR_CACHE")
    if base:
        return Path(base)
    xdg = os.environ.get("XDG_CACHE_HOME", str(Path.home() / ".cache"))
    return Path(xdg) / "bsg-bats-fr"


def _md5sum(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_bsgbat(cache_dir: Path | None = None) -> Path:
    """Download + verify + extract bsgbat.zip if not already present.

    Returns the path to the extracted ``bsgbat/`` directory.
    Idempotent: if the directory already exists, returns it directly.
    """
    cache = (cache_dir or default_cache_dir()).expanduser()
    cache.mkdir(parents=True, exist_ok=True)

    extracted = cache / "bsgbat"
    if extracted.is_dir() and (extracted / "models").is_dir():
        return extracted

    zip_path = cache / ZIP_NAME
    if not zip_path.exists() or _md5sum(zip_path) != ZIP_MD5:
        print(f"[bsg-bats-fr] Downloading bsgbat.zip from Zenodo -> {zip_path}")
        urllib.request.urlretrieve(ZENODO_URL, zip_path)
        got = _md5sum(zip_path)
        if got != ZIP_MD5:
            raise RuntimeError(
                f"MD5 mismatch for {zip_path}: expected {ZIP_MD5}, got {got}"
            )
        print("[bsg-bats-fr] MD5 verified")

    print(f"[bsg-bats-fr] Extracting to {cache}")
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(cache)

    if not (extracted / "models").is_dir():
        raise RuntimeError(f"Extraction produced no models/ dir under {extracted}")
    return extracted
