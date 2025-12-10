import pandas as pd
from pathlib import Path
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from .config import FORECAST_FILE


def forecast_monthly_crime(monthly_df, horizon=6):
    """
    Forecast monthly crime counts using simple Holt-Winters.
    If fewer than 2 data points exist, skip forecasting.
    """

    # aggregate across all grid cells + crime types
    series = (
        monthly_df.groupby("month")["crime_count"]
        .sum()
        .sort_index()
    )

    print("[FORECAST DEBUG] Monthly series length:", len(series))
    print("[FORECAST DEBUG] Series:", series.to_dict())

    # SAFETY CHECK
    if len(series) < 2:
        print("\n[WARNING] Not enough months of data for forecasting.")
        print("Forecasting requires at least 2 months; skipping forecast.\n")

        # create empty placeholder
        forecast = pd.DataFrame({
            "month": [],
            "forecast": []
        })

        FORECAST_FILE.parent.mkdir(parents=True, exist_ok=True)
        forecast.to_parquet(FORECAST_FILE)

        return series, forecast, FORECAST_FILE

    # FIT MODEL
    model = ExponentialSmoothing(
        series,
        trend="add",
        seasonal=None
    ).fit()

    future_index = range(series.index.max() + 1, series.index.max() + horizon + 1)
    forecast_values = model.forecast(horizon)

    forecast = pd.DataFrame({
        "month": list(future_index),
        "forecast": forecast_values
    })

    FORECAST_FILE.parent.mkdir(parents=True, exist_ok=True)
    forecast.to_parquet(FORECAST_FILE)

    return series, forecast, FORECAST_FILE