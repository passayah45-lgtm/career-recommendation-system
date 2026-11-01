# Pure data-shaping helpers used by the pages
# No scoring happens here: scores and matches come from the Phase 3 services

import json
import re
from collections import Counter
from pathlib import Path

from src.data.validation import CATEGORIES, EDUCATION_LEVELS

SKILL_TEXT_SPLIT = re.compile(r"[,;\n]+")


def education_label(level):
    if level is None:
        return "Not provided"
    return f"{level}: {EDUCATION_LEVELS.get(level, 'Unknown level')}"


def parse_skill_text(text):
    # Splits free text on commas, semicolons or new lines. Normalization stays in the service layer.
    if not text:
        return []
    return [part.strip() for part in SKILL_TEXT_SPLIT.split(text) if part.strip()]


def build_profile_input(selected_skills=(), other_skills_text="", interests=(), education_level=None,
                        experience_years=None):
    # Raw profile dict in the exact shape recommend() and analyze_skill_gap() accept
    profile = {
        "skills": list(selected_skills or []) + parse_skill_text(other_skills_text),
        "interests": list(interests or []),
    }
    if education_level is not None:
        profile["education_level"] = education_level
    if experience_years is not None:
        profile["experience_years"] = experience_years
    return profile


def career_label(career):
    return f"{career.title} ({career.career_id})"


def filter_careers(careers, categories=None, query=""):
    # Category filter plus case-insensitive title search, original order kept
    selected = set(categories) if categories else set(CATEGORIES)
    q = (query or "").strip().lower()
    return [c for c in careers if c.category in selected and (not q or q in c.title.lower())]


def career_rows(careers):
    # Compact overview for the explorer table, full skill lists stay in the detail card
    return [
        {
            "Career": c.title,
            "Category": c.category,
            "Required skills": len(c.required_skills),
            "Preferred skills": len(c.preferred_skills),
            "Entry education": c.education_level,
            "ID": c.career_id,
        }
        for c in careers
    ]


def career_list_rows(careers):
    # Two-column list for the explorer, details live in the side panel
    return [{"Career": r["Career"], "Category": r["Category"]} for r in career_rows(careers)]


def career_from_cell(ids, cells):
    # Maps a clicked list cell, given as (row, column), to the career id on that row
    if not cells:
        return None
    row = cells[0][0] if isinstance(cells[0], (list, tuple)) else cells[0].get("row")
    return ids[row] if isinstance(row, int) and 0 <= row < len(ids) else None


def resource_rows(entries, gap_type):
    # Flattens skill_gap resource entries into table rows, one row per resource
    rows = []
    for entry in entries:
        if not entry["resources"]:
            rows.append({"Gap": gap_type, "Skill": entry["skill"], "Resource": "No resource in catalogue",
                         "Provider": "", "Type": "", "Level": "", "Free": None, "Link status": "", "URL": None})
            continue
        for r in entry["resources"]:
            rows.append({
                "Gap": gap_type,
                "Skill": entry["skill"],
                "Resource": r["title"],
                "Provider": r["provider"],
                "Type": r["resource_type"],
                "Level": r["level"],
                "Free": r["is_free"],
                "Link status": r["url_verification"].replace("_", " "),
                "URL": r["url"],
            })
    return rows


def category_counts(careers):
    counts = Counter(c.category for c in careers)
    return [{"Category": cat, "Careers": counts.get(cat, 0)} for cat in CATEGORIES]


def education_counts(careers):
    counts = Counter(c.education_level for c in careers)
    return [{"Level": education_label(lvl), "Careers": counts.get(lvl, 0)} for lvl in sorted(EDUCATION_LEVELS)]


def required_skill_frequency(careers, limit=15):
    # Most common required skills, ties ordered alphabetically
    counts = Counter(s for c in careers for s in c.required_skills)
    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:limit]
    return [{"Skill": s, "Careers": n} for s, n in ranked]


def contribution_rows(recommendations):
    # Score contributions exactly as returned by recommend(), for a stacked chart
    rows = []
    for rec in recommendations:
        for name, comp in rec["score_components"].items():
            rows.append({
                "Career": f"{rec['rank']}. {rec['career_title']}",
                "Component": name.replace("_", " "),
                "Points": comp["contribution"],
            })
    return rows


