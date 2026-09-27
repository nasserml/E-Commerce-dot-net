# ============================================================
# 5) The Loop Transformer LM — from scratch
#    RMSNorm + RoPE + causal MHA + SwiGLU + loop tying + KV cache
# ============================================================
import torch.utils.checkpoint as _ckpt


class RMSNorm(nn.Module):
    def __init__(self, dim, eps=1e-6):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(dim))
        self.eps = eps

    def forward(self, x):
        return self.weight * x * torch.rsqrt(x.pow(2).mean(-1, keepdim=True) + self.eps)


def build_rope_cache(head_dim, max_len, theta=10000.0):
    """NeoX-style RoPE frequencies. Returns cos/sin: [max_len, head_dim//2]."""
    assert head_dim % 2 == 0
    inv = 1.0 / (theta ** (torch.arange(0, head_dim, 2).float() / head_dim))
    pos = torch.arange(max_len).float()
    freqs = torch.outer(pos, inv)
    return freqs.cos(), freqs.sin()


def apply_rope(x, cos, sin):
    """x: [B,H,T,Dh]; cos/sin: [T,Dh/2] already sliced for the right positions."""
    c = cos.to(dtype=x.dtype, device=x.device).unsqueeze(0).unsqueeze(0)  # [1,1,T,Dh/2]
    s = sin.to(dtype=x.dtype, device=x.device).unsqueeze(0).unsqueeze(0)
    x1, x2 = x.chunk(2, dim=-1)
    return torch.cat([x1 * c - x2 * s, x1 * s + x2 * c], dim=-1)


class CausalSelfAttention(nn.Module):
    def __init__(self, d_model, n_heads, dropout=0.0):
        super().__init__()
        assert d_model % n_heads == 0
        self.n_heads = n_heads
        self.head_dim = d_model // n_heads
        self.qkv = nn.Linear(d_model, 3 * d_model, bias=False)
        self.proj = nn.Linear(d_model, d_model, bias=False)
        self.drop = dropout

    def forward(self, x, cos, sin, start_pos=0, past_kv=None, use_cache=False):
        B, T, C = x.shape
        q, k, v = (self.qkv(x).view(B, T, 3, self.n_heads, self.head_dim)
                   .permute(2, 0, 3, 1, 4).unbind(0))  # each [B,H,T,Dh]
        q = apply_rope(q, cos[start_pos:start_pos + T], sin[start_pos:start_pos + T])
        k = apply_rope(k, cos[start_pos:start_pos + T], sin[start_pos:start_pos + T])
        if past_kv is not None:  # decode: append new K/V to the cache
            pk, pv = past_kv
            k = torch.cat([pk, k], dim=2)
            v = torch.cat([pv, v], dim=2)
        present = (k, v) if use_cache else None
        # Prefill (no cache yet): causal over the whole prompt.
        # Decode (1 new token): it may attend to all cached past, no mask needed.
        y = F.scaled_dot_product_attention(
            q, k, v, is_causal=(past_kv is None and T > 1),
            dropout_p=self.drop if self.training else 0.0)
        y = y.transpose(1, 2).reshape(B, T, C)
        return self.proj(y), present


