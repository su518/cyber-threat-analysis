"""
Group industries by attack-pattern similarity.

Business question: which industries share a risk profile, so a security
team can identify their "peer group" and borrow defense strategies from
industries facing similar threats?

Approach: build a per-industry feature vector from attack-source and
attack-type frequencies, reduce to 2D with PCA for visualization, and
cluster with KMeans.
"""

import pandas as pd
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

CLEAN_PATH = Path("data/cleaned_incidents.csv")
OUTPUT_DIR = Path("output")
N_CLUSTERS = 4


def build_industry_features(df: pd.DataFrame) -> pd.DataFrame:
    """One row per industry, columns = share of incidents by attack source."""
    pivot = (
        df.groupby(["target_industry", "attack_source"])
        .size()
        .unstack(fill_value=0)
    )
    # Normalize to shares so industries with more total incidents aren't
    # just clustered together on volume alone
    pivot = pivot.div(pivot.sum(axis=1), axis=0)
    return pivot


def cluster_industries(features: pd.DataFrame, n_clusters: int = N_CLUSTERS):
    scaled = StandardScaler().fit_transform(features)

    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(scaled)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(scaled)

    result = pd.DataFrame(
        {
            "industry": features.index,
            "pca_1": coords[:, 0],
            "pca_2": coords[:, 1],
            "cluster": labels,
        }
    )
    return result


def plot_clusters(result: pd.DataFrame, output_path: Path):
    fig, ax = plt.subplots(figsize=(9, 6))
    scatter = ax.scatter(
        result["pca_1"], result["pca_2"], c=result["cluster"], cmap="tab10", s=80
    )
    for _, row in result.iterrows():
        ax.annotate(row["industry"], (row["pca_1"], row["pca_2"]), fontsize=8)
    ax.set_title("Industries Clustered by Attack-Pattern Similarity")
    ax.set_xlabel("PCA Component 1")
    ax.set_ylabel("PCA Component 2")
    ax.legend(*scatter.legend_elements(), title="Cluster")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    print(f"Saved cluster plot to {output_path}")


if __name__ == "__main__":
    df = pd.read_csv(CLEAN_PATH)
    features = build_industry_features(df)
    result = cluster_industries(features)

    OUTPUT_DIR.mkdir(exist_ok=True)
    result.to_csv(OUTPUT_DIR / "industry_clusters.csv", index=False)
    plot_clusters(result, OUTPUT_DIR / "industry_clusters.png")

    print("\nCluster membership:")
    print(result.sort_values("cluster").to_string(index=False))
