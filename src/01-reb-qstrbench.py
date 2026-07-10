#!/usr/bin/env python3
"""QSTRBench: overall bake-off and accuracy-by-calculus figures."""

import seaborn as sns

from utils import *

RESULTS_PATH = "../data/interim/QSTRBench/results.pkl"
FIGURES_DIR = "../reports/figures"


def load_results(path=RESULTS_PATH):
    """Load the merged questions/answers dataframe produced by bin/process.py."""
    return pd.read_pickle(path)


def get_model_parameters(yaml_file_path):
    import yaml

    with open(yaml_file_path, "r") as f:
        data = yaml.safe_load(f)

    models_with_params = [
        {"model": entry["model"], "parameters": entry["parameters"]}
        for entry in data.get("models", [])
        if "parameters" in entry
    ]

    return pd.DataFrame(models_with_params)


def compute_bake_off_table(df):
    """Per-model total/average strict score, with a column per repeat."""
    result = (
        df.groupby("model")
        .agg(
            total_score=("strict_score", "sum"),
            count=("strict_score", "count"),
        )
        .reset_index()
    )

    repeat_totals = (
        df.groupby(["model", "repeat"])["strict_score"]
        .sum()
        .unstack(fill_value=0)  # wide format: columns = Repeat values
        .add_prefix("repeat")  # rename columns -> repeat1, repeat2...
        .reset_index()
    )

    result = result.merge(repeat_totals, on="model", how="left")
    result["avg_score"] = result["total_score"] / result["count"]
    result = result.sort_values(by="avg_score", ascending=False)

    return result


def summarise_group(sub_df, model_order, score_field="strict_score"):
    per_repeat = sub_df.groupby(["model", "repeat"])[score_field].mean().reset_index()
    stats_df = per_repeat.groupby("model").agg(
        mean=(score_field, "mean"),
        interval=(score_field, prediction_interval),
        n=(score_field, "count"),
    )
    return stats_df.reindex(model_order)


def plot_overall_bakeoff(df, mean_guess_rate, output_path=f"{FIGURES_DIR}/bake-off-strict.pdf"):
    """Single horizontal bar chart of accuracy across all models."""
    plot_model_scores(df, guess=mean_guess_rate, xlabel="Accuracy")
    plt.tight_layout()
    plt.savefig(output_path, format="pdf")


def plot_bakeoff_by_type_grid(df, output_path=f"{FIGURES_DIR}/bake-off-strict-by-type.pdf"):
    """2x2 grid of accuracy charts split by question TYPE (Converse/CT/CN/Combined)."""
    dfs = [
        df[df["TYPE"] == "converse"],
        df[df["TYPE"] == "ct"],
        df[df["TYPE"] == "cn"],
        df,
    ]

    guesses = [
        df[df["TYPE"] == "converse"]["guess_rate"].mean(),
        df[df["TYPE"] == "ct"]["guess_rate"].mean(),
        df[df["TYPE"] == "cn"]["guess_rate"].mean(),
        df["guess_rate"].mean(),
    ]
    print(guesses)

    titles = ["Converse", "CT", "CN", "Combined"]
    fig, axes = plt.subplots(2, 2, figsize=(14, 16))
    axes = axes.flatten()

    for ax, sub_df, guess, title in zip(axes, dfs, guesses, titles):
        plot_model_scores(sub_df, guess=guess, xlabel=None, ax=ax, title=title, abbreviate=True)

    plt.tight_layout()
    plt.savefig(output_path, format="pdf")


def plot_accuracy_by_calculus(df, model_order, output_path=f"{FIGURES_DIR}/accuracy-by-model-by-calculus.pdf"):
    """Heatmap of mean strict score per model per calculus. Returns the sorted score matrix."""
    mean_scores = df.groupby(["model", "CALCULUS"])["strict_score"].mean().unstack()
    print(mean_scores)

    mean_scores_sorted = mean_scores.loc[model_order]
    mean_scores_sorted = mean_scores_sorted.loc[
        :, mean_scores_sorted.sum(axis=0).sort_values(ascending=True).index
    ]

    plt.figure(figsize=(12, 8))
    sns.heatmap(mean_scores_sorted, annot=True, fmt=".2f", cmap="viridis", cbar_kws={"label": "Accuracy"})

    plt.xlabel("Calculus", fontsize=12)
    plt.ylabel("Model", fontsize=12)

    plt.tight_layout()
    plt.savefig(output_path, format="pdf")

    return mean_scores_sorted


