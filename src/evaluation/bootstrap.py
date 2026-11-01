# Profile-level percentile bootstrap: each resample draws whole profiles, and every metric uses the same draw

import random

DEFAULT_RESAMPLES = 2000
DEFAULT_SEED = 64


def _percentile(sorted_values, q):
    # Nearest-rank percentile on an already sorted list
    if not sorted_values:
        return None
    index = min(len(sorted_values) - 1, max(0, int(q * len(sorted_values))))
    return sorted_values[index]


def profile_bootstrap(rows, metric_names, n_resamples=DEFAULT_RESAMPLES, seed=DEFAULT_SEED, confidence=0.95):
    # rows: one dict per profile; a None value is undefined for that profile and skipped for that metric only
    # Returns {metric: {"mean", "ci_low", "ci_high", "defined_profiles", "undefined_profiles", "resamples"}}
    n = len(rows)
    out = {}
    for name in metric_names:
        values = [r[name] for r in rows if r[name] is not None]
        out[name] = {
            "mean": sum(values) / len(values) if values else None,
            "ci_low": None, "ci_high": None,
            "defined_profiles": len(values), "undefined_profiles": n - len(values),
            "resamples": n_resamples,
        }
    if n < 2:
        return out
    rng = random.Random(seed)
    draws = {name: [] for name in metric_names}
    for _ in range(n_resamples):
        sample = [rows[rng.randrange(n)] for _ in range(n)]
        for name in metric_names:
            values = [r[name] for r in sample if r[name] is not None]
            if values:
                draws[name].append(sum(values) / len(values))
    alpha = (1 - confidence) / 2
    for name in metric_names:
        means = sorted(draws[name])
        if out[name]["defined_profiles"] >= 2 and means:
            out[name]["ci_low"] = _percentile(means, alpha)
            out[name]["ci_high"] = _percentile(means, 1 - alpha)
    return out
