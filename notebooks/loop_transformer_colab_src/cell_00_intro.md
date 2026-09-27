# 🔁 Loop Transformer — Train a Tiny Thinking LLM from Scratch (Free Colab GPU)

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nasserml/E-Commerce-dot-net/blob/master/notebooks/Loop_Transformer_Small_LLM_Colab.ipynb)

**What this notebook does:** trains a small (~4M-parameter) decoder-only **large language model from scratch** in PyTorch — no pretrained weights, no Hugging Face model — using a **Loop Transformer** (a.k.a. Universal / weight-tied recurrent Transformer):

- **From scratch:** RMSNorm, RoPE positional encoding, SwiGLU MLP, causal self-attention, a character tokenizer, and the training loop — all implemented right here, no `transformers` library.
- **Loop Transformer:** `n_layers = 4` unique blocks, looped `n_loops = 4` times with **shared weights** → effective depth 16 for the parameter cost of 4. A learned per-loop embedding tells the shared weights which iteration they're on.
- **Thinking:** the model learns to write step-by-step traces inside `<think>...</think>` before answering in `<answer>...</answer>`. Bonus: because weights are loop-tied, you can run **extra loops at inference** (e.g. 8 instead of 4) to give the model more "thinking compute" with zero extra parameters.
- **KV cache:** full key/value caching implemented **per (loop, layer)** so generation stays O(1) per token. We verify cached decoding matches full forward passes exactly, and benchmark the speedup.

**Data:** ~20k synthetic examples generated on the fly — arithmetic with digit-by-digit reasoning traces (75%) + simple English sentences (25%). No downloads required, fully reproducible.

**Requirements:** Colab **free tier** with GPU: `Runtime → Change runtime type → Hardware accelerator → GPU (T4)`.

| Setting | Time on free T4 | Reasoning quality |
|---|---|---|
| `total_steps = 3000` (default) | ~15–25 min | good |
| `total_steps = 8000` | ~45–60 min | better |

> Run cells top to bottom. The only heavy cell is **§8 Train** — everything else runs in seconds.
