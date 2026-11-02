# SHA-256 pins for the published eval64_v1 reports, so public CI protects them without the withheld labels
# Values were taken from commit b861aed, where these files were last changed; never update them to make a test pass

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

from src.evaluation import independent_64_evaluation as ev

ROOT = Path(__file__).resolve().parents[1]
PUBLISHED_EVAL64_SHA256 = {
    "reports/evaluation_64/bias_analysis.csv": "6457a5f77b500a36726efccee12fa727b93075bb91c64d413214488076dd33dd",
    "reports/evaluation_64/career_coverage.csv": "206ebfb337d35440de5ca65622fb993ef0b7a71b6d3997d445f112c1edaf8948",
    "reports/evaluation_64/category_metrics.csv": "114bd3815630bfe3bc97199c2df7ffb2dab8407162c211c30ea8badb06ba367b",
    "reports/evaluation_64/charts/career_exposure.png": "75b42ea87300ed27ec52047308c9a8d04ab3190766e77c5e36181940e73725ae",
    "reports/evaluation_64/charts/category_ndcg.png": "12585c6b8a0007d15b5bc0139172e87f8f986a665b284c380bacd1a954d4de6d",
    "reports/evaluation_64/charts/original_vs_new.png": "f7c978f11cb331bf685f77a91f9add0abefec1e6a1679c3082c8b348ee0a4c37",
    "reports/evaluation_64/charts/overall_metrics.png": "9fbd426e3a8ff85f7eaf02928b53933bc9a0aa922f9b2371cb87acc251462931",
    "reports/evaluation_64/charts/relevant_rank_positions.png": "8c011a37480427ea252dfba42fc1f58abebf238492f39008151956eaf37300ed",
    "reports/evaluation_64/charts/robustness.png": "f50faeac81d78abe45d21254af75825d68c7f58b1726c8aac0ba506a27514bca",
    "reports/evaluation_64/charts/score_distribution.png": "1940739ba1930c57d70cbe745103424d1affa3c1f543c18c44c596c5d679eaf2",
    "reports/evaluation_64/confidence_intervals.csv": "5ec35fe2bb10607c7d7b2981022a768d83393b4b567686c50056e63fc80c3eb5",
    "reports/evaluation_64/evaluation_summary.json": "0eef409649caf708b64b2191f3d6ef5385ad4a38ef89f20df56dcf51430f6289",
    "reports/evaluation_64/exposure_by_career.csv": "b434bd086e121d7aaea18c2aaa3e7fed83054adee8b66daaf327a4a0cbe16c38",
    "reports/evaluation_64/exposure_by_category.csv": "dd5209c9286a9a9d83a9b49645cfadd368d5359b6bdeef6c097aabf816ab79b3",
    "reports/evaluation_64/exposure_interest_frequency.csv": "e16b8cb4153eecba4aeb1f55ca52a8d6d08795f67f38e7b96fa16fc0e77906b1",
    "reports/evaluation_64/exposure_slot_drivers.csv": "f596f2b35dad3ca7d97e2edcbb54d60c381625a9eec6918c21284178dfe18681",
    "reports/evaluation_64/overall_metrics.csv": "aa33374e55e36c2e921c6dfdd948fc39b598694c0d0f324b9afc5691ef1b57c5",
    "reports/evaluation_64/profile_type_metrics.csv": "981576c87bf8e577548e5c1181472e1d343c79add9c01a5ae3a818237e6a96c0",
    "reports/evaluation_64/robustness_results.csv": "c8ad0f5233f27e367389c17fd3535cacd3454cba9143e6e88ddfae11335efdf1",
    "reports/evaluation_64/threshold_sensitivity.csv": "fc440b06ee0a9afc7457ab1b4fb17ee5f14e76212a3d3722b2de80d200bd6622",
    "reports/evaluation_64/tie_profiles.csv": "1484737a181dbfba5fd8881f6e29792e436ad43d6b168a5451383d4a6694ad1a",
    "reports/evaluation_64/tie_summary.csv": "eaf06b6601ce16fc7d3188c3343ef1ce4c569b67a864fa21262c3b82a0c888df",
    "reports/evaluation_64/vocabulary_analysis.csv": "86bc3f52c8013919a0fc1db8941a75d7fe5a67b6ef3afab3f2bb4e1c8cb74603",
    "reports/evaluation_64/vocabulary_unrecognised_terms.csv": "ae5865072e813cb71ed8f90e906569195ad74212ab5cf6cfe0b5cf6c08a0d9d7",
    "reports/evaluation_64/vocabulary_zero_recognised.csv": "298049696c6bbc6447caee7f4a3e5af6b6df64de8e554373ae6d3c80bf39b3fd",
    "reports/evaluation_64_review_design/review_sample_by_career.csv": "771faf7a28f68f2158d979b35a2b0903d1f01d0daa0453cbc8138ec02c738f75",
    "reports/evaluation_64_review_design/review_sample_by_category.csv": "d924f3c7c9d8539a3077c0e4af51ad3b96a494c758d1b473cf01b127dc045021",
    "reports/evaluation_64_review_design/review_sample_by_grade.csv": "428f318c8c83aee961cf0cefbeaa18154a57107bd86d1f23ab83df50c0985674",
    "reports/evaluation_64_review_design/review_sample_design.json": "164bb8361b21604bd6400edbb6270ead001039a042faf500425ecbfe887ab1ec",
    "reports/evaluation_64_sensitivity/interest_career_exposure.csv": "8d0275855da4732d5d3a590dc17fb1d1f730d6aea5bb952233a994e57b7ed426",
    "reports/evaluation_64_sensitivity/interest_category_exposure.csv": "2f3d9ea4f4bfec8d0a4270a547472e25308aacd8a157049d04475ae7c2ccc4f0",
    "reports/evaluation_64_sensitivity/interest_results.csv": "1e5f13250f91fa14e819eb55c11e38fdbc07ce7d56112373e0878f34baff3c4c",
    "reports/evaluation_64_sensitivity/sensitivity_summary.json": "bfc8034ac021fc57ddc6d5aa37deb316b0b180352410553ea87516d54eeae042",
    "reports/evaluation_64_sensitivity/tie_break_random_runs.csv": "0e74be7c3ef720a59d23cc6531567a1366d9f8c04f427abc17496f9626fda34d",
    "reports/evaluation_64_sensitivity/tie_break_results.csv": "6f04fe4bab176062e32f85c231fa75b4c8857ce0b6479615beb97c7d92706bfe",
}
FROZEN_DIRS = ("reports/evaluation_64", "reports/evaluation_64_sensitivity", "reports/evaluation_64_review_design")


