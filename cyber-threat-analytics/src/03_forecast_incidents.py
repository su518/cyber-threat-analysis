"""
Forecast yearly incident volume.

Business question: is incident volume trending up, down, or flat, and
what should we plan for over the next few years?

Approach: Simple Exponential Smoothing (SES) on yearly incident counts.
SES is intentionally simple here -- it's transparent and easy to explain
to a non-technical stakeholder, at the cost of not capturing seasonality
or sudden shifts. That tradeoff is called out explicitly rather than
hidden behind a more complex model.
"""

import pandas as pd
from pathlib import Path
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
import matplotlib.pyplot as plt

CLEAN_PATH = Path("data/cleaned_incidents.csv")
OUTPUT_DIR = Path("output")
FORECAST_YEARS = 3


def build_yearly_counts(df: pd.DataFrame) -> pd.Series:
    counts = df.groupby("year").size()
    counts.index = pd.to_datetime(counts.index.astype(str) + "-12-31")
    counts = counts.asfreq("YE-DEC")
    return counts


def forecast(counts: pd.Series, periods: int = FORECAST_YEARS) -> pd.Series:
    model = SimpleExpSmoothing(counts, initialization_method="estimated").fit()
    forecast_values = model.forecast(periods)

    last_year = counts.index[-1].year
    forecast_values.index = pd.to_datetime(
        [f"{y}-12-31" for y in range(last_year + 1, last_year + 1 + periods)]
    )
    return forecast_values


def plot_forecast(actual: pd.Series, forecast_values: pd.Series, output_path: Path):
    # Bridge point so the forecast line connects visually to the actual line
    bridge = pd.Series([actual.iloc[-1]], index=[actual.index[-1]])
    forecast_with_bridge = pd.concat([bridge, forecast_values])

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(actual.index, actual.values, "o-", label="Actual")
    ax.plot(forecast_with_bridge.index, forecast_with_bridge.values, "o--", label="Forecast")
    ax.set_title("Cyber Incident Volume: Actual vs. Forecast (SES)")
    ax.set_xlabel("Year")
    ax.set_ylabel("Incident Count")
    ax.legend()
    ax.grid(True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    print(f"Saved forecast plot to {output_path}")


if __name__ == "__main__":
    df = pd.read_csv(CLEAN_PATH)
    yearly_counts = build_yearly_counts(df)
    forecast_values = forecast(yearly_counts)

    OUTPUT_DIR.mkdir(exist_ok=True)
    forecast_values.to_csv(OUTPUT_DIR / "incident_forecast.csv", header=["forecast_count"])
    plot_forecast(yearly_counts, forecast_values, OUTPUT_DIR / "incident_forecast.png")

    print("\nForecast (next 3 years):")
    print(forecast_values)
