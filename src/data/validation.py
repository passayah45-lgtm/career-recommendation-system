# Validation rules for the career, resource and skill alias datasets
# The validator reports problems and never repairs data
# Run from the project root: python -m src.data.validation

import argparse
import csv
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

# Dataset locations relative to the project root
DEFAULT_DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"
CAREERS_FILE = "careers.csv"
RESOURCES_FILE = "resources.csv"
ALIASES_FILE = "skill_aliases.csv"

# Schema definitions
CAREER_COLUMNS = [
    "career_id", "career_title", "category", "description", "required_skills",
    "preferred_skills", "education_level", "interests", "learning_goals", "onet_code", "source_url",
]
CAREER_REQUIRED_FIELDS = [
    "career_id", "career_title", "category", "description", "required_skills",
    "education_level", "interests", "learning_goals",
]
RESOURCE_COLUMNS = [
    "resource_id", "skill_name", "resource_title", "provider", "resource_url", "is_free",
    "resource_type", "level", "language", "url_verification", "verified_on", "notes",
]
RESOURCE_REQUIRED_FIELDS = [
    "resource_id", "skill_name", "resource_title", "provider", "resource_url", "is_free",
    "resource_type", "level", "language", "url_verification",
]
ALIAS_COLUMNS = ["alias", "canonical_skill"]

# Allowed values
EXPECTED_CAREER_COUNT = 50
LIST_DELIMITER = "|"
CATEGORIES = (
    "Data and AI", "Software", "Cybersecurity", "Design",
    "Business", "Education", "Healthcare", "Engineering",
)
EDUCATION_LEVELS = {
    0: "No formal qualification specified",
    1: "Secondary education or equivalent",
    2: "Certificate, vocational training or diploma",
    3: "Bachelor's degree or equivalent",
    4: "Master's degree or higher",
}
INTERESTS = (
    "analysis", "building software", "business", "communication", "design", "engineering",
    "environment", "healthcare", "helping people", "leadership", "mathematics", "organization",
    "problem solving", "research", "science", "security", "teaching", "technology",
    "visual arts", "writing",
)
RESOURCE_TYPES = ("book", "course", "documentation", "guide", "standard", "tutorial")
LEVELS = ("beginner", "intermediate", "advanced")
BOOLEAN_VALUES = ("true", "false")
URL_VERIFICATION_VALUES = ("search_index_confirmed", "http_checked", "unverified")

# Patterns
ID_PATTERNS = {"career_id": re.compile(r"^C\d{3}$"), "resource_id": re.compile(r"^R\d{3}$")}
TOKEN_PATTERN = re.compile(r"^[a-z0-9]+( [a-z0-9]+)*$")
ONET_PATTERN = re.compile(r"^\d{2}-\d{4}\.\d{2}$")
LANGUAGE_PATTERN = re.compile(r"^[a-z]{2}$")

ERROR = "error"
WARNING = "warning"


@dataclass
class Issue:
    severity: str
    dataset: str
    record: str
    field: str
    message: str

    def __str__(self):
        return f"[{self.severity.upper()}] {self.dataset} | {self.record} | {self.field}: {self.message}"


@dataclass
class ValidationReport:
    issues: list = field(default_factory=list)

    @property
    def errors(self):
        return [i for i in self.issues if i.severity == ERROR]

    @property
    def warnings(self):
        return [i for i in self.issues if i.severity == WARNING]

    @property
    def ok(self):
        return not self.errors

    def extend(self, issues):
        self.issues.extend(issues)


def read_csv(path):
    # Returns (rows, columns) or raises FileNotFoundError / ValueError
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames or []
        rows = list(reader)
    return rows, columns


def split_list(value):
    # Splits a delimited field without cleaning the tokens
    if value is None or value == "":
        return []
    return value.split(LIST_DELIMITER)


def is_normalized_token(token):
    return bool(TOKEN_PATTERN.match(token))


def is_valid_url(value):
    if not value or value != value.strip() or " " in value:
        return False
    parsed = urlparse(value)
    return parsed.scheme in ("http", "https") and "." in parsed.netloc


