"""
eda_utils.py
Reusable plotting and statistical-testing helpers for the churn EDA.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from scipy import stats

sns.set_theme(style="whitegrid", palette="Set2")
CHURN_PALETTE = {0: "#4C72B0", 1: "#DD3B3B"}


def churn_rate_by(df: pd.DataFrame, column: str) -> pd.Series:
    """Return churn rate (%) grouped by a categorical column, sorted descending."""
    return (
        df.groupby(column, observed=True)["churned"]
        .mean()
        .mul(100)
        .sort_values(ascending=False)
        .round(2)
    )


def plot_churn_rate_by(df: pd.DataFrame, column: str, title: str, ax=None):
    """Bar plot of churn rate (%) by a categorical column."""
    rates = churn_rate_by(df, column)
    if ax is None:
        fig, ax = plt.subplots(figsize=(7, 4.5))
    sns.barplot(x=rates.index, y=rates.values, ax=ax, color="#E50914")
    ax.set_ylabel("Churn Rate (%)")
    ax.set_xlabel(column.replace("_", " ").title())
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.bar_label(ax.containers[0], fmt="%.1f%%")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    return ax


def plot_numeric_by_churn(df: pd.DataFrame, column: str, title: str):
    """Side-by-side KDE/box comparison of a numeric feature split by churn status."""
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

    sns.kdeplot(data=df, x=column, hue="churned", fill=True,
                palette=CHURN_PALETTE, common_norm=False, ax=axes[0])
    axes[0].set_title(f"Distribution of {column}", fontsize=11, fontweight="bold")

    sns.boxplot(data=df, x="churned", y=column, hue="churned",
                palette=CHURN_PALETTE, legend=False, ax=axes[1])
    axes[1].set_xticks([0, 1])
    axes[1].set_xticklabels(["Retained", "Churned"])
    axes[1].set_title(f"{column} by Churn Status", fontsize=11, fontweight="bold")

    fig.suptitle(title, fontsize=13, fontweight="bold")
    plt.tight_layout()
    return fig


def independent_ttest(df: pd.DataFrame, column: str):
    """Welch's t-test comparing `column` between churned and retained customers."""
    group0 = df.loc[df["churned"] == 0, column]
    group1 = df.loc[df["churned"] == 1, column]
    t_stat, p_val = stats.ttest_ind(group0, group1, equal_var=False)
    return {
        "feature": column,
        "mean_retained": round(group0.mean(), 3),
        "mean_churned": round(group1.mean(), 3),
        "t_stat": round(t_stat, 3),
        "p_value": p_val,
        "significant_at_0.05": p_val < 0.05,
    }


def chi_square_test(df: pd.DataFrame, column: str):
    """Chi-square test of independence between a categorical column and churn."""
    contingency = pd.crosstab(df[column], df["churned"])
    chi2, p_val, dof, _ = stats.chi2_contingency(contingency)
    return {
        "feature": column,
        "chi2": round(chi2, 3),
        "dof": dof,
        "p_value": p_val,
        "significant_at_0.05": p_val < 0.05,
    }
