# Cross-Project Bug Localisation (CPL): Replication Package

Code and results for the paper *"What Works, What Doesn't, and Why: An Empirical Investigation
of Cross-Project Bug Localisation"* (A Eashaan Rao, Sridhar Chimalakonda, IIT Tirupati).

We compare three bug localisation models (**TRANP-CNN**, **COOBA**, **BLAZE**) on 63
source→target pairs from 13 Python projects, under four training scenarios:

| Scenario | Source project data | Target project data |
|---|---|---|
| WP-small | none | 20% of target bugs |
| WP-large | none | 80% of target bugs |
| CP-cold-start | all source bugs | none |
| CP-transfer | all source bugs | 20% of target bugs |

All scenarios are tested on the same 20% target test split. Each model reranks the same
top-300 FAISS candidates (`BAAI/bge-code-v1` embeddings).

The archived replication package, with the data (bug reports, project metadata, a sample
embedding database), is on Zenodo: <https://doi.org/10.5281/zenodo.23984359>.

## Quick start: reproduce the paper's tables and figures

This doesn't need a GPU. The analysis scripts read the result CSVs already in `results/`,
plus `project_metadata.parquet` and `bug_reports.parquet` from the Zenodo data.

All paths are relative to the repository root, so you can run the scripts from any folder.

```bash
# 1. Set up the environment (Python 3.12)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Download cpl_data_artifact.zip from Zenodo and put the .parquet files in data/processed/
unzip cpl_data_artifact.zip
mkdir -p data/processed
cp cpl_data_artifact/*.parquet data/processed/

# 3. Run the analyses
python Scripts/analysis/main_results_table.py               # main results + Wilcoxon tests
python Scripts/analysis/effect_size_analysis.py             # Cohen's d
python Scripts/analysis/negative_transfer_analysis.py       # negative transfer
python Scripts/analysis/mixed_effects_check.py              # robustness check (run after the line above)
python Scripts/analysis/cold_start_viability_analysis.py    # CP-cold-start
python Scripts/analysis/cross_model_consistency_analysis.py # agreement between models
python Scripts/analysis/source_quality_transfer_analysis.py # source quality vs. transfer
python Scripts/analysis/source_selection_analysis.py        # source project selection
python Scripts/analysis/equivalence_and_robustness_tests.py # TOST equivalence tests
python Scripts/analysis/journal_figures.py                  # paper figures -> journal_draft/figs/
```

Outputs are written to `results/` and `results/images/`.

## Full re-run of the experiments (GPU recommended)

This retrains every model, so you also need the cloned project repositories and the full
embedding databases. `cpl_data_artifact/DATA_README.md` (inside the Zenodo zip) explains how
to rebuild them. The scripts
expect this layout inside the repository:

```
data/
├── repos/<language>/<owner>_<repo>/     # cloned project repositories
├── processed/                           # .parquet files, embedding_dbs/, model caches
└── glove/glove.6B.300d.txt              # GloVe vectors (COOBA only)
```

```bash
python Scripts/build_embed_database_pipeline.py        # 1. build embedding databases
python Scripts/run_expts_ph1.py                        # 2. all models, pairs and scenarios
python Scripts/run_wp_small_matched_budget.py          # 3. WP-small (once per target)
python Scripts/analysis/merge_wp_small_matched_budget.py
python Scripts/run_faiss_experiment.py                 # 4. FAISS retrieval recall
python Scripts/domain_gap.py                           # 5. domain gap between projects
```

If a run stops, start it again and it skips what's already done. To split the work across
GPUs, set the `SHARD` and `NUM_SHARDS` environment variables.

## What's in the repository

| Folder | Contents |
|---|---|
| `src/` | Model code: `tranp_cnn/`, `cooba/`, `blaze/` (`blgan/` is imported by the runner but not used in the paper) |
| `Scripts/` | Experiment runners; `Scripts/analysis/` holds the statistics and figures |
| `results/` | All result CSVs, per-bug diagnostics and figures |
| `journal_draft/figs/` | Figures as they appear in the paper |
| `benchmark_dataset_analysis/` | Notebooks showing how the 13 projects were chosen |
| `docs/model_guides/` | Notes on how COOBA and TRANP-CNN were re-implemented |
| `docs/supplementary_results.pdf` | Extended results for the paper (search protocol, model and statistical details, further RQ1–RQ3 results) |

The main results file is `results/paper_results_complete_corrected.csv`, with 756 rows
(63 pairs × 4 scenarios × 3 models) and Top-1/5/10, MAP and MRR for each run.

BLAZE note: in the paper's runs, BLAZE split every file into fixed 60-line chunks. Its
code-structure chunker fell back silently to this split because `tree-sitter==0.25.2` is
incompatible with `tree-sitter-languages==1.10.2`. With a working tree-sitter install the
chunker splits at code-structure boundaries instead, so BLAZE numbers will differ from the
paper. Use those two versions to reproduce the paper exactly.

## Citation

If you use this code, please cite the paper. The Zenodo record has the citation details.
