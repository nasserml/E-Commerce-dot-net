# RSNA Knee Win Blend — operations card

Push-ready Kaggle submission package for
[RSNA Knee Abnormality Detection](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection).

Read **ANALYSIS.md** first (deep analysis, evidence, and the phased plan to ≥ 0.961).
This file is only the how-to-run.

## Contents

| File | What it is |
|---|---|
| `rsna-knee-win-blend.ipynb` | the notebook to submit (26 cells; cell 1 = probe-config) |
| `kernel-metadata.json` | attachments for `kaggle kernels push` (15 datasets, GPU, internet off) |
| `submit_win.py` | validator + push wrapper |
| `build_win_notebook.py` / `v1_cells.json` / `coat_section.py` | reproducible rebuild: reference + v1 grafted-cell snapshot + v2 grafts |
| `dryrun_coat_graft.py` | 8-scenario semantic dry-run (all passing) |

## Push & submit

```bash
# 1 — put your Kaggle username into kernel-metadata.json ("id": "<you>/rsna-knee-win-blend")
# 2 — validate
python3 submit_win.py
#     validation OK: rsna-knee-win-blend.ipynb (268460 bytes), 26 cells, 15 datasets
# 3 — push (requires kaggle CLI authenticated)
python3 submit_win.py --push
# 4 — on Kaggle: run the private kernel (GPU, internet off), then submit its
#     submission.csv. 5 slots/day — see the probing plan in ANALYSIS.md §7.
```

## Probe between submissions (v2)

Edit **cell 1** of the notebook only — one knob per submission:

- `WIN_OUTER_W = {"Lateral Meniscus": 1.00}` — per-label raptor/CoAt routing
- `WIN_OUTER_BASE = 0.55` — routing for every other label
- `WIN_ALPHA = 0.45` — inner raptor/CoAt hybrid alpha
- `WIN_ARM_W = {"widedense-v4": 0.25}` — raptor arm probability-blend weights

Defaults (empty/None) reproduce the 0.946-proven recipe exactly (asserted by dry-run
scenario G). Grids and the 5/day probing plan: ANALYSIS.md §7.

## First-run checklist

- `btkd_v559_complete.json` → `coat_family_members == 4`, `family_reduction ==
  "rank_of_member_probability_mean"`, no `*_child_failed` events.
- `_coat_raptor_blend_receipt.json` → members `resgated_top3, global96_top3, d4_swa3,
  repairv1_top3`, `within_coat` all 0.25, `private_alpha` 0.4.
- `submission.csv`: one row per test study, 13 columns, finite values, SHA recorded.
- `raptor_raw.npz` → `raw_probabilities` has **5** slices (arms: maxspan-v5, v10,
  reverse, v8, widedense-v4); publish events would flag `raptor_preparation_identities_...`
  if the v4 arm skipped studies.
- If a coat member is missing the run still scores (~degraded to the 0.941-class
  baseline) — check the events, fix, re-run; nothing crashes.

## Re-verification after any edit

```bash
python3 build_win_notebook.py     # rebuild: reference + v1_cells.json + v2 grafts (deterministic)
python3 dryrun_coat_graft.py      # must end with ALL SCENARIOS PASSED
python3 submit_win.py             # must end with validation OK
```
