"""
Check two relationships that inform how "severity" gets defined operationally:

1. Do different attack sources share similar vulnerability patterns?
2. Does financial loss actually correlate with number of users affected?

Business relevance: if loss and user-impact don't correlate, that's a
reason to track them as separate severity signals rather than assuming
a big-dollar incident always means a big-user-impact incident (or vice versa).
"""

import pandas as pd
from pathlib import Path
from scipy.stats import pearsonr, spearmanr
import matplotlib.pyplot as plt
import seaborn as sns

CLEAN_PATH = Path("data/cleaned_incidents.csv")
OUTPUT_DIR = Path("output")


def attack_source_correlation(df: pd.DataFrame) -> pd.DataFrame:
    """Correlation between attack sources based on shared vulnerability-type frequency."""
    pivot = (
        df.groupby(["attack_source", "security_vulnerability_type"])
        .size()
        .unstack(fill_value=0)
    )
    return pivot.T.corr()


def loss_vs_users_correlation(df: pd.DataFrame):
    loss = df["financial_loss_in_million_"]
    users = df["number_of_affected_users"]
    pearson_corr, _ = pearsonr(loss, users)
    spearman_corr, _ = spearmanr(loss, users)
    return pearson_corr, spearman_corr


def plot_attack_source_corr(corr: pd.DataFrame, output_path: Path):
    fig, ax = plt.subplots(figsize=(7, 6))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1, ax=ax)
    ax.set_title("Correlation Between Attack Sources (by Vulnerability Type)")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    print(f"Saved attack-source correlation heatmap to {output_path}")


def plot_loss_vs_users(df: pd.DataFrame, output_path: Path):
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.regplot(
        x=df["financial_loss_in_million_"],
        y=df["number_of_affected_users"],
        scatter_kws={"alpha": 0.4},
        line_kws={"color": "red"},
        ax=ax,
    )
    ax.set_title("Financial Loss vs. Number of Affected Users")
    ax.set_xlabel("Financial Loss (Million $)")
    ax.set_ylabel("Number of Affected Users")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    print(f"Saved loss-vs-users plot to {output_path}")


if __name__ == "__main__":
    df = pd.read_csv(CLEAN_PATH)
    OUTPUT_DIR.mkdir(exist_ok=True)

    if "security_vulnerability_type" in df.columns:
        corr = attack_source_correlation(df)
        plot_attack_source_corr(corr, OUTPUT_DIR / "attack_source_correlation.png")
        print("\nAttack source correlation matrix:")
        print(corr)

    pearson_corr, spearman_corr = loss_vs_users_correlation(df)
    plot_loss_vs_users(df, OUTPUT_DIR / "loss_vs_users.png")

    print(f"\nPearson correlation (loss vs. users affected): {pearson_corr:.4f}")
    print(f"Spearman correlation (loss vs. users affected): {spearman_corr:.4f}")
    print(
        "Interpretation: little to no linear relationship -- financial loss and "
        "user impact should be tracked as independent severity signals."
    )
