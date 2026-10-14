# Career Recommendation System

A transparent career recommender with skill-gap analysis and free learning resources. A learner enters skills, interests and education level. The system ranks 50 careers, explains every score, shows which skills are missing, and links a learning resource for each one.

Built as an MSc Computer Science and Data Analysis assignment at KIIT University. The engine is designed for later integration into T-Career.

## Features

| Page | What it does |
|---|---|
| Home | Purpose, dataset size, how the system works |
| Career Assessment | Skills (list plus free text with aliases such as ML or CI/CD), interests, education level, optional experience |
| Recommendations | Top K careers with score, matched and missing skills, interests, reasons and a score breakdown |
| Skill-Gap Analysis | Required and optional gaps, coverage, and learning resources with links and verification status |
| Career Explorer | Browse all 50 careers, filter by category, search by title, view details and sources |
| Analytics | Dataset charts, plus your own score contributions and skill coverage |

Answers stay in the browser session. There are no accounts and nothing is written to disk.

## Tech stack

Python 3.12+, Streamlit, Plotly, pandas, pytest. NumPy and scikit-learn are listed for compatibility. The evaluation code uses only the standard library. GitHub Actions runs data validation and tests.

## Install and run

```bash
git clone https://github.com/passayah45-lgtm/career-recommendation-system.git
cd career-recommendation-system
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

The app opens at http://localhost:8501.

## Validate data and run tests

```bash
python -m src.data.validation
python -m pytest -q
```

The tests cover the data validator, the engine, the services, the evaluation code, the URL checker (with mocked responses) and every Streamlit page (through Streamlit's AppTest). GitHub Actions runs both commands on every push and pull request, and checks that the saved evaluation report is reproducible.

## Evaluate and check links

```bash
python -m src.evaluation.experiments --output reports/evaluation_results.json   # synthetic-profile evaluation
python -m src.data.url_checker --output reports/url_check.json                 # needs internet, about 5 minutes
```

The URL checker never runs in CI. Results and method: docs/evaluation_report.md.

## Use the engine without Streamlit

```python
from src.services.catalog import load_catalog
from src.services.recommendations import recommend
from src.services.skill_gap import analyze_skill_gap

catalog = load_catalog()
result = recommend({"skills": ["Python", "SQL"], "interests": ["analysis"], "education_level": 3}, catalog, top_k=5)
gap = analyze_skill_gap({"skills": ["Python", "SQL"]}, "C002", catalog)
```

Both functions take and return plain dicts, ready for a REST API.

## Project structure

| Folder | Purpose |
|---|---|
| app.py, pages/ | Streamlit pages (presentation only) |
| src/ui | Page helpers: session state, tables, Plotly charts |
| src/services | Catalog loading, profile validation, recommendations, skill gap, resources |
| src/engine | Matching, scoring, ranking and explanations (no Streamlit, no I/O) |
| src/data | Loading, normalization and validation of the CSV files |
| data/raw | careers.csv, resources.csv, skill_aliases.csv |
| tests | Automated tests |
| docs | Requirements, architecture, dataset and algorithm documentation |

## Dataset

| File | Content |
|---|---|
| data/raw/careers.csv | 50 careers in 8 categories |
| data/raw/resources.csv | 114 free learning resources, one per skill |
| data/raw/skill_aliases.csv | 37 alternative skill names |

## How the score works

Compatibility score (0 to 100) = required skills 55% + preferred skills 15% + interests 25% + education 5%. Each part is the share of the career's items the learner matches. The score ranks careers for one learner. It is not a probability of being hired or of success.

## Limitations

1. Skills are matched by exact name after alias resolution. Related skills (statistics and probability) earn no partial credit.
2. Career skills, interests and education levels are curated by the author. 46 of 50 careers link to an O*NET occupation for source context.
3. Skill coverage divides by the length of each career's required list, so one shared skill counts more for careers with short lists (for example Excel and Financial Analyst). Phase 5 found this and kept the weights. See docs/evaluation_report.md.
4. One resource per skill, in English, several from US or UK sources (tax, health privacy, medical coding).
5. Resource links were confirmed in web search results on 2026-10-14, not HTTP-checked.
6. Evaluation uses 36 synthetic profiles labelled by the author. It measures agreement with those labels, not real-world accuracy.

Details: docs/dataset_documentation.md and docs/recommendation_algorithm.md.

## Deploy to Streamlit Community Cloud

The repository is ready: app.py is the entry point, requirements.txt pins tested versions, and .streamlit/config.toml sets the theme. No secrets are needed.

1. Sign in at https://share.streamlit.io with the GitHub account that owns this repository.
2. Click Create app, then choose to deploy from a GitHub repository.
3. Repository: passayah45-lgtm/career-recommendation-system. Branch: main. Main file path: app.py.
4. Open Advanced settings and choose Python 3.12 or newer (the pinned numpy needs at least 3.12). Leave secrets empty.
5. Click Deploy. The first build installs the requirements and takes a few minutes.
6. Open the app link, run one assessment, and check each page before sharing it.

Free apps go to sleep after a period without visitors. The first visit afterwards takes a short time to wake the app.

## Documentation

docs/requirements.md, docs/architecture.md, docs/dataset_documentation.md, docs/recommendation_algorithm.md, docs/evaluation_report.md

## Author

Issa Toure
