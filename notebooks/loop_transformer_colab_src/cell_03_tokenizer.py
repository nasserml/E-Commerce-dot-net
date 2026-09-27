# ============================================================
# 2) Tokenizer from scratch (character-level + special tokens)
#    Char-level is ideal here: tiny vocab, great for arithmetic,
#    zero dependencies, trains in milliseconds.
# ============================================================
class CharTokenizer:
    def __init__(self):
        self.specials = ["<pad>", "<unk>", "<bos>", "<eos>",
                         "<think>", "</think>", "<answer>", "</answer>"]
        self.stoi, self.itos = {}, {}
        self._spec_sorted = sorted(self.specials, key=len, reverse=True)

    def train(self, texts):
        chars = sorted(set("".join(texts)))
        chars = [c for c in chars if c not in "<>"]  # <> reserved for specials
        vocab = self.specials + chars
        self.stoi = {t: i for i, t in enumerate(vocab)}
        self.itos = {i: t for t, i in self.stoi.items()}
        print(f"vocab size: {len(vocab)} ({len(self.specials)} specials + {len(chars)} chars)")

    def encode(self, s, add_bos=True, add_eos=True):
        ids = []
        i = 0
        while i < len(s):
            hit = None
            if s[i] == "<":  # all specials start with '<'
                for sp in self._spec_sorted:  # longest match first
                    if s.startswith(sp, i):
                        hit = sp
                        break
            if hit is not None:
                ids.append(self.stoi[hit])
                i += len(hit)
            else:
                ids.append(self.stoi.get(s[i], self.unk_id))
                i += 1
        if add_bos:
            ids = [self.bos_id] + ids
        if add_eos:
            ids = ids + [self.eos_id]
        return ids

    def decode(self, ids):
        return "".join(self.itos.get(i, "<unk>") for i in ids)

    @property
    def pad_id(self): return self.stoi["<pad>"]

    @property
    def unk_id(self): return self.stoi["<unk>"]

    @property
    def bos_id(self): return self.stoi["<bos>"]

    @property
    def eos_id(self): return self.stoi["<eos>"]

    def save(self, path):
        with open(path, "w") as f:
            json.dump({"stoi": self.stoi}, f)

    @classmethod
    def load(cls, path):
        t = cls()
        with open(path) as f:
            t.stoi = json.load(f)["stoi"]
        t.itos = {i: s for s, i in t.stoi.items()}
        return t


# tiny self-test (the real vocab is trained on the dataset in §3)
_t = CharTokenizer()
_t.train(["Q: 1+2=?\n<think>ones: 1+2+0=3.</think>\n<answer>3</answer>"])
_s = "Q: 1+2=?\n<think>ones: 1+2+0=3.</think>\n<answer>3</answer>"
assert _t.decode(_t.encode(_s)) == "<bos>" + _s + "<eos>", "roundtrip failed"
print("tokenizer roundtrip OK | first ids:", _t.encode(_s)[:10])