# Saved results of the ML comparison, read only; the app never trains or runs these models
ML_REPORT_PATH = Path(__file__).resolve().parents[2] / "reports" / "ml_results.json"
ML_METHOD_LABELS = (
    ("weighted_formula", "Weighted formula (used by this app)"),
    ("random_forest", "Random Forest"),
    ("logistic_regression", "Logistic Regression"),
    ("xgboost", "XGBoost"),
    ("decision_tree", "Decision Tree"),
)


def read_ml_report(path=None):
    # Returns (report dict, None) or (None, plain reason); never raises, so the page can show a fallback
    path = Path(path) if path is not None else ML_REPORT_PATH
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None, f"the results file {path.name} was not found"
    except (OSError, UnicodeDecodeError):
        return None, f"the results file {path.name} could not be read"
    try:
        report = json.loads(text)
    except ValueError:
        return None, f"the results file {path.name} is not valid JSON"
    if not isinstance(report, dict):
        return None, f"the results file {path.name} has an unexpected structure"
    if not isinstance(report.get("methods"), dict) or not report["methods"]:
        return None, f"the results file {path.name} contains no model results"
    return report, None


def load_ml_report(path=None):
    # Returns the saved report as a dict, or None when it is missing, unreadable or has no model results
    return read_ml_report(path)[0]


def _count(value):
    # A usable count is a positive whole number, not a bool
    return value if isinstance(value, int) and not isinstance(value, bool) and value > 0 else None


def report_counts(report):
    # (profiles, careers) from the report's data section; None for anything missing or invalid
    data = report.get("data") if isinstance(report, dict) else None
    if not isinstance(data, dict):
        return None, None
    return _count(data.get("profiles")), _count(data.get("careers"))


def ml_results_caption(report):
    # Caption under the saved results; counts are named only when the report states them
    profiles, careers = report_counts(report)
    who = f"{profiles} synthetic profiles" if profiles else "synthetic profiles"
    catalogue = f"the original {careers}-career catalogue" if careers else "the original catalogue"
    return (f":material/warning: These results come from {who} written and labelled by the project author for "
            f"{catalogue} (dataset v1.2.0). They measure agreement with those labels, not how well careers suit real "
            "learners, and they do not cover careers added later.")


def model_comparison_rows(report):
    # One row per method in a fixed order, values copied from the saved report; malformed entries are skipped
    if not isinstance(report, dict) or not isinstance(report.get("methods"), dict):
        return []
    significance = report.get("significance_vs_formula")
    tests = significance.get("average_precision", {}) if isinstance(significance, dict) else {}
    tests = tests if isinstance(tests, dict) else {}
    rows = []
    for key, label in ML_METHOD_LABELS:
        method = report["methods"].get(key)
        if method is None:
            continue
        try:
            rank = method["ranking"]
            cls = method["classification_mean_over_repeats"]
            p = tests.get(key, {}).get("p_holm") if isinstance(tests.get(key, {}), dict) else None
            rows.append({
                "Method": label,
                "Trained model": key != "weighted_formula",
                "MAP": round(rank["average_precision"]["mean"], 3),
                "NDCG@5": round(rank["ndcg_at_5"]["mean"], 3),
                "MRR": round(rank["reciprocal_rank"]["mean"], 3),
                "ROC-AUC": round(cls["roc_auc"], 3),
                "F1": round(cls["f1"], 3),
                "p vs formula (Holm)": ("reference" if key == "weighted_formula"
                                        else ("n/a" if p is None else f"{p:.3f}")),
            })
        except (KeyError, TypeError, ValueError):
            continue
    return rows


def saved_list_rows(career_ids, catalog, formula_recommendations=None):
    # One row per saved career, in formula order when scores exist, otherwise by title
    # Scores and ranks come from recommend() without feedback, so they match the score breakdown
    by_id = {c.career_id: c for c in catalog.careers}
    scored = {r["career_id"]: r for r in (formula_recommendations or [])}
    rows = []
    for cid in career_ids:
        career = by_id.get(cid)
        if career is None:
            continue
        rec = scored.get(cid)
        rows.append({
            "career_id": cid,
            "title": career.title,
            "category": career.category,
            "formula_score": rec["score"] if rec else None,
            "formula_rank": rec["rank"] if rec else None,
            "matched_required": len(rec["matched_required_skills"]) if rec else None,
            "required_total": len(career.required_skills),
        })
    if scored:
        return sorted(rows, key=lambda r: (r["formula_rank"] is None, r["formula_rank"] or 0, r["title"]))
    return sorted(rows, key=lambda r: r["title"])