@pytest.mark.parametrize("rel,digest", sorted(PUBLISHED_EVAL64_SHA256.items()))
def test_published_eval64_report_is_unchanged(rel, digest):
    assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == digest, rel


def test_every_published_eval64_report_is_pinned():
    # A new tracked file in a frozen report folder must be pinned deliberately, not slip in unprotected
    try:
        tracked = subprocess.run(["git", "ls-files", *FROZEN_DIRS], cwd=ROOT, capture_output=True, text=True,
                                 check=True).stdout.split()
    except (OSError, subprocess.CalledProcessError):
        pytest.skip("git is not available")
    assert set(tracked) == set(PUBLISHED_EVAL64_SHA256)


def test_frozen_summary_still_records_the_freezing_state():
    summary = json.loads((ROOT / "reports" / "evaluation_64" / "evaluation_summary.json").read_text(encoding="utf-8"))
    assert summary["data"][ev.LIVE_FIELD] is True
    assert summary["data"]["dataset_version"] == "1.3.0"


def summaries(saved_value, recomputed_value):
    return {"data": {ev.LIVE_FIELD: saved_value, "careers": 64}}, {"data": {ev.LIVE_FIELD: recomputed_value, "careers": 64}}


def test_live_field_passes_only_with_the_expected_pair(monkeypatch):
    monkeypatch.setattr(ev, "_live_version", lambda: "1.4.0")
    saved, recomputed = summaries(True, False)
    assert ev._live_field_issues(saved, recomputed) == []
    assert saved == recomputed == {"data": {"careers": 64}}


@pytest.mark.parametrize("saved_value,recomputed_value", [(False, False), (None, False), ("true", False), (True, True)])
def test_live_field_tampering_or_drift_is_reported(monkeypatch, saved_value, recomputed_value):
    monkeypatch.setattr(ev, "_live_version", lambda: "1.4.0")
    assert ev._live_field_issues(*summaries(saved_value, recomputed_value))


def test_live_field_is_compared_normally_while_live_is_v130(monkeypatch):
    monkeypatch.setattr(ev, "_live_version", lambda: "1.3.0")
    saved, recomputed = summaries(True, False)
    assert ev._live_field_issues(saved, recomputed) == []
    assert saved != recomputed
