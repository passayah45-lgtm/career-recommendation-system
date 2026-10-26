# Draws MAP with 95% bootstrap intervals for the formula and the four trained models from the saved report
import json
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

report = json.load(open(sys.argv[1]))
order = [("weighted_formula", "Weighted formula"), ("random_forest", "Random Forest"),
         ("logistic_regression", "Logistic Regression"), ("xgboost", "XGBoost"), ("decision_tree", "Decision Tree")]
names, means, lo, hi = [], [], [], []
for key, label in order:
    a = report["methods"][key]["ranking"]["average_precision"]
    names.append(label)
    means.append(a["mean"])
    lo.append(a["mean"] - a["ci95"][0])
    hi.append(a["ci95"][1] - a["mean"])
fig, ax = plt.subplots(figsize=(7.5, 3.6), dpi=200)
y = list(range(len(names)))[::-1]
colors = ["#0B7F78"] + ["#94A3B8"] * 4
ax.errorbar(means, y, xerr=[lo, hi], fmt="none", ecolor="#475569", capsize=4, lw=1.2)
ax.scatter(means, y, c=colors, s=80, zorder=3)
for yi, m in zip(y, means):
    ax.text(m, yi + 0.22, f"{m:.3f}", ha="center", fontsize=9, color="#14213D")
ax.set_yticks(y)
ax.set_yticklabels(names, fontsize=10)
ax.set_xlim(0.86, 1.0)
ax.set_xlabel("Mean average precision (95% bootstrap interval)", fontsize=10)
ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="x", color="#E2E8F0", lw=0.8)
ax.set_axisbelow(True)
fig.tight_layout()
fig.savefig(sys.argv[2])
