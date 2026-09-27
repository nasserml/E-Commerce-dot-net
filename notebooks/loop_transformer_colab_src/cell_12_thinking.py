# ============================================================
# 10) Thinking at test time: more loops = more compute, same params
#     (model was trained with n_loops=4; max_loops=8 allows scaling)
# ============================================================
print("Sweeping inference loops:")
for L in [1, 2, 4, 6, 8]:
    acc = eval_accuracy(n=100, n_loops=L)
    print(f"  n_loops={L}: think-answer acc = {acc * 100:5.1f}%", flush=True)

print("\nSame question, loops=1 vs loops=8 (greedy):")
sample_show(["Q: 68+27=?\n<think>"], n_loops=1)
sample_show(["Q: 68+27=?\n<think>"], n_loops=8)

print("\nNo-think baseline (direct answer — a format never seen in training):")
sample_show(["Q: 68+27=?\n<answer>"], n_loops=4, max_new_tokens=12)
