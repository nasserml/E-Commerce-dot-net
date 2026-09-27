"""CPU smoke test: executes the notebook's cell sources end-to-end on tiny data.

Run:
    python smoke_test.py        (requires torch, numpy)
"""
import json
import math
import os
import random
import re
import time
from contextlib import nullcontext
from dataclasses import dataclass, asdict

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

SRC = os.path.dirname(os.path.abspath(__file__))
device = "cpu"
torch.manual_seed(1337)
np.random.seed(1337)
random.seed(1337)


def run(cell):
    print(f"\n===== {cell} =====", flush=True)
    with open(os.path.join(SRC, cell), encoding="utf-8") as f:
        code = f.read()
    exec(compile(code, cell, "exec"), globals())


run("cell_02_config.py")
# shrink for a fast CPU smoke test
cfg.n_train = 400
cfg.n_val = 60
cfg.total_steps = 6
cfg.batch_size = 16
cfg.eval_every = 5
cfg.sample_every = 1000
cfg.n_loops = 2
cfg.max_loops = 4
run("cell_03_tokenizer.py")
run("cell_04_data.py")
run("cell_05_dataset.py")
run("cell_07_model.py")
run("cell_08_sanity.py")
run("cell_09_trainutils.py")

# --- mini training: a few plain steps (no AMP on CPU) ---
loader = iter(train_loader)
model.train()
for step in range(1, cfg.total_steps + 1):
    try:
        xb, yb = next(loader)
    except StopIteration:
        loader = iter(train_loader)
        xb, yb = next(loader)
    for pg in optimizer.param_groups:
        pg["lr"] = lr_schedule(step)
    optimizer.zero_grad(set_to_none=True)
    logits, _ = model(xb)
    loss = F.cross_entropy(logits.reshape(-1, logits.size(-1)), yb.reshape(-1), ignore_index=-100)
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), cfg.grad_clip)
    optimizer.step()
    print(f"smoke step {step} loss {loss.item():.4f}", flush=True)

print("val loss:", eval_loss(n_batches=2), flush=True)
print("acc(4):", eval_accuracy(n=4), flush=True)
sample_show(["Q: 7+5=?\n<think>"], max_new_tokens=40)
print("\nSMOKE TEST PASSED", flush=True)
