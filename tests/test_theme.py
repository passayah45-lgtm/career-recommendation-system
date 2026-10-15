# Design system: tokens, theme config, stylesheet, icons and verification labels stay consistent

import ast
import tomllib
from pathlib import Path

import pytest

from src.ui import theme

ROOT = Path(__file__).resolve().parents[1]
CONFIG = tomllib.loads((ROOT / ".streamlit" / "config.toml").read_text(encoding="utf-8"))
CSS = (ROOT / "src" / "ui" / "styles.css").read_text(encoding="utf-8")


def contrast(a, b):
    def lum(hex_color):
        rgb = [int(hex_color.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4)]
        rgb = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
        return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]
    hi, lo = sorted((lum(a), lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def test_config_matches_tokens():
    t = CONFIG["theme"]
    assert t["primaryColor"] == theme.TEAL_DARK
    assert t["backgroundColor"] == theme.PAGE_BG
    assert t["secondaryBackgroundColor"] == theme.SURFACE_TINT
    assert t["textColor"] == theme.TEXT
    assert t["borderColor"] == theme.BORDER
    assert t["linkColor"] == theme.BLUE_DARK
    assert CONFIG["theme"]["sidebar"]["backgroundColor"] == theme.NAVY
    assert CONFIG["client"]["showErrorDetails"] is False


def test_stylesheet_variables_match_tokens():
    for name, value in (("navy", theme.NAVY), ("teal", theme.TEAL), ("teal-dark", theme.TEAL_DARK),
                        ("blue", theme.BLUE), ("border", theme.BORDER), ("muted", theme.TEXT_MUTED)):
        assert f"--crs-{name}: {value};" in CSS


def test_stylesheet_has_no_imports_or_remote_urls():
    # The app must work offline and on Community Cloud without extra requests
    assert "@import" not in CSS and "http" not in CSS


@pytest.mark.parametrize("fg,bg", [
    (theme.TEXT, theme.PAGE_BG), (theme.TEXT_MUTED, theme.PAGE_BG), (theme.TEXT_SUBTLE, theme.SURFACE),
    ("#FFFFFF", theme.TEAL_DARK), (theme.BLUE_DARK, theme.SURFACE),
    (CONFIG["theme"]["sidebar"]["textColor"], theme.NAVY),
])
def test_text_colors_meet_wcag_aa(fg, bg):
    assert contrast(fg, bg) >= 4.5


def test_every_page_has_an_icon():
    tree = ast.parse((ROOT / "app.py").read_text(encoding="utf-8"))
    titles = [kw.value.value for node in ast.walk(tree) if isinstance(node, ast.Call)
              for kw in node.keywords if kw.arg == "title"]
    assert set(titles) == set(theme.PAGE_ICONS)
    assert all(icon.startswith(":material/") for icon in theme.PAGE_ICONS.values())


def test_logo_files_exist():
    assert (ROOT / "static" / "logo.svg").is_file() and (ROOT / "static" / "logo_icon.svg").is_file()


def test_only_http_checked_links_use_the_success_badge():
    pytest.importorskip("streamlit")
    from src.ui.components import verification_badge
    assert verification_badge("http_checked", "2026-10-14") == ":green-badge[:material/verified: Link checked 2026-10-14]"
    for status in ("search_index_confirmed", "unverified", "", "anything_else"):
        badge = verification_badge(status, "2026-10-14")
        assert not badge.startswith(":green") and "Link checked" not in badge
    assert "not opened" in verification_badge("search_index_confirmed")


def test_status_badges_always_carry_an_icon():
    pytest.importorskip("streamlit")
    from src.ui.components import have_badges, missing_badges, optional_badges
    assert have_badges(["sql"]) == ":green-badge[:material/check: sql]"
    assert missing_badges(["sql"]) == ":orange-badge[:material/close: sql]"
    assert optional_badges(["git"]) == ":gray-badge[:material/add: git]"
    assert have_badges([]) == ":gray[_None yet_]"


def test_category_palette_covers_every_category():
    from src.data.validation import CATEGORIES
    assert len(set(theme.CATEGORY_PALETTE)) >= len(CATEGORIES)


def test_one_product_name_across_logo_readme_and_home():
    name = "Career Recommendation System"
    logo = (ROOT / "static" / "logo.svg").read_text(encoding="utf-8")
    assert f'aria-label="{name}"' in logo and "Career Recommendation" in logo
    assert (ROOT / "README.md").read_text(encoding="utf-8").startswith(f"# {name}")
    assert f'"{name}"' in (ROOT / "home.py").read_text(encoding="utf-8")
