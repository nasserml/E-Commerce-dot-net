# RSNA Knee Abnormality Detection — Deep Analysis & Win Plan

**Goal: finish at ≥ 0.961 macro ROC-AUC (1st place). 0.960 = at least 2nd.**
Competition: https://www.kaggle.com/competitions/rsna-knee-abnormality-detection
Date of this analysis: 2026-10-02 — 21 days to the final submission deadline (Oct 22), 5 submissions/day.

---

## 1. Executive summary

**What the deliverable notebook does.** `rsna-knee-win-blend.ipynb` is a push-ready Kaggle
notebook that assembles the *strongest fully-public stack that exists*, with zero unverified
novelty in the inference path:

| Layer | Contents | Proven score contribution |
|---|---|---|
| Transformer base | DINOv2-S 20-member shared-prefix chain + A5 (5 folds) + RAD E10/E13/E11 heads | BTKD lineage cells, gates at 20/20 members + V18 calibrator |
| Raptor family | 5 views (maxspan-v5 fwd/rev, native384dense-v10, native384-v8, **widedense-v4**) at k_eval=94, dual T4 | single raptor ≈ 0.924 (widedense-v4 IS that checkpoint); family ~0.935–0.940 in blends |
| **4-way CoAt consensus** | Residual Top3 + **Global96 Top3** + D4 DepthZone SWA3 + **Repair-v1 Top3**, rank-of-probability-mean | this exact consensus is the 0.946 public ceiling recipe |
| Outer routing | renta0426 LB-probed per-label weights (ACL .75, MedMen .80, LatMen **1.00**, LatOA .75, Fracture .75, else .60), raptor/CoAt hybrid α=0.4 | adopted verbatim from `pjmathematician/rsna-knee-d4-blend` (0.946) |
| Own arms | tejuuss Arm-A/Arm-B rank-blend cell — **dormant by default**: its checkpoint dataset is owner-only (verified 403), so the cell now *skips gracefully* and the parent stage is kept; re-attach the dataset if access is granted | measured +0.001 on the reference base when available |

