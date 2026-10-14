# Architecture

## Layers

```
Streamlit pages (pages/, app.py)
        |
        v
Services (src/services/)        profiles, recommendations, skill_gap, learning_resources
        |
        v
Engine (src/engine/)            scoring, matching, ranking, explanations
        |
        v
Data (src/data/)                loader, preprocessing, validation
        |
        v
CSV files (data/raw/)           careers.csv, resources.csv
```

Rule: each layer calls only the layer below it. The engine never imports Streamlit.

## Request flow

1. The learner fills the assessment form (pages/1_Career_Assessment.py).
2. services/profiles.py builds and validates a LearnerProfile.
3. services/recommendations.py loads careers and calls the engine.
4. engine/scoring.py computes Ss, Si, Se, Sg and the weighted total.
5. engine/ranking.py sorts results and applies the tie-break rule.
6. engine/explanations.py writes a plain-language reason per career.
7. services/skill_gap.py lists missing skills and attaches resources.
8. The page renders results and Plotly charts.

## Key interfaces

```python
recommend(profile: LearnerProfile, top_k: int = 5) -> list[Recommendation]
skill_gap(profile: LearnerProfile, career_id: str) -> SkillGap
```

These two functions become the T-Career API endpoints in Phase 7.

## Deployment

| Part | Where |
|---|---|
| Code | GitHub repository |
| Experiments | Google Colab (optional) |
| Demo app | Streamlit Community Cloud |
| CI tests | GitHub Actions (.github/workflows/tests.yml) |
