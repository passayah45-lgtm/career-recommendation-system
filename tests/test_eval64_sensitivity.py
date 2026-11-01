# Exploratory sensitivity analysis (tie-break and interest scoring): replica fidelity, isolation, reproducibility

import json
import random
from pathlib import Path

import pytest

from src.engine.matching import match_career
from src.engine.scoring import score_match
from src.evaluation import eval64_sensitivity as sens
from src.evaluation import independent_64_evaluation as ev
from src.evaluation.eval64_data import verify_frozen
from src.evaluation.snapshot import verify_snapshot

from tests.conftest import needs_eval64_labels  # noqa: E402

pytestmark = needs_eval64_labels

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "evaluation_64_sensitivity"


@pytest.fixture(scope="module")
def setup():
    catalog, profiles, labels = ev.load_frozen()
    return catalog, profiles, labels, sens._profiles(catalog, profiles)


def test_local_scoring_replica_equals_production(setup):
    catalog, _, _, prepared = setup
    for p, prof in prepared[:40]:
        for career in catalog.careers:
            match = match_career(prof, career)
            assert sens.score(match, prof)[0] == pytest.approx(score_match(match).total, abs=1e-9)


def test_current_tie_break_reproduces_production_ranking(setup):
    catalog, profiles, labels, prepared = setup
    rows, _ = ev.run_profiles(catalog, profiles, labels)
    production = {r["profile_id"]: r["ranking"] for r in rows}
    assert {p.profile_id: sens.rank(p.profile_id, prof, catalog) for p, prof in prepared} == production


def test_alternative_tie_breaks_keep_the_first_three_keys(setup):
    catalog, _, _, prepared = setup
    p, prof = prepared[0]
    base = sens.rank(p.profile_id, prof, catalog)
    hashed = sens.rank(p.profile_id, prof, catalog, tie="hash")
    scores = {c.career_id: sens.score(match_career(prof, c), prof)[0] for c in catalog.careers}
    assert [round(scores[c], 9) for c in base] == [round(scores[c], 9) for c in hashed]
    a = sens.rank(p.profile_id, prof, catalog, tie="random", rng=random.Random(7))
    b = sens.rank(p.profile_id, prof, catalog, tie="random", rng=random.Random(7))
    assert a == b


def test_interest_rules(setup):
    catalog, _, _, prepared = setup
    p, prof = next((p, prof) for p, prof in prepared if len(prof.interests) >= 2)
    career = next(c for c in catalog.careers if set(c.interests) & set(prof.interests))
    match = match_career(prof, career)
    n = len(match.matched_interests)
    assert sens.interest_value(match, prof, "fixed_unit") == min(n, 3) / 3
    assert sens.interest_value(match, prof, "cosine") == pytest.approx(
        n / (len(career.interests) * len(prof.interests)) ** 0.5)
    # With no interest weight, interests cannot change the score
    assert sens.score(match, prof, "none")[0] == pytest.approx(
        sens.score(match_career(prof.__class__(**{**prof.__dict__, "interests": ()}), career), prof, "none")[0])


def test_saved_outputs_reproduce_and_are_labelled():
    assert sens.main(["--check", str(OUT)]) == 0
    summary = json.loads((OUT / "sensitivity_summary.json").read_text(encoding="utf-8"))
    assert summary["label"].startswith("Exploratory, post-hoc") and summary["replica_reproduces_production"]
    current = summary["tie_break"]["results"]["career_id_current"]["comparison"]
    assert current["top5_positions_changed"] == 0
    assert summary["tie_break"]["results"]["random_seeded"]["runs"] == 200


def test_experiments_leave_the_primary_evaluation_untouched():
    assert verify_frozen() == [] and verify_snapshot() == []
    assert ev.check_outputs(ROOT / "reports" / "evaluation_64") == []
