# ============================================================
# 6) Sanity checks: shapes, loss, KV-cache equivalence, loop range
# ============================================================
model.eval()
with torch.no_grad():
    xb0, yb0 = next(iter(val_loader))
    xb0, yb0 = xb0[:4].to(device), yb0[:4].to(device)
    logits0, _ = model(xb0)
    print("logits shape:", tuple(logits0.shape), "(batch, seq, vocab)")
    l0 = F.cross_entropy(logits0.reshape(-1, logits0.size(-1)), yb0.reshape(-1), ignore_index=-100)
    print(f"untrained loss: {float(l0):.3f}  (random ≈ ln(V) = {math.log(len(tok.stoi)):.3f})")

    # --- KV-cache equivalence: incremental decode == one full forward ---
    prompt = "Q: 12+29=?\n<think>ones: "
    ids = torch.tensor([tok.encode(prompt, add_eos=False)], device=device)
    full, _ = model(ids)  # [1, T, V]
    k = ids.size(1) // 2
    pre_lg, past = model(ids[:, :k], use_cache=True, start_pos=0)
    parts = [pre_lg[:, -1:, :]]  # predicts token k
    for j in range(k, ids.size(1)):  # decode rest token-by-token
        lg, past = model(ids[:, j:j + 1], past_kv=past, use_cache=True, start_pos=j)
        parts.append(lg)  # predicts token j+1
    inc = torch.cat(parts, dim=1)
    ref = full[:, k - 1:, :]  # logits predicting tokens k..T-1 (+eos slot)
    diff = (inc.float() - ref.float()).abs().max().item()
    match = (inc.argmax(-1) == ref.argmax(-1)).float().mean().item()
    print(f"cache-vs-full max|Δlogit| = {diff:.2e} | argmax match = {match * 100:.0f}%")
    assert diff < 1e-2, "KV cache diverges from full forward!"

    # --- variable loop counts (test-time thinking range) ---
    for L in (1, cfg.n_loops, cfg.max_loops):
        lg, cache = model(xb0[:1], use_cache=True, n_loops=L)
        assert len(cache) == L and all(len(lc) == cfg.n_layers for lc in cache)
        print(f"n_loops={L}: ok, cache holds {L}x{cfg.n_layers} (loop x layer) KV pairs")

    # --- untrained sample (expect gibberish — that's the "before" picture) ---
    ids = torch.tensor([tok.encode("Q: 7+5=?\n<think>", add_eos=False)], device=device)
    out = model.generate(ids, max_new_tokens=60, temperature=0.0)
    print("untrained sample:", repr(tok.decode(out[0].tolist()))[:220])
