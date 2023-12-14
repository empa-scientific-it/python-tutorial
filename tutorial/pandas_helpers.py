"""Miscellaneous visual aids"""

import matplotlib.pyplot as plt
import pandas as pd


def low_med_high_bins_viz(data, column, ylabel, title, figsize=(15, 3)):
    """Visualize the low, medium, and high equal-width bins."""
    ax = data.plot(y=column, figsize=figsize, color="black", title=title)

    xlims = ax.get_xlim()

    for bin_name, hatch, bounds in zip(
        ["low", "med", "high"],
        ["///", "", "\\\\\\"],
        pd.cut(data[column], bins=3).unique().categories.values,
    ):
        plt.axhspan(
            bounds.left,
            bounds.right,
            alpha=0.2,
            label=bin_name,
            hatch=hatch,
            color="black",
        )
        plt.annotate(
            f"  {bin_name}",
            xy=(xlims[0], (bounds.left + bounds.right) / 2.1),
            ha="left",
        )

    ax.set(xlabel="", ylabel=ylabel)
    plt.legend(bbox_to_anchor=(1, 0.75), frameon=False)

    return ax


def quartile_bins_viz(data, column, ylabel, title, figsize=(15, 8)):
    """Visualize quartile bins."""
    ax = data.plot(y=column, figsize=figsize, color="black", title=title)

    xlims = ax.get_xlim()

    for bin_name, hatch, bounds in zip(
        [r"$Q_1$", r"$Q_2$", r"$Q_3$", r"$Q_4$"],
        ["\\\\\\", "", "///", "||||"],
        pd.qcut(data.volume, q=4).unique().categories.values,
    ):
        plt.axhspan(
            bounds.left,
            bounds.right,
            alpha=0.2,
            label=bin_name,
            hatch=hatch,
            color="black",
        )
        plt.annotate(
            f"  {bin_name}",
            xy=(xlims[0], (bounds.left + bounds.right) / 2.1),
            fontsize=11,
        )

    ax.set(xlabel="", ylabel=ylabel)
    plt.legend(bbox_to_anchor=(1, 0.67), frameon=False, fontsize=14)

    return ax
