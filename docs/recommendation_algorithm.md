# Recommendation Algorithm

Version: 1.0.0 (Phase 3)
Last updated: 2026-10-14

## 1. Overview

The engine is a transparent, content-based recommender. It compares one learner profile with each of the 50 careers in data/raw/careers.csv, computes four component scores, combines them with fixed weights into a compatibility score from 0 to 100, ranks the careers, and explains each result with the values used in the calculation.

The compatibility score ranks careers for one learner against this dataset. It is not a probability of being hired, of succeeding in the career, or of liking it.

No learner interaction data exists, so the engine does not use collaborative filtering or trained models.

## 2. Modules

| Module | Responsibility |
|---|---|
| src/engine/models.py | Immutable Career and LearnerProfile types |
| src/engine/matching.py | Skill, interest and education comparison for one career |
| src/engine/scoring.py | Component values, weights and total score |
| src/engine/ranking.py | Deterministic sorting, tie-breaking and top K |
| src/engine/explanations.py | Reasons and notes built from the computed values |
| src/services/catalog.py | Loads and validates the CSV files into a read-only Catalog |
| src/services/profiles.py | Validates raw input and normalizes skills and interests |
| src/services/recommendations.py | Public recommend() function and output schema |
| src/services/skill_gap.py | analyze_skill_gap() for one career |
| src/services/learning_resources.py | Resource lookup by canonical skill |

The engine package imports nothing from Streamlit, databases or the network. The services package turns raw input into engine objects and engine results into plain dictionaries.

## 3. Data flow

```
raw profile dict
   -> profiles.build_profile      (type checks, normalize_skill + aliases, unknown items set aside)
   -> LearnerProfile + ProfileReport
   -> ranking.rank_careers        (for each career: matching.match_career -> scoring.score_match)
   -> sort + top K
   -> explanations.build_reasons / build_notes
   -> recommendations.recommend   (plain dict output)

career_id + raw profile dict
   -> skill_gap.analyze_skill_gap
   -> learning_resources.ResourceCatalog.for_skills (resources.csv)
```

The Catalog is created once with load_catalog() and passed into every call. There is no module-level cache or other global state. load_catalog() runs the Phase 2 validator first and raises DatasetError if the files fail it.

## 4. Input schema

```python
{
    "skills": ["Python", "SQL", "ML"],          # list of text, optional
    "interests": ["analysis", "mathematics"],   # list of text, optional
    "education_level": 3,                       # int 0 to 4, optional
    "experience_years": 2                       # int 0 to 70, optional, not scored in version 1
}
```

Validation (ProfileValidationError on failure):

1. The profile must be a mapping. None is treated as an empty profile.
2. skills and interests must be lists of text. A single string such as "python, sql" is rejected because splitting it would be a guess.
3. At most 200 items per list.
4. education_level and experience_years must be whole numbers in range. Booleans and numeric strings are rejected.
5. Unsupported fields are ignored and reported in ignored_fields.

## 5. Normalization and aliases

The engine reuses the Phase 2 functions. There is no second normalization system.

1. Each skill goes through src.data.preprocessing.normalize_skill with the alias map from data/raw/skill_aliases.csv. The raw lowercase text is checked against the aliases first ("ci/cd"), then the cleaned text ("Machine_Learning" becomes "machine learning").
2. The result counts as a skill only if it is one of the 114 canonical skills used by the careers.
3. Aliases and repeats collapse to one canonical skill. "machine learning", "ML" and "Machine_Learning" count once. Extra entries are listed in duplicate_skills.
4. Anything else goes to unknown_skills with the learner's original text, so the interface can show it. Unknown skills never count as matches.
5. Interests are cleaned with clean_skill_text and kept only if they belong to the 20-value interest vocabulary. Others go to unknown_interests.

## 6. Scoring formula

For learner L and career C:

```
S_req  = |required(C) ∩ skills(L)|   / |required(C)|
S_pref = |preferred(C) ∩ skills(L)|  / |preferred(C)|
S_int  = |interests(C) ∩ interests(L)| / |interests(C)|
S_edu  = 1 - 0.25 * max(0, level(C) - level(L))     (0 when level(L) is missing)

score = 100 * Σ w_i * S_i / Σ w_i        (sums over applicable components)
```

Each component lies in [0, 1]. The total lies in [0, 100] and is clamped there as a safeguard.

A component is not applicable when the career has nothing to compare, for example a career with no preferred skills. Its weight is then removed from the denominator. In the current dataset every career has 1 to 3 preferred skills, 3 to 5 required skills and 3 or 4 interests, so all four components apply to every real career.

Missing learner input is different from a non-applicable component. A missing field keeps its weight and scores 0. An empty profile therefore scores 0 everywhere and never becomes a perfect match.

## 7. Weights and rationale

