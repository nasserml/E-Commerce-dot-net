#!/usr/bin/env python3
"""Semantic dry-run of the grafted _coat_substitute + outer-blend + call-site wrapper
from rsna-knee-win-blend.ipynb cell 23 (v2; graft cell after the probe-config
insert), against a faked /kaggle/working.

Children are NOT executed; their generated source is asserted for exact
transcription markers instead. Blob-hash compares are neutralized in the test
copy only (the literals are byte-checked against the 0.946-proven source).

Scenarios:
  A  happy path            -> 4 members, rank-of-probability-mean, renta weights
  A2 outer blend           -> stage file written, LM weight 1.0 honored
  B  one npz missing       -> N-member mean-of-ranks fallback (the new guard)
  C  global96 dataset gone -> 3 members, still probability-mean
  D  all children fail     -> return 0, public _raptor.csv untouched
  E  wrapper               -> coat_substitute raising degrades to _coat_n = 0
  F  parallel pairs        -> pool path runs all four readers
"""
import ast
import json
import os
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

WIN = Path("/home/user/E-Commerce-dot-net/rsna-win/rsna-knee-win-blend.ipynb")
WORK = Path("/kaggle/working")
if not WORK.exists():
    # resets drop /kaggle; recreate it (best effort, mirrors the Kaggle runtime)
    import subprocess as _sp
    _sp.run(["sudo", "-n", "mkdir", "-p", str(WORK)], check=False)
    _sp.run(["sudo", "-n", "chown", "-R", __import__("getpass").getuser(), "/kaggle"],
            check=False)
FAKE = Path("/tmp/fake_kaggle_input")

LABELS = ["ACL", "MCL", "Medial Meniscus", "Lateral Meniscus", "Medial OA",
          "Lateral OA", "PF OA", "Effusion", "Synovitis", "Baker's",
          "Contusion", "Fracture"]
UIDS = [f"1.2.3.{i}" for i in range(7)]

failures, events, CHILD_LOG = [], [], []
FAIL_CHILDS, npz_absent = {}, {}


def need(cond, msg):
    if cond:
        return
    failures.append(msg)
    print("  !! " + msg)


# ------------------------------------------------------------------ extract
nb = json.load(open(WIN))
cells = ["".join(c["source"]) for c in nb["cells"]]
cell22 = cells[23]  # v2: graft cell shifted by the config insert
tree = ast.parse(cell22)
fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_coat_substitute")
func_src = ast.get_source_segment(cell22, fn)
need(func_src is not None, "could not extract _coat_substitute")

i_w = cell22.find("try:\n    _coat_n = _coat_substitute()")
i_w2 = cell22.find("{_coat_n} studies',flush=True)")
need(i_w != -1 and i_w2 != -1 and i_w2 > i_w, "wrapper anchors not found")
wrapper_src = cell22[i_w: i_w2 + len("{_coat_n} studies',flush=True)")]
need("coat_substitute_failed" in wrapper_src, "wrapper extraction failed")

i_o = cell22.find("_ke_theirs = _ke_pd.read_csv")
i_o2 = cell22.find("_blend_output.to_csv(_ke_primary, index=False)")
outer_src = cell22[i_o: i_o2 + len("_blend_output.to_csv(_ke_primary, index=False)")]
need("'Lateral Meniscus': 1.00" in outer_src, "LM weight 1.00 missing")
need("'ACL': 0.75" in outer_src, "ACL weight 0.75 missing")
need("'Medial Meniscus': 0.80" in outer_src, "MM weight 0.80 missing")

