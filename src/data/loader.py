# Loads the raw datasets into pandas DataFrames for the recommendation engine
# List fields are split on the documented delimiter, nothing else is changed

from pathlib import Path

import pandas as pd

from src.data.validation import (
    ALIASES_FILE, CAREERS_FILE, DEFAULT_DATA_DIR, RESOURCES_FILE, split_list,
)

CAREER_LIST_FIELDS = ["required_skills", "preferred_skills", "interests", "learning_goals"]


def load_careers(path=None):
    path = Path(path) if path else DEFAULT_DATA_DIR / CAREERS_FILE
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    for col in CAREER_LIST_FIELDS:
        df[col] = df[col].map(split_list)
    df["education_level"] = df["education_level"].astype(int)
    return df


def load_resources(path=None):
    path = Path(path) if path else DEFAULT_DATA_DIR / RESOURCES_FILE
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    df["is_free"] = df["is_free"].map({"true": True, "false": False})
    return df


def load_aliases(path=None):
    # Returns a dict of alias to canonical skill name
    path = Path(path) if path else DEFAULT_DATA_DIR / ALIASES_FILE
    if not path.exists():
        return {}
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    return dict(zip(df["alias"], df["canonical_skill"]))
