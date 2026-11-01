# Charts for the independent 64-career evaluation, drawn from the saved CSV and JSON outputs
# Run: python -m src.evaluation.eval64_charts reports/evaluation_64

import csv
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import MaxNLocator  # noqa: E402

SURFACE, INK, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
BLUE, ORANGE = "#2a78d6", "#eb6834"
LABELS = {"precision_at_1": "Precision@1", "precision_at_3": "Precision@3", "precision_at_5": "Precision@5",
          "recall_at_5": "Recall@5", "f1_at_5": "F1@5", "hit_at_5": "Hit@5", "reciprocal_rank": "MRR",
          "average_precision": "MAP", "ndcg_at_5": "NDCG@5"}


def _style(ax):
    ax.set_facecolor(SURFACE)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def _figure(width=8, height=4.5):
    fig, ax = plt.subplots(figsize=(width, height), dpi=150)
    fig.patch.set_facecolor(SURFACE)
    _style(ax)
    return fig, ax


def _save(fig, path, title, subtitle):
    fig.suptitle(title, x=0.02, ha="left", fontsize=12, color=INK, fontweight="bold")
    fig.text(0.02, 0.905, subtitle, ha="left", fontsize=8.5, color=MUTED)
    fig.tight_layout(rect=(0, 0, 1, 0.88))
    fig.savefig(path, facecolor=SURFACE, metadata={"Software": None})
    plt.close(fig)


def _read(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def overall_chart(d, out):
    rows = [r for r in _read(d / "overall_metrics.csv") if r["metric"] != "hit_at_5"]
    rows.reverse()
    fig, ax = _figure()
    y = range(len(rows))
    means = [float(r["mean"]) for r in rows]
    low = [float(r["mean"]) - float(r["ci_low"]) for r in rows]
    high = [float(r["ci_high"]) - float(r["mean"]) for r in rows]
    ax.barh(y, means, color=BLUE, height=0.55)
    ax.errorbar(means, y, xerr=[low, high], fmt="none", ecolor=INK, elinewidth=1.2, capsize=3)
    for i, r in enumerate(rows):
        ax.text(float(r["ci_high"]) + 0.015, i, f"{float(r['mean']):.3f}", va="center", fontsize=8.5, color=INK)
    ax.set_yticks(list(y), [LABELS[r["metric"]] for r in rows])
    ax.set_xlim(0, 1.08)
    ax.set_xlabel("Mean over profiles (whiskers: 95% bootstrap interval)", color=MUTED, fontsize=9)
    _save(fig, out / "overall_metrics.png", "Ranking metrics, 64-career catalogue",
          "111 synthetic profiles, single-author labels, relevant = grade 2 or 3 (101 profiles defined; NDCG uses all 111)")


def category_chart(d, out):
    rows = [r for r in _read(d / "confidence_intervals.csv")
            if r["scope"].startswith("category: ") and r["metric"] == "ndcg_at_5"]
    rows.sort(key=lambda r: float(r["mean"]))
    fig, ax = _figure()
    y = range(len(rows))
    means = [float(r["mean"]) for r in rows]
    ax.errorbar(means, y, xerr=[[m - float(r["ci_low"]) for m, r in zip(means, rows)],
                                [float(r["ci_high"]) - m for m, r in zip(means, rows)]],
                fmt="o", color=BLUE, ecolor=MUTED, elinewidth=1.2, capsize=3, markersize=7)
    for i, r in enumerate(rows):
        ax.text(1.02, i, f"n={r['defined_profiles']}", va="center", fontsize=8, color=MUTED)
    ax.set_yticks(list(y), [r["scope"].replace("category: ", "") for r in rows])
    ax.set_xlim(0, 1.1)
    ax.set_xlabel("NDCG@5 (dot: mean, whiskers: 95% bootstrap interval)", color=MUTED, fontsize=9)
    _save(fig, out / "category_ndcg.png", "NDCG@5 by primary category",
          "About 10 profiles per category: wide, overlapping intervals; indicative only, no ranking of categories")


def exposure_chart(d, out):
    rows = _read(d / "career_coverage.csv")
    fig, ax = _figure(8, 5)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    x = [int(r["relevant_labels"]) for r in rows]
    y = [int(r["top5_appearances"]) for r in rows]
    ax.scatter(x, y, s=46, color=BLUE, edgecolor=SURFACE, linewidth=1.5, zorder=3)
    x_top, y_top = max(x) + 1, max(y) + 4
    ax.plot([0, x_top], [0, x_top], color=MUTED, linewidth=1, linestyle="--", zorder=2)
    ax.text(x_top - 0.1, 0.8, "dashed line: appearances = relevant labels", ha="right", fontsize=8, color=MUTED)
    # Label the four most over-exposed careers; careers sharing one point get one combined label
    points = {}
    for r in sorted(rows, key=lambda r: int(r["top5_appearances"]) - int(r["relevant_labels"]), reverse=True)[:4]:
        points.setdefault((int(r["relevant_labels"]), int(r["top5_appearances"])), []).append(r["career_title"])
    for (px, py), titles in points.items():
        ax.annotate(" and ".join(titles), (px, py), xytext=(7, 3), textcoords="offset points", fontsize=8, color=INK)
    ax.set_xlabel("Profiles labelling the career relevant (grade 2 or 3)", color=MUTED, fontsize=9)
    ax.set_ylabel("Top-5 appearances across 111 profiles", color=MUTED, fontsize=9)
    ax.set_xlim(-0.3, x_top)
    ax.set_ylim(-0.5, y_top)
    _save(fig, out / "career_exposure.png", "Career exposure against need",
          "Each dot is one of the 64 careers; all 64 appear in at least one top 5. Points above the line are shown more often than labelled")


def score_chart(d, out):
    rows = _read(d / "profile_results.csv")
    top1 = [float(r["top5_scores"].split("|")[0]) for r in rows]
    top5 = [float(s) for r in rows for s in r["top5_scores"].split("|")]
    fig, axes = plt.subplots(1, 2, figsize=(8, 4), dpi=150, sharey=False)
    fig.patch.set_facecolor(SURFACE)
    bins = list(range(0, 105, 5))
    for ax, data, name in ((axes[0], top1, "Rank 1 score"), (axes[1], top5, "Scores in ranks 1 to 5")):
        _style(ax)
        ax.grid(axis="y", color=GRID, linewidth=0.8)
        ax.grid(axis="x", visible=False)
        ax.hist(data, bins=bins, color=BLUE, edgecolor=SURFACE, linewidth=2)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.set_title(name, fontsize=9.5, color=INK, loc="left")
        ax.set_xlabel("Compatibility score (0 to 100)", color=MUTED, fontsize=9)
    axes[0].set_ylabel("Profiles", color=MUTED, fontsize=9)
    axes[1].set_ylabel("Recommendation slots", color=MUTED, fontsize=9)
    _save(fig, out / "score_distribution.png", "Distribution of recommendation scores",
          "Interests add at most 25 points, so the peaks below 25 are careers matched on interests with few or no recognised skills")


def rank_chart(d, out):
    rows = _read(d / "ranking_rows.csv")
    ranks = [int(r["rank"]) for r in rows if int(r["grade"]) >= 2]
    buckets = [str(i) for i in range(1, 11)] + ["11-20", "21+"]
    counts = [sum(1 for x in ranks if x == i) for i in range(1, 11)]
    counts += [sum(1 for x in ranks if 11 <= x <= 20), sum(1 for x in ranks if x > 20)]
    fig, ax = _figure()
    ax.grid(axis="x", visible=False)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.bar(range(len(buckets)), counts, color=[BLUE if i < 5 else MUTED for i in range(len(buckets))], width=0.7)
    for i, c in enumerate(counts):
        ax.text(i, c + 0.8, str(c), ha="center", fontsize=8, color=INK)
    ax.set_xticks(range(len(buckets)), buckets)
    ax.set_xlabel("Rank of the relevant career in the full ranking of 64", color=MUTED, fontsize=9)
    ax.set_ylabel("Relevant profile-career pairs", color=MUTED, fontsize=9)
    _save(fig, out / "relevant_rank_positions.png", "Where relevant careers rank",
          f"{len(ranks)} pairs at grade 2 or 3; blue bars are inside the top 5")


def comparison_chart(d, out):
    summary = json.loads((d / "evaluation_summary.json").read_text(encoding="utf-8"))
    names = ("precision_at_5", "recall_at_5", "f1_at_5", "reciprocal_rank", "average_precision")
    orig = [summary["original_study"]["metrics"][n]["mean"] for n in names]
    new = [summary["overall"][n]["mean"] for n in names]
    fig, ax = _figure()
    ax.grid(axis="x", visible=False)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    xs = range(len(names))
    ax.bar([x - 0.19 for x in xs], orig, width=0.36, color=ORANGE, label="Original study: 50 careers, 35 profiles, binary labels")
    ax.bar([x + 0.19 for x in xs], new, width=0.36, color=BLUE, label="New study: 64 careers, 101 profiles, graded labels (grade 2+)")
    for x, a, b in zip(xs, orig, new):
        ax.text(x - 0.19, a + 0.015, f"{a:.2f}", ha="center", fontsize=8, color=INK)
        ax.text(x + 0.19, b + 0.015, f"{b:.2f}", ha="center", fontsize=8, color=INK)
    ax.set_xticks(list(xs), [LABELS[n] for n in names])
    ax.set_ylim(0, 1.1)
    ax.set_ylabel("Mean over defined profiles", color=MUTED, fontsize=9)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=1, fontsize=8, frameon=False, labelcolor=INK)
    _save(fig, out / "original_vs_new.png", "Two separate studies, shown side by side",
          "Different profiles, labelling and catalogue size: the gap is not evidence that the expansion changed accuracy")


