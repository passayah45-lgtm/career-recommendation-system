# Design tokens for the whole app, plain Python so charts and tests can import them
# .streamlit/config.toml repeats the colors Streamlit needs, tests/test_theme.py keeps both in sync
# Full description: docs/design_system.md

# Brand and surface colors
NAVY = "#14213D"
TEAL = "#0F9D94"
TEAL_DARK = "#0B7F78"
BLUE = "#3B82F6"
BLUE_DARK = "#2563EB"
PAGE_BG = "#F4F7FB"
SURFACE = "#FFFFFF"
SURFACE_TINT = "#E9EEF5"
BORDER = "#DCE3EC"

# Text colors, each at least 4.5:1 contrast on PAGE_BG
TEXT = NAVY
TEXT_MUTED = "#475569"
TEXT_SUBTLE = "#64748B"

# Status colors, always shown together with a text label
SUCCESS = TEAL_DARK
WARNING = "#C2410C"
NEUTRAL = "#94A3B8"

# Score components in the stacked chart and the breakdown, in COMPONENT_ORDER
COMPONENT_COLORS = {
    "required skills": TEAL,
    "preferred skills": "#7DD3C8",
    "interests": BLUE,
    "education": NEUTRAL,
}

# One color per career category in analytics, labelled on the axis so color is never the only cue
CATEGORY_PALETTE = ["#0F9D94", "#3B82F6", "#8B5CF6", "#F59E0B", "#14213D", "#7DD3C8", "#EC4899", "#64748B"]

# Ordered levels in the education donut, light to dark
LEVEL_PALETTE = ["#CBD5E1", "#93C5FD", "#7DD3C8", "#0F9D94", "#14213D"]

# Coverage chart bars: required, preferred, all listed skills
COVERAGE_COLORS = [TEAL, "#7DD3C8", NEUTRAL]

# Spacing scale in rem, used by styles.css
SPACING = {"xs": 0.25, "sm": 0.5, "md": 1.0, "lg": 1.5, "xl": 2.0}

# Material icons from Streamlit's built-in set, one per page
PAGE_ICONS = {
    "Home": ":material/home:",
    "Career Assessment": ":material/assignment:",
    "Recommendations": ":material/recommend:",
    "Skill-Gap Analysis": ":material/school:",
    "Skill Roadmap": ":material/route:",
    "Career Explorer": ":material/explore:",
    "Analytics": ":material/monitoring:",
}

# Link verification labels: only http_checked is shown in the success color
VERIFICATION_BADGES = {
    "http_checked": ("green", ":material/verified:", "Link checked"),
    "search_index_confirmed": ("gray", ":material/travel_explore:", "Found in search, not opened"),
}
UNVERIFIED_BADGE = ("gray", ":material/help:", "Not verified")
