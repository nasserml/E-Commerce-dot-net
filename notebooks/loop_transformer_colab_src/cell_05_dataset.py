# ============================================================
# 4) PyTorch datasets: pad to block_size, shift labels, mask pads
# ============================================================
class LMData(torch.utils.data.Dataset):
    def __init__(self, texts, tok, block_size):
        self.rows = []
        for t in texts:
            ids = tok.encode(t)[:block_size + 1]
            if len(ids) < 2:
                continue
            x = ids[:-1]
            y = ids[1:]
            pad = block_size - len(x)
            x = x + [tok.pad_id] * pad
            y = y + [-100] * pad  # -100 = ignored by cross_entropy
            self.rows.append((torch.tensor(x), torch.tensor(y)))

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, i):
        return self.rows[i]


train_ds = LMData(train_texts, tok, cfg.block_size)
val_ds = LMData(val_texts, tok, cfg.block_size)
train_loader = torch.utils.data.DataLoader(
    train_ds, batch_size=cfg.batch_size, shuffle=True, drop_last=True,
    num_workers=2, pin_memory=True)
val_loader = torch.utils.data.DataLoader(
    val_ds, batch_size=cfg.batch_size, num_workers=2, pin_memory=True)
print(f"batches: {len(train_loader)} train / {len(val_loader)} val")

xb, yb = next(iter(train_loader))
print("x:", tuple(xb.shape), "y:", tuple(yb.shape),
      "| supervised tokens/batch:", int((yb != -100).sum()))
print("decode(x[0]):", tok.decode([i for i in xb[0].tolist() if i != tok.pad_id])[:120], "...")