def _title_key(title):
    # Collapses case and punctuation so near-identical titles collide
    return re.sub(r"[^a-z0-9]", "", title.lower())


def check_columns(columns, expected, dataset):
    missing = [c for c in expected if c not in columns]
    issues = [Issue(ERROR, dataset, "header", c, "required column is missing") for c in missing]
    extra = [c for c in columns if c not in expected]
    issues += [Issue(WARNING, dataset, "header", c, "column is not part of the documented schema") for c in extra]
    return issues


def check_required_fields(rows, fields, id_field, dataset):
    issues = []
    for n, row in enumerate(rows, start=2):
        record = row.get(id_field) or f"row {n}"
        for f in fields:
            value = row.get(f)
            if value is None or value.strip() == "":
                issues.append(Issue(ERROR, dataset, record, f, "required value is missing or empty"))
    return issues


def check_token_list(value, record, field_name, dataset, allow_empty=False):
    # Validates a pipe-delimited list of normalized tokens
    issues = []
    if value is None or value == "":
        if not allow_empty:
            issues.append(Issue(ERROR, dataset, record, field_name, "list is empty"))
        return issues
    tokens = split_list(value)
    for t in tokens:
        if t == "":
            issues.append(Issue(ERROR, dataset, record, field_name, f"empty token in '{value}' (check the '{LIST_DELIMITER}' delimiter)"))
        elif not is_normalized_token(t):
            issues.append(Issue(ERROR, dataset, record, field_name, f"token '{t}' is not normalized (lowercase letters, digits, single spaces)"))
    dupes = [t for t, c in Counter(tokens).items() if c > 1 and t]
    for t in dupes:
        issues.append(Issue(ERROR, dataset, record, field_name, f"token '{t}' is repeated"))
    return issues


def validate_careers(rows, columns, expected_count=EXPECTED_CAREER_COUNT):
    ds = "careers"
    issues = check_columns(columns, CAREER_COLUMNS, ds)
    if any(i.severity == ERROR for i in issues):
        return issues
    issues += check_required_fields(rows, CAREER_REQUIRED_FIELDS, "career_id", ds)

    if len(rows) != expected_count:
        issues.append(Issue(ERROR, ds, "dataset", "row count", f"expected {expected_count} careers, found {len(rows)}"))

    ids = Counter(r["career_id"] for r in rows)
    for cid, c in ids.items():
        if c > 1:
            issues.append(Issue(ERROR, ds, cid, "career_id", f"id appears {c} times"))

    titles = defaultdict(list)
    for r in rows:
        titles[_title_key(r["career_title"])].append(r["career_id"])
    for key, owners in titles.items():
        if key and len(owners) > 1:
            issues.append(Issue(ERROR, ds, ", ".join(owners), "career_title", "duplicate or near-duplicate title"))

    for n, r in enumerate(rows, start=2):
        rec = r["career_id"] or f"row {n}"
        if r["career_id"] and not ID_PATTERNS["career_id"].match(r["career_id"]):
            issues.append(Issue(ERROR, ds, rec, "career_id", "id must match C followed by three digits"))
        if r["career_title"] and r["career_title"] != r["career_title"].strip():
            issues.append(Issue(ERROR, ds, rec, "career_title", "title has leading or trailing spaces"))
        if r["category"] and r["category"] not in CATEGORIES:
            issues.append(Issue(ERROR, ds, rec, "category", f"'{r['category']}' is not an approved category"))
        if r["description"] and len(r["description"].split()) < 6:
            issues.append(Issue(ERROR, ds, rec, "description", "description is too short to be meaningful"))

        edu = r["education_level"]
        if edu:
            if not re.fullmatch(r"\d+", edu.strip()) or edu != edu.strip():
                issues.append(Issue(ERROR, ds, rec, "education_level", f"'{edu}' is not an integer"))
            elif int(edu) not in EDUCATION_LEVELS:
                issues.append(Issue(ERROR, ds, rec, "education_level", f"{edu} is outside the 0 to 4 scale"))

        issues += check_token_list(r["required_skills"], rec, "required_skills", ds)
        issues += check_token_list(r["preferred_skills"], rec, "preferred_skills", ds, allow_empty=True)
        overlap = set(split_list(r["required_skills"])) & set(split_list(r["preferred_skills"]))
        for s in sorted(overlap - {""}):
            issues.append(Issue(ERROR, ds, rec, "preferred_skills", f"'{s}' is also a required skill"))

        issues += check_token_list(r["interests"], rec, "interests", ds)
        for t in split_list(r["interests"]):
            if t and is_normalized_token(t) and t not in INTERESTS:
                issues.append(Issue(ERROR, ds, rec, "interests", f"'{t}' is not in the controlled interest vocabulary"))
        issues += check_token_list(r["learning_goals"], rec, "learning_goals", ds)

        onet, src = r["onet_code"], r["source_url"]
        if onet and not ONET_PATTERN.match(onet):
            issues.append(Issue(ERROR, ds, rec, "onet_code", f"'{onet}' is not a valid O*NET-SOC code"))
        if src:
            if not is_valid_url(src):
                issues.append(Issue(ERROR, ds, rec, "source_url", f"'{src}' is not a valid http(s) URL"))
            elif onet and onet not in src:
                issues.append(Issue(ERROR, ds, rec, "source_url", f"URL does not match onet_code {onet}"))
        else:
            issues.append(Issue(WARNING, ds, rec, "source_url", "no source URL, record is manually curated"))
    return issues


