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

## Run tests

```bash
pytest -q
```

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

See docs/requirements.md and docs/architecture.md.

## Author

Issa Toure
