# Inter-rater agreement for graded labels (library functions only)
# Reviewer sheets are analysed only through the guarded tool: python -m src.evaluation.eval64_review_analysis

from src.evaluation.eval64_data import GRADES


def weighted_kappa(pairs, categories=GRADES, weighting="quadratic", sample_weights=None):
    # Cohen's weighted kappa for (rater_a, rater_b) grade pairs; None when undefined
    # sample_weights: optional design weights (inverse inclusion probabilities), one per pair
    if not pairs:
        return None
    weights = list(sample_weights) if sample_weights is not None else [1.0] * len(pairs)
    if len(weights) != len(pairs) or any(w < 0 for w in weights):
        raise ValueError("sample_weights must give one non-negative weight per pair")
    total = sum(weights)
    if total <= 0:
        return None
    k = len(categories)
    index = {c: i for i, c in enumerate(categories)}
    observed = [[0.0] * k for _ in range(k)]
    for (a, b), w in zip(pairs, weights):
        observed[index[a]][index[b]] += w / total
    row = [sum(observed[i]) for i in range(k)]
    col = [sum(observed[i][j] for i in range(k)) for j in range(k)]

    def disagreement(i, j):
        d = abs(i - j) / (k - 1)
        return d * d if weighting == "quadratic" else d

    disagree_obs = sum(disagreement(i, j) * observed[i][j] for i in range(k) for j in range(k))
    disagree_exp = sum(disagreement(i, j) * row[i] * col[j] for i in range(k) for j in range(k))
    if disagree_exp == 0:
        return None
    return 1 - disagree_obs / disagree_exp