def career_skill_sets(rows):
    required = {s for r in rows for s in split_list(r.get("required_skills", "")) if s}
    preferred = {s for r in rows for s in split_list(r.get("preferred_skills", "")) if s}
    return required, preferred


def validate_resources(rows, columns, required_skills, preferred_skills):
    ds = "resources"
    issues = check_columns(columns, RESOURCE_COLUMNS, ds)
    if any(i.severity == ERROR for i in issues):
        return issues
    issues += check_required_fields(rows, RESOURCE_REQUIRED_FIELDS, "resource_id", ds)
    known = set(required_skills) | set(preferred_skills)

    for rid, c in Counter(r["resource_id"] for r in rows).items():
        if c > 1:
            issues.append(Issue(ERROR, ds, rid, "resource_id", f"id appears {c} times"))

    pairs = Counter((r["skill_name"], r["resource_url"]) for r in rows)
    for (skill, url), c in pairs.items():
        if c > 1 and url:
            issues.append(Issue(ERROR, ds, skill, "resource_url", f"same resource listed {c} times for this skill"))
    url_skills = defaultdict(set)
    for r in rows:
        if r["resource_url"]:
            url_skills[r["resource_url"]].add(r["skill_name"])
    for url, skills in url_skills.items():
        if len(skills) > 1:
            issues.append(Issue(WARNING, ds, url, "resource_url", f"URL is reused for skills: {', '.join(sorted(skills))}"))

    for n, r in enumerate(rows, start=2):
        rec = r["resource_id"] or f"row {n}"
        if r["resource_id"] and not ID_PATTERNS["resource_id"].match(r["resource_id"]):
            issues.append(Issue(ERROR, ds, rec, "resource_id", "id must match R followed by three digits"))
        skill = r["skill_name"]
        if skill:
            if not is_normalized_token(skill):
                issues.append(Issue(ERROR, ds, rec, "skill_name", f"'{skill}' is not normalized"))
            elif skill not in known:
                issues.append(Issue(ERROR, ds, rec, "skill_name", f"'{skill}' is not used by any career"))
        if r["resource_url"] and not is_valid_url(r["resource_url"]):
            issues.append(Issue(ERROR, ds, rec, "resource_url", f"'{r['resource_url']}' is not a valid http(s) URL"))
        if r["is_free"] and r["is_free"] not in BOOLEAN_VALUES:
            issues.append(Issue(ERROR, ds, rec, "is_free", f"'{r['is_free']}' must be 'true' or 'false'"))
        if r["resource_type"] and r["resource_type"] not in RESOURCE_TYPES:
            issues.append(Issue(ERROR, ds, rec, "resource_type", f"'{r['resource_type']}' is not a documented type"))
        if r["level"] and r["level"] not in LEVELS:
            issues.append(Issue(ERROR, ds, rec, "level", f"'{r['level']}' is not a documented level"))
        if r["language"] and not LANGUAGE_PATTERN.match(r["language"]):
            issues.append(Issue(ERROR, ds, rec, "language", f"'{r['language']}' is not a two-letter ISO 639-1 code"))
        status = r["url_verification"]
        if status and status not in URL_VERIFICATION_VALUES:
            issues.append(Issue(ERROR, ds, rec, "url_verification", f"'{status}' is not a documented status"))
        elif status == "unverified":
            issues.append(Issue(WARNING, ds, rec, "url_verification", "URL has not been verified"))
        if r["verified_on"]:
            try:
                date.fromisoformat(r["verified_on"])
            except ValueError:
                issues.append(Issue(ERROR, ds, rec, "verified_on", f"'{r['verified_on']}' is not an ISO date"))

    covered = {r["skill_name"] for r in rows}
    for s in sorted(set(required_skills) - covered):
        issues.append(Issue(ERROR, ds, s, "skill_name", "required skill has no learning resource"))
    for s in sorted(set(preferred_skills) - set(required_skills) - covered):
        issues.append(Issue(ERROR, ds, s, "skill_name", "preferred skill has no learning resource"))
    return issues


