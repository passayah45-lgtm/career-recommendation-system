# Limitations, validity threats, ethics and future work

## 1. Limitations of the current evidence

| Limitation | Evidence | Consequence |
|---|---|---|
| Synthetic profiles only | 36 author-written profiles; 21 of them "strong match" | Results cannot describe real learners |
| One author for everything | Same person wrote the careers, the engine and the labels (`docs/evaluation_report.md` section 10) | Agreement is inflated |
| Shared vocabulary | 129 of 142 profile skill entries (91%) are exact catalogue names, 9 are aliases, 4 are unknown | Exact matching is favoured |
| Small sample | 35 scorable profiles; only 5 or 6 rankings change in most ablations | Low power; non-significant results do not show "no effect" |
| Saturated top-5 metrics | Recall@5 = 1.0 for most methods | Only order-sensitive metrics separate methods |
| Binary labels | Relevant or not | Graded quality hidden; NDCG uses gain 1 |
| Tests not pre-registered | Chosen before results but not registered | Report as exploratory |

**On circularity.** The labels were not produced by the scoring rules. They were committed before the engine ran (commit d93b46b), and rule L1 asks the labeller to judge an occupation's core work rather than count overlap. The evaluation is therefore not mechanically circular. It is still indirectly circular, because one person's view shaped both the skill lists and the labels.

## 2. Limitations of the system and dataset

- 50 careers, against 923 O*NET data-level occupations.
- Exact matching: related skills earn no credit unless an alias exists.
- List-length bias: one shared skill counts more for careers with three required skills than for careers with five.
- Education separates careers very little (42 of 50 at level 3); removing it changed no synthetic ranking.
- Skill lists, interests and education levels are curated without field-level sources. Education is not checked against O*NET Job Zones.
- Three careers have no O*NET occupation; seven map to a broader one.
- U.S.-framed occupations (O*NET) for intended users in India and Guinea.
- English only; one resource per skill.
- No licence file.

## 2b. Session feedback

- The per-student adaptation (Interested / Not for me) uses fixed similarity rules. Its usefulness has not been tested with real students; the planned user study should compare lists before and after feedback.
- Feedback is not stored or pooled, so the app does not learn across students. This protects privacy but means the global models cannot improve from use.

## 3. Threats to validity

| Type | Threat | Mitigation planned |
|---|---|---|
| Construct | Reviewer "relevance" is not a career outcome | Report as expert agreement only |
| Internal | Author influence on labels, weights, aliases | Independent reviewers; freeze tag; no author labelling |
| Internal | Leakage between development and evaluation | Separate data tracks; thresholds tuned on synthetic data only |
| External | One university, one country, English | State scope; invite replication |
| Statistical | Small samples, many comparisons | Power analysis; Holm correction; intervals for all results |
| Conclusion | Reviewer disagreement | Report kappa; per-reviewer sensitivity analysis |

## 4. Ethical considerations

- No participant has been recruited and no human data exists.
- The independent-label study and the user study require KIIT ethics approval before any recruitment.
- Draft instruments are in `research/instruments/`: information sheet and consent form, profile form, reviewer guide, questionnaire.
- Participation is voluntary and limited to adults (18 or older); withdrawal is allowed until anonymisation.
- No names, roll numbers or contact details are stored with answers. Data is encrypted, and anonymised data is shared only with consent.
- Participants are told that recommendations are not hiring predictions or professional career advice.
- O*NET content is CC BY 4.0, so any released data must carry attribution.

## 5. Future work

### Required before a paper's main claims

1. Ethics approval, then the independent-label study (about 70 profiles, 3 reviewers).
2. User study of explanations and gap advice (about 35 students).
3. A held-out synthetic set written before any further change.
4. Semantic-matching baseline B4 with a pinned embedding model.

### Dataset improvements

1. Resolve the three unmatched careers and record every mapping type in the data.
2. Compare skill lists with O*NET technology skills and ESCO essential skills.
3. Compare education levels with O*NET Job Zones.
4. Add a licence and O*NET attribution.

### Longer term

1. ESCO cross-dataset validation.
2. Indian labour-market data and local occupations.
3. Graded skill importance instead of binary lists.
4. More languages (Hindi, Odia, French).
5. CV upload with skill extraction.
6. A REST API for T-Career integration.
