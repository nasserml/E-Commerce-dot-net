# ============================================================
# 1) Config — tuned for a FREE Colab T4 (~15 GB VRAM)
#    3000 steps ≈ 15–25 min. For better reasoning try 6000–8000.
# ============================================================
@dataclass
class Config:
    # --- Model: tiny Loop Transformer (implemented from scratch in §5) ---
    d_model: int = 256
    n_layers: int = 4     # UNIQUE layers (this is what you store in VRAM)
    n_heads: int = 4
    n_loops: int = 4      # weight-tied loops -> effective depth = 4*4 = 16
    max_loops: int = 8    # headroom for extra "thinking" loops at inference
    block_size: int = 192 # max sequence length (chars, incl. <think> trace)
    dropout: float = 0.0
    rope_theta: float = 10000.0
    use_checkpoint: bool = False  # True = less VRAM, ~20% slower (checkpoint over loops)

    # --- Training ---
    batch_size: int = 64
    total_steps: int = 3000
    lr: float = 3e-4
    min_lr: float = 3e-5
    warmup_steps: int = 200
    weight_decay: float = 0.1
    grad_clip: float = 1.0
    eval_every: int = 250
    sample_every: int = 750

    # --- Data ---
    n_train: int = 20000
    n_val: int = 1000
    math_frac: float = 0.75  # math-with-thinking vs plain English sentences

    seed: int = 1337


cfg = Config()
for k, v in asdict(cfg).items():
    print(f"{k:16s} {v}")
