## Next steps & experiments

You now have a from-scratch Loop Transformer that **thinks in tokens**, **refines in loops**, and **decodes with a KV cache**. Ideas to push it further:

1. **Train longer** — set `total_steps = 8000` and watch the loops=8 advantage grow; log at which step explicit traces become reliably correct.
2. **Bigger loop gap** — train with `n_loops=2`, infer with `n_loops=8`: how much test-time compute can compensate for less training compute?
3. **Real text** — swap the synthetic sentences for TinyStories (`!pip install datasets`, stream 50k stories) and mix with the math traces for a more general tiny LM.
4. **BPE tokenizer** — replace `CharTokenizer` with a 2k-token BPE (`!pip install tokenizers`) and compare sample quality vs. training speed.
5. **Adaptive thinking** — add per-token halting (ACT): a small head predicting "loop again / stop", so easy tokens exit after 1–2 loops and hard ones use all 8.
6. **GQA + sliding window** — convert the attention to grouped-query attention to shrink the KV cache, then raise `block_size` to 512.
7. **Distill it** — train a `n_layers=2, n_loops=2` student to imitate this model's traces (sequence-level KD) and measure what survives.

If you publish results, the interesting plots are: **accuracy vs. inference loops** (§10) and **tok/s vs. sequence length with/without cache** (§9).
