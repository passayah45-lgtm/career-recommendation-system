# Shared helpers that build small temporary datasets for negative tests

import csv

import pytest

from src.data.validation import ALIAS_COLUMNS, CAREER_COLUMNS, RESOURCE_COLUMNS


def career_row(n, **overrides):
    row = {
        "career_id": f"C{n:03d}",
        "career_title": f"Test Career {n}",
        "category": "Software",
        "description": "Builds and maintains test software for many different users.",
        "required_skills": "python|sql",
        "preferred_skills": "git",
        "education_level": "3",
        "interests": "technology|problem solving",
        "learning_goals": "write tested code",
        "onet_code": "15-1252.00",
        "source_url": "https://www.onetonline.org/link/summary/15-1252.00",
    }
    row.update(overrides)
    return row


def resource_row(n, skill, **overrides):
    row = {
        "resource_id": f"R{n:03d}",
        "skill_name": skill,
        "resource_title": f"Learn {skill}",
        "provider": "Test Provider",
        "resource_url": f"https://example.org/{skill.replace(' ', '-')}",
        "is_free": "true",
        "resource_type": "tutorial",
        "level": "beginner",
        "language": "en",
        "url_verification": "search_index_confirmed",
        "verified_on": "2026-10-14",
        "notes": "",
    }
    row.update(overrides)
    return row


def write_csv(path, columns, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=columns)
        w.writeheader()
        w.writerows(rows)
    return path


def make_career(cid, required, preferred=(), interests=("technology",), education=3, **kw):
    # Small engine-level Career for controlled ranking tests
    from src.engine.models import Career
    return Career(
        career_id=cid, title=kw.get("title", f"Career {cid}"), category=kw.get("category", "Software"),
        description="Test career used in engine tests only.",
        required_skills=tuple(required), preferred_skills=tuple(preferred), education_level=education,
        interests=tuple(interests), learning_goals=tuple(kw.get("learning_goals", ("learn things",))),
        source_url=kw.get("source_url", ""),
    )


@pytest.fixture
def mini_catalog():
    # Four careers and matching resources, built without touching the real CSV files
    from src.services.catalog import build_catalog
    from src.services.learning_resources import LearningResource, ResourceCatalog
    careers = [
        make_career("C001", ["python", "sql", "statistics", "machine learning"], ["git", "docker"], ["analysis", "technology"]),
        make_career("C002", ["html", "css", "javascript"], ["react"], ["design", "technology"]),
        make_career("C003", ["accounting", "excel", "taxation"], ["communication"], ["business", "mathematics"]),
        make_career("C004", ["python", "linux"], ["git"], ["technology", "security"], education=4),
    ]
    skills = sorted({s for c in careers for s in c.required_skills + c.preferred_skills})
    resources = [
        LearningResource(f"R{i:03d}", s, f"Learn {s}", "Test Provider", f"https://example.org/{s.replace(' ', '-')}",
                         "tutorial", "beginner", True, "en", "search_index_confirmed", "2026-10-14")
        for i, s in enumerate(skills, start=1)
    ]
    resources.append(LearningResource("R900", "sql", "Advanced SQL", "Test Provider", "https://example.org/sql-advanced",
                                      "course", "advanced", False, "en", "unverified"))
    aliases = {"ml": "machine learning", "js": "javascript", "k8s": "kubernetes"}
    interests = ("analysis", "technology", "design", "business", "mathematics", "security")
    return build_catalog(careers, ResourceCatalog(resources), aliases, interests)


@pytest.fixture
def valid_careers():
    return [career_row(1), career_row(2, career_title="Second Career")]


@pytest.fixture
def valid_resources():
    return [resource_row(1, "python"), resource_row(2, "sql"), resource_row(3, "git")]


@pytest.fixture
def dataset_dir(tmp_path, valid_careers, valid_resources):
    # Writes a complete small dataset and returns its folder
    write_csv(tmp_path / "careers.csv", CAREER_COLUMNS, valid_careers)
    write_csv(tmp_path / "resources.csv", RESOURCE_COLUMNS, valid_resources)
    write_csv(tmp_path / "skill_aliases.csv", ALIAS_COLUMNS, [{"alias": "py", "canonical_skill": "python"}])
    return tmp_path
