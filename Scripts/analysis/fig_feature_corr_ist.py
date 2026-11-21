"""Regenerate Figure 4 (feature correlations) for the IST manuscript.

Same data and statistic as Scripts/analysis/negative_transfer_analysis.py
(plot_feature_correlations): Spearman rho between each project feature and
delta_mrr (CP-transfer - WP-small) per model, n = 63 pairs. Changes are
presentation only: one shared, fixed feature order across panels, readable
fonts at print size, plain-English labels, CVD-safe diverging colors, vector
output.

usage: python fig_feature_corr_ist.py <negative_transfer_analysis.csv> <out_prefix>
"""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import spearmanr

CSV, OUT = sys.argv[1], sys.argv[2]

# top-to-bottom display order: target, source, then pair-level features
FEATURES = [
    ("tgt_total_unique_bug_reports", "Target label volume"),
    ("tgt_LoC",                      "Target LoC"),
    ("tgt_bug_report_verbosity",     "Target bug-report verbosity"),
    ("src_total_unique_bug_reports", "Source # bug reports"),
    ("src_LoC",                      "Source LoC"),
    ("src_bug_report_verbosity",     "Source bug-report verbosity"),
    ("loc_ratio",                    "Source-to-target LoC ratio"),
    ("domain_gap",                   "Domain gap"),
]
MODELS = ["BLAZE", "COOBA", "TRANP-CNN"]
POS, NEG = "#2a78d6", "#e34948"          # validated diverging pair (blue / red)
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"

df = pd.read_csv(CSV)

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8,
                     "axes.edgecolor": MUTED, "axes.labelcolor": INK,
                     "xtick.color": MUTED, "ytick.color": INK})
fig, axes = plt.subplots(1, 3, figsize=(7.1, 2.75), sharey=True)
ypos = list(range(len(FEATURES)))[::-1]

for ax, model in zip(axes, MODELS):
    sub = df[df["model_name"] == model]
    for y, (col, label) in zip(ypos, FEATURES):
        m = sub[col].notna() & sub["delta_mrr"].notna()
        rho, p = spearmanr(sub.loc[m, col], sub.loc[m, "delta_mrr"])
        stars = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
        print(f"{model:10s} {label:38s} n={m.sum():2d} rho={rho:+.2f} p={p:.3f} {stars}")
        ax.barh(y, rho, height=0.62, color=POS if rho > 0 else NEG, linewidth=0)
        if stars:  # selective direct labels: significant correlations only
            txt = f"{rho:+.2f}{stars}".replace("-", "\u2212")
            # label sits in the empty half: past a positive bar's end, or just
            # right of zero for a negative bar (keeps clear of the y labels)
            x = rho + 0.04 if rho > 0 else 0.04
            ax.text(x, y, txt, va="center", ha="left", fontsize=7, color=INK)
    ax.axvline(0, color=MUTED, linewidth=0.8)
    ax.set_xlim(-1, 1)
    ax.set_xticks([-1, -0.5, 0, 0.5, 1])
    ax.grid(axis="x", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.set_title(model, fontsize=9, fontweight="bold", color=INK)
    ax.set_xlabel("Spearman $\\rho$ with CPL gain")

axes[0].set_yticks(ypos)
axes[0].set_yticklabels([lbl for _, lbl in FEATURES])
for a in axes:
    a.tick_params(axis="y", length=0)
fig.tight_layout(w_pad=0.8)
fig.savefig(OUT + ".pdf", bbox_inches="tight")
fig.savefig(OUT + ".png", dpi=600, bbox_inches="tight")
print("wrote", OUT + ".pdf", OUT + ".png")