CHILD_MARKERS = {
    "residual": ["import input_resgated_runtime as rt",
                 "assert r['models'] == 3",
                 "assert [i['epoch'] for i in r['checkpoints']] == [4, 6, 8]",
                 "gpu_batch_studies=2, backbone_micro_images=8",
                 "_coat_arm_receipt.json"],
    "global96": ["import coatnet_global96_baseline_top3_inference as rt",
                 "assert rt.MAX_EVAL_WINDOWS == 94, rt.MAX_EVAL_WINDOWS",
                 "assert r['models'] == 3",
                 "assert [i['epoch'] for i in r['checkpoints']] == [16, 23, 18]",
                 "import timm; assert timm.__version__ == '1.0.22', timm.__version__",
                 "assert torch.cuda.device_count() == 2",
                 "_coat_g96_receipt.json",
                 "g96_env"],
    "repairv1": ["import coatnet_repairv1_top3_inference as rt",
                 "assert r['models'] == 3",
                 "assert [i['epoch'] for i in r['checkpoints']] == [12, 7, 11]",
                 "assert torch.cuda.device_count() == 2",
                 "_coat_repairv1_receipt.json"],
}

for old, new in [
    ("if sha(g96_timm) != G96_TIMM_SHA:", "if False and sha(g96_timm) != G96_TIMM_SHA:"),
    ("if sha(timm_whl) != '888981753e65cbaacfc07494370138b1700a27b1f0af587f4f9b47bc024161d0':",
     "if False and sha(timm_whl) != '888981753e65cbaacfc07494370138b1700a27b1f0af587f4f9b47bc024161d0':"),
]:
    need(old in func_src, "hash line not found for neutralization: " + old[:40])
    func_src = func_src.replace(old, new)

t1 = ast.parse(cells[2])  # v2: config cell occupies index 1
hm = next(n for n in t1.body if isinstance(n, ast.FunctionDef) and n.name == "_asset_half_rank_mix")
half_rank_mix_src = ast.get_source_segment(cells[2], hm)

# ------------------------------------------------------------------ fakes
def build_fake_inputs(include_g96=True):
    shutil.rmtree(FAKE, ignore_errors=True)
    res = FAKE / "resgated"; res.mkdir(parents=True)
    (res / "coat_resgated_ep10_top3_manifest.json").write_text("{}")
    (res / "opencv_python_headless-4.12.0.88-py3-none-any.whl").write_bytes(b"fake")
    d4 = FAKE / "d4"; d4.mkdir(parents=True)
    (d4 / "coatnet_pairfilm_manifest.json").write_text("{}")
    (d4 / "timm-1.0.22-py3-none-any.whl").write_bytes(b"fake-timm")
    if include_g96:
        g = FAKE / "g96"; g.mkdir(parents=True)
        (g / "coatnet_global96_top3_manifest.json").write_text("{}")
        (g / "timm-1.0.22-py3-none-any.whl").write_bytes(b"fake-timm")
    rv = FAKE / "rv1"; rv.mkdir(parents=True)
    (rv / "coatnet_repairv1_top3_manifest.json").write_text("{}")


def reset_work():
    shutil.rmtree(WORK, ignore_errors=True)
    WORK.mkdir(parents=True)
    rng = np.random.default_rng(7)
    ranks = pd.DataFrame(rng.random((len(UIDS), len(LABELS))), columns=LABELS)
    ranks = ranks.rank(method="average", pct=True)
    ranks.insert(0, "StudyInstanceUID", UIDS)
    ranks.to_csv(WORK / "_raptor.csv", index=False)
    ours = pd.DataFrame(rng.random((len(UIDS), len(LABELS))), columns=LABELS)
    ours.insert(0, "StudyInstanceUID", UIDS)
    return ours, ranks


# ------------------------------------------------------------------ mocks
def rsna_frame(frame, ids, labels, name):
    if list(frame.columns) != ["StudyInstanceUID"] + list(labels):
        raise RuntimeError(f"{name}: column mismatch")
    f = frame.copy()
    f["StudyInstanceUID"] = f["StudyInstanceUID"].astype(str)
    if set(f["StudyInstanceUID"]) != set(map(str, ids)):
        raise RuntimeError(f"{name}: uid mismatch")
    if f["StudyInstanceUID"].duplicated().any():
        raise RuntimeError(f"{name}: duplicate uid")
    return f.set_index("StudyInstanceUID").reindex([str(u) for u in ids]).reset_index()


