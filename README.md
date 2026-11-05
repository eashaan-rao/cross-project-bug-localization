# Cross-Project Bug Localisation (CPL) — Replication Package (Code)

Code artifact accompanying the paper *"What Works, What Doesn't, and Why: An Empirical
Investigation of Cross-Project Bug Localisation"* (A Eashaan Rao, Sridhar Chimalakonda,
Indian Institute of Technology Tirupati).

The study benchmarks three bug localisation models — **TRANP-CNN**, **COOBA**, and **BLAZE** —
on 63 source→target pairs drawn from 13 Python projects, under four scenarios:

| Scenario | Source data | Target training data |
|---|---|---|
| WP-small | — | 20% of target bugs |
| WP-large | — | 80% of target bugs |
| CP-cold-start | all source bugs | — |
| CP-transfer | all source bugs | 20% of target bugs |

All scenarios share the same held-out target test split (20%, `random_state=42`) and the same
first-stage FAISS retrieval: `BAAI/bge-code-v1` embeddings, `IndexFlatIP`, top-300 candidates,
which every model then reranks.

The companion **data artifact** (curated bug-report / project metadata and a sample embedding
database) is archived on Zenodo: <https://doi.org/10.5281/zenodo.21560518>.

## Repository layout

```
src/                          # Model implementations
├── tranp_cnn/                # TRANP-CNN — CNN-based reranker (text + code)
├── cooba/                    # COOBA — GNN-based bug localisation (AST embeddings, adversarial adaptation)
├── blaze/                    # BLAZE — embedding-based reranker
└── blgan/                    # BL-GAN (imported by the runner; not reported in the paper)

Scripts/
├── build_embed_database_pipeline.py   # Stage 1: build embedding databases
├── run_expts_ph1.py                   # Stage 2: main experiment runner (all pairs x 4 scenarios)
├── run_wp_small_matched_budget.py     # Stage 2b: WP-small, run once per (model, target)
├── run_faiss_experiment.py            # Stage 3: FAISS retrieval recall baseline
├── domain_gap.py                      # Stage 4: pairwise domain-gap analysis
├── analysis/                          # Statistical analyses, tables and figures (see below)
└── utils/check_and_unshallow_repos.py # Helper to verify / unshallow the cloned repositories

benchmark_dataset_analysis/   # Notebooks documenting selection/curation of the project dataset
docs/model_guides/            # Re-implementation notes for COOBA and TRANP-CNN, checked against the original papers
results/                      # Result CSVs, per-bug diagnostics and analysis figures
journal_draft/figs/           # Figures as they appear in the paper (output of journal_figures.py)
```

## Environment setup

Requires **Python 3.12**. A CUDA GPU is used automatically if available; all scripts fall back
to CPU otherwise.

```bash
python3 -m venv obj1
source obj1/bin/activate
pip install -r requirements.txt
```

All scripts use **absolute paths** defined as module-level constants at the top of each file
(`/home/cs21d002_eashaan/PhD/Objective1/...`). Edit these to point at your local checkout and
data locations before running.

## Reproducing the experiments

```bash
# Stage 1: build embedding databases (multi-process, BAAI/bge-code-v1)
python Scripts/build_embed_database_pipeline.py

# Stage 2: train/evaluate all models on all pairs and scenarios
#          -> results/obj1_experimental_results.csv, results/*_ph1_diagnostics/
python Scripts/run_expts_ph1.py

# Stage 2b: WP-small does not depend on the source project, so it is run once per
#           (model, target) and broadcast to every pair sharing that target
python Scripts/run_wp_small_matched_budget.py          # -> results/wp_small_matched_budget.csv
python Scripts/analysis/merge_wp_small_matched_budget.py

# Stage 3: FAISS retrieval recall baseline  -> results/faiss_recall_results/
python Scripts/run_faiss_experiment.py

# Stage 4: pairwise domain gap              -> results/all_project_domain_gaps.csv
python Scripts/domain_gap.py
```

Both runners are resumable (completed rows are skipped) and support `SHARD` / `NUM_SHARDS` for
splitting work across GPUs.

## Reproducing the paper's analyses

Every analysis reads the 63-pair paper results file `results/paper_results_complete_corrected.csv`
(756 rows = 63 pairs × 4 scenarios × 3 models; metric definitions as in the paper). `n_test` is the
number of test bugs per run and `n_reachable` the number whose ground-truth file is in the FAISS top-300.

```bash
python Scripts/analysis/main_results_table.py               # scenario means, CPL gain, Wilcoxon tests
python Scripts/analysis/effect_size_analysis.py             # Cohen's d effect sizes, stratified
python Scripts/analysis/negative_transfer_analysis.py       # negative transfer, commutativity, cross-domain
python Scripts/analysis/mixed_effects_check.py              # clustering-robust check (needs the step above)
python Scripts/analysis/cold_start_viability_analysis.py    # CP-cold-start viability
python Scripts/analysis/cross_model_consistency_analysis.py # cross-model agreement
python Scripts/analysis/source_quality_transfer_analysis.py # source quality vs. transfer
python Scripts/analysis/source_selection_analysis.py        # Kendall tau / Hit@K source selection
python Scripts/analysis/equivalence_and_robustness_tests.py # TOST equivalence and robustness tests
python Scripts/analysis/journal_figures.py                  # paper figures -> journal_draft/figs/
```

## Key results files (in `results/`)

| File | Description |
|---|---|
| `paper_results_complete_corrected.csv` | Paper results: 63 pairs × 4 scenarios × 3 models, Top-1/5/10, MAP, MRR |
| `obj1_experimental_results.csv` / `obj1_experimental_results_corrected.csv` | Raw runner output (all pairs run), with per-run reachability counts in the latter |
| `wp_small_matched_budget.csv` | Per-target WP-small results (13 targets × 3 models) |
| `main_results_*.csv` | Scenario means, CPL gain summary, Wilcoxon tests |
| `effect_size_*.csv`, `negative_transfer_analysis*.csv`, `cross_domain_breakdown.csv` | Effect size and negative transfer analyses |
| `cold_start_viability.csv`, `cross_model_agreement*.csv`, `source_quality_transfer.csv`, `source_selection_validation*.csv` | Remaining RQ analyses |
| `all_project_domain_gaps.csv` | Pairwise domain gap (logistic-regression accuracy) |
| `faiss_recall_results/`, `mrr_per_ext_repo.csv` | FAISS first-stage recall@K per project |
| `{tranp_cnn,cooba,blaze}_ph1_diagnostics/` | Per-bug ranking diagnostics (FAISS rank vs. model rank) for every run |
| `images/` | Figures produced by the analysis scripts |

The raw source-code embedding caches, tokenised training caches and cloned project repositories
are not included (too large); see the data artifact's `DATA_README.md` for regeneration commands.

## Citation

If you use this code, please cite the paper (see the Zenodo record's citation metadata).
