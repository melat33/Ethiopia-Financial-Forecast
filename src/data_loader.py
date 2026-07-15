"""
data_loader.py
Loads and validates the unified Ethiopia financial-inclusion dataset.

The unified schema stores four record types in one table:
    observation  -- measured values (surveys, operator/regulator reports)
    target       -- official policy goals
    event        -- policies, launches, milestones (pillar is intentionally blank)
    impact_link  -- modeled event -> indicator relationships (parent_id -> event)
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
PROCESSED_DIR = Path(__file__).resolve().parents[1] / "data" / "processed"

NUMERIC_COLS = ["value_numeric", "magnitude_estimate_pct", "lag_months"]
DATE_COLS = ["observation_date", "period_start", "period_end", "collection_date"]


def load_unified_data(path: Path | str = RAW_DIR / "ethiopia_fi_unified_data.csv") -> pd.DataFrame:
    """Load the unified dataset with correct dtypes."""
    df = pd.read_csv(path)
    for c in NUMERIC_COLS:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    for c in DATE_COLS:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")
    return df


def load_reference_codes(path: Path | str = RAW_DIR / "reference_codes.csv") -> pd.DataFrame:
    return pd.read_csv(path)


def validate_against_reference(df: pd.DataFrame, ref: pd.DataFrame) -> dict[str, list[str]]:
    """
    Checks every categorical column that has entries in reference_codes.csv
    and returns a dict of {field: [invalid values found]}. Empty dict = clean.
    """
    issues: dict[str, list[str]] = {}
    for field in ref["field"].unique():
        if field not in df.columns:
            continue
        valid = set(ref.loc[ref["field"] == field, "code"].astype(str))
        seen = set(df[field].dropna().astype(str)) - {""}
        bad = sorted(seen - valid)
        if bad:
            issues[field] = bad
    return issues


def split_by_record_type(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    return {rt: g.copy() for rt, g in df.groupby("record_type")}


def get_indicator_series(df: pd.DataFrame, indicator_code: str, gender: str = "all",
                          location: str = "national") -> pd.DataFrame:
    """Return a clean time series (date, value) for one indicator_code."""
    obs = df[(df["record_type"] == "observation") & (df["indicator_code"] == indicator_code)]
    obs = obs[(obs["gender"].fillna("all") == gender)]
    if "location" in obs.columns:
        obs = obs[(obs["location"].fillna("national") == location) | obs["location"].isna()]
    out = obs[["observation_date", "value_numeric", "confidence", "source_name"]].dropna(
        subset=["observation_date", "value_numeric"]
    )
    return out.sort_values("observation_date").reset_index(drop=True)


def save_processed(df: pd.DataFrame, name: str) -> Path:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PROCESSED_DIR / name
    df.to_csv(out_path, index=False)
    return out_path


if __name__ == "__main__":
    data = load_unified_data()
    ref = load_reference_codes()
    print("Loaded", len(data), "records")
    print(data["record_type"].value_counts().to_string())
    problems = validate_against_reference(data, ref)
    if problems:
        print("\nSchema issues found:")
        for field, bad_vals in problems.items():
            print(f"  {field}: {bad_vals}")
    else:
        print("\nAll categorical fields match reference_codes.csv")
