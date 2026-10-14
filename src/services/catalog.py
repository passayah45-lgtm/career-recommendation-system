# Read-only bundle of careers, resources and aliases used by every service
# Callers create a Catalog once and pass it in, so there is no global state

from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType

from src.data.loader import load_aliases, load_careers, load_resources
from src.data.validation import (
    ALIASES_FILE, CAREERS_FILE, DEFAULT_DATA_DIR, EXPECTED_CAREER_COUNT, INTERESTS, RESOURCES_FILE, validate_all,
)
from src.engine.models import Career
from src.services.learning_resources import ResourceCatalog


class DatasetError(RuntimeError):
    pass


class UnknownCareerError(KeyError):
    pass


@dataclass(frozen=True)
class Catalog:
    careers: tuple
    resources: ResourceCatalog
    aliases: MappingProxyType
    interests: frozenset

    @property
    def known_skills(self):
        return frozenset(s for c in self.careers for s in c.required_skills + c.preferred_skills)

    def get_career(self, career_id):
        if not isinstance(career_id, str):
            raise UnknownCareerError(f"career_id must be a string, got {type(career_id).__name__}")
        for career in self.careers:
            if career.career_id == career_id:
                return career
        raise UnknownCareerError(f"Unknown career_id: {career_id}")


def careers_from_dataframe(df):
    careers = []
    for row in df.to_dict(orient="records"):
        careers.append(Career(
            career_id=row["career_id"], title=row["career_title"], category=row["category"],
            description=row["description"], required_skills=tuple(row["required_skills"]),
            preferred_skills=tuple(row["preferred_skills"]), education_level=int(row["education_level"]),
            interests=tuple(row["interests"]), learning_goals=tuple(row["learning_goals"]),
            source_url=row.get("source_url", ""),
        ))
    return tuple(careers)


def build_catalog(careers, resources, aliases=None, interests=INTERESTS):
    # Checks the minimum the engine needs, full checks live in src.data.validation
    careers = tuple(careers)
    if not careers:
        raise DatasetError("The career dataset is empty.")
    ids = [c.career_id for c in careers]
    if len(ids) != len(set(ids)):
        raise DatasetError("The career dataset has duplicate career_id values.")
    for c in careers:
        if not c.required_skills:
            raise DatasetError(f"Career {c.career_id} has no required skills.")
    return Catalog(
        careers=careers,
        resources=resources,
        aliases=MappingProxyType(dict(aliases or {})),
        interests=frozenset(interests),
    )


def load_catalog(data_dir=None, validate=True, expected_count=EXPECTED_CAREER_COUNT):
    # Loads the CSV files, by default refusing data that fails Phase 2 validation
    data_dir = Path(data_dir) if data_dir else DEFAULT_DATA_DIR
    if validate:
        report = validate_all(data_dir, expected_count=expected_count)
        if not report.ok:
            first = "; ".join(str(e) for e in report.errors[:3])
            raise DatasetError(f"Dataset failed validation with {len(report.errors)} error(s): {first}")
    try:
        careers = careers_from_dataframe(load_careers(data_dir / CAREERS_FILE))
        resources = ResourceCatalog.from_dataframe(load_resources(data_dir / RESOURCES_FILE))
        aliases = load_aliases(data_dir / ALIASES_FILE)
    except (OSError, KeyError, ValueError) as exc:
        raise DatasetError(f"Could not load the dataset: {exc}") from exc
    return build_catalog(careers, resources, aliases)
