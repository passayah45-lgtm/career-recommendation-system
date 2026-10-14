# End-to-end validation tests on the real project data and on temporary folders

from collections import Counter

from src.data.loader import load_aliases, load_careers, load_resources
from src.data.preprocessing import clean_skill_text, normalize_skill, normalize_skill_list
from src.data.validation import (
    CATEGORIES, EXPECTED_CAREER_COUNT, career_skill_sets, main, read_csv, validate_all,
)
from src.data.validation import DEFAULT_DATA_DIR


def test_real_datasets_pass_validation():
    report = validate_all()
    assert report.errors == [], "\n".join(str(e) for e in report.errors)


def test_real_dataset_has_fifty_careers_in_all_categories():
    rows, _ = read_csv(DEFAULT_DATA_DIR / "careers.csv")
    assert len(rows) == EXPECTED_CAREER_COUNT
    counts = Counter(r["category"] for r in rows)
    assert set(counts) == set(CATEGORIES)
    assert min(counts.values()) >= 5


def test_every_real_skill_has_a_resource():
    careers, _ = read_csv(DEFAULT_DATA_DIR / "careers.csv")
    resources, _ = read_csv(DEFAULT_DATA_DIR / "resources.csv")
    required, preferred = career_skill_sets(careers)
    covered = {r["skill_name"] for r in resources}
    assert (required | preferred) - covered == set()


def test_missing_file_is_reported(tmp_path):
    report = validate_all(tmp_path)
    assert not report.ok
    assert any("cannot read file" in e.message for e in report.errors)


def test_small_valid_dataset_passes(dataset_dir):
    report = validate_all(dataset_dir, expected_count=2)
    assert report.ok, "\n".join(str(e) for e in report.errors)


def test_cli_exit_codes(dataset_dir, capsys):
    assert main(["--data-dir", str(DEFAULT_DATA_DIR)]) == 0
    # The small fixture has 2 careers, so the default count of 50 fails
    assert main(["--data-dir", str(dataset_dir)]) == 1
    out = capsys.readouterr().out
    assert "expected 50 careers, found 2" in out


def test_loader_parses_lists_and_types():
    careers = load_careers()
    assert isinstance(careers.loc[0, "required_skills"], list)
    assert careers["education_level"].between(0, 4).all()
    resources = load_resources()
    assert resources["is_free"].isin([True, False]).all()
    aliases = load_aliases()
    assert aliases["ml"] == "machine learning"


def test_skill_normalization_is_explicit():
    aliases = {"ml": "machine learning", "ci/cd": "ci cd"}
    assert clean_skill_text("  Machine_Learning ") == "machine learning"
    assert normalize_skill("ML", aliases) == "machine learning"
    assert normalize_skill("CI/CD", aliases) == "ci cd"
    assert normalize_skill_list(["Python", "python ", "", None, "SQL"]) == ["python", "sql"]
