# The v1.4.0 taxonomy evaluation: frozen snapshot, reproducible outputs, no change to earlier studies

import csv
import json
from pathlib import Path

import pytest

from src.data.interest_taxonomy import CURRENT_TAXONOMY, LEGACY_TAXONOMY
from src.evaluation import taxonomy_v140_evaluation as tv
from src.evaluation.eval64_data import verify_frozen
from src.evaluation.snapshot import verify_snapshot as verify_original_snapshot
from src.services.catalog import load_catalog
from tests.conftest import needs_eval64_labels

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "evaluation_v1_4_0"


def test_snapshot_is_frozen_and_uses_taxonomy_2():
    assert tv.verify_snapshot() == []
    catalog = load_catalog(tv.SNAPSHOT_DIR)
    assert catalog.interest_taxonomy == CURRENT_TAXONOMY and len(catalog.careers) == 64
    assert all(len(c.interests) == 3 for c in catalog.careers)


def test_snapshot_is_never_overwritten():
    with pytest.raises(tv.SnapshotError):
        tv.freeze()


def test_earlier_snapshots_are_untouched_and_legacy():
    assert verify_original_snapshot() == []
    assert load_catalog(ROOT / "data" / "evaluation" / "catalog_v1.3.0").interest_taxonomy == LEGACY_TAXONOMY


@needs_eval64_labels
def test_frozen_eval64_inputs_are_untouched():
    # verify_frozen hashes the withheld labels file too, so it runs only where the labels exist
    assert verify_frozen() == []


def test_published_outputs_hold_no_per_pair_labels():
    assert {p.name for p in OUT.iterdir()} == set(tv.OUTPUT_FILES)
    for name in (tv.COMPARISON_FILE, tv.CATEGORY_FILE, tv.MIGRATION_FILE):
        with open(OUT / name, newline="", encoding="utf-8") as f:
            header = next(csv.reader(f))
        assert not {"grade", "career_id", "ranking", "top5", "relevant_ranks"} & set(header), name
    summary = json.loads((OUT / tv.SUMMARY_FILE).read_text(encoding="utf-8"))
    assert "Owner-authorized" in summary["status"] and summary["limitations"]


def test_profile_migration_counts_are_consistent():
    with open(OUT / tv.MIGRATION_FILE, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 111
    for r in rows:
        assert int(r["interests_before"]) == int(r["migrated"]) + int(r["retired"]) + int(r["unknown"])
        assert int(r["interests_after"]) <= int(r["migrated"])


@needs_eval64_labels
def test_outputs_reproduce_exactly():
    assert tv.check_outputs(OUT) == []


@needs_eval64_labels
def test_condition_a_reproduces_the_frozen_eval64_results():
    summary = json.loads((OUT / tv.SUMMARY_FILE).read_text(encoding="utf-8"))
    frozen = json.loads((ROOT / "reports" / "evaluation_64" / "evaluation_summary.json").read_text(encoding="utf-8"))
    assert summary["data"]["a_reproduces_frozen_eval64_v1"] is True
    for name, stats in frozen["overall"].items():
        assert summary["overall"]["A_v130_original"][name]["mean"] == stats["mean"], name
