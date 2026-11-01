# Second review for eval64_v1

| File | Content | Send to reviewer? |
|---|---|---|
| `second_reviewer_sheet.csv` | Frozen blank sheet with original IDs, 585 pairs: all 363 listed pairs plus 2 random unlisted careers per profile (seed 6464), shuffled within each profile. Rebuilt byte for byte by `src/evaluation/eval64_review_sampling.py`. Never edit | No |
| `reviewer_packet.md` | Readable version with original IDs | No |
| `anonymised/reviewer_sheet.csv` | Blank sheet with random profile and career codes, random order | **Yes** |
| `anonymised/reviewer_packet.md` | Readable packet with the same codes, no O*NET column | **Yes** |
| `private/anonymisation_map.json` | Private mapping from codes to IDs, with SHA-256 checks | **Never** |

The reviewer bundle is: `docs/reviewer_handover.md`, `docs/independent_64_second_review_guide.md` (sent as `second_review_guide.md`), and the two files in `anonymised/`.

Analysis after a real review: `python -m src.evaluation.eval64_review_analysis <completed anonymised sheet> --anonymised --confirm-independent-reviewer`.

The original labels (`../relevance_labels.csv`) and the private key are not in the public repository until the review is complete; see `docs/independent_64_evaluation_results.md`, section 18.

No reviewer grades and no agreement statistics exist yet.
