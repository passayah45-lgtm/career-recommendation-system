# Design System

The interface uses one shared visual system. Pages never set colors or CSS themselves.

## Where the styling lives

| Layer | File | What it controls |
|---|---|---|
| Native theme | .streamlit/config.toml | Colors, font sizes, radius, borders, badge colors, chart palette, dark sidebar |
| Tokens | src/ui/theme.py | The same colors as Python constants, page icons, chart colors, verification badges |
| Stylesheet | src/ui/styles.css | Card surfaces, hero accent, section headings, resource cards, phone layout |
| Components | src/ui/components.py | page_setup, badges, section, resource_card, sidebar summary, empty states |
| Charts | src/ui/charts.py | Plotly layout, fonts and colors taken from theme.py |
| Logo | static/logo.svg, static/logo_icon.svg | Sidebar logo and browser tab icon |

page_setup() runs first on every page. It sets the tab title and icon, injects the stylesheet once with a style-only st.html block, adds the logo and renders the page header.

tests/test_theme.py checks that config.toml, theme.py and styles.css use the same colors, that text colors pass WCAG AA contrast, that every page has an icon, and that only http_checked links get the success badge.

## Color tokens

| Token | Value | Use |
|---|---|---|
| NAVY | #14213D | Headings, body text, sidebar background |
| TEAL | #0F9D94 | Decorative accent: hero edge, chart bars, top recommendation border |
| TEAL_DARK | #0B7F78 | Buttons, progress bars, active states (4.86:1 with white text) |
| BLUE | #3B82F6 | Secondary accent: transparency note, interest component in charts |
| BLUE_DARK | #2563EB | Links (5.17:1 on white) |
| PAGE_BG | #F4F7FB | Page background |
| SURFACE | #FFFFFF | Cards, panels, forms |
| SURFACE_TINT | #E9EEF5 | Inputs and secondary surfaces |
| BORDER | #DCE3EC | Card and input borders |
| TEXT_MUTED | #475569 | Supporting text (7.05:1 on PAGE_BG) |
| TEXT_SUBTLE | #64748B | Small labels on white |
| WARNING | #C2410C | Missing required skills |

Pure teal #0F9D94 gives only 3.35:1 with white text, so buttons use TEAL_DARK.

## Typography and spacing

Source Sans (Streamlit default, no external font request). Heading sizes from config.toml: page title 1.85rem, section 1.4rem, card title 1.3rem. Base size 15px. Small uppercase labels (0.78rem) name each group of skills.

Spacing scale: xs 0.25rem, sm 0.5rem, md 1rem, lg 1.5rem, xl 2rem. Page content is capped at 1180px.

## Components

| Component | Look | Used for |
|---|---|---|
| Card | White surface, 1px border, soft shadow, 0.6rem radius | Every keyed container (panel_, card_, step_, rec_, res_ keys) |
| Hero | Card with a 4px teal left edge | Home page header |
| Top recommendation | 2px teal border, faint tint, "Highest score for your answers" badge | Rank 1 only |
| Section heading | Numbered circle, title, help line | Assessment form sections |
| Status badges | Native Streamlit badges, always with an icon | Have (green, check), missing (orange, cross), optional (gray, plus), interests (blue) |
| Verification badge | Green "Link checked DATE" only for http_checked; gray "Found in search, not opened" for search_index_confirmed; gray "Not verified" otherwise | Learning resources |
| Progress bar | Teal on light track | Compatibility score, skill coverage |
| Empty state | Card with icon, sentence and a link to the next step | Pages without an assessment, explorer with no match |

Status is never shown by color alone: every badge has an icon and a text label.

## Navigation

st.navigation with Material icons from Streamlit's built-in set: home, assignment, recommend, school, explore, monitoring. The sidebar uses the navy sidebar theme. The active page has a lighter navy background. Below the navigation, the sidebar shows the assessment status and the career selected for skill-gap analysis.

## Charts

All bars use TEAL, except the score breakdown (required teal, preferred light teal, interests blue, education gray) and coverage (required teal, preferred light teal, all skills gray). Titles are left aligned in navy, axis labels are named, tooltips show the value with its unit, and the toolbar is hidden.

## Responsive rules

Streamlit columns stack on narrow screens. On screens under 640px the stylesheet reduces side padding, shrinks the page title and shows the home statistics two per row. Checked in headless Chromium at 1440, 1280, 820 and 390 pixels wide with no horizontal scroll.

## Selector policy

The stylesheet targets the st-key-* classes Streamlit adds to containers created with a key, plus classes this app writes itself (crs-*). Three Streamlit test ids are used where no keyed element exists: stForm (form surface), stMetric (stat cards) and stHorizontalBlock/stColumn (two-per-row stats on phones). If a Streamlit upgrade renames them, the app still works and only loses that styling.
