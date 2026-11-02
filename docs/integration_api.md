# Integration notes (T-Career and other callers)

The public entry point is `src.services.recommendations.recommend(profile, catalog, top_k)`. The full input and output schema is in `docs/recommendation_algorithm.md`, sections 4 and 7.

## Interests from dataset v1.4.0 (interest taxonomy 2.0)

- Send interests as the full names of the 23 current interests, for example "Caring for people's health". The stored form (`caring for peoples health`) and any capitalisation are also accepted.
- Draft French names are accepted as input. They are unreviewed drafts and may change.
- Old names from the 20-term vocabulary still work where a direct replacement exists, and the response lists them under `profile.report.migrated_interests`. Five old names are not scored (communication, design, engineering, problem solving, technology) and are listed under `profile.report.retired_interests`. Callers should move to the new names: migrated old profiles rank somewhat worse (`docs/interest_taxonomy_implementation.md`, section 4).
- Each recommendation returns `matched_interests` and `career_interests` (stored forms) and `matched_interest_labels` and `career_interest_labels` (full names to display).
- More than 5 interests adds a warning but every interest is scored.
- The list of interests with descriptions, examples, related skills and RIASEC display groups is `src.data.interest_taxonomy.INTEREST_TERMS`.

Status: owner-authorized implementation pending lecturer feedback.

## Notice to integrators (3 November 2026)

Dataset v1.4.0 replaces the 20 interest words with 23 described interests, and every career's interests changed, so rankings for the same input change too.
- Please send the new full names from `INTEREST_TERMS`.
- Old names are still accepted. 15 are translated and reported in `migrated_interests`. communication, design, engineering, problem solving and technology are not scored and are reported in `retired_interests`.
- Show `matched_interest_labels` to users instead of the stored forms.
- The output schema is unchanged apart from the added label fields and report lists.
- The taxonomy is an owner-authorized implementation. Lecturer feedback is still pending, so further changes are possible in a later dataset version.
