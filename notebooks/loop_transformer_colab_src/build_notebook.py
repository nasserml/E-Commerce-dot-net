"""Assemble Loop_Transformer_Small_LLM_Colab.ipynb from the cell_* sources.

Usage:
    python build_notebook.py
"""
import glob
import json
import os
import uuid

SRC = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(SRC), "Loop_Transformer_Small_LLM_Colab.ipynb")


def main():
    cells = []
    for path in sorted(glob.glob(os.path.join(SRC, "cell_*"))):
        with open(path, encoding="utf-8") as f:
            src = f.read()
        if not src.endswith("\n"):
            src += "\n"
        kind = "markdown" if path.endswith(".md") else "code"
        cell = {
            "id": uuid.uuid4().hex[:8],
            "metadata": {},
            "source": src.splitlines(keepends=True),
        }
        if kind == "code":
            cell.update({"cell_type": "code", "execution_count": None, "outputs": []})
        else:
            cell.update({"cell_type": "markdown"})
        cells.append(cell)
        print(f"+ {os.path.basename(path)} ({kind}, {len(src.splitlines())} lines)")

    nb = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.10"},
        },
        "cells": cells,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(f"\nwrote {OUT} ({len(cells)} cells)")


if __name__ == "__main__":
    main()
