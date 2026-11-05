"""
project_metadata.py
Shared loader for project-level metadata used by the analysis scripts.

The experiments, their train/test splits and Table 2 of the paper all use
the bug-report database (bug_reports.parquet) as the source of truth for
per-project bug counts, so this loader sets `total_unique_bug_reports` in
project_metadata.parquet to the per-project row count from that database.
"""
import pandas as pd


def load_project_metadata(metadata_pkl, bug_reports_pkl=None):
    """Return project metadata with `total_unique_bug_reports` taken from the
    bug-report database (one row per bug report with ground truth)."""
    if bug_reports_pkl is None:
        bug_reports_pkl = metadata_pkl.replace("project_metadata.parquet", "bug_reports.parquet")
    meta = pd.read_parquet(metadata_pkl)
    counts = pd.read_parquet(bug_reports_pkl, columns=["repo_name"])["repo_name"].value_counts()
    meta["total_unique_bug_reports"] = (
        meta["repo_name"].map(counts).fillna(meta["total_unique_bug_reports"]).astype(int)
    )
    return meta
