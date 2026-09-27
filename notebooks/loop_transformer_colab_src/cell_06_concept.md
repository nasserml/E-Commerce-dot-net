## How a Loop Transformer works (the 2-minute version)

A standard decoder-only Transformer stacks `L` **different** layers and runs the tokens through once:

```
tokens → [L0] → [L1] → [L2] → [L3] → logits        (depth 4, params of 4 layers)
```

A **Loop Transformer** (Universal Transformer family) reuses the *same* `L` layers `T` times — weights tied across loops — plus a small learned **loop embedding** (an iteration counter) so the shared weights know which pass they're on:

```
loop 0:  x → [L0] → [L1] → [L2] → [L3] ─┐  (+ loop_emb[0])
loop 1:  x → [L0] → [L1] → [L2] → [L3] ─┤  (+ loop_emb[1])
loop 2:  x → [L0] → [L1] → [L2] → [L3] ─┤  (+ loop_emb[2])
loop 3:  x → [L0] → [L1] → [L2] → [L3] ─┴→ logits
                                         (depth 16, params of 4 layers)
```

**Why loop?**
1. **Parameter efficiency** — depth (which drives reasoning) without the memory cost.
2. **Iterative refinement** — each pass can fix mistakes of the previous one, like re-reading your own draft.
3. **Test-time thinking** — train with `T=4`, infer with `T=8`. More compute per token, zero new parameters (§10 measures this).

**Thinking traces.** We train the model to emit `<think>…step-by-step…</think><answer>…</answer>`. The loops do *latent* refinement; the tokens do *explicit* reasoning. Both are visible and measurable here.

**KV cache with loops.** Normal caching stores K/V per layer. With loops, the *same* layer sees *different* representations on each pass, so we store K/V per **(loop, layer)** pair — `T×L` caches. Prefill the prompt once, then decode one token at a time in O(1). §6 proves cached decoding matches full recomputation; §9 benchmarks the speedup.
