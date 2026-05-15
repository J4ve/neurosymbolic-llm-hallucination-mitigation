"""Generate figures for the final paper and poster.

Outputs (in ../figures/):
    fig_hallucination.{pdf,png}   - bar chart of hallucination rates
    fig_confusion.{pdf,png}       - 3 confusion matrix heatmaps
    fig_perclass_f1.{pdf,png}     - per-class F1 grouped bar chart

Hardcodes the final metric values (from results/all_metrics.json) so the
plot script does not need access to the predictions to re-run.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


OUT = Path(__file__).resolve().parent.parent / "figures"
OUT.mkdir(parents=True, exist_ok=True)

SYSTEMS = ["Vanilla", "CoT", "Ours\n(Few-shot + Z3)"]
COLORS = ["#7A8FA6", "#5B7796", "#E8A33D"]  # neutral, neutral, amber for ours

# Hallucination rate (Tab. 2) — fraction of 400 ill-defined problems
# returned with a confident numeric answer.
HALL = [19.25, 21.00, 2.00]

# Per-class F1 (Tab. 1).
F1_SOLVABLE = [0.798, 0.822, 0.100]
F1_MISSING  = [0.623, 0.625, 0.500]
F1_CONTRA   = [0.000, 0.000, 0.029]

# Confusion (Tab. 4). Rows = gold, cols = pred (Solvable, Missing, Contra).
CONF = {
    "Vanilla": np.array([[184, 16,  0],
                         [ 32, 168, 0],
                         [ 45, 155, 0]]),
    "CoT":     np.array([[198,  2,  0],
                         [ 38, 162, 0],
                         [ 46, 154, 0]]),
    "Ours":    np.array([[ 11, 189, 0],
                         [  4, 194, 2],
                         [  4, 193, 3]]),
}

CLASS_LABELS = ["Solv", "Miss", "Contra"]


def fig_hallucination():
    fig, ax = plt.subplots(figsize=(5.0, 3.4))
    bars = ax.bar(SYSTEMS, HALL, color=COLORS, edgecolor="black", linewidth=0.8)
    ax.set_ylabel("Hallucination rate (\\%)", fontsize=11)
    ax.set_title("Confident wrong answers on ill-defined problems\n(out of 400)",
                 fontsize=11)
    ax.set_ylim(0, 26)
    for b, v in zip(bars, HALL):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.6, f"{v:.2f}%",
                ha="center", va="bottom", fontsize=11, fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="x", labelsize=10)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"fig_hallucination.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)


def fig_perclass_f1():
    classes = ["Solvable", "Missing", "Contra"]
    values = {
        "Vanilla":            [F1_SOLVABLE[0], F1_MISSING[0], F1_CONTRA[0]],
        "CoT":                [F1_SOLVABLE[1], F1_MISSING[1], F1_CONTRA[1]],
        "Ours (Few-shot+Z3)": [F1_SOLVABLE[2], F1_MISSING[2], F1_CONTRA[2]],
    }

    x = np.arange(len(classes))
    width = 0.27
    fig, ax = plt.subplots(figsize=(6.0, 3.6))
    for i, (name, vals) in enumerate(values.items()):
        offset = (i - 1) * width
        bars = ax.bar(x + offset, vals, width, label=name,
                      color=COLORS[i], edgecolor="black", linewidth=0.6)
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, v + 0.01, f"{v:.2f}",
                    ha="center", va="bottom", fontsize=8)

    ax.set_xticks(x)
    ax.set_xticklabels(classes, fontsize=10)
    ax.set_ylabel("F1", fontsize=11)
    ax.set_ylim(0, 1.0)
    ax.set_title("Per-class F1 by system", fontsize=11)
    ax.legend(loc="upper right", fontsize=9, frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"fig_perclass_f1.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)


def fig_confusion():
    fig, axes = plt.subplots(1, 3, figsize=(8.5, 3.0))
    vmax = max(int(m.max()) for m in CONF.values())
    cmap = plt.cm.Blues

    for ax, (name, m) in zip(axes, CONF.items()):
        im = ax.imshow(m, cmap=cmap, vmin=0, vmax=vmax)
        ax.set_title(name, fontsize=11)
        ax.set_xticks(range(3))
        ax.set_yticks(range(3))
        ax.set_xticklabels(CLASS_LABELS, fontsize=9)
        ax.set_yticklabels(CLASS_LABELS, fontsize=9)
        ax.set_xlabel("Predicted", fontsize=10)
        if ax is axes[0]:
            ax.set_ylabel("Gold", fontsize=10)
        for i in range(3):
            for j in range(3):
                v = m[i, j]
                color = "white" if v > vmax * 0.55 else "black"
                ax.text(j, i, str(v), ha="center", va="center",
                        color=color, fontsize=10, fontweight="bold")

    fig.suptitle("Confusion matrices (rows: gold, cols: predicted)",
                 fontsize=11, y=1.02)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"fig_confusion.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)


def main():
    fig_hallucination()
    fig_perclass_f1()
    fig_confusion()
    print(f"Wrote 6 files to {OUT}/")


if __name__ == "__main__":
    main()
