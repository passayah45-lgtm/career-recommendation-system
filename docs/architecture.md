# Architecture

## Layers

```
Streamlit pages (app.py navigation, home.py, pages/)
        |
        v
UI helpers (src/ui/)            state (session + cached catalog), components, views, charts
        |
        v
Services (src/services/)        catalog, profiles, recommendations, skill_gap, learning_resources
        |                 \
        v                  v
Engine (src/engine/)       Data (src/data/)
models, matching,          loader, preprocessing, validation
scoring, ranking,                 |
explanations                      v
                           CSV files (data/raw/)  careers.csv, resources.csv, skill_aliases.csv
```

Rule: services call the engine and the data layer. The engine works only on in-memory Career and LearnerProfile objects. It never imports Streamlit, pandas, the data layer, a database or the network.

## Request flow

1. The learner fills the assessment form (pages/1_Career_Assessment.py). The raw answers are kept in Streamlit session state only.
2. services/catalog.py load_catalog() validates and loads the CSV files once.
3. services/profiles.py validates the raw input and normalizes skills with the Phase 2 aliases.
4. engine/matching.py compares the profile with each career.
5. engine/scoring.py computes the four components and the weighted total.
6. engine/ranking.py sorts results and applies the tie-break rule.
7. engine/explanations.py writes reasons and notes from the computed values.
8. services/skill_gap.py lists missing skills and attaches resources from services/learning_resources.py.
9. The page renders results and Plotly charts. Pages display service output and never compute scores themselves.

app.py only registers the pages with st.navigation, so each page has an explicit sidebar title and icon. home.py is the default page.

Styling: .streamlit/config.toml holds the native theme, src/ui/theme.py the matching design tokens, and src/ui/styles.css a small shared stylesheet. components.page_setup() applies them on every page. Details: docs/design_system.md.

Streamlit layer rules: src/ui/state.py loads the Catalog once with st.cache_resource (it is read-only), and session state holds only the learner's raw answers, the Top K choice and the selected career. src/ui/views.py and src/ui/charts.py are plain Python so they can be tested without a browser. A data folder can be swapped with the CAREER_DATA_DIR environment variable. If the data fails validation, every page shows an error message instead of crashing.

Data quality: src/data/validation.py checks the CSV files in CI before any code reads them. src/data/loader.py then parses the pipe-separated lists, and src/data/preprocessing.py normalizes learner skill input with the alias file.

## Key interfaces

```python
catalog = load_catalog()                                         # src/services/catalog.py
recommend(profile: dict, catalog, top_k=5, weights=DEFAULT_WEIGHTS) -> dict   # src/services/recommendations.py
analyze_skill_gap(profile: dict, career_id: str, catalog) -> dict            # src/services/skill_gap.py
```

Both functions take a plain dict and return plain dicts and lists, so a future REST API can pass request bodies in and return the results as JSON. The Catalog is loaded once and passed in, there is no global state. These two functions become the T-Career API endpoints in Phase 7. Algorithm details: docs/recommendation_algorithm.md.

## Deployment

| Part | Where |
|---|---|
| Code | GitHub repository |
| Experiments | Google Colab (optional) |
| Demo app | Streamlit Community Cloud |
| CI tests | GitHub Actions (.github/workflows/tests.yml) |

## Evaluation and link checking

src/evaluation/ (dataset, metrics, experiments) runs the labelled profiles in data/evaluation/labelled_profiles.json through the same recommend() service the app uses, and writes reports/evaluation_results.json. It uses only the standard library and the existing services.

src/data/url_checker.py checks resource and career source URLs over HTTP. It is the only module that uses the network, and it runs only when called by hand. CI and the test suite use a mocked transport.
