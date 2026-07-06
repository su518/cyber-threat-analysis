"""
Data preparation for the Global Cybersecurity Threats dataset.

Loads the raw incident-level CSV, standardizes column names and types,
handles missing values, and writes a cleaned copy that every other
script in this project reads from. Keeping this as its own step means
the cleaning logic only lives in one place.
"""

import pandas as pd
from pathlib import Path

RAW_PATH = Path("data/Global_Cybersecurity_Threats_2015-2024.csv")
CLEAN_PATH = Path("data/cleaned_incidents.csv")


def load_and_clean(raw_path: Path = RAW_PATH) -> pd.DataFrame:
    df = pd.read_csv(raw_path)

    # Standardize column names: lowercase, no spaces
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
        .str.replace(r"[()$]", "", regex=True)
    )

    # Coerce the numeric columns that commonly arrive as strings/objects
    numeric_cols = [
        "year",
        "financial_loss_in_million_",
        "number_of_affected_users",
        "incident_resolution_time_in_hours",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop rows missing the fields the rest of the pipeline depends on
    required = [c for c in numeric_cols if c in df.columns] + [
        c for c in ["country", "target_industry", "attack_source"] if c in df.columns
    ]
    before = len(df)
    df = df.dropna(subset=required)
    dropped = before - len(df)

    print(f"Loaded {before:,} rows, dropped {dropped:,} incomplete rows, kept {len(df):,}.")

    return df


if __name__ == "__main__":
    cleaned = load_and_clean()
    CLEAN_PATH.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(CLEAN_PATH, index=False)
    print(f"Wrote cleaned data to {CLEAN_PATH}")