class SwiGLU(nn.Module):
    def __init__(self, d_model, mult=4):
        super().__init__()
        hidden = ((mult * d_model + 63) // 64) * 64
        self.gate = nn.Linear(d_model, hidden, bias=False)
        self.up = nn.Linear(d_model, hidden, bias=False)
        self.down = nn.Linear(hidden, d_model, bias=False)

    def forward(self, x):
        return self.down(F.silu(self.gate(x)) * self.up(x))


class LoopBlock(nn.Module):
    """One pre-norm Transformer block. Each layer instance is unique,
    but the SAME instances are reused on every loop (weight tying)."""
    def __init__(self, d_model, n_heads, dropout=0.0):
        super().__init__()
        self.ln1 = RMSNorm(d_model)
        self.attn = CausalSelfAttention(d_model, n_heads, dropout)
        self.ln2 = RMSNorm(d_model)
        self.mlp = SwiGLU(d_model)

    def forward(self, x, cos, sin, start_pos=0, past_kv=None, use_cache=False):
        h, present = self.attn(self.ln1(x), cos, sin, start_pos, past_kv, use_cache)
        x = x + h
        x = x + self.mlp(self.ln2(x))
        return x, present


class LoopTransformerLM(nn.Module):
    """Tiny Loop (Universal / weight-tied) Transformer LM.

    - `n_layers` unique blocks; the whole stack is repeated `n_loops`
      times with shared weights + a learned per-loop embedding.
    - KV cache is kept per (loop, layer): cache[t][li] = (K, V).
    - At inference you may pass a larger `n_loops` ("thinking harder").
    """
    def __init__(self, cfg, vocab_size):
        super().__init__()
        self.cfg = cfg
        self.n_layers, self.n_heads = cfg.n_layers, cfg.n_heads
        self.n_loops, self.max_loops = cfg.n_loops, cfg.max_loops
        self.block_size = cfg.block_size

        self.tok_emb = nn.Embedding(vocab_size, cfg.d_model)
        self.loop_emb = nn.Embedding(cfg.max_loops, cfg.d_model)  # learned loop counter
        self.drop = nn.Dropout(cfg.dropout)
        self.layers = nn.ModuleList(
            [LoopBlock(cfg.d_model, cfg.n_heads, cfg.dropout) for _ in range(cfg.n_layers)])
        self.norm = RMSNorm(cfg.d_model)
        self.head = nn.Linear(cfg.d_model, vocab_size, bias=False)
        self.head.weight = self.tok_emb.weight  # tied input/output embeddings

        cos, sin = build_rope_cache(cfg.d_model // cfg.n_heads, cfg.block_size, cfg.rope_theta)
        self.register_buffer("rope_cos", cos, persistent=False)
        self.register_buffer("rope_sin", sin, persistent=False)
        self.apply(self._init)

    @staticmethod
    def _init(m):
        if isinstance(m, (nn.Linear, nn.Embedding)):
            nn.init.normal_(m.weight, std=0.02)

    def forward(self, input_ids, past_kv=None, use_cache=False, n_loops=None, start_pos=0):
        n_loops = self.n_loops if n_loops is None else n_loops
        if not 1 <= n_loops <= self.max_loops:
            raise ValueError(f"n_loops must be in [1, {self.max_loops}], got {n_loops}")
        B, T = input_ids.shape
        if start_pos + T > self.block_size:
            raise ValueError(f"length {start_pos + T} exceeds block_size {self.block_size}")
        x = self.drop(self.tok_emb(input_ids))
        cos, sin = self.rope_cos, self.rope_sin
        ckpt = self.cfg.use_checkpoint and self.training and not use_cache and past_kv is None
        new_cache = [] if use_cache else None

        for t in range(n_loops):
            x = x + self.loop_emb.weight[t].view(1, 1, -1)  # "this is loop t"
            loop_cache = [] if use_cache else None
            for li, layer in enumerate(self.layers):
                past = past_kv[t][li] if past_kv is not None else None
                if ckpt:
                    def _f(_x, _layer=layer, _cos=cos, _sin=sin, _sp=start_pos):
                        out, _ = _layer(_x, _cos, _sin, _sp, None, False)
                        return out
                    x = _ckpt.checkpoint(_f, x, use_reentrant=False)
                else:
                    x, present = layer(x, cos, sin, start_pos, past, use_cache)
                    if use_cache:
                        loop_cache.append(present)
            if use_cache:
                new_cache.append(loop_cache)
        return self.head(self.norm(x)), new_cache

    @torch.no_grad()
    def generate(self, input_ids, max_new_tokens=64, temperature=0.7, top_k=50, top_p=0.0,
                 use_cache=True, n_loops=None, eos_id=None):
        """Autoregressive decoding. temperature<=0 = greedy. Set eos_id to stop early."""
        self.eval()
        n_loops = self.n_loops if n_loops is None else n_loops
        logits, past = self(input_ids, past_kv=None, use_cache=use_cache,
                            n_loops=n_loops, start_pos=0)
        out = input_ids
        neg_inf = torch.tensor(float("-inf"), device=input_ids.device)
        for _ in range(max_new_tokens):
            last = logits[:, -1, :]
            if temperature is None or temperature <= 0:  # greedy
                nxt = last.argmax(-1, keepdim=True)
            else:
                l = last / temperature
                if top_k and top_k < l.size(-1):
                    thr = torch.topk(l, top_k).values[:, [-1]]
                    l = torch.where(l < thr, neg_inf, l)
                if top_p and 0 < top_p < 1.0:
                    s, idx = torch.sort(l, descending=True)
                    probs = F.softmax(s, dim=-1)
                    mask = (probs.cumsum(-1) - probs) > top_p
                    s = torch.where(mask, neg_inf, s)
                    l = torch.full_like(l, float("-inf")).scatter(1, idx, s)
                nxt = torch.multinomial(F.softmax(l, dim=-1), 1)
            out = torch.cat([out, nxt], dim=1)
            if out.size(1) >= self.block_size:
                break
            if eos_id is not None and bool((nxt == eos_id).all()):
                break
            if use_cache:
                logits, past = self(nxt, past_kv=past, use_cache=True,
                                    n_loops=n_loops, start_pos=out.size(1) - 1)
            else:
                logits, _ = self(out, use_cache=False, n_loops=n_loops, start_pos=0)
        return out


def count_params(m):
    return sum(p.numel() for p in m.parameters())


def kv_cache_mb(n_loops, batch=1, seq=None, dtype_bytes=2):
    seq = seq or cfg.block_size
    n = 2 * batch * n_loops * cfg.n_layers * cfg.d_model * seq * dtype_bytes
    return n / 1e6  # K and V per (loop, layer): d_model elems per token


model = LoopTransformerLM(cfg, vocab_size=len(tok.stoi)).to(device)
print(f"params: {count_params(model) / 1e6:.2f}M | "
      f"{cfg.n_layers} layers x {cfg.n_loops} loops = effective depth {cfg.n_layers * cfg.n_loops}")
print(f"KV cache fp16, batch=1, seq={cfg.block_size}: "
      f"{kv_cache_mb(cfg.n_loops):.2f} MB @train loops, {kv_cache_mb(cfg.max_loops):.2f} MB @max loops")
