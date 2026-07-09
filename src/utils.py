# utils.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats


def summarise_model_scores(df, score_field="strict_score"):
    df_summary = df.groupby("model")[score_field].mean().reset_index()
    df_summary = df_summary.rename(columns={score_field: "mean_score"})
    df_summary = df_summary.sort_values("mean_score", ascending=True).reset_index(drop=True)
    return df_summary


def prediction_interval(samples, confidence=0.95):
    mean = np.mean(samples)
    n = len(samples)
    std_dev = np.std(samples, ddof=1)
    t_crit = stats.t.ppf((1 + confidence) / 2, df=n - 1)
    margin_of_error = t_crit * std_dev * np.sqrt(2 / n)
    return margin_of_error


def plot_model_scores(
    df,
    title="",
    ax=None,
    hide_yticks=False,
    guess=False,
    score_field="strict_score",
    xlabel="Accuracy",
    abbreviate=False,
    fontsize=16,
):
    created_fig = False
    if ax is None:
        fig, ax = plt.subplots(figsize=(12, 12))
        created_fig = True

    ax.margins(y=0.02)

    df = df.groupby(["model", "repeat"])[score_field].mean().reset_index()

    df = (
        df.groupby("model")
        .agg(
            mean=(score_field, "mean"),
            interval=(score_field, prediction_interval),
            n=(score_field, "count"),
        )
        .reset_index()
        .sort_values("mean", ascending=True)
    )

    abbreviations = {
        "ollama-phi4-reasoning-14b": "phi4",
        "deepseek-r1-distill-qwen-14b": "deepseek-r1-14b",
        "azure-gpt-45-preview-2025-02-07": "gpt-45-preview",
        "openai-gpt-5-2-high": "gpt-5.2-high",
    }

    if abbreviate:
        df["model"] = df["model"].str.replace(r"^.*/", "", regex=True)
        df["model"] = df["model"].replace(abbreviations)

    bars = ax.barh(df["model"], df["mean"], capsize=5, alpha=0.7)

    ax.set_xlabel(xlabel, fontsize=fontsize)
    ax.set_xlim(0, 1.0)
    ax.set_title(title, fontsize=fontsize)
    ax.tick_params(axis="both", which="major", labelsize=fontsize)

    if hide_yticks:
        ax.set_yticklabels([])

    split = 0.5

    for bar, model, mean, interval, n in zip(
        bars, df["model"], df["mean"], df["interval"], df["n"]
    ):
        ax.text(
            mean - 0.03 if mean > split else mean + 0.03,
            bar.get_y() + bar.get_height() / 2,
            f"{mean:.2f} ± {interval:.3f} (n={n})" if n > 1 else f"{mean:.2f}",
            ha="right" if mean > split else "left",
            va="center",
            fontsize=fontsize - 6,
        )

    if guess:
        ax.axvline(x=guess, color="red", linestyle="dotted", linewidth=2)

    if created_fig:
        return fig, ax
