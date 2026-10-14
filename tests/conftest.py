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