def npz_payload(uids, seed, mode):
    rng = np.random.default_rng(seed)
    uids = np.asarray(uids, dtype=str)
    if mode == "mean":
        return dict(study_uids=uids, probability_mean=rng.random((len(uids), len(LABELS))))
    return dict(study_uids=uids, raw_probabilities=rng.random((3, len(uids), len(LABELS))))


def write_member(uids, csv_path, npz_path, seed, with_npz=True, shuffle=False, mode="mean"):
    csv_path = Path(csv_path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    df = pd.DataFrame(rng.random((len(uids), len(LABELS))), columns=LABELS)
    df.insert(0, "StudyInstanceUID", uids)
    df.to_csv(csv_path, index=False)
    if with_npz:
        order = list(reversed(uids)) if shuffle else list(uids)
        np.savez(npz_path, **npz_payload(order, seed + 1, mode))


def fake_run_required_child(cmd, env, log):
    src = cmd[2]
    if "input_resgated_runtime" in src:
        kind = "residual"
    elif "coatnet_global96_baseline_top3_inference" in src:
        kind = "global96"
    elif "coatnet_repairv1_top3_inference" in src:
        kind = "repairv1"
    else:
        raise AssertionError("unknown child source: " + src[:200])
    missing = [m for m in CHILD_MARKERS[kind] if m not in src]
    if missing:
        raise AssertionError(f"{kind} child source missing markers: {missing}")
    CHILD_LOG.append(kind)
    if FAIL_CHILDS.get(kind):
        raise RuntimeError(f"simulated {kind} child failure")
    if kind == "residual":
        write_member(UIDS, WORK / "_coat_arm.csv",
                     WORK / "coat_resgated_ep10_top3_predictions.npz", 11,
                     with_npz=not npz_absent.get("resgated"))
        (WORK / "_coat_arm_receipt.json").write_text(json.dumps(
            {"status": "SUBMISSION", "models": 3,
             "checkpoints": [{"epoch": 4}, {"epoch": 6}, {"epoch": 8}],
             "fallback_studies": 0}))
    elif kind == "global96":
        write_member(UIDS, WORK / "g96_input/_coat_g96.csv",
                     WORK / "g96_input/coatnet_global96_top3_predictions.npz", 22,
                     with_npz=not npz_absent.get("global96"), shuffle=True)
        (WORK / "_coat_g96_receipt.json").write_text(json.dumps(
            {"status": "SUBMISSION", "models": 3,
             "checkpoints": [{"epoch": 16}, {"epoch": 23}, {"epoch": 18}],
             "fallback_studies": 0}))
    else:
        write_member(UIDS, WORK / "_coat_repairv1.csv",
                     WORK / "coatnet_repairv1_top3_predictions.npz", 33,
                     with_npz=not npz_absent.get("repairv1"))
        (WORK / "_coat_repairv1_receipt.json").write_text(json.dumps(
            {"status": "SUBMISSION", "models": 3,
             "checkpoints": [{"epoch": 12}, {"epoch": 7}, {"epoch": 11}],
             "fallback_studies": 0}))


def fake_asset_run_d4(art, env, root, out):
    CHILD_LOG.append("d4")
    if FAIL_CHILDS.get("d4"):
        raise RuntimeError("simulated d4 failure")
    write_member(UIDS, out, Path(out).parent / "coatnet_d4_depthzone_swa3_predictions.npz",
                 44, mode="raw")


def fake_asset_find_asset(name, want):
    for p in sorted(FAKE.rglob(name)):
        return p
    return None


def fake_write_coat_runtime(art, runtime_path, helper_source):
    Path(runtime_path).write_text("# runtime stub\n")
    return "0" * 64


def dense_allocate():
    pass


def dense_unique_linspace():
    pass


def dense_coat_specs():
    pass


def rsna_phase(*a, **k):
    pass


def rsna_event(name, **kw):
    events.append((name, kw))


def rsna_save_predictions(name, uids, values, labels):
    assert np.isfinite(values).all(), name


def fake_subprocess_run(*a, **k):
    class P:
        returncode = 0
    return P()


subprocess.run = fake_subprocess_run  # children never really spawn


def build_globals(extra=None):
    G = {
        "_pd": pd, "_ke_pd": pd, "_ke_np": np, "_np": np,
        "_RSNA_TEST_IDS": UIDS, "_KE_LAB": LABELS, "_RSNA_LABELS": LABELS,
        "_KE_NS": {"find_test_root": lambda: "/tmp/fakecomp", "LAB": LABELS},
        "_asset_find_asset": fake_asset_find_asset,
        "_asset_write_coat_runtime": fake_write_coat_runtime,
        "_asset_run_d4": fake_asset_run_d4,
        "_run_required_child": fake_run_required_child,
        "_dense_allocate": dense_allocate,
        "_dense_unique_linspace": dense_unique_linspace,
        "_dense_coat_specs": dense_coat_specs,
        "rsna_frame": rsna_frame, "rsna_save_predictions": rsna_save_predictions,
        "rsna_phase": rsna_phase, "rsna_event": rsna_event,
        "_KeThreadPool": ThreadPoolExecutor,
        "_ke_primary": WORK / "_pipeline_stage.csv",
    }
    if extra:
        G.update(extra)
    exec(compile(half_rank_mix_src, "<half>", "exec"), G)
    exec(compile(func_src, "<coat>", "exec"), G)
    return G


def read_receipt():
    p = WORK / "_coat_raptor_blend_receipt.json"
    return json.loads(p.read_text()) if p.exists() else None


def run_substitute(include_g96=True, extra=None):
    build_fake_inputs(include_g96=include_g96)
    ours, ranks = reset_work()
    G = build_globals(extra)
    G["_ke_ours"] = ours
    n = G["_coat_substitute"]()
    return G, ours, ranks, n


def bad_events():
    return [e for e, _ in events if "child_failed" in e or "rejected" in e]


os.environ["RSNA_PARALLEL_COAT_READERS"] = "0"

# ================================================================== A
print("scenario A: happy path (4 members, probability-mean, sequential)")
events.clear(); CHILD_LOG.clear(); FAIL_CHILDS.clear(); npz_absent.clear()
G, ours, ranks, n = run_substitute()
need(n == len(UIDS), f"A returned {n}")
need(CHILD_LOG == ["residual", "global96", "d4", "repairv1"], f"A child order {CHILD_LOG}")
rc = read_receipt()
need(rc is not None, "A receipt missing")
if rc:
    need(rc["members"] == ["resgated_top3", "global96_top3", "d4_swa3", "repairv1_top3"],
         f"A members {rc['members']}")
    need(all(abs(v - 0.25) < 1e-12 for v in rc["within_coat"].values()),
         f"A within_coat {rc['within_coat']}")
    need(rc["private_alpha"] == 0.4, f"A alpha {rc['private_alpha']}")
    need(rc["family_reduction"] == "rank_of_member_probability_mean",
         f"A reduction {rc['family_reduction']}")
hyb = pd.read_csv(WORK / "_raptor.csv")
need(set(hyb["StudyInstanceUID"]) == set(UIDS), "A hybrid uid set")
probs = []
for pth in [WORK / "coat_resgated_ep10_top3_predictions.npz",
            WORK / "g96_input/coatnet_global96_top3_predictions.npz",
            WORK / "d4_input/coatnet_d4_depthzone_swa3_predictions.npz",
            WORK / "coatnet_repairv1_top3_predictions.npz"]:
    z = np.load(pth)
    arr = z["probability_mean"] if "probability_mean" in z.files else z["raw_probabilities"].mean(0)
    df = pd.DataFrame(arr, columns=LABELS)
    df.insert(0, "StudyInstanceUID", [str(u) for u in z["study_uids"]])
    probs.append(df.set_index("StudyInstanceUID").reindex(UIDS))
pm = sum(p[LABELS] for p in probs) / 4.0
pm_rank = pm.rank(method="average", pct=True)
pub_rank = ranks.set_index("StudyInstanceUID").reindex(UIDS)[LABELS]
expect = 0.6 * pub_rank.to_numpy() + 0.4 * pm_rank.to_numpy()
got = hyb.set_index("StudyInstanceUID").reindex(UIDS)[LABELS].to_numpy()
need(np.allclose(got, expect, atol=1e-9), "A hybrid formula mismatch")
need((WORK / "_raptor_public.csv").exists(), "A public stash missing")
need((WORK / "btk_v32_rest_input.npz").exists(), "A btk npz missing")
need((WORK / "_coat_family_rank.csv").exists(), "A family rank csv missing")
need(not bad_events(), f"A unexpected failures {bad_events()}")

# ================================================================== A2
print("scenario A2: outer blend with renta weights + wrapper re-run")
G["_ke_ours"] = ours
exec(compile(outer_src, "<outer>", "exec"), G)
stage = pd.read_csv(WORK / "_pipeline_stage.csv")
need(list(stage.columns) == ["StudyInstanceUID"] + LABELS, "A2 stage columns")
need(np.isfinite(stage[LABELS].to_numpy()).all(), "A2 stage non-finite")
lo, hi = stage[LABELS].to_numpy().min(), stage[LABELS].to_numpy().max()
need(0 < lo <= hi <= 1, f"A2 stage range [{lo},{hi}]")
theirs = pd.read_csv(WORK / "_raptor.csv").set_index("StudyInstanceUID").reindex(UIDS)
lm_expect = theirs["Lateral Meniscus"].rank(method="average", pct=True).to_numpy()
lm_got = stage.set_index("StudyInstanceUID").reindex(UIDS)["Lateral Meniscus"].to_numpy()
need(np.allclose(lm_got, lm_expect, atol=1e-12),
     "A2 LM column != rankpct(theirs) under weight 1.0")
# ACL weight 0.75: column must differ from pure theirs
acl_expect_mixed = False
tr = ours.set_index("StudyInstanceUID").reindex(UIDS)[LABELS].rank(method="average", pct=True)
mixed = 0.25 * tr["ACL"].to_numpy() + 0.75 * theirs["ACL"].to_numpy()
mixed_ranked = pd.Series(mixed).rank(method="average", pct=True).to_numpy()
acl_got = stage.set_index("StudyInstanceUID").reindex(UIDS)["ACL"].to_numpy()
need(np.allclose(acl_got, mixed_ranked, atol=1e-12), "A2 ACL 0.75 blend mismatch")
exec(compile(wrapper_src, "<wrap>", "exec"), G)
need(G["_coat_n"] == len(UIDS), f"A2 wrapper coat_n {G['_coat_n']}")

# ================================================================== B
print("scenario B: repairv1 npz missing -> N-member rank fallback")
events.clear(); CHILD_LOG.clear()
npz_absent = {"repairv1": True}
G, ours, ranks, n = run_substitute()
rc = read_receipt()
need(rc and rc["family_reduction"] ==
     "mean_of_member_ranks_fallback_probabilities_unavailable",
     f"B reduction {rc and rc['family_reduction']}")
need(rc and len(rc["members"]) == 4, "B members")
need("coat_member_probability_unavailable" in [e for e, _ in events], "B event missing")
hyb = pd.read_csv(WORK / "_raptor.csv")
need(np.isfinite(hyb[LABELS].to_numpy()).all(), "B hybrid non-finite")
need(not bad_events(), f"B unexpected failures {bad_events()}")

# ================================================================== C
print("scenario C: global96 dataset absent -> 3 members")
events.clear(); CHILD_LOG.clear(); npz_absent = {}
G, ours, ranks, n = run_substitute(include_g96=False)
rc = read_receipt()
need(rc and rc["members"] == ["resgated_top3", "d4_swa3", "repairv1_top3"],
     f"C members {rc and rc['members']}")
need(rc and rc["family_reduction"] == "rank_of_member_probability_mean",
     f"C reduction {rc and rc['family_reduction']}")
need(any(e == "coat_global96_child_failed" for e, _ in events), "C g96 failure event missing")
need(CHILD_LOG == ["residual", "d4", "repairv1"], f"C child log {CHILD_LOG}")

# ================================================================== D
print("scenario D: every child fails -> public input retained")
events.clear(); CHILD_LOG.clear()
FAIL_CHILDS = {"residual": True, "global96": True, "repairv1": True, "d4": True}
build_fake_inputs(include_g96=True)
ours, ranks = reset_work()
pub_before = (WORK / "_raptor.csv").read_bytes()
G = build_globals(); G["_ke_ours"] = ours
n = G["_coat_substitute"]()
need(n == 0, f"D returned {n}")
need((WORK / "_raptor.csv").read_bytes() == pub_before, "D public raptor mutated")
need(not (WORK / "_coat_raptor_blend_receipt.json").exists(), "D receipt should not exist")
need("coat_family_unavailable" in [e for e, _ in events], "D event missing")

# ================================================================== E
print("scenario E: call-site wrapper contains the failure")
events.clear()


def raiser():
    raise RuntimeError("boom")


G["_coat_substitute"] = raiser
exec(compile(wrapper_src, "<wrap>", "exec"), G)
need(G["_coat_n"] == 0, f"E coat_n {G['_coat_n']}")
need(any(e == "coat_substitute_failed" for e, _ in events), "E event missing")

# ================================================================== F
print("scenario F: parallel pairs path")
del os.environ["RSNA_PARALLEL_COAT_READERS"]
events.clear(); CHILD_LOG.clear(); FAIL_CHILDS = {}; npz_absent = {}
G, ours, ranks, n = run_substitute()
os.environ["RSNA_PARALLEL_COAT_READERS"] = "0"
need(n == len(UIDS), f"F returned {n}")
need(set(CHILD_LOG) == {"residual", "global96", "d4", "repairv1"}, f"F children {CHILD_LOG}")
rc = read_receipt()
need(rc and len(rc["members"]) == 4, "F members")
need(not bad_events(), f"F unexpected failures {bad_events()}")

# ================================================================== G
print("scenario G: probe-config cell knobs are honored (WIN_ALPHA/OUTER/arms)")
events.clear(); CHILD_LOG.clear(); FAIL_CHILDS = {}; npz_absent = {}
G, ours, ranks, n = run_substitute(extra={
    "WIN_ALPHA": 0.45,
    "WIN_OUTER_W": {"Lateral OA": 0.68, "Bogus Label": 1.0},
    "WIN_OUTER_BASE": 0.55,
    "WIN_ARM_W": {"widedense-v4": 0.25, "ghost-arm": 1.0},
})
rc = read_receipt()
need(rc and rc["private_alpha"] == 0.45, f"G alpha {rc and rc['private_alpha']}")
exec(compile(outer_src, "<outer>", "exec"), G)
stage = pd.read_csv(WORK / "_pipeline_stage.csv")
theirs = pd.read_csv(WORK / "_raptor.csv").set_index("StudyInstanceUID").reindex(UIDS)
tr = ours.set_index("StudyInstanceUID").reindex(UIDS)[LABELS].rank(method="average", pct=True)
# Lateral OA explicitly probed to 0.68
loa_expect = pd.Series(
    0.32 * tr["Lateral OA"].to_numpy() + 0.68 * theirs["Lateral OA"].to_numpy()
).rank(method="average", pct=True).to_numpy()
loa_got = stage.set_index("StudyInstanceUID").reindex(UIDS)["Lateral OA"].to_numpy()
need(np.allclose(loa_got, loa_expect, atol=1e-12), "G Lateral OA 0.68 override not applied")
# labels without an override take WIN_OUTER_BASE=0.55
eff_expect = pd.Series(
    0.45 * tr["Effusion"].to_numpy() + 0.55 * theirs["Effusion"].to_numpy()
).rank(method="average", pct=True).to_numpy()
eff_got = stage.set_index("StudyInstanceUID").reindex(UIDS)["Effusion"].to_numpy()
need(np.allclose(eff_got, eff_expect, atol=1e-12), "G WIN_OUTER_BASE not applied to unprobed labels")
need(any(e == "win_config_unknown_label" for e, _ in events), "G unknown-label event missing")
# arm-weight hook (runs in the raptor runner section): exec the graft snippet
_i_h = cell22.find("for _k_name, _k_w in (globals().get('WIN_ARM_W')")
need(_i_h != -1, "G arm hook not found")
_e_h = cell22.find('flush=True)', cell22.find("[win-config] arm", _i_h)) + len("flush=True)")
hook_src = cell22[_i_h:_e_h]
G["_KE_NS"]["ARMS"] = [
    {"name": "widedense-v4", "w": 0.15},
    {"name": "maxspan-v5", "w": 0.60},
]
exec(compile(hook_src, "<armhook>", "exec"), G)
_got_w = {a["name"]: a["w"] for a in G["_KE_NS"]["ARMS"]}
need(_got_w["widedense-v4"] == 0.25, f"G arm override not applied: {_got_w}")
need(_got_w["maxspan-v5"] == 0.60, f"G untouched arm changed: {_got_w}")
need(any(e == "win_config_unknown_arm" and kw.get("arm") == "ghost-arm"
         for e, kw in events), "G ghost-arm event payload wrong")
# defaults still reproduce when the config cell is untouched
events.clear()
G2, ours2, ranks2, n2 = run_substitute(extra=None)
rc2 = read_receipt()
need(rc2 and rc2["private_alpha"] == 0.4, f"G default alpha {rc2 and rc2['private_alpha']}")
need(all(abs(v - 0.25) < 1e-12 for v in rc2["within_coat"].values()),
     f"G default within_coat {rc2['within_coat']}")
need(not bad_events(), f"G unexpected failures {bad_events()}")

# ------------------------------------------------------- transcription literals
print("transcription check: d4-blend literals present")
full = "\n".join(cells)
for lit in [
    "015f09030e76f86274cadae40777b3c3cf5c19f8c835d5ad88e15db41903779e",
    "99288a9a42f36ba544d7b0ad2fe645e3b1fc9c507c23802c16ca0d2e5085f684",
    "888981753e65cbaacfc07494370138b1700a27b1f0af587f4f9b47bc024161d0",
    "[16, 23, 18]", "[12, 7, 11]",
    "coatnet_global96_baseline_top3_inference",
    "coatnet_repairv1_top3_inference",
    "MAX_EVAL_WINDOWS == 94",
    "'ACL': 0.75", "'Medial Meniscus': 0.80", "'Lateral Meniscus': 1.00",
    "'Lateral OA': 0.75", "'Fracture': 0.75",
    # v2 probe-config cell + fifth arm
    "WIN_OUTER_W = {}", "WIN_OUTER_BASE = None", "WIN_ALPHA = None",
    "WIN_ARM_W = {}", '"name": "widedense-v4"',
    '"file": "raptor_ft_coatnet_v4_full.pt"', "run_single(4, torch.device(",
]:
    need(lit in full, f"missing literal {lit}")
for lit in ["'ACL': 0.68", "'Lateral Meniscus': 0.65", "private_alpha = 0.45"]:
    need(lit not in full, f"stale ref literal present: {lit}")

print()
if failures:
    print(f"FAILED ({len(failures)}):")
    for f in failures:
        print(" -", f)
    sys.exit(1)
print("ALL SCENARIOS PASSED")