def plot_accuracy_by_calculus_extended(
    df,
    model_order,
    mean_scores_sorted,
    output_path=f"{FIGURES_DIR}/accuracy-by-model-by-calculus-extended.pdf",
):
    """Extended heatmap: per-calculus accuracy plus Converse/CT/CN/Combined summary columns."""
    groups = {
        "Converse": df[df["TYPE"] == "converse"],
        "CT": df[df["TYPE"] == "ct"],
        "CN": df[df["TYPE"] == "cn"],
        "Combined": df,
    }

    extra_values = {}
    extra_annot = {}
    for name, gdf in groups.items():
        stats_df = summarise_group(gdf, model_order)
        extra_values[name] = stats_df["mean"]
        extra_annot[name] = stats_df.apply(
            lambda r: (
                f"{r['mean']:.2f} ± {r['interval']:.3f} (n={int(r['n'])})"
                if r["n"] > 1
                else f"{r['mean']:.2f}"
            ),
            axis=1,
        )

    extra_values_df = pd.DataFrame(extra_values)
    extra_annot_df = pd.DataFrame(extra_annot)

    calculus_annot_df = mean_scores_sorted.map(lambda x: f"{x:.2f}")

    combined_values = pd.concat([mean_scores_sorted, extra_values_df], axis=1)
    combined_annot = pd.concat([calculus_annot_df, extra_annot_df], axis=1)

    font_size = 12

    left_values = combined_values.iloc[:, :-4]
    right_values = combined_values.iloc[:, -4:]

    left_annot = combined_annot.iloc[:, :-4]
    right_annot = combined_annot.iloc[:, -4:]

    fig, (ax1, ax2) = plt.subplots(
        1,
        2,
        figsize=(22, 10),
        sharey=True,
        gridspec_kw={
            "width_ratios": [9, 12],  # make the summary columns wider
            "wspace": 0.02,
        },
    )

    # Left heatmap (calculus columns)
    sns.heatmap(
        left_values,
        annot=left_annot,
        fmt="",
        cmap="viridis",
        cbar=False,
        annot_kws={"fontsize": font_size},
        ax=ax1,
    )

    # Right heatmap (summary columns)
    sns.heatmap(
        right_values,
        annot=right_annot,
        fmt="",
        cmap="viridis",
        cbar_kws={"label": "Accuracy"},
        annot_kws={"fontsize": font_size},
        ax=ax2,
    )

    ax1.set_xlabel("")
    ax2.set_xlabel("")
    ax1.set_ylabel("Model", fontsize=12)
    ax2.set_ylabel("")

    # Show model names only on the left
    ax1.set_yticks(np.arange(len(left_values.index)) + 0.5)
    ax1.set_yticklabels(left_values.index, rotation=0, fontsize=10)

    ax2.tick_params(axis="y", left=False, labelleft=False)

    plt.tight_layout()
    plt.savefig(output_path, format="pdf", bbox_inches="tight", pad_inches=0.02)


def compute_perfect_score_counts(df, score_field="strict_score"):
    """Per calculus, count how many models score a perfect 1.0 (all questions, all repeats correct)."""
    per_model = df.groupby(["CALCULUS", "model"])[score_field].mean().reset_index()
    per_model["is_perfect"] = per_model[score_field] == 1.0

    n_models = df["model"].nunique()
    counts = per_model.groupby("CALCULUS")["is_perfect"].sum().sort_values(ascending=False)
    counts = counts.rename("perfect_models").to_frame()
    counts["n_models"] = n_models
    counts["n_questions"] = df.groupby("CALCULUS")["id"].nunique().reindex(counts.index)

    return counts


def report_easiest_calculus(df):
    """Check the paper's claim that PA is the easiest calculus (most models with a perfect score)."""
    counts = compute_perfect_score_counts(df)
    print(counts.to_string())

    easiest = counts.index[0]
    top = counts.iloc[0]
    print(
        f"Easiest calculus is {easiest}: {int(top['perfect_models'])}/{int(top['n_models'])} models "
        f"answer all {int(top['n_questions'])} questions correctly"
    )

    return counts


def report_perfect_by_type(df, type_value, type_label):
    """Print perfect-score model counts by calculus, restricted to one question TYPE."""
    type_df = df[df["TYPE"] == type_value]
    counts = compute_perfect_score_counts(type_df)
    print(f"\nPerfect-score models on {type_label} questions, by calculus:")
    print(counts.to_string())
    return counts


def report_converse_by_calculus(df):
    """Check the paper's claim that Converse is better handled for IA than INDU
    (originally: IA 22/33 models perfect vs INDU 15/33)."""
    counts = report_perfect_by_type(df, "converse", "Converse")

    ia = counts.loc["IA"]
    indu = counts.loc["INDU"]
    print(
        f"Converse: IA {int(ia['perfect_models'])}/{int(ia['n_models'])} models perfect vs "
        f"INDU {int(indu['perfect_models'])}/{int(indu['n_models'])} models perfect"
    )

    return counts


def report_cn_by_calculus(df):
    """Print perfect-score model counts by calculus for Conceptual Neighbourhood (CN) questions."""
    return report_perfect_by_type(df, "cn", "Conceptual Neighbourhood (CN)")


def report_ct_by_calculus(df):
    """Print perfect-score model counts by calculus for Composition Table (CT) questions."""
    return report_perfect_by_type(df, "ct", "Composition Table (CT)")


def compute_calculus_by_type_table(df, score_field="strict_score"):
    """Mean score by calculus x question TYPE (Converse/CT/CN), aggregated across all models."""
    table = df.groupby(["CALCULUS", "TYPE"])[score_field].mean().unstack()
    table = table.reindex(columns=["converse", "ct", "cn"])
    table.columns = ["Converse", "CT", "CN"]
    table["Combined"] = df.groupby("CALCULUS")[score_field].mean()
    table = table.sort_values("Combined", ascending=False)
    return table


def report_calculus_by_type(df):
    """Print mean accuracy by calculus x question type, across all models."""
    table = compute_calculus_by_type_table(df)
    print(table.to_string(float_format="%.2f"))
    return table


def main():
    df = load_results()
    print(len(df))
    print("Total number of models tested:", df["model"].nunique())

    result = compute_bake_off_table(df)
    print(result.to_string())
    print(result["model"].nunique())
    print("The best performing model is", result["model"].iloc[0])

    mean_guess_rate = df["guess_rate"].mean()
    print("Mean guess rate:", mean_guess_rate)

    report_easiest_calculus(df)
    report_calculus_by_type(df)
    report_converse_by_calculus(df)
    report_cn_by_calculus(df)
    report_ct_by_calculus(df)

    model_order = result["model"].tolist()

    plot_overall_bakeoff(df, mean_guess_rate)
    plot_bakeoff_by_type_grid(df)
    mean_scores_sorted = plot_accuracy_by_calculus(df, model_order)
    plot_accuracy_by_calculus_extended(df, model_order, mean_scores_sorted)


if __name__ == "__main__":
    main()
