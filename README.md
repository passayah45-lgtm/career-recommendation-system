# Career Recommendation System

A content-based career recommender with skill-gap analysis. Built as an MSc assignment at KIIT University, designed for later integration into T-Career.

## Features

1. Career assessment form
2. Ranked career matches with scores and explanations
3. Skill-gap analysis with learning resources
4. Career explorer
5. Score analytics

## Tech stack

Python, Pandas, NumPy, Scikit-learn, Streamlit, Plotly, Pytest.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Dataset

| File | Content |
|---|---|
| data/raw/careers.csv | 50 careers in 8 categories |
| data/raw/resources.csv | 114 free learning resources, one per skill |
| data/raw/skill_aliases.csv | 37 alternative skill names |

Details, sources and limitations: docs/dataset_documentation.md

## Validate data and run tests

```bash
python -m src.data.validation
python -m pytest -q
```

GitHub Actions runs both on every push and pull request.

## Use the engine

```python
from src.services.catalog import load_catalog
from src.services.recommendations import recommend
from src.services.skill_gap import analyze_skill_gap

catalog = load_catalog()
result = recommend({"skills": ["Python", "SQL"], "interests": ["analysis"], "education_level": 3}, catalog, top_k=5)
gap = analyze_skill_gap({"skills": ["Python", "SQL"]}, "C002", catalog)
```

Scoring, ranking and output schema: docs/recommendation_algorithm.md

## Project structure

| Folder | Purpose |
|---|---|
| src/data | Load, clean and validate data |
| src/engine | Score, rank and explain careers |
| src/services | Profile, recommendation and skill-gap logic |
| src/evaluation | Metrics and experiments |
| pages | Streamlit pages |
| tests | Automated tests |
| docs | Requirements, architecture, evaluation |

## Documentation

See docs/requirements.md, docs/architecture.md, docs/dataset_documentation.md and docs/recommendation_algorithm.md.

## Author

Issa Toure
