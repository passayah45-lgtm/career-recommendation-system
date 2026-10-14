# Data

raw/ holds the source CSV files committed to the repository.
processed/ holds generated files. They are not committed.

| File | Rows | Content |
|---|---|---|
| raw/careers.csv | 50 | Careers in 8 categories |
| raw/resources.csv | 114 | One learning resource per skill |
| raw/skill_aliases.csv | 37 | Alternative skill names mapped to canonical names |
| evaluation/labelled_profiles.json | 36 | Synthetic learner profiles with author-written relevant careers, for evaluation only |

Field definitions, sources and limitations: docs/dataset_documentation.md

Rules:
1. Lists use the pipe character as separator, for example python|sql|excel.
2. Skill names are lowercase, use single spaces and contain no punctuation.
3. No personal learner data goes in this folder.

Check the files after any edit:

```bash
python -m src.data.validation
```
