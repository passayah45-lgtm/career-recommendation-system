# The Analytics page reads reports/ml_results.json; every broken form must give a clear fallback, never a crash

import json

import pytest

from src.ui.views import (
    ML_REPORT_PATH, load_ml_report, ml_results_caption, model_comparison_rows, read_ml_report, report_counts,
)

VALID_CAPTION = (":material/warning: These results come from 36 synthetic profiles written and labelled by the "
                 "project author for the original 50-career catalogue (dataset v1.2.0). They measure agreement with "
                 "those labels, not how well careers suit real learners, and they do not cover careers added later.")


def write(tmp_path, content):
    path = tmp_path / "ml_results.json"
    path.write_text(content if isinstance(content, str) else json.dumps(content), encoding="utf-8")
    return path


def test_valid_saved_report_keeps_the_current_display():
    report, problem = read_ml_report()
    assert problem is None and report is not None
    assert report_counts(report) == (36, 50)
    assert ml_results_caption(report) == VALID_CAPTION
    rows = model_comparison_rows(report)
    assert [r["Method"] for r in rows][0] == "Weighted formula (used by this app)"
    assert len(rows) == 5 and rows[0]["MAP"] == 0.971


@pytest.mark.parametrize("content, reason", [
    ("{not json", "is not valid JSON"),
    ("", "is not valid JSON"),
    ("[1, 2, 3]", "unexpected structure"),
    ({"data": {"profiles": 36}}, "contains no model results"),
    ({"methods": {}}, "contains no model results"),
    ({"methods": ["weighted_formula"]}, "contains no model results"),
])
def test_broken_files_give_a_reason_not_an_error(tmp_path, content, reason):
    report, problem = read_ml_report(write(tmp_path, content))
    assert report is None and reason in problem
    assert load_ml_report(write(tmp_path, content)) is None
    assert model_comparison_rows(report) == []


def test_missing_and_unreadable_files(tmp_path):
    report, problem = read_ml_report(tmp_path / "missing.json")
    assert report is None and "was not found" in problem
    binary = tmp_path / "binary.json"
    binary.write_bytes(b"\xff\xfe\x00bad")
    report, problem = read_ml_report(binary)
    assert report is None and "could not be read" in problem


def test_malformed_method_entries_are_skipped(tmp_path):
    saved = json.loads(ML_REPORT_PATH.read_text(encoding="utf-8"))
    saved["methods"]["random_forest"] = {"ranking": {}}
    saved["methods"]["decision_tree"] = "broken"
    saved["significance_vs_formula"] = "broken"
    report, problem = read_ml_report(write(tmp_path, saved))
    assert problem is None
    rows = model_comparison_rows(report)
    methods = [r["Method"] for r in rows]
    assert "Random Forest" not in methods and "Decision Tree" not in methods
    assert "Weighted formula (used by this app)" in methods
    assert all(r["p vs formula (Holm)"] in ("reference", "n/a") for r in rows)


@pytest.mark.parametrize("data, counts, fragment", [
    (None, (None, None), "come from synthetic profiles written and labelled by the project author for the original "
                         "catalogue"),
    ("broken", (None, None), "for the original catalogue"),
    ({"profiles": 36}, (36, None), "come from 36 synthetic profiles"),
    ({"careers": 50}, (None, 50), "the original 50-career catalogue"),
    ({"profiles": True, "careers": -3}, (None, None), "for the original catalogue"),
    ({"profiles": "36", "careers": 50.0}, (None, None), "for the original catalogue"),
])
def test_missing_or_invalid_counts_use_neutral_wording(data, counts, fragment):
    report = {"methods": {"weighted_formula": {}}}
    if data is not None:
        report["data"] = data
    assert report_counts(report) == counts
    caption = ml_results_caption(report)
    assert fragment in caption and "None" not in caption
    assert "do not cover careers added later" in caption
