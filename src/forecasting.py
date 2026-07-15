"""
forecasting.py
Forecasts Access (ACC_OWNERSHIP) and Usage (USG_DIGITAL_PAYMENT) for 2025-2027.

Two layers, matching the brief's required approach:
  1. Baseline trend: linear regression on the 5 Findex survey points (2011-2024).
  2. Event-augmented: baseline + the sum of modeled event effects (event_impact.py)
     active by each forecast date.

Scenarios (optimistic/base/pessimistic) scale the *event* contribution only
(0.5x / 1.0x / 1.5x), since the trend itself is the least uncertain part and
the events are where the real forecasting risk sits (see impact_links_methodology.md).
Confidence intervals widen with forecast horizon (a standard, simple
heuristic given only 5 historical data points -- not a fitted prediction
interval, and documented as such).
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from data_loader import load_unified_data, get_indicator_series
from event_impact import event_effect_at

FORECAST_YEARS = [2025, 2026, 2027]
SCENARIO_MULTIPLIERS = {"pessimistic": 0.5, "base": 1.0, "optimistic": 1.5}


def fit_trend(series: pd.DataFrame) -> tuple[float, float, bool]:
    """
    OLS fit of value on year. Returns (slope, intercept, is_fallback).
    With fewer than 2 points a trend cannot be estimated from this indicator's
    own history; falls back to a flat line (slope=0) anchored on the single
    known value, and flags is_fallback=True so callers can surface the caveat.
    """
    x = series["observation_date"].dt.year.values.astype(float)
    y = series["value_numeric"].values.astype(float)
    if len(x) < 2:
        return 0.0, float(y[0]) if len(y) else 0.0, True
    slope, intercept = np.polyfit(x, y, 1)
    return slope, intercept, False


def forecast_indicator(df: pd.DataFrame, indicator_code: str) -> pd.DataFrame:
    series = get_indicator_series(df, indicator_code)
    slope, intercept, is_fallback = fit_trend(series)
    last_year = series["observation_date"].dt.year.max()
    last_obs_date = series["observation_date"].max()

    # Events that occurred before the last observation are already baked into
    # that observed value (and, for multi-point series, into the trend fit).
    # Only the effect accrued AFTER the last observation should be added --
    # otherwise Telebirr/M-Pesa's historical impact gets counted twice.
    baseline_event_effect = event_effect_at(df, indicator_code, last_obs_date)

    rows = []
    for year in FORECAST_YEARS:
        as_of = pd.Timestamp(year=year, month=12, day=31)
        trend_value = slope * year + intercept
        cumulative_event_effect = event_effect_at(df, indicator_code, as_of)
        incremental_event_effect = cumulative_event_effect - baseline_event_effect
        horizon = year - last_year
        # wider CI when the baseline itself is a single-point fallback --
        # there's no historical trend to anchor uncertainty against
        ci_width = (3.0 if is_fallback else 1.5) * horizon

        for scenario, mult in SCENARIO_MULTIPLIERS.items():
            point = trend_value + incremental_event_effect * mult
            rows.append({
                "indicator_code": indicator_code,
                "year": year,
                "scenario": scenario,
                "trend_only": round(trend_value, 2),
                "event_contribution": round(incremental_event_effect * mult, 2),
                "forecast": round(point, 2),
                "ci_low": round(point - ci_width, 2),
                "ci_high": round(point + ci_width, 2),
                "trend_is_single_point_fallback": is_fallback,
            })
    return pd.DataFrame(rows)


def build_forecast_table(df: pd.DataFrame) -> pd.DataFrame:
    acc = forecast_indicator(df, "ACC_OWNERSHIP")
    usg = forecast_indicator(df, "USG_DIGITAL_PAYMENT")
    return pd.concat([acc, usg], ignore_index=True)


def progress_to_target(df: pd.DataFrame, forecast_df: pd.DataFrame) -> pd.DataFrame:
    """Compares base-scenario 2025 forecast to the NFIS-II 70% target (REC_0031)."""
    target_row = df[(df["record_type"] == "target") & (df["indicator_code"] == "ACC_OWNERSHIP")]
    target_val = float(target_row["value_numeric"].iloc[0]) if len(target_row) else None
    base_2025 = forecast_df[(forecast_df["indicator_code"] == "ACC_OWNERSHIP") &
                             (forecast_df["scenario"] == "base") &
                             (forecast_df["year"] == 2025)]["forecast"]
    forecast_val = float(base_2025.iloc[0]) if len(base_2025) else None
    return pd.DataFrame([{
        "target_2025": target_val,
        "base_forecast_2025": forecast_val,
        "gap_pp": round(target_val - forecast_val, 2) if target_val and forecast_val else None,
    }])


if __name__ == "__main__":
    data = load_unified_data()
    table = build_forecast_table(data)
    print(table.to_string(index=False))
    print("\n=== Progress toward NFIS-II 70% Access target ===")
    print(progress_to_target(data, table).to_string(index=False))
    table.to_csv("../data/processed/forecast_table.csv", index=False)
