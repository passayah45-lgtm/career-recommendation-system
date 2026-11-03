# Project instructions for contributors and coding assistants

These instructions apply to every change in this repository, by people or by AI coding assistants.

## Permanent rule: preserve existing functionality

**Never remove, delete, disable, replace, simplify, or silently alter existing functionality unless Issa TOURE explicitly authorizes the change.**

This applies to:

- features
- pages
- buttons
- navigation
- learning resources
- resource links
- career information
- skill mappings
- user workflows
- integrations
- tests
- documentation
- existing UI components

Requirements:

1. Every requested feature must preserve unrelated existing functionality.
2. Before removing or replacing anything, inspect the existing implementation.
3. If a requested change conflicts with an existing feature, explain the conflict and propose a solution that preserves both.
4. Never treat a request to add or improve functionality as permission to remove existing functionality.
5. Never remove a test just because it fails after a change. Investigate the regression first.
6. Obtain explicit approval before removing existing functionality.

## Related safeguards already in the repository

- `tests/test_learning_resources_regression.py` protects the learning resources, their links, their skill mappings, their free status, the Skill-Gap resource tabs and table view, the Skill Roadmap and the navigation.
- `tests/test_frozen_report_hashes.py` and the frozen snapshot checks protect the published evaluation reports and data.
- Pushing to `main` redeploys the live Streamlit application, so commits and pushes need the owner's explicit approval.
