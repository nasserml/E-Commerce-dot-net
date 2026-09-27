# ============================================================
# 11) Save everything, download, (optional) push to Hugging Face
# ============================================================
torch.save({"step": cfg.total_steps, "model": model.state_dict(),
            "opt": optimizer.state_dict(), "cfg": asdict(cfg),
            "stoi": tok.stoi}, "loop_llm_final.pt")
tok.save("loop_tok.json")
print("saved loop_llm_final.pt + loop_tok.json")

# Download to your laptop (Colab only)
try:
    from google.colab import files
    files.download("loop_llm_final.pt")
    files.download("loop_tok.json")
    print("downloads started")
except Exception as e:
    print("not on Colab (or download blocked):", e)

# --- Reload later (any machine with torch + the class definitions above) ---
print("""
# ckpt = torch.load("loop_llm_final.pt", map_location="cpu", weights_only=False)
# cfg  = Config(**ckpt["cfg"])
# tok  = CharTokenizer(); tok.stoi = ckpt["stoi"]; tok.itos = {i: s for s, i in tok.stoi.items()}
# model = LoopTransformerLM(cfg, len(tok.stoi)); model.load_state_dict(ckpt["model"]); model.eval()
""")

# --- Optional: push to Hugging Face Hub ---
# !pip install -q huggingface_hub
# from huggingface_hub import HfApi
# HfApi().create_repo("loop-transformer-tiny", exist_ok=True)
# HfApi().upload_file("loop_llm_final.pt", path_in_repo="loop_llm_final.pt",
#                     repo_id="<your-username>/loop-transformer-tiny")