def validate_aliases(rows, columns, canonical_skills):
    ds = "skill_aliases"
    issues = check_columns(columns, ALIAS_COLUMNS, ds)
    if any(i.severity == ERROR for i in issues):
        return issues
    issues += check_required_fields(rows, ALIAS_COLUMNS, "alias", ds)
    for alias, c in Counter(r["alias"] for r in rows).items():
        if c > 1:
            issues.append(Issue(ERROR, ds, alias, "alias", f"alias appears {c} times"))
    for r in rows:
        alias, target = r["alias"], r["canonical_skill"]
        if alias and (alias != alias.strip().lower() or "  " in alias):
            issues.append(Issue(ERROR, ds, alias, "alias", "alias must be lowercase and trimmed"))
        if alias in canonical_skills:
            issues.append(Issue(ERROR, ds, alias, "alias", "alias is already a canonical skill"))
        if target and target not in canonical_skills:
            issues.append(Issue(ERROR, ds, alias, "canonical_skill", f"'{target}' is not a canonical skill"))
    return issues


def _load(path, dataset, report):
    try:
        return read_csv(path)
    except (FileNotFoundError, UnicodeDecodeError, csv.Error) as exc:
        report.extend([Issue(ERROR, dataset, "file", str(path), f"cannot read file: {exc}")])
        return None


def validate_all(data_dir=DEFAULT_DATA_DIR, expected_count=EXPECTED_CAREER_COUNT):
    data_dir = Path(data_dir)
    report = ValidationReport()
    careers = _load(data_dir / CAREERS_FILE, "careers", report)
    if careers is None:
        return report
    rows, cols = careers
    report.extend(validate_careers(rows, cols, expected_count))
    required, preferred = career_skill_sets(rows)

    resources = _load(data_dir / RESOURCES_FILE, "resources", report)
    if resources is not None:
        report.extend(validate_resources(*resources, required, preferred))

    aliases_path = data_dir / ALIASES_FILE
    if aliases_path.exists():
        aliases = _load(aliases_path, "skill_aliases", report)
        if aliases is not None:
            report.extend(validate_aliases(*aliases, required | preferred))
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate the career recommendation datasets.")
    parser.add_argument("--data-dir", default=str(DEFAULT_DATA_DIR), help="folder holding the raw CSV files")
    parser.add_argument("--quiet-warnings", action="store_true", help="print the warning count only")
    args = parser.parse_args(argv)

    report = validate_all(args.data_dir)
    for issue in report.errors:
        print(issue)
    if args.quiet_warnings:
        if report.warnings:
            print(f"{len(report.warnings)} warning(s) hidden")
    else:
        for issue in report.warnings:
            print(issue)
    print(f"Validation finished: {len(report.errors)} error(s), {len(report.warnings)} warning(s)")
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
