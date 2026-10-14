# Looks up learning resources for canonical skills from resources.csv
# Resources are never hard-coded here: they always come from the dataset

from dataclasses import asdict, dataclass

from src.data.preprocessing import normalize_skill

LEVEL_ORDER = {"beginner": 0, "intermediate": 1, "advanced": 2}
VERIFICATION_MEANING = {
    "search_index_confirmed": "The exact URL appeared in web search results on the verified_on date. Reachability was not HTTP-checked.",
    "http_checked": "The URL returned a successful HTTP response on the verified_on date.",
    "unverified": "The URL has not been verified.",
}


@dataclass(frozen=True)
class LearningResource:
    resource_id: str
    skill_name: str
    title: str
    provider: str
    url: str
    resource_type: str
    level: str
    is_free: bool
    language: str
    url_verification: str
    verified_on: str = ""
    notes: str = ""

    def to_dict(self):
        data = asdict(self)
        data["url_verification_meaning"] = VERIFICATION_MEANING.get(self.url_verification, "Unknown status.")
        return data


def _sort_key(resource):
    return (LEVEL_ORDER.get(resource.level, len(LEVEL_ORDER)), resource.resource_id)


class ResourceCatalog:
    # Read-only index of resources by canonical skill name

    def __init__(self, resources):
        index = {}
        for r in resources:
            index.setdefault(r.skill_name, []).append(r)
        self._index = {skill: tuple(sorted(items, key=_sort_key)) for skill, items in index.items()}

    @classmethod
    def from_dataframe(cls, df):
        resources = [
            LearningResource(
                resource_id=row["resource_id"], skill_name=row["skill_name"], title=row["resource_title"],
                provider=row["provider"], url=row["resource_url"], resource_type=row["resource_type"],
                level=row["level"], is_free=bool(row["is_free"]), language=row["language"],
                url_verification=row["url_verification"], verified_on=row.get("verified_on", ""),
                notes=row.get("notes", ""),
            )
            for row in df.to_dict(orient="records")
        ]
        return cls(resources)

    @property
    def skills(self):
        return frozenset(self._index)

    def __len__(self):
        return sum(len(v) for v in self._index.values())

    def for_skill(self, skill, aliases=None, level=None):
        # Resources for one skill, beginner first, optionally filtered to one level
        if level is not None and level not in LEVEL_ORDER:
            raise ValueError(f"level must be one of {', '.join(LEVEL_ORDER)}")
        canonical = normalize_skill(skill, aliases)
        items = self._index.get(canonical, ())
        if level is not None:
            items = tuple(r for r in items if r.level == level)
        return items

    def for_skills(self, skills, aliases=None):
        # One entry per skill in input order, including skills with no resource
        result = []
        seen = set()
        for skill in skills:
            canonical = normalize_skill(skill, aliases)
            if not canonical or canonical in seen:
                continue
            seen.add(canonical)
            items = self.for_skill(canonical)
            result.append({
                "skill": canonical,
                "has_resources": bool(items),
                "resources": [r.to_dict() for r in items],
            })
        return result
