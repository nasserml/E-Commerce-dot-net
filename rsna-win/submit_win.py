#!/usr/bin/env python3
"""Validate and push the RSNA win-blend notebook (v2).

  python3 submit_win.py            # validate only (no kaggle CLI needed)
  python3 submit_win.py --push     # validate, then `kaggle kernels push`

Validation (all must pass before anything is pushed):
  * exactly 26 cells: probe-config at 1, refs at 0 and 2-22, graft at 23,
    arm guard at 24, publish+audit at 25
  * cell 1 carries the probe-config knobs with safe defaults
  * cell 23 contains the 4-way coat graft (Global96 + Repair-v1 readers,
    probability-mean reduction, N-member fallback guard) AND the v2
    additions: widedense-v4 fifth arm, dispatch for arm index 4,
    WIN_* config hooks, 0.946-proven renta outer weights, alpha 0.4 base
  * cell 24 keeps the no-checkpoint skip guard (degrade to parent)
  * publish cell keeps the DINOv2 20/20 and V18 calibrator gates
  * every code cell compiles
  * kernel-metadata.json carries all 15 dataset attachments
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NB = HERE / "rsna-knee-win-blend.ipynb"
META = HERE / "kernel-metadata.json"

REQUIRED_DATASETS = {
    "dreaddevelopment/raptor-knee-maxspan",
    "dreaddevelopment/raptor-knee-native384",
    "dreaddevelopment/raptor-knee-native384dense",
    "dreaddevelopment/raptor-knee-widedense",
    "mattiaangeli/knee-mri-fold-weights",
    "mattiaangeli/opencv-python-headless-4120088-x86",
    "marwanmath/resnet-50-radimagenet-marwan",
    "mattiaangeli/rsna-knee-coat-resgated-ep10-top3",
    "mattiaangeli/rsna-knee-coatnet-d4-depthzone-swa3-b2",
    "mattiaangeli/rsna-knee-coatnet-global96-top3",
    "antoinegg1/rsna-knee-e11-diverse-heads-v20",
    "antoinegg1/rsna-knee-e9-radimagenet-heads-v15",
    "pilkwang/rsna-knee-llm-labels",
    "prvsiyan/rsna-knee-v52-radimagenet-heads-20260812",
    "pilkwang/rsna-knee-weights",
}

problems = []


def need(cond, msg):
    if not cond:
        problems.append(msg)


nb = json.load(open(NB))
cells = nb["cells"]
need(len(cells) == 26, f"expected 26 cells, got {len(cells)}")
src = ["".join(c.get("source", [])) for c in cells]

for i, text in enumerate(src):
    if cells[i]["cell_type"] != "code":
        continue
    try:
        compile(text, f"<cell {i}>", "exec")
    except SyntaxError as e:
        problems.append(f"cell {i} does not compile: {e}")

# ---- probe-config cell (index 1)
cfg = src[1] if len(src) > 1 else ""
for marker in ("WIN_OUTER_W = {}", "WIN_OUTER_BASE = None",
               "WIN_ALPHA = None", "WIN_ARM_W = {}"):
    need(marker in cfg, f"config cell missing {marker!r}")
need("ANALYSIS.md" in cfg, "config cell must point at the probe plan")

# ---- graft cell (index 23)
c23 = src[23]
for marker in (
    "coatnet_global96_top3_manifest.json",
    "coatnet_repairv1_top3_manifest.json",
    "_run_global96_reader",
    "_run_repairv1_reader",
    "rank_of_member_probability_mean",
    "mean_of_member_ranks_fallback_probabilities_unavailable",
    "coat_substitute_failed",
    "private_alpha = 0.4 if _win_alpha is None",
    "'ACL': 0.75",
    "'Medial Meniscus': 0.80",
    "'Lateral Meniscus': 1.00",
    "'Lateral OA': 0.75",
    "'Fracture': 0.75",
    # v2 additions
    '"name": "widedense-v4"',
    '"file": "raptor_ft_coatnet_v4_full.pt"',
    '"span": (0.06, 0.94), "k_eval": 42',
    "run_single(4, torch.device(",
    "globals().get('WIN_ARM_W')",
    "globals().get('WIN_OUTER_W')",
    "globals().get('WIN_OUTER_BASE')",
    "globals().get('WIN_ALPHA')",
    "win_config_unknown_arm",
    "win_config_unknown_label",
):
    need(marker in c23, f"cell 23 missing {marker!r}")
for stale in ("private_alpha = 0.45", "'ACL': 0.68", "'Lateral Meniscus': 0.65"):
    need(stale not in c23, f"cell 23 still contains stale {stale!r}")

# ---- arm-guard cell (index 24)
need("APPENDED ARM BLEND" in src[24], "cell 24 is not the arm-blend cell")
need("skipping the arm blend" in src[24], "cell 24 missing no-ckpt skip guard")
need('raise RuntimeError("no armA_fold' not in src[24],
     "cell 24 still raises when checkpoints are absent")

# ---- publish + audit cell (index 25)
pub = src[25]
for gate in ("_DINOV2_MATCHED_MEMBERS", "V18_CALIBRATOR_APPLIED",
             "coat_family_members", "global96_epochs"):
    need(gate in pub, f"publish cell missing {gate}")
need("'widedense-v4'" in pub, "publish expected-arms missing widedense-v4")

meta = json.load(open(META))
need(set(meta["dataset_sources"]) == REQUIRED_DATASETS,
     "kernel-metadata dataset set mismatch: "
     f"missing={sorted(REQUIRED_DATASETS - set(meta['dataset_sources']))} "
     f"extra={sorted(set(meta['dataset_sources']) - REQUIRED_DATASETS)}")
need(meta.get("enable_internet") is False, "internet must stay disabled")
need(meta.get("enable_gpu") is True, "GPU must be enabled")
need(meta.get("competition_sources") == ["rsna-knee-abnormality-detection"],
     "competition source mismatch")
need(meta.get("model_sources") == ["metaresearch/dinov2/PyTorch/small/1"],
     "DINOv2 model source missing")
need(len(meta.get("kernel_sources", [])) == 2, "expected 2 kernel sources")

if problems:
    print("VALIDATION FAILED:")
    for p in problems:
        print(" -", p)
    sys.exit(1)
print(f"validation OK: {NB.name} ({NB.stat().st_size} bytes), 26 cells, "
      f"{len(meta['dataset_sources'])} datasets")

if "--push" in sys.argv:
    if "your-kaggle-username" in meta["id"]:
        sys.exit("set your Kaggle username in kernel-metadata.json first")
    r = subprocess.run(["kaggle", "kernels", "push", "-p", str(HERE)])
    sys.exit(r.returncode)
