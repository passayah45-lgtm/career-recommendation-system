# Career Recommendation System

A transparent career recommender with skill-gap analysis and free learning resources. A learner enters skills, interests and education level. The system ranks 50 careers, explains every score, shows which skills are missing, and links a learning resource for each one.

Built as an MSc Computer Science and Data Analysis assignment at KIIT University. The engine is designed for later integration into T-Career.

**Live demo:** https://t-career-recommendation-2026.streamlit.app

The app sleeps after 12 hours without visitors. If you see a sleep page, click "Yes, get this app back up!" and wait about a minute.

## Features

| Page | What it does |
|---|---|
| Home | Purpose, dataset size, how the system works |
| Career Assessment | Skills (list plus free text with aliases such as ML or CI/CD), interests, education level, optional experience |
| Recommendations | Top K careers with score, matched and missing skills, interests, reasons and a score breakdown |
| Skill-Gap Analysis | Required and optional gaps, coverage, and learning resources with links and verification status |
| Career Explorer | Browse all 50 careers, filter by category, search by title, view details and sources |
| Analytics | Dataset charts, plus your own score contributions and skill coverage |

The interface uses a shared design system (navy, teal and blue on a light blue-gray background, a navy sidebar with icons, card layouts and labelled status badges). See docs/design_system.md.

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
| app.py, home.py, pages/ | Streamlit entry point and pages (presentation only) |
| src/ui | Page helpers: session state, components, design tokens (theme.py), stylesheet (styles.css), SVG graphics (illustrations.py), Plotly charts |
| static | Sidebar logo and browser tab icon |
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
5. 104 of 114 resource links passed an HTTP check on 2026-10-14. The other 10 block automated checks or were temporarily down, and keep their search-confirmed status.
6. Evaluation uses 36 synthetic profiles labelled by the author. It measures agreement with those labels, not real-world accuracy.

Details: docs/dataset_documentation.md and docs/recommendation_algorithm.md.

## Deploy to Streamlit Community Cloud

The repository is ready for Community Cloud:

| Item | Value |
|---|---|
| Entry point | app.py (registers the six pages with st.navigation) |
| Python | 3.12 (Community Cloud's default, and the version CI uses) |
| Dependencies | requirements.txt in the repository root, pinned versions |
| System packages | none, so no packages.txt is needed |
| Secrets | none |
| Data | data/raw/*.csv in the repository, loaded with repository-relative paths |

### Steps (from a Windows laptop, in any browser)

1. Go to https://share.streamlit.io, click **Continue to sign-in**, then **Continue with GitHub**. Sign in as passayah45-lgtm on github.com, then fill in the short profile form and click **Continue**.
2. Connect GitHub to your workspace: click the **Workspaces** menu in the upper-left corner (it shows a warning icon until connected), click **Connect GitHub account**, and on the GitHub page click **Authorize streamlit**. The repository is public, so no extra private-repository access is needed. Never type your GitHub password anywhere except github.com.
3. In your workspace, click **Create app** (upper-right corner).
4. When asked whether you already have an app, click **Yup, I have an app**.
5. Fill in:
   - Repository: `passayah45-lgtm/career-recommendation-system`
   - Branch: `main`
   - Main file path: `app.py`
6. Optional: in **App URL**, choose a short subdomain, for example `career-recommender-kiit`. If it is taken, try another.
7. Click **Advanced settings**, check that **Python version** is 3.12, leave **Secrets** empty, then click **Save**.
8. Click **Deploy**. The build log opens on the right. The first build installs the packages and usually takes a few minutes.
9. When the home page appears, copy the app URL from the browser address bar.
10. Run the checklist in docs/deployment_checklist.md before sharing the link.

### Reading the logs

While signed in, open your app and click **Manage app** in the lower-right corner. The logs show the package installation and any Python error. You can reboot the app from the same panel (**Reboot app**). Only accounts with write access to the repository can see the logs.

### Updating the app

Every push to the main branch redeploys the app automatically within a few minutes. Run `python -m pytest -q` before pushing.

### Sleep and wake-up

Apps without visitors for 12 hours go to sleep. A visitor then sees a sleep page with the button **Yes, get this app back up!**. Anyone can click it, and the app wakes in about a minute. Open the link a few minutes before a demonstration.

### Troubleshooting

| Symptom in the logs or page | Likely cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named ...` | A package is missing from requirements.txt, or the file is not in the repository root | Add the package with a pinned version to requirements.txt, push, wait for the redeploy |
| `No matching distribution found for numpy==2.5.4` or `requires a different Python` | The app was created with a Python version older than 3.12 | Python cannot be changed in place. Note the subdomain, delete the app in the workspace, and deploy again with Python 3.12 in Advanced settings. The subdomain becomes free again immediately |
| `FileNotFoundError` or the page says "The career data could not be loaded" | A data file is missing from GitHub or was renamed | Check that data/raw/careers.csv, resources.csv and skill_aliases.csv exist on GitHub, run `python -m src.data.validation` locally, push the fix |
| `ModuleNotFoundError: No module named 'src'` | The main file path is not app.py at the repository root | Set the main file path to `app.py` (delete and redeploy if needed) |
| "This app has gone over its resource limits" | Memory limit reached | Click **Manage app** then **Reboot app**. This app uses little memory, so report it if it repeats |
| The answers disappear | The browser page was refreshed or a URL was typed by hand | Expected: each new browser session starts empty. Use the sidebar to move between pages |
| `ImportError: cannot import name ...` right after a push | Community Cloud pulled new code without restarting Python, so old modules stayed in memory | app.py reloads changed modules automatically (src/ui/freshness.py). If it still appears, click **Manage app**, then **Reboot app** |
| The build hangs for more than 15 minutes | Temporary platform problem | Check https://www.streamlitstatus.com, then reboot the app |

The app hides detailed error messages from visitors (`client.showErrorDetails = false` in .streamlit/config.toml). The full traceback is always in the logs.

## Documentation

docs/requirements.md, docs/architecture.md, docs/dataset_documentation.md, docs/recommendation_algorithm.md, docs/evaluation_report.md, docs/design_system.md, docs/deployment_checklist.md

## Author

Issa Toure