| Component | Weight | Rationale |
|---|---|---|
| Required skills | 0.55 | Main signal. The required list is the core of each career record |
| Preferred skills | 0.15 | Useful but optional, so one preferred skill is worth less than one required skill |
| Interests | 0.25 | Separates careers when a learner has few skills, which is common for students |
| Education | 0.05 | Weak signal: 42 of 50 careers sit at level 3, and levels are curated estimates |

Properties that follow from these weights:

1. Skills carry 70% of the score.
2. In a career with 4 required and 2 preferred skills, one required skill adds 13.75 points and one preferred skill adds 7.5 points.
3. The largest possible education effect is 5 points (from 4 levels below to meeting the level). One required skill in any real career (at most 5 required) adds at least 11 points, so education alone cannot outrank a skill match. tests/test_scoring.py checks this.
4. If a career had no preferred skills, renormalization would raise the education share to 5.9 points. This does not happen in the current data.

These are initial weights chosen from the structure of the dataset, not tuned on results. They live in one place, ScoringWeights in src/engine/scoring.py, and recommend() accepts a weights argument, so Phase 5 can compare other settings without code changes.

Learning goals are not scored. careers.csv stores them as free-text outcomes ("build predictive models") and the learner profile has no structured equivalent. Matching free text would need fuzzy matching that this dataset cannot validate. Goals are returned in the output for display only. The Phase 1 goal component (Sg) is removed in version 1.

Experience years are accepted and returned but not scored, because careers.csv has no experience field.

## 8. Ranking and tie-breaking

Careers are sorted by:

1. Total score, highest first (compared after rounding to 9 decimals so float noise cannot reorder equal scores).
2. Required-skill coverage S_req, highest first.
3. Number of matched required skills, highest first.
4. career_id, ascending.

The result is the same for the same profile and data, whatever the order of the career list. The Phase 1 plan used the title as the last key. Version 1 uses career_id because ids are stable and titles may be edited.

top_k must be a positive whole number or None (all careers). The default in recommend() is 5. Ranking returns new objects and never changes the catalog.

## 9. Output schema

recommend(profile, catalog, top_k=5, weights=DEFAULT_WEIGHTS) returns:

```python
{
  "profile": {
    "skills": [...], "interests": [...], "education_level": 3, "experience_years": None,
    "report": {"recognized_skills", "unknown_skills", "duplicate_skills",
               "recognized_interests", "unknown_interests", "missing_fields", "ignored_fields"},
    "profile_complete": bool
  },
  "weights": {"required_skills": 0.55, "preferred_skills": 0.15, "interests": 0.25, "education": 0.05},
  "careers_scored": 50,
  "recommendations": [
    {
      "rank": 1, "career_id": "C001", "career_title": "...", "category": "...",
      "score": 61.5,                                    # 0 to 100, one decimal
      "score_components": {
        "required_skills": {"value": 0.8, "weight": 0.55, "applicable": True, "provided": True, "contribution": 44.0},
        ...
      },
      "matched_required_skills": [...], "missing_required_skills": [...],
      "matched_preferred_skills": [...], "missing_preferred_skills": [...],
      "matched_interests": [...], "career_interests": [...],
      "education": {"learner_level": 3, "career_level": 3, "meets_level": True, "levels_below": 0},
      "learning_goals": [...],
      "reasons": [...],      # why the score is what it is
      "notes": [...],        # missing input and missing required skills
      "source_url": "..."
    }
  ],
  "warnings": [...],
  "disclaimer": "..."
}
```

The contributions of a recommendation add up to its score (before rounding).

Explanations are built only from the computed values. A reason appears for a component only when it contributed (a matched skill, a matched interest, a provided education level). The required-skill line always appears, including "You have none of the N required skills yet." Missing input appears in notes, not as a reason.

## 10. Skill-gap analysis

analyze_skill_gap(profile, career_id, catalog) returns:

| Field | Meaning |
|---|---|
| have_required_skills, missing_required_skills | Required skills split by the profile |
| have_preferred_skills, missing_preferred_skills | Preferred (optional) skills split by the profile |
| required_coverage | matched required / all required |
| preferred_coverage | matched preferred / all preferred, None if the career has none |
| overall_skill_coverage | (matched required + matched preferred) / (all required + all preferred) |
| meets_all_required | True when no required skill is missing |
| unknown_skills | Profile skills that were not recognized |
| resources | {"required": [...], "preferred": [...]} for missing skills only |
| resource_note | States that links were search-index confirmed, not HTTP-checked |

Required and preferred gaps are never merged. A missing preferred skill is labelled optional in explanations and listed under "preferred". An unknown career_id raises UnknownCareerError.

## 11. Learning-resource retrieval

ResourceCatalog indexes data/raw/resources.csv by canonical skill name. No URL is written in the code.

1. Lookup normalizes the skill with the same aliases, so "ML" finds the resources for "machine learning".
2. Resources for a skill are sorted beginner, intermediate, advanced, then by resource_id. A level filter is optional.
3. Each resource returns skill_name, title, provider, url, resource_type, level, is_free, language, url_verification, verified_on, notes and a plain-language url_verification_meaning.
4. A skill without resources still appears with has_resources False, so gaps are never hidden.
5. The level shown is the level recorded in the dataset. The engine does not claim a resource suits every learner.

