"""
Compare models for predicting high-severity (high financial loss) incidents.

Business question: can we predict, from incident metadata, whether a new
incident is likely to be high-severity -- and which modeling approach is
most trustworthy for that call?

Approach: define "high severity" as the top quartile of financial loss,
then compare Logistic Regression, Random Forest, and Gradient Boosting
on F1-score for that class specifically (not overall accuracy, since the
high-severity class is the minority and the one that actually matters
operationally).
"""

import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import classification_report, f1_score
import matplotlib.pyplot as plt

CLEAN_PATH = Path("data/cleaned_incidents.csv")
OUTPUT_DIR = Path("output")

CATEGORICAL_FEATURES = ["target_industry", "attack_source", "country"]
NUMERIC_FEATURES = ["number_of_affected_users", "incident_resolution_time_in_hours"]


def build_target(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    threshold = df["financial_loss_in_million_"].quantile(0.75)
    df["high_severity"] = (df["financial_loss_in_million_"] >= threshold).astype(int)
    return df


def build_pipeline(model):
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
        ],
        remainder="passthrough",
    )
    return Pipeline(steps=[("preprocessor", preprocessor), ("model", model)])


def compare_models(df: pd.DataFrame) -> dict:
    features = CATEGORICAL_FEATURES + NUMERIC_FEATURES
    X = df[features]
    y = df["high_severity"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, stratify=y, test_size=0.2, random_state=42
    )

    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000),
        "Random Forest": RandomForestClassifier(n_estimators=200, random_state=42),
        "Gradient Boosting": GradientBoostingClassifier(random_state=42),
    }

    scores = {}
    for name, model in models.items():
        pipeline = build_pipeline(model)
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        scores[name] = f1_score(y_test, y_pred, pos_label=1)
        print(f"\n{name}")
        print(classification_report(y_test, y_pred))

    return scores


def plot_comparison(scores: dict, output_path: Path):
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(scores.keys(), scores.values(), color=["#4C9BE0", "#F0A73A", "#3AA76D"])
    for i, (name, score) in enumerate(scores.items()):
        ax.text(i, score + 0.01, f"{score:.2f}", ha="center")
    ax.set_title("F1-Score Comparison (High-Severity Class)")
    ax.set_ylabel("F1-Score")
    ax.set_ylim(0, 1)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    print(f"\nSaved comparison plot to {output_path}")


if __name__ == "__main__":
    df = pd.read_csv(CLEAN_PATH)
    df = build_target(df)
    scores = compare_models(df)

    OUTPUT_DIR.mkdir(exist_ok=True)
    plot_comparison(scores, OUTPUT_DIR / "severity_model_comparison.png")

    best = max(scores, key=scores.get)
    print(f"\nBest performer for high-severity detection: {best} (F1: {scores[best]:.2f})")
