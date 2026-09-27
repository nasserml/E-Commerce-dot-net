# ============================================================
# 0) Environment: GPU check + speed flags + reproducibility
# ============================================================
# If the GPU check below fails, enable one:
# Colab menu: Runtime > Change runtime type > Hardware accelerator > GPU
try:
    import google.colab  # noqa: F401  (only exists on Colab)
    get_ipython().system("nvidia-smi -L")
except Exception:
    pass

import math
import os
import random
import re
import json
import time
from contextlib import nullcontext
from dataclasses import dataclass, asdict

import torch
import torch.nn as nn
import torch.nn.functional as F

print(f"torch {torch.__version__} | cuda: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))
    tot = torch.cuda.get_device_properties(0).total_memory / 1e9
    print(f"VRAM: {tot:.1f} GB | bf16 ok: {torch.cuda.is_bf16_supported()}")
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    try:
        torch.set_float32_matmul_precision("high")
    except Exception:
        pass
else:
    print("⚠️ No GPU detected — on Colab set Runtime > Change runtime type > T4 GPU.")

device = "cuda" if torch.cuda.is_available() else "cpu"
print("device:", device)

try:
    import numpy as np
    print("numpy", np.__version__)
except ImportError:
    raise SystemExit("numpy is required (it is preinstalled on Colab).")

SEED = 1337
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)
