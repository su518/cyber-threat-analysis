"""
Flag incidents worth escalating first.

Business question: out of thousands of logged incidents, which ones
should a security team look at first?

Approach: Isolation Forest on financial loss, users affected, and
resolution time. This is unsupervised on purpose -- there's no labeled
"this incident mattered" column in the raw data, so the model looks for
incidents that are structurally unusual across all three signals at once,
rather than just sorting by a single column.
"""

import pandas as pd
from pathlib import Path
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt

CLEAN_PATH = Path("data/cleaned_incidents.csv")
OUTPUT_DIR = Path("output")
CONTAMINATION = 0.05  # expected share of incidents flagged as anomalous


def flag_anomalies(df: pd.DataFrame, contamination: float = CONTAMINATION) -> pd.DataFrame:
    features = df[
        [
            "financial_loss_in_million_",
            "number_of_affected_users",
            "incident_resolution_time_in_hours",
        ]
    ]

    model = IsolationForest(contamination=contamination, random_state=42)
    df = df.copy()
    df["is_anomaly"] = (model.fit_predict(features) == -1).astype(int)
    return df


def plot_anomalies(df: pd.DataFrame, output_path: Path):
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.scatter(range(len(df)), df["is_anomaly"], c=df["is_anomaly"], cmap="coolwarm", s=10)
    ax.set_title("Flagged Incidents: Early-Stage Escalation Candidates")
    ax.set_xlabel("Incident Index")
    ax.set_ylabel("Flagged (1) / Not Flagged (0)")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    print(f"Saved anomaly plot to {output_path}")


if __name__ == "__main__":
    df = pd.read_csv(CLEAN_PATH)
    flagged = flag_anomalies(df)

    n_flagged = flagged["is_anomaly"].sum()
    print(f"Flagged {n_flagged:,} of {len(flagged):,} incidents ({n_flagged / len(flagged):.1%})")

    OUTPUT_DIR.mkdir(exist_ok=True)
    top_flagged = flagged[flagged["is_anomaly"] == 1].sort_values(
        "financial_loss_in_million_", ascending=False
    )
    top_flagged.head(10).to_csv(OUTPUT_DIR / "top_flagged_incidents.csv", index=False)
    plot_anomalies(flagged, OUTPUT_DIR / "anomaly_flags.png")

    print("\nTop 5 flagged incidents by financial loss:")
    print(
        top_flagged[
            ["country", "year", "target_industry", "financial_loss_in_million_", "number_of_affected_users"]
        ].head()
    )
