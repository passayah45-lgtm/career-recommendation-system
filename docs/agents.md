# AI assistants in the Career Recommendation System

Status: Phase 2 (isolated Python module) and Phase 3 (optional panel on the assessment page, behind a feature flag that is off by default), 5 November 2026. Not enabled on the live app. Approved by the project owner. Lecturer review pending.

## 1. Career Assessment Assistant

File: `src/agents/profile_assistant.py`. Tests: `tests/test_profile_assistant.py`.

The assistant reads a student's own description, such as "I enjoy analysing data, solving mathematical problems, teaching people Python, and working with machine learning", and suggests:

- `suggested_skills`: catalogue skills, for example `python` and `machine learning`.
- `suggested_interests`: official interests, for example "Analysing data and information", "Working with numbers and calculations" and "Teaching and training others".
- `unmatched_phrases`: words it could not match, each with a reason, for the student to review.
- `match_details`: every match in order, including repeats, with the phrase that triggered it, the match type, a confidence level and a plain explanation.

```python
from src.agents.profile_assistant import suggest_profile
from src.services.catalog import load_catalog

result = suggest_profile("I use Python and SQL and enjoy helping people", load_catalog())
result.suggested_skills          # list of Suggestion objects
result.to_dict()                 # plain dictionaries for a future interface
result.profile_selection()       # {"skills": [...], "interests": [...]} after the student confirms
```

The assistant never changes a profile. `profile_selection()` only returns the official entries in the shape `recommend()` accepts, for use after the student has confirmed them.

## 2. How matching works

All entries come from the existing definitions. Nothing is copied or redefined:

- Skills: `catalog.known_skills` (the 144 skills used by the careers) and `catalog.aliases` (`data/raw/skill_aliases.csv`), only where the alias points to a catalogue skill.
- Interests: `INTEREST_TERMS`, their French draft names, and `LEGACY_TO_CURRENT` (former interest names) in `src/data/interest_taxonomy.py`, limited to the interests in `catalog.interests`.
- Text cleaning: `clean_skill_text` in `src/data/preprocessing.py`, so capitals, accents, hyphens and slashes do not matter.

Steps, for each part of the text between punctuation marks:

1. Skills: the longest catalogue name or alias first ("engineering mathematics" wins over a shorter name inside it).
2. Interests by full name, in English or in the French draft.
3. Interests by a former name, with simple word endings removed ("mathematical" reaches "mathematics", which now means "Working with numbers and calculations").
4. Interests by key words: at least 2 key words of one interest's name in the same part of the text, ignoring common words such as "working", "with" and "people".
5. Words that match nothing, and the 5 retired interest names (communication, design, engineering, problem solving, technology), are reported for review. Retired names are never guessed.

| Match type | Confidence |
|---|---|
| Catalogue skill name | high |
| Skill alias | high |
| Full interest name, English or French | high |
| Former interest name | medium |
| Key words of an interest name | low |

Results are deterministic: the same text and catalogue always give the same result. Text longer than 5,000 characters is cut, and `text_truncated` is set.

## 3. Limitations

- It matches names, not meaning. "I build websites" does not find "web development" unless the words match a name or alias. Examples and explanations of interests are not used, so "visiting mines and rivers" is reported for review.
- It does not understand negation. "I do not like teaching" still suggests teaching. The student must confirm every suggestion.
- Key-word matches have low confidence and can be wrong.
- French support covers the French draft interest names and the French skill aliases already in the dataset only. The French drafts are unreviewed.
- Terms outside the catalogue, such as farming or agriculture, are reported, not mapped, because the catalogue has no such entry.

## 4. Why it does not touch the recommendation engine

The assistant only proposes inputs. It does not import or change the engine, the scoring weights (55% required skills, 15% preferred skills, 25% interests, 5% education), ranking, tie-breaks, the dataset or saved sessions. Confirmed suggestions go through the same validation and scoring as manual choices. `tests/test_profile_assistant.py` checks that the same official profile scores exactly the same either way.

## 5. Running the tests

```bash
python -m pytest -q tests/test_profile_assistant.py
python -m pytest -q
```

## 6. The assistant panel on the assessment page (Phase 3)

Files: `src/ui/assessment_assistant.py`, one call in `pages/1_Career_Assessment.py`. Tests: `tests/test_assessment_assistant_ui.py`.

### Turning it on

The panel is hidden unless the environment variable `CRS_ASSESSMENT_ASSISTANT` is `1`, `true`, `yes` or `on`. It is not set anywhere in the repository or on the live app, so the live app is unchanged.

```bash
CRS_ASSESSMENT_ASSISTANT=1 streamlit run app.py
```

On Windows PowerShell: `$env:CRS_ASSESSMENT_ASSISTANT="1"; streamlit run app.py`.

### What the student does

1. Opens "Career Assessment Assistant" above the assessment and writes a description (up to 5,000 characters).
2. Presses "Suggest skills and interests". The Phase 2 matcher runs. Nothing changes yet.
3. Reviews the suggestions. Each one shows its confidence, the student's words that triggered it and an explanation. High and medium confidence suggestions start ticked, low confidence ones start unticked. Entries already chosen are shown as "already in your answers" and cannot be added twice. Words that matched nothing are listed for review.
4. Presses "Add the ticked suggestions to my answers". Ticked interests are added to the list in section 1, ticked skills to the list in section 2. Choices already made are kept.
5. Presses "Save my assessment" as before. Saving, validation and scoring are unchanged.

### Privacy and safety

- The matcher is local Python. No network call, model, API key or paid service is used.
- The description stays only in the open page. It is cleared after confirming, with "Clear", with "Start a new assessment" and when a saved session is uploaded (Phase 3.1), together with any suggestions and ticks, so nothing from one student remains for the next on a shared computer. It is never part of the saved profile, the address bar or the session file.
- The student's words are shown as plain text, so Markdown or HTML in them never becomes a link or image.
- Nothing in the description is run as code, and the catalogue cannot be changed.
- If the matcher fails, the panel shows a message and the assessment keeps working.

## 7. Future option: a local Ollama model (not implemented)

A later phase could add an optional local model for descriptions that name-matching misses. It would not need a paid API.

1. Ollama, running on the student's or owner's computer, receives the student's text.
2. It proposes candidate skills and interests, using only the catalogue names it was given.
3. Python checks every candidate against `catalog.known_skills` and `catalog.interests`.
4. Any candidate not in the catalogue is rejected and never shown as a suggestion.
5. The student approves or removes each suggestion.
6. The existing assessment logic processes only the confirmed selections, exactly as with manual choices.

Constraints for that phase:

- The model would run locally only. Streamlit Community Cloud allows at most about 2.7 GB of memory, which is not enough for a local model, so the live app would keep the Python matcher.
- The student's text would be treated as data, never as instructions, and never stored.
- The Python matcher in this file stays the default and the fallback.
