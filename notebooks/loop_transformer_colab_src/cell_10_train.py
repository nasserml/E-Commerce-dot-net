# ============================================================
# 8) Train (~15–25 min on a free T4 for 3000 steps)
# ============================================================
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

loader = iter(train_loader)
hist = {"step": [], "loss": [], "estep": [], "val": [], "acc": []}
best_val, t0 = float("inf"), time.time()
run_loss, run_n = 0.0, 0

model.train()
for step in range(1, cfg.total_steps + 1):
    try:
        xb, yb = next(loader)
    except StopIteration:
        loader = iter(train_loader)
        xb, yb = next(loader)
    xb, yb = xb.to(device, non_blocking=True), yb.to(device, non_blocking=True)

    for pg in optimizer.param_groups:
        pg["lr"] = lr_schedule(step)
    optimizer.zero_grad(set_to_none=True)
    ctx = torch.amp.autocast("cuda", dtype=amp_dtype) if device == "cuda" else nullcontext()
    with ctx:
        logits, _ = model(xb)
        loss = F.cross_entropy(logits.reshape(-1, logits.size(-1)), yb.reshape(-1), ignore_index=-100)
    scaler.scale(loss).backward()
    scaler.unscale_(optimizer)
    torch.nn.utils.clip_grad_norm_(model.parameters(), cfg.grad_clip)
    scaler.step(optimizer)
    scaler.update()

    run_loss += loss.item()
    run_n += 1
    if step % 50 == 0 or step == 1:
        dt = (time.time() - t0) / 60
        print(f"step {step:5d}/{cfg.total_steps}  train {run_loss / run_n:.4f}  "
              f"lr {lr_schedule(step):.1e}  [{dt:.1f} min]", flush=True)
        hist["step"].append(step)
        hist["loss"].append(run_loss / run_n)
        run_loss, run_n = 0.0, 0

    if step % cfg.eval_every == 0 or step == cfg.total_steps:
        v = eval_loss()
        acc = eval_accuracy(n=48)
        hist["estep"].append(step)
        hist["val"].append(v)
        hist["acc"].append(acc)
        print(f"  ↳ val loss {v:.4f} | think-answer acc {acc * 100:5.1f}% "
              f"(ppl {math.exp(min(v, 20)):.1f})", flush=True)
        if v < best_val and step < cfg.total_steps:
            best_val = v
            torch.save({"step": step, "model": model.state_dict(),
                        "opt": optimizer.state_dict(), "cfg": asdict(cfg),
                        "stoi": tok.stoi}, "best_loop_llm.pt")
            print("  ↳ ✅ saved best_loop_llm.pt", flush=True)
        model.train()

    if step % cfg.sample_every == 0 or step == cfg.total_steps:
        sample_show(["Q: 47+58=?\n<think>", "Q: 9*7=?\n<think>", "The happy cat"],
                    max_new_tokens=120)

print(f"\nDone in {(time.time() - t0) / 60:.1f} min. Final think-answer acc: {hist['acc'][-1] * 100:.1f}%")

# --- curves ---
fig, ax = plt.subplots(1, 2, figsize=(11, 3.5))
ax[0].plot(hist["step"], hist["loss"], label="train")
ax[0].set(xlabel="step", ylabel="loss", title="Training loss")
ax[0].legend()
ax[0].grid(alpha=.3)
ax[1].plot(hist["estep"], hist["val"], label="val loss")
ax[1].legend(loc="upper left")
ax[1].grid(alpha=.3)
ax2 = ax[1].twinx()
ax2.plot(hist["estep"], hist["acc"], color="tab:orange", marker="o", label="val acc")
ax2.set(ylabel="accuracy", title="Validation")
ax2.legend(loc="upper right")
fig.tight_layout()
fig.savefig("curves.png", dpi=120)
try:
    from IPython.display import Image, display
    display(Image("curves.png"))
except Exception:
    print("saved curves.png")
