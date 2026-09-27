# ============================================================
# 3) Data: arithmetic with step-by-step traces + plain sentences
#    Generated locally — no downloads, fully reproducible.
#    Format: Q: 47+58=?\n<think>...steps...</think>\n<answer>105</answer>
# ============================================================
_POS = ["ones", "tens", "hundreds", "thousands"]


def trace_add(a, b):
    sa, sb = str(a), str(b)
    i, j = len(sa) - 1, len(sb) - 1
    carry, steps, digits, p = 0, [], [], 0
    while i >= 0 or j >= 0:
        da = int(sa[i]) if i >= 0 else 0
        db = int(sb[j]) if j >= 0 else 0
        s = da + db + carry
        steps.append(f"{_POS[p]}: {da}+{db}+{carry}={s}, write {s % 10} carry {s // 10}")
        digits.append(str(s % 10))
        carry = s // 10
        i -= 1; j -= 1; p += 1
    if carry:
        steps.append(f"leftover carry {carry}")
        digits.append(str(carry))
    return "; ".join(steps) + f". So {a}+{b}={a + b}."


def trace_sub(a, b):
    assert a >= b
    sa, sb = str(a), str(b)
    i, j = len(sa) - 1, len(sb) - 1
    borrow, steps, digits, p = 0, [], [], 0
    while i >= 0 or j >= 0:
        da = int(sa[i]) if i >= 0 else 0
        db = int(sb[j]) if j >= 0 else 0
        d = da - borrow - db
        if d < 0:
            steps.append(f"{_POS[p]}: {da}-{borrow}-{db} needs borrow, "
                         f"{da + 10}-{borrow}-{db}={d + 10}, write {d + 10} borrow 1")
            d += 10
            borrow = 1
        else:
            steps.append(f"{_POS[p]}: {da}-{borrow}-{db}={d}, write {d} borrow 0")
            borrow = 0
        digits.append(str(d))
        i -= 1; j -= 1; p += 1
    return "; ".join(steps) + f". So {a}-{b}={a - b}."


def trace_mul(a, b):
    if a == 0 or b == 0:
        return f"Anything times 0 is 0. So {a}*{b}=0."
    return f"Add {b} {a} times: {'+'.join([str(b)] * a)}={a * b}. So {a}*{b}={a * b}."


def math_example(rng):
    r = rng.random()
    if r < 0.45:
        a, b = int(rng.integers(0, 100)), int(rng.integers(0, 100))
        q, ans, tr = f"{a}+{b}", str(a + b), trace_add(a, b)
    elif r < 0.75:
        a, b = int(rng.integers(0, 100)), int(rng.integers(0, 100))
        a, b = max(a, b), min(a, b)
        q, ans, tr = f"{a}-{b}", str(a - b), trace_sub(a, b)
    else:
        a, b = int(rng.integers(0, 13)), int(rng.integers(0, 13))
        q, ans, tr = f"{a}*{b}", str(a * b), trace_mul(a, b)
    return f"Q: {q}=?\n<think>{tr}</think>\n<answer>{ans}</answer>", q, ans


_NOUN = ["cat", "dog", "bird", "fish", "frog", "fox", "bear", "bee", "owl", "wolf",
         "tree", "sun", "moon", "star", "lake", "hill", "cloud", "stone"]
_VERB = ["runs", "jumps", "sings", "sleeps", "plays", "eats", "flies", "swims",
         "glows", "dances", "hides", "watches", "shines", "rests"]
_ADJ = ["red", "big", "small", "happy", "quick", "bright", "soft", "loud",
        "calm", "wild", "tiny", "warm", "cold", "green"]
_PREP = ["on", "under", "near", "by", "over", "behind"]


def lang_example(rng):
    n1, n2 = rng.choice(_NOUN, 2, replace=False)
    s1 = (f"The {rng.choice(_ADJ)} {n1} {rng.choice(_VERB)} {rng.choice(_PREP)} "
          f"the {rng.choice(_ADJ)} {n2}.")
    if rng.random() < 0.5:
        s2 = f"It is a {rng.choice(_ADJ)} day and the {n1} feels {rng.choice(_ADJ)}."
        return s1 + " " + s2
    return s1


def build_corpus(n, seed, math_frac):
    rng = np.random.default_rng(seed)
    texts, prompts, answers = [], [], []
    for _ in range(n):
        if rng.random() < math_frac:
            t, q, a = math_example(rng)
            texts.append(t)
            prompts.append(f"Q: {q}=?\n<think>")  # generation prompt (answer held out)
            answers.append(a)
        else:
            texts.append(lang_example(rng))
    return texts, prompts, answers


train_texts, _, _ = build_corpus(cfg.n_train, cfg.seed, cfg.math_frac)
val_texts, val_prompts, val_answers = build_corpus(cfg.n_val, cfg.seed + 999, cfg.math_frac)
print(f"train: {len(train_texts)} texts | val: {len(val_texts)} texts ({len(val_prompts)} math)")

tok = CharTokenizer()
tok.train(train_texts)
print("special ids:", {s: tok.stoi[s] for s in tok.specials})

# length audit: everything must fit block_size (+ bos/eos)
lens = np.array([len(tok.encode(t)) for t in train_texts])
print(f"encoded len: mean {lens.mean():.0f} | max {lens.max()} | "
      f"limit {cfg.block_size + 1} | truncated: {(lens > cfg.block_size + 1).mean() * 100:.2f}%")
bad = sum(1 for t in train_texts if tok.unk_id in tok.encode(t))
print("train examples containing <unk>:", bad, "(expect 0)")

print("\n--- sample math ---")
print(next(t for t in train_texts if t.startswith("Q:")))
print("\n--- sample language ---")
print(next(t for t in train_texts if not t.startswith("Q:")))