The current dataset has exactly one resource per skill. The code supports several.

## 12. Edge cases

| Case | Behavior |
|---|---|
| Empty profile | All scores 0, careers listed in career_id order, warning explains why |
| Only unknown skills | Treated as no skills, unknown items listed in warnings |
| Duplicate or alias skills | Counted once |
| Missing education | Education scores 0, note added |
| Career with no preferred skills | Component not applicable, weights renormalized, note added |
| Invalid profile values | ProfileValidationError with the field name |
| Invalid top_k or weights | ValueError |
| Unknown career_id | UnknownCareerError |
| Empty, duplicate-id or invalid dataset | DatasetError from load_catalog or build_catalog |

## 13. Complexity

With C careers, average k required plus preferred skills and i interests per career, one call to recommend() costs O(C x (k + i)) for matching (set lookups) and O(C log C) for sorting. For 50 careers this is a few hundred operations. Memory is O(C) for the score list. A skill-gap call is O(k).

## 14. Worked example (real dataset)

The profile below is illustrative. It is not a real learner and the result is not an evaluation metric. tests/test_recommendations.py reruns this example on every build.

Input:

```python
{"skills": ["Python", "SQL", "Excel", "ML", "statistics"],
 "interests": ["analysis", "mathematics"],
 "education_level": 3}
```

Normalized skills: python, sql, excel, machine learning (from the alias "ml"), statistics.

Top 5:

| Rank | Career | S_req | S_pref | S_int | S_edu | Score |
|---|---|---|---|---|---|---|
| 1 | C001 Data Scientist | 4/5 | 0/3 | 2/4 | 1.00 | 61.5 |
| 2 | C002 Data Analyst | 3/4 | 1/3 | 1/3 | 1.00 | 59.6 |
| 3 | C029 Financial Analyst | 1/3 | 3/3 | 2/3 | 1.00 | 55.0 |
| 4 | C031 Market Research Analyst | 2/4 | 2/3 | 1/3 | 1.00 | 50.8 |
| 5 | C006 Statistician | 1/4 | 1/2 | 2/3 | 0.75 | 41.7 |

Calculation for C001 Data Scientist:

```
required:  python, statistics, machine learning, sql matched, data visualization missing -> 0.8
preferred: deep learning, cloud computing, git all missing                             -> 0.0
interests: analysis, mathematics matched of analysis, mathematics, research, technology -> 0.5
education: learner 3, career 3                                                          -> 1.0
score = 100 x (0.55 x 0.8 + 0.15 x 0.0 + 0.25 x 0.5 + 0.05 x 1.0) = 44.0 + 0 + 12.5 + 5.0 = 61.5
```

Skill gap for C001: required coverage 0.8, preferred coverage 0.0, overall 0.5. Resources returned:

| Gap | Skill | Resource | Provider | Level |
|---|---|---|---|---|
| Required | data visualization | Fundamentals of Data Visualization | Claus O. Wilke | beginner |
| Preferred | deep learning | Dive into Deep Learning | d2l.ai | intermediate |
| Preferred | cloud computing | Introduction to Cloud Infrastructure: Describe Cloud Concepts | Microsoft Learn | beginner |
| Preferred | git | Pro Git (2nd edition) | git-scm.com | beginner |

Observation: C029 Financial Analyst ranks third with only 1 of 3 required skills, because the learner holds all its preferred skills and two of its interests. This is how the formula is designed, but it shows that preferred skills plus interests (40% together) can lift a career with low required coverage. Phase 5 tested higher required weights. They did not improve agreement with the labels and did not remove this effect, so the baseline was kept (docs/evaluation_report.md section 7).

## 15. Dataset limitations that affect results

1. Skills, interests and education levels are curated by the project author (docs/dataset_documentation.md section 9).
2. Exact skill matching only: "data analysis" is not in the vocabulary, and close skills such as "statistics" and "probability" earn no partial credit.
3. Coverage depends on list length: a career with 3 required skills moves more per skill than one with 5.
4. One resource per skill, mostly in English, several US or UK specific.
5. Phase 5 evaluated the engine on 36 labelled synthetic profiles (docs/evaluation_report.md). That evaluation found list-length bias in coverage scoring and kept the weights unchanged. It measures agreement with author-written labels, not real-world accuracy.

## 16. Fairness and explainability

1. Education has a 5% weight and only partial penalties, so the engine does not exclude learners without degrees.
2. The engine uses no personal attributes: no age, gender, nationality or location.
3. Every score is decomposed into contributions that add up to the total, and every reason maps to one component.
4. Unknown inputs are reported back instead of silently dropped, so learners can correct their profile.
5. Regional bias in sources (O*NET, US and UK resources) may make some careers or resources less relevant for learners in India or Guinea.
6. The score must be presented as a ranking aid with the disclaimer, never as a prediction about the learner.
