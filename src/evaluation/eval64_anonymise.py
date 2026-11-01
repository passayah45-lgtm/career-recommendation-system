# Builds the anonymised reviewer copy of the eval64_v1 second-review sheet and packet
# Profile and career IDs are replaced by neutral codes drawn from a system random source (not reproducible from a seed),
# profile order and career order are re-randomised, and the private mapping is written outside the reviewer bundle.
# The frozen sheet, profiles, labels and catalogue are only read.
# Build once: python -m src.evaluation.eval64_anonymise --build   (refuses to overwrite an existing mapping)
# Verify:     python -m src.evaluation.eval64_anonymise --verify

import argparse
import csv
import hashlib
import io
import json
import secrets
import sys
from pathlib import Path

from src.evaluation.eval64_data import EVAL64_DIR
from src.evaluation.eval64_review_sampling import SHEET

ANON_DIR = EVAL64_DIR / "review" / "anonymised"
PRIVATE_DIR = EVAL64_DIR / "review" / "private"
ANON_SHEET = ANON_DIR / "reviewer_sheet.csv"
ANON_PACKET = ANON_DIR / "reviewer_packet.md"
MAPPING = PRIVATE_DIR / "anonymisation_map.json"
ANON_COLUMNS = ("profile_code", "career_code", "career_title", "relevance_label", "justification", "reviewer",
                "confidence")
# No letters used as category initials in the original profile IDs, and no easily confused characters
CODE_ALPHABET = "ACFKMPQRTVWZ2346789"
EDU = {"0": "0 none specified", "1": "1 secondary", "2": "2 certificate or diploma", "3": "3 bachelor's",
       "4": "4 master's or higher", "": "not given"}


def _rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build(rng=None):
    rng = rng or secrets.SystemRandom()
    careers = {r["career_id"]: r for r in _rows(EVAL64_DIR / "careers.csv")}
    profiles = {r["profile_id"]: r for r in _rows(EVAL64_DIR / "profiles.csv")}
    pairs = {}
    for r in _rows(SHEET):
        pairs.setdefault(r["profile_id"], []).append(r["career_id"])
    profile_order = list(pairs)
    rng.shuffle(profile_order)
    profile_code = {pid: f"PR-{i:03d}" for i, pid in enumerate(profile_order, start=1)}
    codes = set()
    career_code = {}
    for cid in rng.sample(sorted(careers), len(careers)):
        while True:
            code = "JOB-" + "".join(rng.choice(CODE_ALPHABET) for _ in range(4))
            if code not in codes:
                codes.add(code)
                career_code[cid] = code
                break
    sheet_rows, packet = [], [
        "# Reviewer packet", "",
        "Read `reviewer_handover.md` and `second_review_guide.md` first. Enter your grades in your copy of "
        "`reviewer_sheet.csv`.", "",
        "You will grade 585 selected profile and career pairs, not every possible combination. Each profile lists "
        "between 4 and 9 careers in random order. Codes such as PR-017 and JOB-K7Q2 are random labels with no meaning.", "",
        "Scale: 3 strong, 2 moderate, 1 weak, 0 not relevant. If the profile does not give enough information, grade "
        "only what is stated, choose confidence `low`, and begin the justification with `INSUFFICIENT:`. Never leave "
        "a row blank.", "",
        "This packet contains no grades, justifications or app results.", "",
    ]
    for pid in profile_order:
        p = profiles[pid]
        order = list(pairs[pid])
        rng.shuffle(order)
        packet += [f"## {profile_code[pid]}", "",
                   f"- Learner: {p['description']}",
                   f"- Goal: {p['learning_goal']}",
                   f"- Skills typed: {', '.join(p['skills'].split('|')) if p['skills'] else 'none'}",
                   f"- Interests: {', '.join(p['interests'].split('|')) if p['interests'] else 'none'}",
                   f"- Education: {EDU[p['education_level']]}; experience: {p['experience_years'] or 'not given'} years",
                   "", "| Career code | Title | What the job does | Usual entry level | Grade (0-3) |",
                   "|---|---|---|---|---|"]
        for cid in order:
            c = careers[cid]
            packet.append(f"| {career_code[cid]} | {c['career_title']} | {c['description']} | "
                          f"{EDU[c['education_level']]} | |")
            sheet_rows.append({"profile_code": profile_code[pid], "career_code": career_code[cid],
                               "career_title": c["career_title"], "relevance_label": "", "justification": "",
                               "reviewer": "", "confidence": ""})
        packet.append("")
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=ANON_COLUMNS, lineterminator="\n")
    w.writeheader()
    w.writerows(sheet_rows)
    sheet_text, packet_text = buf.getvalue(), "\n".join(packet)
    mapping = {
        "note": "PRIVATE. Do not send to reviewers. Maps anonymised codes back to eval64_v1 IDs.",
        "source_sheet_sha256": hashlib.sha256(SHEET.read_bytes()).hexdigest(),
        "anonymised_sheet_sha256": _sha(sheet_text),
        "anonymised_packet_sha256": _sha(packet_text),
        "profiles": {code: pid for pid, code in profile_code.items()},
        "careers": {code: cid for cid, code in career_code.items()},
    }
    return sheet_text, packet_text, mapping


