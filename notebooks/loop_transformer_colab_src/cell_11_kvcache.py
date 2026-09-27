# ============================================================
# 9) KV-cache: prove it matches full recompute + measure speedup
# ============================================================
model.eval()
prompt = "Q: 83+47=?\n<think>"
ids = torch.tensor([tok.encode(prompt, add_eos=False)], device=device)

with torch.no_grad():
    t_cached = tok.decode(model.generate(
        ids, max_new_tokens=130, temperature=0.0, use_cache=True)[0].tolist())
    t_full = tok.decode(model.generate(
        ids, max_new_tokens=130, temperature=0.0, use_cache=False)[0].tolist())
print("identical outputs:", t_cached == t_full)
print(t_cached)


# --- benchmark: greedy, 100 new tokens ---
def bench(use_cache, iters=3, new_tokens=100):
    if device == "cuda":
        torch.cuda.synchronize()
    ts = []
    with torch.no_grad():
        for _ in range(iters):
            s = time.time()
            model.generate(ids, max_new_tokens=new_tokens, temperature=0.0, use_cache=use_cache)
            if device == "cuda":
                torch.cuda.synchronize()
            ts.append(time.time() - s)
    return sum(ts) / len(ts)


with torch.no_grad():
    c = bench(True)
    f = bench(False)
print(f"\ncached   : {c:.2f}s for 100 tokens ({100 / c:.0f} tok/s)")
print(f"no cache : {f:.2f}s for 100 tokens ({100 / f:.0f} tok/s)")
print(f"speedup  : {f / c:.1f}x  (grows with sequence length)")
