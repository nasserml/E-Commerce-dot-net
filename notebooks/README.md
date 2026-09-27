# Loop Transformer — Tiny Thinking LLM (Colab notebook)

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nasserml/E-Commerce-dot-net/blob/master/notebooks/Loop_Transformer_Small_LLM_Colab.ipynb)

**[`Loop_Transformer_Small_LLM_Colab.ipynb`](Loop_Transformer_Small_LLM_Colab.ipynb)** trains a small (~4M-parameter)
decoder-only LLM **from scratch** on a **free Colab T4 GPU** (~15–25 min):

- **Loop Transformer** (Universal / weight-tied): 4 unique layers looped 4× → effective depth 16,
  with a learned per-loop embedding. Implemented from scratch in PyTorch
  (RMSNorm, RoPE, SwiGLU, causal attention) — no `transformers` library.
- **Thinking**: learns `<think>…step-by-step…</think><answer>…</answer>` traces, and supports
  **test-time scaling** (train 4 loops → infer up to 8 loops, zero new parameters).
- **KV cache** per (loop, layer): O(1) decoding, proven identical to full recomputation, with a benchmark.
- **Data**: 20k synthetic examples (arithmetic reasoning traces + English sentences), generated in-notebook.
  No downloads, fully reproducible.

## Layout

- `Loop_Transformer_Small_LLM_Colab.ipynb` — the notebook (generated, Colab-ready).
- `loop_transformer_colab_src/cell_*` — one file per notebook cell (`.py` = code, `.md` = markdown).
- `loop_transformer_colab_src/build_notebook.py` — assembles the `.ipynb` from the cells.
- `loop_transformer_colab_src/smoke_test.py` — CPU test that executes the notebook code end-to-end
  on tiny data (requires `torch`, `numpy`).

## Regenerating the notebook

```bash
python notebooks/loop_transformer_colab_src/build_notebook.py
python notebooks/loop_transformer_colab_src/smoke_test.py   # needs torch + numpy
```