def write(force=False):
    if MAPPING.exists() and not force:
        raise SystemExit(f"{MAPPING} exists; refusing to replace a mapping that may already be in use")
    sheet_text, packet_text, mapping = build()
    ANON_DIR.mkdir(parents=True, exist_ok=True)
    PRIVATE_DIR.mkdir(parents=True, exist_ok=True)
    ANON_SHEET.write_text(sheet_text, encoding="utf-8")
    ANON_PACKET.write_text(packet_text, encoding="utf-8")
    MAPPING.write_text(json.dumps(mapping, indent=2) + "\n", encoding="utf-8")


def read_mapping(path=MAPPING):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def verify(mapping_path=MAPPING):
    # Returns a list of problems; empty means the anonymised copy matches the frozen sheet exactly
    m = read_mapping(mapping_path)
    problems = []
    if m["source_sheet_sha256"] != hashlib.sha256(SHEET.read_bytes()).hexdigest():
        problems.append("source sheet changed since anonymisation")
    if m["anonymised_sheet_sha256"] != hashlib.sha256(ANON_SHEET.read_bytes()).hexdigest():
        problems.append("anonymised sheet changed")
    if m["anonymised_packet_sha256"] != hashlib.sha256(ANON_PACKET.read_bytes()).hexdigest():
        problems.append("anonymised packet changed")
    if len(set(m["profiles"].values())) != len(m["profiles"]) or len(set(m["careers"].values())) != len(m["careers"]):
        problems.append("mapping is not one to one")
    original = sorted((r["profile_id"], r["career_id"]) for r in _rows(SHEET))
    anon = _rows(ANON_SHEET)
    mapped = sorted((m["profiles"][r["profile_code"]], m["careers"][r["career_code"]]) for r in anon)
    if mapped != original:
        problems.append("anonymised pairs differ from the frozen sheet")
    titles = {r["career_id"]: r["career_title"] for r in _rows(EVAL64_DIR / "careers.csv")}
    if any(titles[m["careers"][r["career_code"]]] != r["career_title"] for r in anon):
        problems.append("a career title does not match its code")
    return problems


def to_original_rows(anon_path, mapping_path=MAPPING):
    # Converts a completed anonymised sheet back to the original sheet's columns for the guarded analysis
    m = read_mapping(mapping_path)
    rows = _rows(anon_path)
    if not rows or tuple(rows[0].keys()) != ANON_COLUMNS:
        raise ValueError(f"columns must be {', '.join(ANON_COLUMNS)}")
    out = []
    for r in rows:
        if r["profile_code"] not in m["profiles"] or r["career_code"] not in m["careers"]:
            raise ValueError(f"unknown code in row {r['profile_code']} {r['career_code']}")
        out.append({"profile_id": m["profiles"][r["profile_code"]], "career_id": m["careers"][r["career_code"]],
                    "relevance_label": r["relevance_label"], "justification": r["justification"],
                    "reviewer": r["reviewer"], "confidence": r["confidence"]})
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description="Anonymised reviewer copy for eval64_v1.")
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args(argv)
    if args.build:
        write()
        print(f"Wrote {ANON_SHEET}, {ANON_PACKET} and the private mapping {MAPPING}")
    problems = verify()
    print("Anonymised copy verified." if not problems else "Problems: " + "; ".join(problems))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
