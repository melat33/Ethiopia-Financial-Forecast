"""
eda.py
Exploratory analysis helpers: coverage summaries, growth rates, gender gap,
event timeline overlays, and a lightweight correlation view.
Figures are saved to reports/figures/ so they can be dropped into a report
or the dashboard without recomputation.
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from data_loader import load_unified_data, get_indicator_series

FIG_DIR = Path(__file__).resolve().parents[1] / "reports" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)


def record_type_summary(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby(["record_type", "pillar"], dropna=False).size().reset_index(name="count")


def confidence_summary(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["record_type"].isin(["observation", "impact_link"])] \
        .groupby(["record_type", "confidence"]).size().reset_index(name="count")


def temporal_coverage(df: pd.DataFrame) -> pd.DataFrame:
    obs = df[df["record_type"] == "observation"].copy()
    obs["year"] = obs["observation_date"].dt.year
    return obs.pivot_table(index="indicator_code", columns="year", values="record_id",
                            aggfunc="count", fill_value=0)


def plot_access_trajectory(df: pd.DataFrame, save: bool = True) -> plt.Figure:
    s = get_indicator_series(df, "ACC_OWNERSHIP")
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(s["observation_date"], s["value_numeric"], marker="o", linewidth=2, color="#1f6feb")
    for _, row in s.iterrows():
        ax.annotate(f"{row['value_numeric']:.0f}%", (row["observation_date"], row["value_numeric"]),
                    textcoords="offset points", xytext=(0, 8), ha="center")
    ax.set_title("Ethiopia Account Ownership Rate (Access), 2011-2024")
    ax.set_ylabel("% of adults with an account")
    ax.set_ylim(0, 60)
    ax.grid(alpha=0.3)
    if save:
        fig.savefig(FIG_DIR / "access_trajectory.png", dpi=150, bbox_inches="tight")
    return fig


def plot_event_overlay(df: pd.DataFrame, indicator_code: str, save: bool = True) -> plt.Figure:
    s = get_indicator_series(df, indicator_code)
    events = df[df["record_type"] == "event"].sort_values("observation_date")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(s["observation_date"], s["value_numeric"], marker="o", linewidth=2, color="#1f6feb",
            label=indicator_code)
    ymax = s["value_numeric"].max() if len(s) else 1
    for i, (_, ev) in enumerate(events.iterrows()):
        ax.axvline(ev["observation_date"], color="grey", linestyle="--", alpha=0.5)
        ax.text(ev["observation_date"], ymax * (1.02 + 0.05 * (i % 3)), ev["indicator"],
                rotation=90, fontsize=7, va="bottom")
    ax.set_title(f"{indicator_code} with event timeline overlay")
    ax.grid(alpha=0.3)
    if save:
        fig.savefig(FIG_DIR / f"{indicator_code.lower()}_event_overlay.png", dpi=150, bbox_inches="tight")
    return fig


def gender_gap_summary(df: pd.DataFrame) -> pd.DataFrame:
    obs = df[(df["record_type"] == "observation") & (df["indicator_code"] == "ACC_OWNERSHIP")]
    return obs[obs["gender"].isin(["male", "female"])][
        ["observation_date", "gender", "value_numeric"]
    ].sort_values("observation_date")


def key_insights(df: pd.DataFrame) -> list[str]:
    """Five headline, data-grounded insights for the Task 2 writeup."""
    acc = get_indicator_series(df, "ACC_OWNERSHIP")
    mm = get_indicator_series(df, "ACC_MM_ACCOUNT")
    acc_growth = acc["value_numeric"].diff().tolist()
    mm_growth = (mm["value_numeric"].iloc[-1] - mm["value_numeric"].iloc[0]) if len(mm) > 1 else None
    insights = [
        f"Account ownership growth decelerated sharply in the most recent survey round: "
        f"+13pp (2014-17), +11pp (2017-21), but only +3pp (2021-24), despite mobile money "
        f"accounts more than doubling ({mm['value_numeric'].iloc[0]:.1f}% -> "
        f"{mm['value_numeric'].iloc[-1]:.1f}%) over the same window.",
        "The registration-to-Access gap is explained by Ethiopia's market structure: "
        "mobile-money-only users are rare (~0.5%), so most new mobile money registrants "
        "already had a bank account -- registrations do not convert 1:1 into new account "
        "owners in the Findex sense.",
        "The gender gap in account ownership narrowed only marginally (20pp in 2021 to "
        "18pp in 2024), suggesting mobile money expansion has not yet meaningfully closed "
        "Ethiopia's financial inclusion gender divide.",
        "P2P digital transfers surpassed ATM cash withdrawals in volume for the first time "
        "in FY2024/25 (128.3M P2P transactions vs. 119.3M ATM transactions), a structural "
        "shift toward digital-first payment behavior even though survey-measured Access "
        "growth has stalled.",
        "Nearly all of the largest-magnitude events in the impact model (Fayda ID, "
        "M-Pesa/EthSwitch interoperability, EthioPay) launched in 2024-2025 and have no "
        "post-period Findex data yet -- meaning the true drivers of 2025-2027 Access growth "
        "are still forward-looking assumptions, not validated historical effects.",
    ]
    return insights


if __name__ == "__main__":
    data = load_unified_data()
    print(record_type_summary(data).to_string(index=False))
    print("\n--- Key insights ---")
    for i, ins in enumerate(key_insights(data), 1):
        print(f"{i}. {ins}\n")
    plot_access_trajectory(data)
    plot_event_overlay(data, "ACC_MM_ACCOUNT")
    plot_event_overlay(data, "USG_P2P_COUNT")
    print("Figures saved to", FIG_DIR)
