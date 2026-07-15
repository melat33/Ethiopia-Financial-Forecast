"""
Run with: pytest tests/ -v   (from the project root, after `pip install -r requirements.txt`)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd
import pytest

from data_loader import load_unified_data, load_reference_codes, validate_against_reference, get_indicator_series
from event_impact import build_association_matrix, event_effect_at, validate_telebirr
from forecasting import build_forecast_table, fit_trend, progress_to_target


@pytest.fixture(scope="module")
def data():
    return load_unified_data()


def test_load_unified_data_has_all_record_types(data):
    types = set(data["record_type"].unique())
    assert types == {"observation", "target", "event", "impact_link"}


def test_no_schema_violations(data):
    ref = load_reference_codes()
    issues = validate_against_reference(data, ref)
    assert issues == {}, f"Found invalid category values: {issues}"


def test_indicator_series_sorted_and_clean(data):
    s = get_indicator_series(data, "ACC_OWNERSHIP")
    assert len(s) >= 4
    assert s["observation_date"].is_monotonic_increasing
    assert s["value_numeric"].notna().all()


def test_association_matrix_shape(data):
    matrix = build_association_matrix(data)
    assert matrix.shape[0] == data[data["record_type"] == "event"].shape[0] - 1  # EVT_0006 (milestone) has no links
    assert "ACC_MM_ACCOUNT" in matrix.columns


def test_telebirr_validation_within_tolerance(data):
    result = validate_telebirr(data)
    # modeled estimate should be within 2pp of the actual observed 2024 value
    assert abs(result["modeled_vs_observed_gap_pp"]) < 2.0


def test_event_effect_zero_before_event_date(data):
    effect = event_effect_at(data, "ACC_MM_ACCOUNT", pd.Timestamp("2020-01-01"))
    assert effect == pytest.approx(0.0, abs=0.5)  # before Telebirr/M-Pesa existed


def test_forecast_table_covers_required_indicators_and_years(data):
    forecast = build_forecast_table(data)
    assert set(forecast["indicator_code"].unique()) == {"ACC_OWNERSHIP", "USG_DIGITAL_PAYMENT"}
    assert set(forecast["year"].unique()) == {2025, 2026, 2027}
    assert set(forecast["scenario"].unique()) == {"pessimistic", "base", "optimistic"}


def test_forecast_ci_bounds_are_ordered(data):
    forecast = build_forecast_table(data)
    assert (forecast["ci_low"] <= forecast["forecast"]).all()
    assert (forecast["forecast"] <= forecast["ci_high"]).all()


def test_scenario_ordering_pessimistic_le_optimistic(data):
    forecast = build_forecast_table(data)
    for (ind, yr), grp in forecast.groupby(["indicator_code", "year"]):
        pess = grp[grp["scenario"] == "pessimistic"]["forecast"].iloc[0]
        opt = grp[grp["scenario"] == "optimistic"]["forecast"].iloc[0]
        assert pess <= opt, f"{ind} {yr}: pessimistic forecast exceeds optimistic"


def test_progress_to_target_computes_gap(data):
    forecast = build_forecast_table(data)
    result = progress_to_target(data, forecast)
    assert result["target_2025"].iloc[0] == 70.0
    assert result["gap_pp"].iloc[0] > 0  # base forecast falls short of target
