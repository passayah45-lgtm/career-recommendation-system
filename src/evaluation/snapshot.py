# The frozen 50-career catalogue (dataset v1.2.0) behind every saved evaluation report
# Future additions to data/raw never change these results; the files are checked against SHA-256 values

import hashlib
import json
from functools import lru_cache
from pathlib import Path

from src.services.catalog import DatasetError, load_catalog

EVALUATION_CATALOG_DIR = Path(__file__).resolve().parents[2] / "data" / "evaluation" / "catalog_v1.2.0"
SNAPSHOT_FILES = ("careers.csv", "resources.csv", "skill_aliases.csv")
# The 8 categories of the snapshot, in report order; new live categories never enter the saved reports
EVALUATION_CATEGORIES = (
    "Data and AI", "Software", "Cybersecurity", "Design",
    "Business", "Education", "Healthcare", "Engineering",
)


def snapshot_manifest(data_dir=EVALUATION_CATALOG_DIR):
    return json.loads((Path(data_dir) / "dataset_manifest.json").read_text(encoding="utf-8"))


def verify_snapshot(data_dir=EVALUATION_CATALOG_DIR):
    # Returns a list of files whose bytes differ from the recorded SHA-256 values
    expected = snapshot_manifest(data_dir).get("sha256", {})
    changed = []
    for name in SNAPSHOT_FILES:
        digest = hashlib.sha256((Path(data_dir) / name).read_bytes()).hexdigest()
        if expected.get(name) != digest:
            changed.append(name)
    return changed


@lru_cache(maxsize=1)
def load_evaluation_catalog():
    # Catalog for reproducing the saved 50-career evaluation; refuses a modified snapshot
    changed = verify_snapshot()
    if changed:
        raise DatasetError(f"The evaluation snapshot was modified: {', '.join(changed)}")
    return load_catalog(EVALUATION_CATALOG_DIR)
