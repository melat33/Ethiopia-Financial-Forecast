"""
Ethiopia Financial Inclusion Forecasting Dashboard
Run locally with:  streamlit run dashboard/app.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from data_loader import load_unified_data, get_indicator_series
from event_impact import build_association_matrix, validate_telebirr
from forecasting import build_forecast_table, progress_to_target
from eda import key_insights

st.set_page_config(page_title="Ethiopia Financial Inclusion Forecast", layout="wide")


@st.cache_data
def get_data():
    df = load_unified_data()
    forecast = build_forecast_table(df)
    return df, forecast


df, forecast = get_data()

st.sidebar.title("Ethiopia Financial Inclusion")
page = st.sidebar.radio("Navigate", ["Overview", "Trends", "Forecasts", "Inclusion Projections"])

# ---------------------------------------------------------------- OVERVIEW
if page == "Overview":
    st.title("Financial Inclusion Overview")
    st.caption("Selam Analytics -- Findex-aligned Access & Usage tracking for Ethiopia")

    acc = get_indicator_series(df, "ACC_OWNERSHIP")
    mm = get_indicator_series(df, "ACC_MM_ACCOUNT")
    p2p = get_indicator_series(df, "USG_P2P_COUNT")
    atm = get_indicator_series(df, "USG_ATM_COUNT")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Account Ownership (Access)", f"{acc['value_numeric'].iloc[-1]:.0f}%",
              f"+{acc['value_numeric'].diff().iloc[-1]:.0f}pp since {acc['observation_date'].dt.year.iloc[-2]}")
    c2.metric("Mobile Money Accounts", f"{mm['value_numeric'].iloc[-1]:.1f}%",
              f"+{mm['value_numeric'].diff().iloc[-1]:.1f}pp since {mm['observation_date'].dt.year.iloc[-2]}")
    if len(p2p) and len(atm):
        ratio = p2p["value_numeric"].iloc[-1] / atm["value_numeric"].iloc[-1]
        c3.metric("P2P / ATM Crossover Ratio", f"{ratio:.2f}x",
                  "P2P now exceeds ATM volume" if ratio > 1 else "ATM still leads")
    c4.metric("NFIS-II Access Target (2025)", "70%",
              f"{progress_to_target(df, forecast)['gap_pp'].iloc[0]:.1f}pp gap vs. base forecast")

    st.subheader("Key Insights")
    for i, ins in enumerate(key_insights(df), 1):
        st.markdown(f"**{i}.** {ins}")

# ---------------------------------------------------------------- TRENDS
elif page == "Trends":
    st.title("Trends")
    indicators = sorted(df.loc[df["record_type"] == "observation", "indicator_code"].dropna().unique())
    choice = st.selectbox("Indicator", indicators, index=indicators.index("ACC_OWNERSHIP")
                           if "ACC_OWNERSHIP" in indicators else 0)

    years = df["observation_date"].dt.year.dropna()
    yr_range = st.slider("Date range", int(years.min()), int(years.max()),
                          (int(years.min()), int(years.max())))

    series = get_indicator_series(df, choice)
    series = series[(series["observation_date"].dt.year >= yr_range[0]) &
                     (series["observation_date"].dt.year <= yr_range[1])]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=series["observation_date"], y=series["value_numeric"],
                              mode="lines+markers", name=choice, line=dict(width=3)))
    events = df[df["record_type"] == "event"]
    events = events[(events["observation_date"].dt.year >= yr_range[0]) &
                     (events["observation_date"].dt.year <= yr_range[1])]
    for _, ev in events.iterrows():
        fig.add_vline(x=ev["observation_date"], line_dash="dash", line_color="grey",
                       annotation_text=ev["indicator"], annotation_textangle=-90,
                       annotation_font_size=9)
    fig.update_layout(title=f"{choice} over time, with event overlay", height=500)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Channel comparison: P2P vs ATM volume")
    p2p = get_indicator_series(df, "USG_P2P_COUNT")
    atm = get_indicator_series(df, "USG_ATM_COUNT")
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=p2p["observation_date"].dt.strftime("%Y"), y=p2p["value_numeric"], name="P2P"))
    fig2.add_trace(go.Bar(x=atm["observation_date"].dt.strftime("%Y"), y=atm["value_numeric"], name="ATM"))
    fig2.update_layout(barmode="group", height=400)
    st.plotly_chart(fig2, use_container_width=True)

    st.download_button("Download indicator series (CSV)", series.to_csv(index=False),
                        file_name=f"{choice}_series.csv")

# ---------------------------------------------------------------- FORECASTS
elif page == "Forecasts":
    st.title("Forecasts: Access & Usage, 2025-2027")
    target_indicator = st.selectbox("Indicator", ["ACC_OWNERSHIP", "USG_DIGITAL_PAYMENT"])
    sub = forecast[forecast["indicator_code"] == target_indicator]

    fig = go.Figure()
    colors = {"pessimistic": "#e74c3c", "base": "#1f6feb", "optimistic": "#2ecc71"}
    for scenario in ["pessimistic", "base", "optimistic"]:
        s = sub[sub["scenario"] == scenario]
        fig.add_trace(go.Scatter(x=s["year"], y=s["forecast"], mode="lines+markers",
                                  name=scenario.title(), line=dict(color=colors[scenario])))
        fig.add_trace(go.Scatter(
            x=list(s["year"]) + list(s["year"])[::-1],
            y=list(s["ci_high"]) + list(s["ci_low"])[::-1],
            fill="toself", fillcolor=colors[scenario], opacity=0.08,
            line=dict(width=0), showlegend=False, hoverinfo="skip"))
    hist = get_indicator_series(df, target_indicator)
    fig.add_trace(go.Scatter(x=hist["observation_date"].dt.year, y=hist["value_numeric"],
                              mode="markers", name="Observed", marker=dict(size=10, color="black")))
    fig.update_layout(title=f"{target_indicator} forecast with confidence bands", height=550)
    st.plotly_chart(fig, use_container_width=True)

    if sub["trend_is_single_point_fallback"].iloc[0]:
        st.warning("This indicator has only one historical observation (2024), so the "
                   "baseline trend is a flat-line assumption, not a fitted trend. Confidence "
                   "intervals are widened accordingly. See the methodology note.")

    st.subheader("Forecast table")
    st.dataframe(sub[["year", "scenario", "trend_only", "event_contribution", "forecast",
                       "ci_low", "ci_high"]], use_container_width=True)
    st.download_button("Download forecast table (CSV)", forecast.to_csv(index=False),
                        file_name="forecast_table.csv")

    st.subheader("Model validation: Telebirr/M-Pesa vs. observed mobile money growth")
    st.json(validate_telebirr(df))

# ---------------------------------------------------------------- PROJECTIONS
elif page == "Inclusion Projections":
    st.title("Inclusion Projections")
    scenario = st.radio("Scenario", ["pessimistic", "base", "optimistic"], horizontal=True, index=1)

    acc_sub = forecast[(forecast["indicator_code"] == "ACC_OWNERSHIP") & (forecast["scenario"] == scenario)]
    target_val = 70.0

    fig = go.Figure()
    hist = get_indicator_series(df, "ACC_OWNERSHIP")
    fig.add_trace(go.Scatter(x=hist["observation_date"].dt.year, y=hist["value_numeric"],
                              mode="lines+markers", name="Historical"))
    fig.add_trace(go.Scatter(x=acc_sub["year"], y=acc_sub["forecast"], mode="lines+markers",
                              name=f"Forecast ({scenario})", line=dict(dash="dot")))
    fig.add_hline(y=target_val, line_color="red", annotation_text="NFIS-II Target (70%)")
    fig.update_layout(title="Account Ownership: progress toward the 70% NFIS-II target", height=500)
    st.plotly_chart(fig, use_container_width=True)

    gap = target_val - acc_sub[acc_sub["year"] == 2027]["forecast"].iloc[0]
    st.metric("Projected gap to target by 2027", f"{gap:.1f}pp",
              delta=f"{-gap:.1f}pp" if gap > 0 else "Target met", delta_color="inverse")

    st.subheader("Association matrix: which events move which indicators")
    st.dataframe(build_association_matrix(df), use_container_width=True)

    st.subheader("Answers to the consortium's key questions")
    st.markdown("""
- **What drives financial inclusion in Ethiopia?** Telebirr and M-Pesa registration
  growth is the dominant driver of mobile money account expansion, but converts only
  partially into headline Access growth because most registrants were already banked.
- **How do events affect outcomes?** See the association matrix above -- Telebirr and
  M-Pesa show the largest *validated* (empirical) effects; Fayda, EthioPay, and
  interoperability effects are still forward-looking assumptions pending 2025-2027 data.
- **2025-2027 outlook?** See the Forecasts page -- base-case Access is projected to fall
  well short of the 70% NFIS-II target without additional interventions.
    """)
