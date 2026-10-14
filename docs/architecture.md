# Architecture

## Layers

```
Streamlit pages (pages/, app.py)
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

1. The learner fills the assessment form (pages/1_Career_Assessment.py, Phase 4).
2. services/catalog.py load_catalog() validates and loads the CSV files once.
3. services/profiles.py validates the raw input and normalizes skills with the Phase 2 aliases.
4. engine/matching.py compares the profile with each career.
5. engine/scoring.py computes the four components and the weighted total.
6. engine/ranking.py sorts results and applies the tie-break rule.
7. engine/explanations.py writes reasons and notes from the computed values.
8. services/skill_gap.py lists missing skills and attaches resources from services/learning_resources.py.
9. The page renders results and Plotly charts (Phase 4).

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