def robustness_chart(d, out):
    rows = [r for r in _read(d / "robustness_results.csv") if r["mean_ndcg_at_5_before"]]
    rows.reverse()
    fig, ax = _figure()
    for i, r in enumerate(rows):
        b, a = float(r["mean_ndcg_at_5_before"]), float(r["mean_ndcg_at_5_after"])
        ax.plot([b, a], [i, i], color=GRID, linewidth=3, zorder=2)
        ax.scatter([b], [i], s=50, color=MUTED, zorder=3)
        ax.scatter([a], [i], s=50, color=BLUE, zorder=4)
        ax.text(1.01, i, f"n={r['profiles']}", va="center", fontsize=8, color=MUTED)
    ax.set_yticks(range(len(rows)), [r["condition"].split("_", 1)[1].replace("_", " ") for r in rows])
    ax.set_xlim(0, 1.1)
    ax.set_xlabel("Mean NDCG@5 against the unchanged labels (grey: original profile, blue: changed profile)",
                  color=MUTED, fontsize=8.5)
    _save(fig, out / "robustness.png", "Robustness: NDCG@5 before and after each change",
          "Removing or adding inputs changes what the learner says, so a lower score is behaviour, not an error by itself")


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    d = Path(argv[0] if argv else "reports/evaluation_64")
    out = d / "charts"
    out.mkdir(parents=True, exist_ok=True)
    for chart in (overall_chart, category_chart, exposure_chart, score_chart, rank_chart, comparison_chart,
                  robustness_chart):
        chart(d, out)
    print(f"Charts written to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
