# Data Enrichment Log

Documents every record added to the starter dataset (33 observations/targets
+ 10 events = 43 records) to reach the current 60-record unified file.

## Added observations (1)

| record_id | indicator | value | source | confidence | why added |
|---|---|---|---|---|---|
| REC_0034 | Digital Payment Adoption Rate (USG_DIGITAL_PAYMENT) | 35% (2024) | Global Findex 2024, cited in the challenge brief text | medium | The brief names Usage/Digital Payment Adoption as one of the two required forecast targets, but no `observation` row for `USG_DIGITAL_PAYMENT` existed in the starter data -- only `impact_link` records referenced it. Without this row the forecasting model has nothing to anchor a baseline to. Confidence set to `medium` (not `high`) because the brief states the figure as approximate ("~35%"). |

**Still open**: this is the *only* observation for `USG_DIGITAL_PAYMENT`, so
`forecasting.py` cannot fit a trend from history -- it falls back to a flat
baseline (see `trend_is_single_point_fallback` in `forecast_table.csv`).
Sourcing an earlier digital-payment figure (2021 Findex microdata, or an
EthSwitch/NBE composite) would materially improve this forecast and should be
the top priority for further enrichment.

## Added impact_links (16)

All 16 are new -- the starter dataset shipped with events and indicators but
no records connecting them (`impact_link` count was 0 in the pasted data,
vs. 14 mentioned in the challenge README). See `reports/impact_links_methodology.md`
for full reasoning, evidence basis, and confidence per record. Summary:

- 6 records (`IMP_0001`-`IMP_0006`) are `evidence_basis: empirical`, derived
  by decomposing Ethiopia's own observed Findex deltas (2021→2024) between
  Telebirr and M-Pesa's contributions.
- 7 records lean on `literature` (comparable-country patterns: interoperability
  effects, instant-payment-rail adoption, e-KYC/digital-ID account-opening
  effects) because the underlying events (Fayda, M-Pesa/EthSwitch interop,
  EthioPay) launched in 2024-2025 with no Ethiopian post-period data yet.
- 2 records use `theoretical` reasoning (price elasticity, FX-liberalization
  incentives) with no specific comparable case cited.
- 1 record (NFIS-II) uses `expert` judgment that its effect isn't separable
  from the events it enabled.

## Not yet added (open items from the enrichment guide)

- **Sheet B (Direct Correlation)**: active accounts, agent density, POS
  terminals, QR merchants -- would strengthen the Usage model in particular.
- **Sheet C (Indirect/Proxy)**: smartphone penetration, data affordability
  trend (only one point currently), urbanization, literacy, electricity
  access -- useful as leading indicators / regression features.
- **Gender/urban-rural disaggregation** beyond the 4 gender rows already in
  the starter data (REC_0004/0005/0027/0028/0029/0030) -- Findex microdata
  would let the dashboard show urban vs. rural trajectories per the Task 2
  brief.
- **56-record discrepancy**: the schema doc (`SCHEMA_DESIGN.md`) states the
  real file has 56 records; the pasted starter data + this enrichment reaches
  60. Worth reconciling against the actual master file before final
  submission to avoid duplicate impact_link coverage of the same
  event→indicator relationships.

collected_by: Melat · collection_date: 2026-07-13
