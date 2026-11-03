# Skill picker (3 November 2026): grouped by career field, every catalogue skill once, Select all disabled

from src.data.validation import CATEGORIES
from src.services.catalog import load_catalog
from src.ui import skill_picker as sp


def test_every_catalogue_skill_appears_once_with_a_derived_group():
    catalog = load_catalog()
    groups = sp.skill_groups(catalog)
    assert set(groups) == set(catalog.known_skills) and len(groups) == 144
    ordered = sp.ordered_skills(groups)
    assert len(ordered) == len(set(ordered)) == 144
    assert set(groups.values()) <= set(CATEGORIES) | {sp.SEVERAL_FIELDS}


def test_groups_follow_the_careers_that_use_each_skill():
    catalog = load_catalog()
    groups = sp.skill_groups(catalog)
    for skill, group in groups.items():
        fields = {c.category for c in catalog.careers if skill in c.required_skills + c.preferred_skills}
        assert group == (next(iter(fields)) if len(fields) == 1 else sp.SEVERAL_FIELDS), skill
    assert groups["communication"] == sp.SEVERAL_FIELDS
    assert groups["patient care"] == "Healthcare"


def test_options_are_grouped_in_category_order_then_alphabetical():
    groups = sp.skill_groups(load_catalog())
    ordered = sp.ordered_skills(groups)
    order = sp.group_order()
    keys = [(order.index(groups[s]), s) for s in ordered]
    assert keys == sorted(keys)


def test_labels_keep_the_exact_skill_name_and_select_all_is_off():
    groups = sp.skill_groups(load_catalog())
    assert sp.skill_label("patient care", groups) == "Healthcare · patient care"
    assert sp.skill_label("unknown skill", groups) == "unknown skill"
    assert sp.SELECT_ALL is False and sp.FILTER_MODE == "contains"


def test_skill_counter():
    assert sp.skill_counter_text(1).startswith("1 skill selected")
    assert sp.skill_counter_text(4).startswith("4 skills selected")
