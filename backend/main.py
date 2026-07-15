"""
FastAPI backend for the Ethiopia Financial Inclusion dashboard.
Wraps the already-tested src/ pipeline (data_loader, eda, event_impact,
forecasting) in JSON endpoints for the React frontend.

Run locally:
    pip install -r ../requirements.txt fastapi uvicorn
    uvicorn main:app --reload --port 8000
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

from data_loader import load_unified_data, get_indicator_series
from eda import key_insights, gender_gap_summary
from event_impact import build_association_matrix, validate_telebirr
from forecasting import build_forecast_table, progress_to_target

app = FastAPI(title="Ethiopia Financial Inclusion API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten to the deployed frontend origin in production
    allow_methods=["*"],
    allow_headers=["*"],
)

_df = load_unified_data()
_forecast = build_forecast_table(_df)


def _series_json(indicator_code: str):
    s = get_indicator_series(_df, indicator_code)
    return [
        {"date": row["observation_date"].strftime("%Y-%m-%d"),
         "year": row["observation_date"].year,
         "value": row["value_numeric"],
         "confidence": row["confidence"],
         "source": row["source_name"]}
        for _, row in s.iterrows()
    ]


@app.get("/api/overview")
def overview():
    acc = get_indicator_series(_df, "ACC_OWNERSHIP")
    mm = get_indicator_series(_df, "ACC_MM_ACCOUNT")
    p2p = get_indicator_series(_df, "USG_P2P_COUNT")
    atm = get_indicator_series(_df, "USG_ATM_COUNT")
    prog = progress_to_target(_df, _forecast).iloc[0]

    return {
        "access": {
            "current": float(acc["value_numeric"].iloc[-1]),
            "year": int(acc["observation_date"].dt.year.iloc[-1]),
            "delta": float(acc["value_numeric"].diff().iloc[-1]),
            "prev_year": int(acc["observation_date"].dt.year.iloc[-2]),
        },
        "mobile_money": {
            "current": float(mm["value_numeric"].iloc[-1]),
            "delta": float(mm["value_numeric"].diff().iloc[-1]),
        },
        "crossover_ratio": float(p2p["value_numeric"].iloc[-1] / atm["value_numeric"].iloc[-1])
            if len(p2p) and len(atm) else None,
        "target_2025": float(prog["target_2025"]) if prog["target_2025"] else None,
        "base_forecast_2025": float(prog["base_forecast_2025"]) if prog["base_forecast_2025"] else None,
        "gap_pp": float(prog["gap_pp"]) if prog["gap_pp"] else None,
        "insights": key_insights(_df),
    }


@app.get("/api/indicators")
def indicators():
    obs = _df[_df["record_type"] == "observation"]
    return sorted(obs["indicator_code"].dropna().unique().tolist())


@app.get("/api/trends/{indicator_code}")
def trends(indicator_code: str):
    series = _series_json(indicator_code)
    if not series:
        raise HTTPException(404, f"No observations for indicator '{indicator_code}'")
    events = _df[_df["record_type"] == "event"].sort_values("observation_date")
    return {
        "indicator_code": indicator_code,
        "series": series,
        "events": [
            {"name": row["indicator"], "date": row["observation_date"].strftime("%Y-%m-%d"),
             "category": row["category"]}
            for _, row in events.iterrows()
        ],
    }


@app.get("/api/gender-gap")
def gender_gap():
    g = gender_gap_summary(_df)
    return [
        {"date": row["observation_date"].strftime("%Y-%m-%d"), "gender": row["gender"],
         "value": row["value_numeric"]}
        for _, row in g.iterrows()
    ]


@app.get("/api/forecast")
def forecast():
    return _forecast.to_dict(orient="records")


@app.get("/api/association-matrix")
def association_matrix():
    matrix = build_association_matrix(_df)
    return {
        "events": matrix.index.tolist(),
        "indicators": matrix.columns.tolist(),
        "values": matrix.values.tolist(),
    }


@app.get("/api/validation")
def validation():
    return validate_telebirr(_df)


@app.get("/api/health")
def health():
    return {"status": "ok", "records_loaded": len(_df)}
