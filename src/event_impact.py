"""
event_impact.py
Turns impact_link records into (1) an event x indicator association matrix
and (2) a function that estimates an event's effect on an indicator at a
given point in time, given its lag and magnitude.

Functional form: each event contributes its full estimated effect once
`lag_months` has elapsed since its date, using a logistic ramp (not a hard
step) so effects build in gradually over roughly +/-6 months around the lag
midpoint -- closer to how registration/usage effects actually accumulate
than an instant jump.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from data_loader import load_unified_data

MAGNITUDE_TO_PCT = {"high": 20.0, "medium": 10.0, "low": 3.0, "negligible": 0.5}


def _signed_pct(row: pd.Series) -> float:
    """Numeric effect size in % terms, using magnitude_estimate_pct if present,
    else falling back to the categorical bucket's midpoint."""
    if pd.notna(row.get("magnitude_estimate_pct")):
        val = float(row["magnitude_estimate_pct"])
    else:
        val = MAGNITUDE_TO_PCT.get(row["impact_magnitude"], 0.0)
        if row["impact_direction"] == "decrease":
            val = -val
    return val


def build_association_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Rows = events, columns = indicators, values = estimated effect (see _signed_pct)."""
    links = df[df["record_type"] == "impact_link"].copy()
    events = df[df["record_type"] == "event"][["record_id", "indicator"]].rename(
        columns={"record_id": "parent_id", "indicator": "event_name"})
    links = links.merge(events, on="parent_id", how="left")
    links["effect"] = links.apply(_signed_pct, axis=1)
    matrix = links.pivot_table(index="event_name", columns="related_indicator",
                                values="effect", aggfunc="sum", fill_value=0.0)
    return matrix.round(2)


def event_effect_at(df: pd.DataFrame, indicator_code: str, as_of_date: pd.Timestamp) -> float:
    """
    Sum of all events' contributions to `indicator_code` by `as_of_date`,
    using a logistic ramp centered on (event_date + lag_months).
    Returns a value in the indicator's own units (pp for most Access/Usage
    rate indicators; % relative for count-based ones -- see notes column).
    """
    links = df[(df["record_type"] == "impact_link") & (df["related_indicator"] == indicator_code)].copy()
    if links.empty:
        return 0.0
    events = df[df["record_type"] == "event"][["record_id", "observation_date"]]
    links = links.merge(events, left_on="parent_id", right_on="record_id", suffixes=("", "_evt"))

    total = 0.0
    for _, row in links.iterrows():
        midpoint = row["observation_date_evt"] + pd.DateOffset(months=int(row["lag_months"] or 0))
        months_elapsed = (as_of_date - midpoint).days / 30.44
        ramp = 1 / (1 + np.exp(-months_elapsed / 3))  # logistic, ~6-month build-in window
        total += _signed_pct(row) * ramp
    return round(total, 2)


def validate_telebirr(df: pd.DataFrame) -> dict:
    """
    Sanity check named in the brief: does the modeled Telebirr+M-Pesa effect
    on ACC_MM_ACCOUNT roughly track the observed 4.7% (2021) -> 9.45% (2024) move?
    """
    from data_loader import get_indicator_series
    s = get_indicator_series(df, "ACC_MM_ACCOUNT")
    observed_start, observed_end = s["value_numeric"].iloc[0], s["value_numeric"].iloc[-1]
    modeled_end = observed_start + event_effect_at(df, "ACC_MM_ACCOUNT", s["observation_date"].iloc[-1])
    return {
        "observed_2021": observed_start,
        "observed_2024": observed_end,
        "observed_delta_pp": round(observed_end - observed_start, 2),
        "modeled_2024_estimate": round(modeled_end, 2),
        "modeled_vs_observed_gap_pp": round(modeled_end - observed_end, 2),
    }


if __name__ == "__main__":
    data = load_unified_data()
    matrix = build_association_matrix(data)
    print("=== Event x Indicator Association Matrix ===")
    print(matrix.to_string())
    print("\n=== Validation: Telebirr/M-Pesa effect vs. observed ACC_MM_ACCOUNT ===")
    for k, v in validate_telebirr(data).items():
        print(f"  {k}: {v}")
    matrix.to_csv("../data/processed/event_indicator_matrix.csv")
