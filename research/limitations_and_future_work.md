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

**On circularity.** The labels were not produced by the scoring rules. They were committed in d93b46b, 47 minutes after the engine code (d29ecaa), and have not changed since. The author states they were written before the engine was run on any profile; git cannot confirm that part (`model_audit.md`, section 2). Rule L1 asks the labeller to judge an occupation's core work rather than count overlap. The evaluation is therefore not mechanically circular. It is still indirectly circular, because one person's view shaped both the skill lists and the labels.

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
- The Interested and Not for me lists survive a page refresh through the page address only. They do not follow a student to another browser or device, and anyone given the address sees the chosen career ids. Accounts would be needed for lasting, private lists.
- Feedback is not stored or pooled, so the app does not learn across students. This protects privacy but means the global models cannot improve from use.

## 2c. Live model comparison

- The three models are trained on 56 author-written relevant labels from 36 synthetic profiles. Their rankings show how the methods differ for one learner, not which method is right. No accuracy is claimed for live profiles.
- Model scores come from balanced class weights and are not calibrated probabilities.
- The Decision Tree gives the same score to many careers; ties are ordered by career id, so the end of its list can be arbitrary. The page says when this happens.
- Random Forest explanations are path contributions averaged over trees. They add up exactly to the score but depend on tree structure and can differ from permutation-based importance.
- Training time and comparison time were measured once in the development container; other servers will differ.

## 2d. Machine-learning audit (29 October 2026)

- The main ML report breaks ties by career id. Random tie-breaking lowers the Decision Tree's MAP by 0.043 and Random Forest's by 0.013 in a one-repeat check, so tree models look slightly better in the main table than their expected ranking quality.
- The audit checks (random ties, leave-one-category-out, label permutation) use one repeat and scikit-learn models only; XGBoost was not included.
- Whether the engine was run before the labels were written rests on the author's statement; git shows only that the engine code was committed 47 minutes earlier.
- Further data needed for valid supervised learning on real learners: independent labels from at least three reviewers on a few hundred real profiles (Part B of the protocol), graded relevance, and a held-out test set written before any method change.

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
