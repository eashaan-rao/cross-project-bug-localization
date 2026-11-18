"""
merge_wp_small_matched_budget.py
──────────────────────────────────
Broadcasts the per-target WP-small results (20% of target bugs, matching
CP-transfer's target-side share) into the primary pair-keyed results files.

Input
─────
results/wp_small_matched_budget.csv  -- WP-small run (13 targets x 3 models),
                                         from Scripts/run_wp_small_matched_budget.py

Each row is keyed by (model_name, target_project) only -- WP-small doesn't
depend on the source project, so the same value is broadcast to every pair
that shares a target.

What this does
───────────────
Fills every row with scenario == 'WP-small' in:
    results/paper_results_complete_corrected.csv
    results/obj1_experimental_results_corrected.csv
    results/obj1_experimental_results.csv
setting top-1/top-5/top-10/MAP/MRR to the WP-small run's values for that
row's (model_name, target_project). WP-small is reported from a single
run, like every other scenario. The script overwrites in place and is
idempotent, since it replaces the WP-small metric columns wholesale.

Run inside the obj1 virtualenv:
    python Scripts/analysis/merge_wp_small_matched_budget.py
"""

import os
import pandas as pd

# Repository root; all data and result paths below are relative to it.
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
WPS_CSV = os.path.join(REPO_ROOT, "results/wp_small_matched_budget.csv")

METRICS = ["top-1", "top-5", "top-10", "MAP", "MRR"]

TARGET_FILES = [
    os.path.join(REPO_ROOT, "results/paper_results_complete_corrected.csv"),
    os.path.join(REPO_ROOT, "results/obj1_experimental_results_corrected.csv"),
    os.path.join(REPO_ROOT, "results/obj1_experimental_results.csv"),
]


def patch_file(path, wps):
    df = pd.read_csv(path)
    wps_cols = {m: f"{m}_wps" for m in METRICS}
    merged = df.merge(
        wps.rename(columns=wps_cols)[["model_name", "target_project"] + list(wps_cols.values())],
        on=["model_name", "target_project"], how="left",
    )
    is_wps = merged["scenario"] == "WP-small"
    has_wps = merged["MRR_wps"].notna()
    mask = is_wps & has_wps
    n_patched = mask.sum()
    n_unmatched = (is_wps & ~has_wps).sum()
    for metric, wps_col in wps_cols.items():
        merged.loc[mask, metric] = merged.loc[mask, wps_col]
    merged = merged.drop(columns=list(wps_cols.values()))
    merged.to_csv(path, index=False)
    print(f"  patched {n_patched} WP-small rows in {path}"
          + (f"  [WARNING: {n_unmatched} WP-small rows had no matching WP-small run]" if n_unmatched else ""))


def main():
    wps = pd.read_csv(WPS_CSV)
    print("Patching primary results files...")
    for path in TARGET_FILES:
        patch_file(path, wps)


if __name__ == "__main__":
    main()