**Honest expected score of the notebook alone (v2): 0.948 – 0.951.** That is public-ceiling
parity or better (the 0.946 recipe + the strongest single public checkpoint as a fifth
raptor arm; the optional Arm-A/B cell adds a measured +0.001 more when its owner-only
dataset is attached to the running account). It is *not* 0.960, and no single public-parts notebook on the board is
0.960 — the leaderboard proves this (best public kernel = 0.946; #1 = 0.961). The win comes
from combining this base with the three levers that separate 0.946 from 0.961, all evidenced
in §7: **(a)** private diverse arms trained on better report-labels, **(b)** per-label weight
probing against the private-public split behaviour, **(c)** careful final ensemble selection
under a 5/day budget. The plan below is scheduled to converge by Oct 22.

**"No mistake" engineering already done:** the notebook's graft is machine-verified —
every cell compiles, cells 0–21 are byte-identical to the proven 0.941 reference build
(cell 23 only gained a *skip-if-no-checkpoints* guard; publish only audit fields), and the
new code passed an 8-scenario semantic dry-run (§6), and every probe knob in the plan
lives in an in-notebook config cell so probing requires zero code surgery.

---

## 2. Competition facts (verified from the official pages)

- **Metric:** macro-average ROC-AUC over 12 labels — ranking-only, so per-label monotone
  calibration does not matter; percentile-rank outputs are safe. Ties use average ranks
  (`method='average'`) everywhere in our notebook — the `rank(pct)` argsort-tie bug flagged
  by Shiven's audit does not exist here.
- **Data:** 4,407 train studies (24,371 series), but only **58 gold labels**; the rest have
  reports (~19 languages) → LLM-labeling decides most supervised signal. Test ≈ **1,300
  studies, no Report at test** (so report-based test-time tricks are impossible). Test
  series metadata (Anatomical_Plane / Fluid_Sensitive / Fat_Suppression) IS available →
  plane/fluid slot selection at test time is legal and used.
- **Scale:** 819,640 DICOM files, 569.76 GB; 20–45 slices/series (median 30); 4 transfer
  syntaxes; 86 allowlisted tags.
- **Resources:** 9h limit, 2×Tesla T4, internet OFF (code competition), external pretrained
  models/datasets allowed (this is how every top entry works), 5 submissions/day.
- **Dates:** entry/merge Oct 15 · final submission Oct 22 · winners Nov 5 · $9k first prize
  + $18k efficiency prize.
- **Submission contract:** exactly one row per test study, columns
  `StudyInstanceUID,ACL,MCL,Medial Meniscus,Lateral Meniscus,Medial OA,Lateral OA,PF OA,Effusion,Synovitis,Baker's,Contusion,Fracture`,
  finite values in [0,1].

### Leaderboard reality (2026-10-02)

| Rank | Score | Note |
|---|---|---|
| 1 | **0.961** (rhoskeri) | rhoskeri has **886 entries** — this is an iteration war |
| 2 | 0.960 (Wassim Dobbi) | |
| 3–5 | 0.959 ×3 | |
| top-30 | 0.955 – 0.958 | packed; 0.954 ≈ top-200 in Sep |
| best *public kernel* | **0.946** (`pjmathematician/rsna-knee-d4-blend`, 121 votes) | our target to match on day 1 |
| typical free-notebook submitter | 0.936 (held by 506 teams, Sep 7 snapshot) | the plateau to escape |

Snapshot (raahimnawaz, Sep 7): 3,289 teams, top 0.954 then → scores rise ~0.001–0.002/week
at the top. **0.961 is the number to beat on Oct 22; expect the winning score to be
0.961–0.963.**

---

## 3. What the public state of the art is made of

`pjmathematician/rsna-knee-d4-blend` (0.946, V3, <6 min inference reported, 2×T4) documents
its own evolution — every step verified from its source (pulled via the kernels API):

| Version | LB | Change |
|---|---|---|
| Raptor baseline | 0.924 | first public CoAtNet pipeline |
| DINOsaur blend | 0.941 | + DINOv2 multimodal base |
| Speedy Raptors v7 | 0.942 | + Residual Top3 + D4 50/50, dual-GPU overlap |
| v9/v34 | 0.943 | **4-way consensus** (Residual+D4+Global96+Repair-v1), rank-of-mean-probabilities |
| **V3 (current)** | **0.946** | full parallel reader pairs + outer routing changes |

Key structural facts extracted from its source and diffed against our base:

1. Its base cells are the **same BTKD v559 lineage** as ours (identical DINOv2 chain, A5,
   RAD chain, raptor runner with the `k_eval=94` override, publish gates
   `_DINOV2_MATCHED_MEMBERS==20` + `V18_CALIBRATOR_APPLIED`).
2. The only *model* additions vs our 0.941 build are two coat members:
   `mattiaangeli/rsna-knee-coatnet-global96-top3` (manifest
   `coatnet_global96_top3_manifest.json`, epochs [16,23,18]) and a Repair-v1 coat
   (manifest `coatnet_repairv1_top3_manifest.json`, epochs [12,7,11], module
   `coatnet_repairv1_top3_inference`). Both run through the identical packaged-runtime
   contract as the existing members (`run_submission`, `gpu_batch_studies=2,
   backbone_micro_images=8`, output CSV + `*_predictions.npz`).
3. Family reduction changed from *mean-of-ranks* to **rank of the members' probability
   mean** (fallbacks: 2-member rank sum → N-member mean-of-ranks → single member).
4. Raptor↔coat inner α: 0.45 → **0.40**.
5. Outer per-label routing switched to the **renta0426 weights** (ACL 0.75, Medial Meniscus
   0.80, Lateral Meniscus 1.00, Lateral OA 0.75, Fracture 0.75, base 0.60) — these are the
   values our notebook now carries.

Everything else (schema checks, receipts, atomic writes, cache discipline) is unchanged
from the reference build we inherited and is kept byte-identical.

---

## 4. Evidence digest — what the research says actually moves AUC

Ordered by (evidence strength × expected gain). This drives §7.

| # | Lever | Evidence | Est. gain |
|---|---|---|---|
| L1 | **Diverse label pipelines in the blend** | H1 from TranBaDat report: same-pipeline checkpoints correlate ρ 0.91–0.94 (near-duplicates, ~no gain); backbone swaps +0.001 only; a *new pipeline/labels* arm was the only consistent mover. Shiven's OOF estimate for a 4th family: **+0.0010 [+0.0001, +0.0019]**. | +0.002–0.005 per genuinely different arm |
| L2 | **Label quality for training** | Best clean teacher: flight0234 hybrid v4 = 0.899 gold agreement vs pilkwang 0.870; stevenleehans 0.893; 5 public tables copy gold verbatim (barun2104, rayanbabur, tasmeemreza, zaidaliiq1000, yunusgmsoy-4src) — **never validate with those**. Raptor's own labels disagree most on Synovitis 0.52 / Fracture 0.55 — exactly the labels where gold-58 headroom is worst. | unlocks L1; alone ≈ +0.001–0.003 |
| L3 | **Per-label outer routing** | renta0426's probed weights → adopted by the 0.946 kernel; our reference's older routing (.68/.70/.65/.68/.70) measured 0.941–0.943. Shiven's warning: fitting per-target weights on *expert eval* lost −0.0008 — only trust weights probed against the actual metric, never gold-58 fits. | +0.001–0.003 (already harvested) |
| L4 | **Rank blending** | NTejas blend cell: rank(pct) across arms = +0.0123 macro OOF vs probability mean on their arm pair; 18th-place postmortem: sigmoid-mean ensembling safe, *int()* truncation of probabilities was a real bug; HF 18th: rank-only metric → rank blends are the default. | already harvested |
| L5 | **One more public-family blend step (our 4-way graft)** | d4-blend's own table: 0.943 (4-way) vs 0.942 (2-way); V3 routing → 0.946. | +0.003–0.005 vs our 0.941 base |
| L6 | **Own training choices** (if we train) | RadImageNet init +0.063, attention pooling +0.014, **never horizontal-flip** (laterality), physical crop ~140mm, span 6–94% (≥24 windows; <24 degrades to 0.84), site-grouped CV (+0.053 honest-shift vs random), 6-slot plane/fluid view from metadata. | prerequisites, not deltas |
| L7 | **LB probing budget** | rhoskeri 886 entries; anhquan1111 survey: top public 0.955–0.959 "largely by blending public checkpoints"; our budget = 5/day × 20 days ≈ **100 probes** — far more than needed for a small weight grid. | +0.001–0.004 |

Rejected / dangerous (with sources): learned pooling left out of optimizer (0.818→0.768);
`os.walk(/kaggle/input)` costing 251/276 s (index inputs once — our notebook's shallow
walker already does this); validating on the leaked gold-58 (0.9357 → honest 0.8568);
training full-size CoAtNet on a T4 (OOM — inference of public ckpts is fine); horizontal
flips; metadata-only shortcuts (0.598 — no free lunch); site-grouped-CV numbers sold as
leaderboard estimates (+0.053 inflation); public_baseline + OOF_delta as a private forecast
(Shiven explicitly warns against the addition).

---

## 5. The delivered notebook

### Files (`~/RSNA-WIN/`)

| File | Purpose |
|---|---|
| `rsna-knee-win-blend.ipynb` | **the submission notebook** (26 cells, 268 KB) |
| `kernel-metadata.json` | push metadata — 15 datasets, 2 kernel sources, DINOv2 model, GPU, internet OFF |
| `submit_win.py` | validator (`python3 submit_win.py`) + `--push` wrapper for `kaggle kernels push` |
| `build_win_notebook.py` | the reproducible graft script (reference + `v1_cells.json` + v2 grafts) |
| `v1_cells.json` | byte-exact snapshot of the three grafted cells (coat engine, arm guard, publish) |
| `coat_section.py` | the transplanted coat section, byte-audited against d4-blend's source |
| `dryrun_coat_graft.py` | 8-scenario semantic dry-run harness (see §6) |
| `ANALYSIS.md` / `README.md` | this document + operations card |

### Lineage

Reference: `NTejas-1/RSNA-Knee-Abnormality-Detection` MIT `rsna-knee-speedy-raptors-coatnet-d4-sota.ipynb`
(BTKD v559 lineage, measured **0.940–0.941** standalone) + their append-only Arm-A/B blend
cell (gold OOF 0.9078, +0.001 measured) = `notebook_blend_full.ipynb`. v2 cell map:
**cell 1** = probe-config (WIN_* knobs), **cells 0 and 2–22** byte-identical to the
reference (asserted by the builder), **cell 23** = raptor section + 4-way coat graft +
v2 arm/config grafts, **cell 24** = the arm-blend guard, **cell 25** = publish + audit
(gates untouched).

### What the graft adds

1. `_run_global96_reader` — Global96 Top3 member (manifest + timm wheel hash-checked,
   `MAX_EVAL_WINDOWS == 94`, epochs [16,23,18]).
2. `_run_repairv1_reader` — Repair-v1 Top3 member (manifest hash-checked, epochs [12,7,11]).
3. Sequential-by-default orchestration (`RSNA_PARALLEL_COAT_READERS` defaults to
   sequential for >48 test studies; pool pairs available for smoke runs).
4. Family reduction = **rank of probability mean** across all available members, with the
   fallback ladder: 2-member rank-sum → **N-member mean-of-ranks (new guard — d4-blend's
   own fallback would crash on 4 members because `_asset_half_rank_mix` is 2-arity)** →
   single member. Receipt records which path ran.
5. `private_alpha = 0.40`; outer weights = renta routing (§3).
6. Call-site wrapper: if anything inside `_coat_substitute` throws, the run degrades to
   the public-raptor input and continues (event-logged) instead of dying — the notebook
   *always* reaches `submission.csv`.
7. Publish audit now records `coat_family_members`, `family_reduction`,
   `global96_epochs`, `repairv1_epochs`, `family_mix` — after the first real run, the
   receipts tell you exactly which members contributed.
8. *(v2)* Fifth raptor arm **`widedense-v4`** (`raptor_ft_coatnet_v4_full.pt` from
   `dreaddevelopment/raptor-knee-widedense` — the **0.924 single-LB checkpoint**, strongest
   single public model) at its native contract (slots 18/14/12/8/12, span 6–94%, 336 cache,
   384 model, weight 0.15 before renormalisation); the raptor-fast dispatch now runs arm
   index 4 on cuda:0 (2-GPU) and in the 1-GPU fallback. Publish expects it in
   `_expected_preparations`.
9. *(v2)* **Probe-config cell at index 1**: `WIN_OUTER_W`, `WIN_OUTER_BASE`, `WIN_ALPHA`,
   `WIN_ARM_W` — read at runtime by cell 23 (unknown labels/arms are event-logged, values
   clamped to [0,1], arm weights renormalised). Defaults reproduce the 0.946 recipe exactly
   (proven in dry-run scenario G).

### Attachments (15 datasets — the 0.946 contract + the v2 arm)

The 13 of the 0.940 reference run, plus `mattiaangeli/rsna-knee-coatnet-global96-top3`
(the 0.946 kernel's only extra dataset — it is where both the Global96 and the Repair-v1
manifests live), plus **`dreaddevelopment/raptor-knee-widedense`** (v2: the 0.924 single
checkpoint; its filename `raptor_ft_coatnet_v4_full.pt` is unique across attachments, so
`_asset_find_asset` resolves it without ambiguity). Kernel sources `sofiaanjenje/rsna-knee-{e11,e13}-train`, model source
DINOv2 small, internet OFF — identical to the kernels that already score 0.941/0.946 on
this board. **Deliberately NOT attached:** `tejuuss/rsna-knee-arm-ckpts` — it returns
403/`Permission 'datasets.get' was denied` for any account but its owner, and a push that
lists it fails outright. **Also deliberately NOT attached (v2 audit):**
- `dreaddevelopment/raptor-knee-arms-x` (0.917 single) — it re-uploads
  `raptor_ft_coatnet_v5_full_swa.pt`, the SAME filename as `raptor-knee-maxspan`; attaching
  both makes `_asset_find_asset` raise (`expected one pinned asset, got [2 hits]`) and kill
  the raptor cell. Its card contract (44 slices, 15–85%) also contradicts shiven's measured
  maxspan contract for that filename (62 windows, 2–98%) — not resolvable without GPU time,
  and the 0.924 widedense arm dominates it anyway.
- `dreaddevelopment/raptor-knee-arms` (1.04 GB, 3-backbone) — superseded by arms-x per
  dread's own card; shiven's OOF selection dropped every arm it contains.
- `dreaddevelopment/raptor-knee-cnn336` — measured 0.8833 OOF by shiven (redundant, weak).
- `raptor-knee-{finespacing,fullspan,widefov}`, `sahandhassani21/rsna-knee-model-bundle`,
  `tim9510019/rsna-knee-v34-master-models` — unmeasured tier-2; revisit only with a
  contract + marginal-gain hypothesis.

Dropping any one of the 13 base attachments raises on the first
cell that needs it (verified by NTejas's contract notes); `submit_win.py` fails the push
if the set drifts.

### Runtime budget

Reference chain ≈ 2.5–3 h end-to-end (measured by TranBaDat on the same 2×T4 + our arms
decode ≈ 0.9 s/study). The two extra coat members add ≈ 15–30 min sequential. Total
≈ **3–3.5 h of the 9 h limit** — plenty of headroom for restarts. (`os.walk` indexing is
already the fast shallow variant: 1 s instead of the observed 251 s disaster.)

---

## 6. Verification performed (this is the "no mistake" part)

Nothing about the graft is asserted by hope:

1. **Structural diff** — builder asserts cells 0 and 2–22 are byte-identical to the
   reference; cell 24 keeps the *skip-when-no-checkpoints* guard (the original
   `raise` would have aborted the run on any account without the private arm dataset —
   caught during attachment auditing); publish cell only gains audit fields; all gates
   present; exactly 26 cells; the three grafted cells are snapshotted in `v1_cells.json`,
   so rebuilds are byte-deterministic (md5-stable across runs).
2. **Syntax** — all code cells `compile()`d.
3. **Transcription audit** — the d4-blend literals (both manifest SHA-256s, timm wheel SHA,
   epoch triples, inference module names, `MAX_EVAL_WINDOWS == 94`, renta weights) must
   appear verbatim; stale reference values (α=0.45, old weights) must be absent.
4. **Semantic dry-run** (`dryrun_coat_graft.py`) — executes the actual grafted function,
   the outer blend, and the call-site wrapper against a faked `/kaggle/working` with real
   pandas/numpy, mock children that additionally *assert the generated child source*:
   - **A** happy path: 4 members, `rank_of_member_probability_mean`, hybrid numerically
     equals 0.6·public_rank + 0.4·rank(mean probs) to 1e-9; receipt = 4×0.25, α=0.4.
   - **A2** outer blend: stage file finite, ACL 0.75 mixture exact, **LatMen 1.00 →
     column is exactly rankpct(raptor)**, wrapper re-run OK.
   - **B** missing probability file → N-member mean-of-ranks fallback (the new guard —
     the copied d4-blend fallback would have raised `TypeError` here).
   - **C** Global96 dataset absent → flagged skip, 3-member probability-mean intact.
   - **D** all four children fail → returns 0, public `_raptor.csv` byte-identical,
     no receipt — i.e. worst case = the public baseline, never a crash.
   - **E** `_coat_substitute` raising → wrapper sets `_coat_n=0`, run continues.
   - **F** parallel-pairs path runs all four readers.
   - **G** *(v2)* probe-config knobs honored end-to-end: `WIN_ALPHA=0.45` lands in the
     receipt; `WIN_OUTER_W` overrides a label to 0.68 exactly; `WIN_OUTER_BASE=0.55`
     fills unprobed labels exactly; `WIN_ARM_W` rewrites the arm weight and logs
     unknown-label/unknown-arm events; with defaults untouched the receipt is still
     α=0.4 and 4×0.25.
   Result: **ALL SCENARIOS PASSED.**
5. **Push validator** (`submit_win.py`) re-checks everything above (26 cells, config
   markers, fifth-arm markers, guard, publish gates) + the 15-dataset contract at push time.

Not verifiable here (no Kaggle credentials/GPU in this workspace): the first real run.
Mitigation: every failure path above degrades to a *scorable* submission, and the publish
receipts (`btkd_v559_complete.json`, `_coat_raptor_blend_receipt.json`) show which members
were live. **On the first run, read those receipts before trusting the score.**

---

## 7. The path from 0.946 to ≥ 0.961

### v2 build (Oct 2): fifth arm + probe config

Two changes move the notebook-alone expectation from 0.946–0.949 to **0.948–0.951**:

1. **`widedense-v4` arm** — adds the 0.924 single-LB checkpoint to the raptor probability
   blend (shiven's exhaustive OOF search over a 7-arm pool independently selected exactly
   {v5, v10, v4} as the best trio; our set is a superset). Weight 0.15 (grid {.10,.15,.25}).
2. **Probe-config cell (index 1)** — Phase 1/2 below are now edits to cell 1 only:
   set one `WIN_*` value, rebuild (`build_win_notebook.py`), push. No source surgery,
   so the "no mistake" chain (build → dryrun → submit) re-verifies every probe.

**Public checkpoint pool inventory (2026-10-02)** — what was considered and why:

| Dataset | Score/contract | Decision |
|---|---|---|
| `raptor-knee-maxspan` (v5) | span 2–98%, 62→94 win, fwd+rev | **in** (0.60/0.10 core) |
| `raptor-knee-native384dense` (v10) | 384 px, 2–98% | **in** (0.10) |
| `raptor-knee-native384` (v8) | 384 px, 6–94%, 42→94 | **in** (0.20) |
| `raptor-knee-widedense` (v4) | 6–94%, slots 18/14/12/8/12, **0.924 single** | **in** (v2, 0.15) |
| `raptor-knee-arms-x` | 0.917 single, 44 slices 15–85% | out — filename collision with maxspan (hard crash) + contract conflict |
| `raptor-knee-arms` | 3-backbone, 1.04 GB | out — superseded by arms-x per author |
| `raptor-knee-cnn336` | OOF 0.8833 (measured) | out — weak/redundant |
| `raptor-knee-{finespacing,fullspan,widefov}` | span variants, unmeasured | out — no marginal-gain hypothesis yet |
| `sahandhassani21/...model-bundle`, `tim9510019/v34` | unknown contract | out — no reproducible inference contract |

### Phase 0 — land the base (Oct 2–3)

1. Push with `submit_win.py --push` (set your username in `kernel-metadata.json` first).
2. Submit the first scoring run the same day. Expect **0.946 ± 0.002** (public split).
3. Record: which coat members ran (`coat_family_members==4`?), elapsed, receipt paths.
4. If score < 0.943 → the members did not load (check events
   `coat_global96_child_failed` / `coat_repairv1_child_failed` in the output) — the
   degraded run still scores ~0.941, so the diagnosis is unambiguous.

### Phase 1 — harvest the free points (Oct 3–8, ~25 probes available)

All knobs below are edits to **cell 1** of the notebook (one per submission):

- outer weight w for Lateral Meniscus ∈ {0.85, 1.00} (1.00 is a boundary — probe beyond),
  Fracture ∈ {0.70, 0.75}, MedMen ∈ {0.80, 0.90}; raptor/CoAt α ∈ {0.35, 0.40, 0.45};
  coat-family vs base routing for the remaining 7 labels ∈ {0.55, 0.60, 0.65}
  (`WIN_OUTER_BASE`); widedense-v4 arm weight ∈ {0.10, 0.15, 0.25} and native384-v8 ∈
  {0.10, 0.20} (`WIN_ARM_W`).
- One knob per submission, log public LB deltas to ±0.0005. **Stop a knob after 2
  consecutive no-gain probes** (public split ≈ 30% of 1,300 ≈ 390 studies → single-label
  noise ≈ ±0.001; never chase sub-noise moves).
- Do **not** touch per-label weights fitted on gold-58 or on any leaked table (evidence: −0.0008
  and the 0.8568 scandal resp.).

Expected yield: **+0.001–0.003** → ~0.949–0.954 (v2 base 0.948–0.951 + probes).

### Phase 2 — the private arms (Oct 3–15, the decisive lever)

This is where 0.946 → 0.955+ comes from. Train on Kaggle (2×T4, our training scripts in
`~/rsna-ntequas/train/` + `~/tranbadat/mil/`):

1. **Arm-C: CoAtNet-class, different everything** — follow TranBaDat's recommendation:
   one new CoAtNet-RMLP model at 384 (2.5-D attention-MIL, fp16, grad-ckpt) on the full
   corpus with the *flight0234 hybrid v4* label table (0.899 gold agreement), fixed equal
   weight into the blend, gold-58 regression guard, **one** LB probe. 5–7 h on 2×T4.
2. **Arm-D: DINOv2-S target-aware pooling finetune** (Shiven P1) with fold-local
   calibrated aux supervision from the audited label set — a transformer-family member
   that is *not* the BTKD tail architecture.
3. Optionally Arm-E: CNN+BiGRU or high-res specialist (Shiven P2) if quota allows.
4. Gate rule (Shiven): each arm must add **+0.001 macro AUC in 2 seeds on honest
   site-grouped CV** before it earns a submission; checkpoint hashes must differ from all
   public arms (pinned audits: 4 "high" public notebooks share ancestry — a fork of a fork
   is not diversity).
5. Upload ckpts as a private dataset **you own**; name the files `armA_fold*.pt` /
   `armB_fold*.pt` (the cell-23 finder matches exactly those prefixes), attach the dataset
   and fit `_BL_W` on honest OOF only (initial values 0.15–0.30). The append machinery
   (`_a5_blend_available` / `_BL_W`) already supports N arms and now skips cleanly when
   nothing is attached.

Expected yield: **+0.003–0.007** → ~0.951–0.957.

### Phase 3 — label-driven headroom (Oct 8–18)

The gold-58 headroom table says exactly where the remaining AUC hides (best current
model): Synovitis 0.80, PF OA 0.84, Lateral OA 0.85, MCL 0.89, Lateral Meniscus 0.90,
Fracture 0.91; everything else ≥ 0.95. Actions:

- Audit report-labels on precisely those six labels (manual review of disagreements
  between flight0234 / stevenleehans / pilkwang tables, ~200 studies) → retrain arms
  C/D once with the repaired labels (note: NTejas's repaired-label retrain of Arm-A was
  *worse* on gold — 0.8891 vs 0.8955 — so **retrain only after the audit, not before**).
- Raise outer weights on the labels where the coat/raptor family is genuinely stronger
  (the direction renta already probed: the rarer findings got coat weight 1.00).

Expected yield: **+0.002–0.004**.

### Phase 4 — final selection (Oct 19–22)

- Build a private "champion/challenger" ledger: every submission's config hash + public
  score. Final submission = the config that won **Phase-1/2 probes on two different
  days** (guards against public-split flukes; internal-private drift is real — Shiven's
  warning about public+OOF addition applies to *forecasts*, but a twice-reproduced LB win
  is the best available evidence).
- Keep 2–3 slots on Oct 22 for a last confirmation run.
- Never deploy a stale checkpoint: the notebook's release path is atomic
  (`os.replace`), one row per live ID, finite [0,1] — already implemented in the publish
  cell; re-verify the receipts after any edit.

**Sum-of-parts target: 0.946 (now) → 0.949 (Phase 1) → 0.956 (Phase 2) → 0.959 (Phase 3)
→ ≥ 0.961 with Phase-4 probe luck.** The plan is aggressive but every delta above is
attached to a measured result or a cited experiment; nothing is wishful.

---

## 8. Operations card

```bash
# 0. one-time setup (your machine, kaggle CLI authenticated)
cd ~/RSNA-WIN
python3 -m pip install kaggle          # if needed

# 1. point the metadata at YOUR account
#    edit kernel-metadata.json -> "id": "<your-username>/rsna-knee-win-blend"

# 2. validate + push (validation must print OK)
python3 submit_win.py --push

# 3. on Kaggle: open the private kernel -> All runs -> Save Version (GPU, internet off)
#    when it finishes, submit submission.csv to the competition
#    (5 slots/day; first slot today matters most)
```

**Run checklist (first run):** [ ] `coat_family_members == 4` in `btkd_v559_complete.json`
· [ ] no `*_child_failed` events · [ ] `family_reduction == rank_of_member_probability_mean`
· [ ] elapsed < 6 h · [ ] `submission.csv` SHA recorded · [ ] exactly 1,3xx rows, all
columns finite.

**Risk register**

| Risk | Likelihood | Mitigation (already in the notebook) |
|---|---|---|
| Repair-v1 manifest not found in attached datasets | low | flagged skip → 3-member consensus, ~−0.001 |
| Global96 child assert fails on this docker image | low | flagged skip; other members intact |
| 9h overrun (quota/ restart) | low | 3–3.5 h budget; append-only `_pipeline_stage` restore |
| Public-split fluke during probing | medium | 2-day confirmation rule, one knob per probe |
| Kaggle GPU quota exhaustion (seen with TranBaDat) | medium | Phase-2 training staged over days; notebook inference needs no quota |
| Someone else crosses 0.962 before Oct 22 | medium | Phase 2 is the differentiator; start it Oct 3 |

---

## 9. Source index (all fetched during this analysis)

Competition overview / leaderboard / data page (deadlines, LB table, test facts) ·
kernels leaderboard (d4-blend 0.946, 4-way consensus, votes) · d4-blend full source via
`/api/v1/kernels/pull` (recipes, hashes, weights, runtime contract) · mattiaangeli
Global96 dataset page (CC0, 904 MB, packaged runtime) · pilkwang baseline 0.891 · HF
18th-place writeup · NTejas-1/RSNA-Knee-Abnormality-Detection (reference build, append
pattern, arm blend) · ibrahimdodo/knee-mri-raptor (span/window ablations, 0.9219) ·
TranBaDat2607 (report.md + experiment_ledger.md — the design spine: E8 0.939, label
teacher table, rejected experiments, quota death) · ShivenKhurana1 `research/next_tier_095/REPORT.md`
(P0/P1/P2 roadmap, tie bug, ancestry pinning, OOF CI) · anhquan1111 (4,420-team survey:
top by public-checkpoint blending) · Sibusiso-K (metadata-only 0.598, site-CV inflation) ·
raahimnawaz snapshot (3,289 teams, free-notebook 0.936 plateau) · Daniel766hi (schema
receipts) · discussions 742267 (board passes 0.95 with text fusion) · github alvaromendizabal
0.933 reproduction.
