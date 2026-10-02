#!/usr/bin/env python3
"""Build the v2 win notebook: NTejas reference + d4-blend glue + arm blend
   + probe-config cell (window, arms, optional arm entry).

v2 additions over the 0.946-lineage recipe (see ANALYSIS.md section 8):
  1. Config cell at index 1: WIN_OUTER_W / WIN_OUTER_BASE / WIN_ALPHA /
     WIN_ARM_W knobs read by cell 23 at runtime.
  2. Fifth raptor arm `widedense-v4` (dreaddevelopment/raptor-knee-widedense,
     raptor_ft_coatnet_v4_full.pt = 0.924 single-LB, contract per dread card:
     slots 18/14/12/8/12 (=_SLOTS64), 6-94%, 336 cache, 384 model).
  3. raptor-fast dispatch extended to run arm index 4.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIN = ROOT / 'rsna-win'
REF = ROOT.parent / 'rsna-ntequas' / 'out' / 'notebook_blend_full.ipynb'
OUT = WIN / 'rsna-knee-win-blend.ipynb'

if not REF.exists():
    # workspace resets drop everything outside the repo; re-fetch the reference
    import subprocess as _sp
    repo = REF.parent.parent
    print(f'[build] reference missing; cloning NTejas-1 into {repo} ...')
    _sp.run(['git', 'clone', '--depth', '1',
             'https://github.com/NTejas-1/RSNA-Knee-Abnormality-Detection.git',
             str(repo)], check=True)
    if not REF.exists():
        raise SystemExit(f'reference still missing after clone: {REF}')

def set_source(cell, text):
    src = text.splitlines(keepends=True)
    if src and src[-1] and not src[-1].endswith('\n'):
        src[-1] += '\n'
    cell['source'] = src


def get_source(cell):
    return ''.join(cell['source'])


ref = json.loads(REF.read_text())
nb = json.loads(REF.read_text())   # always rebuild from the pristine reference
orig = json.loads(REF.read_text())
if ref != orig:
    raise SystemExit('ref file changed since graft? abort')
cells = nb['cells']
if len(cells) != 25:
    raise SystemExit(f'expected 25-cell reference notebook, got {len(cells)}')

# Reapply the v1 graft cells (coat engine, arm guard, publish audit) captured
# byte-exact in v1_cells.json; the v2 grafts below then run on top of them.
snap = json.loads((WIN / 'v1_cells.json').read_text())
for idx, key in ((22, 'c22'), (23, 'c23'), (24, 'c24')):
    cell = {'cell_type': 'code', 'metadata': {}, 'outputs': [],
            'execution_count': None}
    set_source(cell, snap[key])
    cells[idx] = cell


# --------------------------------------------------------------- config cell
CFG = '''\
# ===================== WIN-BLEND PROBE CONFIG (v2) =====================
# The ONLY cell you edit between submissions. Defaults reproduce the
# 0.946-proven recipe when left empty/None. One knob per submission;
# probing plan: ANALYSIS.md section 7. Grids below are the researched
# recommendations (shiven next-tier OOF + d4-blend alpha + arm audit).
#
# 1) Per-label OUTER routing overrides (raptor/CoAt side vs transformer base).
#    Grid: ACL {.68,.75}  Medial Meniscus {.70,.80,.90}
#          Lateral Meniscus {.85,1.00}  Lateral OA {.68,.75}
#          Fracture {.70,.75}  -> base for other 7 {.55,.60,.65}
WIN_OUTER_W = {}          # e.g. {"Lateral Meniscus": 1.00}
#
# 2) Weight applied to EVERY label without a specific override above
#    (None = the 0.946 value 0.60; grid {.55,.60,.65}).
WIN_OUTER_BASE = None     # e.g. 0.55
#
# 3) Inner raptor/CoAt hybrid alpha (0.40 is the 0.946 value; grid
#    {.35,.40,.45,.50}). Use .05 step between submissions.
WIN_ALPHA = None          # e.g. 0.45
#
# 4) Raptor probability-blend arm weights (renormalised automatically).
#    Defaults: maxspan-v5 .60, native384dense-v10 .10,
#              maxspan-v5-reverse .10, native384-v8 .20,
#              widedense-v4 .15 (v2 addition, 0.924 single-LB).
#    Grid: widedense-v4 {.10,.15,.25}  native384-v8 {.10,.20}
WIN_ARM_W = {}            # e.g. {"widedense-v4": 0.25, "native384-v8": 0.10}
# ======================================================================
print("[win-config] outer:", WIN_OUTER_W or "-", "base:",
      WIN_OUTER_BASE if WIN_OUTER_BASE is not None else 0.6,
      "| alpha:", WIN_ALPHA if WIN_ALPHA is not None else 0.4,
      "| arm w:", WIN_ARM_W or "-", flush=True)
'''

# ----------------------------------------------------- cell 23 (old 22) grafts
s = get_source(cells[22])
guards = 0


def graft(src, old, new, expect=1):
    global guards
    n = src.count(old)
    if n != expect:
        raise SystemExit(f'anchor count {n} != {expect}: {old[:70]!r}')
    guards += 1
    return src.replace(old, new)


# 2a. fifth arm entry (anchor: native384-v8 block closing the ARMS list)
s = graft(
    s,
    '''     "img": 384, "slots": _SLOTS44, "span": (0.06, 0.94), "k_eval": 42,
     "reverse": False, "w": 0.20},
]''',
    '''     "img": 384, "slots": _SLOTS44, "span": (0.06, 0.94), "k_eval": 42,
     "reverse": False, "w": 0.20},
    {"name": "widedense-v4", "file": "raptor_ft_coatnet_v4_full.pt",
     "arch": "coatnet_rmlp_2_rw_384.sw_in12k_ft_in1k", "res": 384,
     "img": 336, "slots": _SLOTS64, "span": (0.06, 0.94), "k_eval": 42,
     "reverse": False, "w": 0.15},
]''')

# 2b. raptor-fast dispatch: also run arm 4 (2-GPU on cuda:0, 1-GPU after arm 3)
s = graft(
    s,
    '''if torch.cuda.device_count() >= 2:
        def gpu_zero():
            with torch.cuda.device(0):
                run_shared_maxspan(torch.device('cuda:0'))

        def gpu_one():
            with torch.cuda.device(1):
                run_single(1, torch.device('cuda:1'))
                run_single(3, torch.device('cuda:1'))

        with _KeThreadPool(max_workers=2) as executor:
            workers = [executor.submit(gpu_zero), executor.submit(gpu_one)]
            for w in workers:
                w.result()
    else:
        with torch.cuda.device(0):
            run_shared_maxspan(torch.device('cuda:0'))
            run_single(1, torch.device('cuda:0'))
            run_single(3, torch.device('cuda:0'))
        for worker in workers:
            worker.result()''',
    '''if torch.cuda.device_count() >= 2:
        def gpu_zero():
            with torch.cuda.device(0):
                run_shared_maxspan(torch.device('cuda:0'))
                if len(arms) > 4:
                    run_single(4, torch.device('cuda:0'))

        def gpu_one():
            with torch.cuda.device(1):
                run_single(1, torch.device('cuda:1'))
                run_single(3, torch.device('cuda:1'))

        with _KeThreadPool(max_workers=2) as executor:
            workers = [executor.submit(gpu_zero), executor.submit(gpu_one)]
            for w in workers:
                w.result()
    else:
        with torch.cuda.device(0):
            run_shared_maxspan(torch.device('cuda:0'))
            run_single(1, torch.device('cuda:0'))
            run_single(3, torch.device('cuda:0'))
            if len(arms) > 4:
                run_single(4, torch.device('cuda:0'))
        for worker in workers:
            worker.result()''')

# 2c. arm-weight config hook after the k_eval override loop
s = graft(
    s,
    '''for _arm in _KE_NS['ARMS']:
    _arm['parent_k_eval'] = _arm['k_eval']
    _arm['k_eval'] = 94''',
    '''for _arm in _KE_NS['ARMS']:
    _arm['parent_k_eval'] = _arm['k_eval']
    _arm['k_eval'] = 94
for _k_name, _k_w in (globals().get('WIN_ARM_W') or {}).items():
    _k_hits = [a for a in _KE_NS['ARMS'] if a['name'] == _k_name]
    if not _k_hits:
        rsna_event('win_config_unknown_arm', arm=str(_k_name))
    for _k_arm in _k_hits:
        _k_arm['w'] = float(_k_w)
        print(f"[win-config] arm {_k_name} w -> {_k_arm['w']}", flush=True)''')

# 2d. alpha config (inside the coat routine)
s = graft(s, '    private_alpha = 0.4\n',
          '''    _win_alpha = globals().get('WIN_ALPHA')
    private_alpha = 0.4 if _win_alpha is None else float(_win_alpha)
    if private_alpha != 0.4:
        print(f"[win-config] inner alpha -> {private_alpha}", flush=True)
''')

# 2e. outer-weight config after the renta-weight update
m = re.search(r'(_coatnet_weight\.update\(\{.*?\}\))', s, re.S)
if not m:
    raise SystemExit('renta _coatnet_weight.update anchor missing')
guards += 1
s = s.replace(m.group(1), m.group(1) + '''

for _k, _v in (globals().get('WIN_OUTER_W') or {}).items():
    if _k in _coatnet_weight:
        _coatnet_weight[_k] = min(1.0, max(0.0, float(_v)))
        print(f"[win-config] outer {_k} -> {_coatnet_weight[_k]}", flush=True)
    else:
        rsna_event('win_config_unknown_label', label=str(_k))
_win_outer_base = globals().get('WIN_OUTER_BASE')
if _win_outer_base is not None:
    for _k in list(_coatnet_weight):
        if _k not in (globals().get('WIN_OUTER_W') or {}):
            _coatnet_weight[_k] = min(1.0, max(0.0, float(_win_outer_base)))
    print(f"[win-config] outer base -> {min(1.0, max(0.0, float(_win_outer_base)))}", flush=True)''')

set_source(cells[22], s)
compile(s, '<cell22-graft>', 'exec')

# ------------------------------------------------- cell 24 guard (old 23)
s = get_source(cells[23])
if 'skipping the arm blend' not in s:
    raise SystemExit('cell23 skip-guard marker missing')
_i = s.find('skipping the arm blend')
if 'return' not in s[_i:_i + 400]:
    raise SystemExit('cell23 skip path does not return (degrade to parent)')

# ------------------------------------------- cell 25 publish (old 24)
s = get_source(cells[24])
old_exp = "('maxspan-v5','native384dense-v10','native384-v8')"
new_exp = ("('maxspan-v5','native384dense-v10','native384-v8',"
           "'widedense-v4')")
if s.count(old_exp) != 1:
    raise SystemExit('publish expected-arms anchor missing')
guards += 1
set_source(cells[24], s.replace(old_exp, new_exp))
compile(get_source(cells[24]), '<cell24-publish>', 'exec')

# ------------------------------------------------ insert config cell at 1
cfg = {'cell_type': 'code', 'metadata': {}, 'outputs': [],
       'execution_count': None}
set_source(cfg, CFG)
compile(CFG, '<config>', 'exec')
cells.insert(1, cfg)
if len(cells) != 26:
    raise SystemExit(f'expected 26 cells after insert, got {len(cells)}')

# ------------------------------------------------------------- assertions
if get_source(cells[0]) != ''.join(orig['cells'][0]['source']):
    raise SystemExit('cells[0] differs')
for new_i, old_i in [(i, i - 1) for i in range(2, 23)]:
    if get_source(cells[new_i]) != ''.join(orig['cells'][old_i]['source']):
        raise SystemExit(f'cells[{new_i}] != original cells[{old_i}]')

s1 = get_source(cells[1])
for marker in ('WIN_OUTER_W = {}', 'WIN_OUTER_BASE = None',
               'WIN_ALPHA = None', 'WIN_ARM_W = {}'):
    if marker not in s1:
        raise SystemExit(f'config cell missing {marker}')

s23 = get_source(cells[23])
for marker in ('"name": "widedense-v4"', '"file": "raptor_ft_coatnet_v4_full.pt"',
               '"span": (0.06, 0.94)', '"k_eval": 42',
               'run_single(4, torch.device(', 'WIN_ARM_W',
               'private_alpha = 0.4 if _win_alpha is None',
               'WIN_OUTER_W', 'WIN_OUTER_BASE'):
    if marker not in s23:
        raise SystemExit(f'cell23 graft missing {marker}')
for forbidden in ('"w": 0.999', 'raptor_ft_coatnet_v11'):
    if forbidden in s23:
        raise SystemExit(f'cell23 contains {forbidden}')

s24 = get_source(cells[24])
if 'skipping the arm blend' not in s24:
    raise SystemExit('cell24 skip-guard missing')
_i = s24.find('skipping the arm blend')
if 'return' not in s24[_i:_i + 400]:
    raise SystemExit('cell24 skip path does not return (degrade to parent)')

s25 = get_source(cells[25])
if "'widedense-v4'" not in s25:
    raise SystemExit('cell25 publish expected-arms missing widedense-v4')

for i in (1, 23, 24, 25):
    compile(get_source(cells[i]), f'<cell{i}>', 'exec')
for i, c in enumerate(cells):
    if c['cell_type'] == 'code':
        compile(get_source(c), f'<cell{i}>', 'exec')

nb['metadata'] = orig['metadata']
OUT.write_text(json.dumps(nb, ensure_ascii=False) + '\n')
print(f'built {OUT.name}: {OUT.stat().st_size} bytes, {len(cells)} cells,'
      f' {guards} graft guards, every code cell compiles')
