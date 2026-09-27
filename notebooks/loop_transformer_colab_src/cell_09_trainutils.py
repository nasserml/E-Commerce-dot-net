# ============================================================
# 7) Optimizer, cosine schedule, AMP + eval helpers
# ============================================================
def lr_schedule(step):
    if step < cfg.warmup_steps:
        return cfg.lr * step / max(1, cfg.warmup_steps)
    p = (step - cfg.warmup_steps) / max(1, cfg.total_steps - cfg.warmup_steps)
    p = min(1.0, max(0.0, p))
    return cfg.min_lr + 0.5 * (cfg.lr - cfg.min_lr) * (1 + math.cos(math.pi * p))


optimizer = torch.optim.AdamW(model.parameters(), lr=cfg.lr,
                              weight_decay=cfg.weight_decay, betas=(0.9, 0.95))
use_bf16 = device == "cuda" and torch.cuda.is_bf16_supported()
amp_dtype = torch.bfloat16 if use_bf16 else torch.float16  # T4 has no bf16 -> fp16
scaler = torch.amp.GradScaler("cuda", enabled=(device == "cuda" and not use_bf16))
print(f"AMP dtype: {amp_dtype} | GradScaler: {scaler.is_enabled()}")


def extract_answer(text):
    m = re.search(r"<answer>(.*?)</answer>", text, re.S)
    return m.group(1).strip() if m else None


@torch.no_grad()
def eval_loss(n_batches=20):
    model.eval()
    tot, n = 0.0, 0
    it = iter(val_loader)
    for _ in range(n_batches):
        try:
            xb, yb = next(it)
        except StopIteration:
            break
        xb, yb = xb.to(device), yb.to(device)
        logits, _ = model(xb)
        tot += F.cross_entropy(logits.reshape(-1, logits.size(-1)), yb.reshape(-1),
                               ignore_index=-100).item()
        n += 1
    return tot / max(1, n)


@torch.no_grad()
def eval_accuracy(n=48, n_loops=None, max_new_tokens=150, verbose=0):
    """Greedy think-then-answer accuracy on held-out math questions."""
    model.eval()
    n = min(n, len(val_prompts))
    correct = 0
    for i in range(n):
        ids = torch.tensor([tok.encode(val_prompts[i], add_eos=False)], device=device)
        out = model.generate(ids, max_new_tokens=max_new_tokens, temperature=0.0,
                             use_cache=True, n_loops=n_loops, eos_id=tok.eos_id)
        pred = extract_answer(tok.decode(out[0].tolist()))
        ok = (pred == val_answers[i])
        correct += ok
        if verbose and (i < verbose or not ok):
            print(f"{'✓' if ok else '✗'} {val_prompts[i]!r} → {pred!r} (true {val_answers[i]!r})")
    return correct / max(1, n)


@torch.no_grad()
def sample_show(prompts, max_new_tokens=150, temperature=0.0, n_loops=None, top_k=50):
    model.eval()
    for p in prompts:
        ids = torch.tensor([tok.encode(p, add_eos=False)], device=device)
        out = model.generate(ids, max_new_tokens=max_new_tokens, temperature=temperature,
                             top_k=top_k, use_cache=True, n_loops=n_loops, eos_id=tok.eos_id)
        print("—" * 70)
        print(tok.decode(out[0].tolist()))
    print("—" * 70)
