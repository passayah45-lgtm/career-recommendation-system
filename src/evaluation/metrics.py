# Ranking metrics against binary relevance labels
# Every function returns None when the metric is undefined, it never substitutes a value

import math
import random
from collections import Counter


def _hits(ranked_ids, relevant, k):
    return sum(1 for cid in ranked_ids[:k] if cid in relevant)


def precision_at_k(ranked_ids, relevant, k=5):
    # Hits in the top k divided by the number of items actually shown (k, or fewer if fewer exist)
    relevant = set(relevant)
    shown = min(k, len(ranked_ids))
    if not relevant or shown == 0:
        return None
    return _hits(ranked_ids, relevant, k) / shown


def attainable_precision_at_k(ranked_ids, relevant, k=5):
    # Hits divided by min(k, |relevant|), so a profile with 2 relevant careers can reach 1.0
    relevant = set(relevant)
    if not relevant or not ranked_ids:
        return None
    return _hits(ranked_ids, relevant, k) / min(k, len(relevant))


def recall_at_k(ranked_ids, relevant, k=5):
    relevant = set(relevant)
    if not relevant:
        return None
    return _hits(ranked_ids, relevant, k) / len(relevant)


def f1_score(precision, recall):
    # Harmonic mean, 0 when both are 0, undefined when either is undefined
    if precision is None or recall is None:
        return None
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def hit_at_k(ranked_ids, relevant, k=5):
    relevant = set(relevant)
    if not relevant:
        return None
    return 1.0 if _hits(ranked_ids, relevant, k) else 0.0


def reciprocal_rank(ranked_ids, relevant):
    # 1 / rank of the first relevant career in the full ranking, 0 if none appears
    relevant = set(relevant)
    if not relevant:
        return None
    for position, cid in enumerate(ranked_ids, start=1):
        if cid in relevant:
            return 1.0 / position
    return 0.0


def r_precision(ranked_ids, relevant):
    # Hits in the top |relevant| positions divided by |relevant|. Order-sensitive, reaches 1.0 only
    # when every relevant career ranks above every non-relevant one.
    relevant = set(relevant)
    if not relevant:
        return None
    return _hits(ranked_ids, relevant, len(relevant)) / len(relevant)


def average_precision(ranked_ids, relevant):
    # Mean of precision at each rank where a relevant career appears, over the full ranking
    relevant = set(relevant)
    if not relevant:
        return None
    found, total = 0, 0.0
    for position, cid in enumerate(ranked_ids, start=1):
        if cid in relevant:
            found += 1
            total += found / position
    return total / len(relevant)


def mean_defined(values):
    # Macro average over defined values. Returns (mean or None, defined count, undefined count)
    defined = [v for v in values if v is not None]
    undefined = len(values) - len(defined)
    if not defined:
        return None, 0, undefined
    return sum(defined) / len(defined), len(defined), undefined


def bootstrap_ci(values, n_resamples=2000, confidence=0.95, seed=42):
    # Percentile bootstrap interval of the mean over defined values, fixed seed for reproducibility
    data = [v for v in values if v is not None]
    if len(data) < 2:
        return None
    rng = random.Random(seed)
    means = sorted(sum(rng.choice(data) for _ in data) / len(data) for _ in range(n_resamples))
    low = means[int(((1 - confidence) / 2) * n_resamples)]
    high = means[min(n_resamples - 1, int((1 - (1 - confidence) / 2) * n_resamples))]
    return low, high


def catalogue_coverage(top_k_lists, catalogue_ids):
    # Share of catalogue careers that appear in at least one top-k list
    catalogue = set(catalogue_ids)
    if not catalogue:
        return None
    shown = {cid for lst in top_k_lists for cid in lst if cid in catalogue}
    return len(shown) / len(catalogue)


def category_distribution(top_k_lists, category_of):
    # Count and share of recommended slots per category
    counts = Counter(category_of[cid] for lst in top_k_lists for cid in lst)
    total = sum(counts.values())
    return {cat: {"count": n, "share": n / total if total else 0.0} for cat, n in sorted(counts.items())}


def ndcg_at_k(ranked_ids, relevant, k=5, grades=None):
    # Normalised discounted cumulative gain with log2 discount; gain 1 per relevant career unless grades are given
    gain = grades if grades is not None else {cid: 1 for cid in relevant}
    ideal = sorted((g for g in gain.values() if g > 0), reverse=True)[:k]
    if not ideal:
        return None
    dcg = sum(gain.get(cid, 0) / math.log2(i + 2) for i, cid in enumerate(ranked_ids[:k]))
    idcg = sum(g / math.log2(i + 2) for i, g in enumerate(ideal))
    return dcg / idcg


def paired_randomization_test(a, b, n_resamples=10000, seed=42):
    # Two-sided sign-flip test on paired per-profile differences; pairs with a None value are dropped
    diffs = [x - y for x, y in zip(a, b) if x is not None and y is not None]
    if not diffs:
        return None
    observed = abs(sum(diffs) / len(diffs))
    if all(d == 0 for d in diffs):
        return {"n": len(diffs), "mean_difference": 0.0, "p_value": 1.0, "nonzero_pairs": 0}
    rng = random.Random(seed)
    extreme = 0
    for _ in range(n_resamples):
        s = sum(d if rng.random() < 0.5 else -d for d in diffs)
        if abs(s / len(diffs)) >= observed - 1e-12:
            extreme += 1
    return {
        "n": len(diffs),
        "mean_difference": sum(diffs) / len(diffs),
        "p_value": (extreme + 1) / (n_resamples + 1),
        "nonzero_pairs": sum(1 for d in diffs if d != 0),
    }


def holm_adjust(p_values):
    # Holm step-down adjusted p-values, returned in the input order
    order = sorted(range(len(p_values)), key=lambda i: p_values[i])
    adjusted = [0.0] * len(p_values)
    running = 0.0
    m_total = len(p_values)
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (m_total - rank) * p_values[i]))
        adjusted[i] = running
    return adjusted
