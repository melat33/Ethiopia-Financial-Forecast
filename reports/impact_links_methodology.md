# Impact Link Enrichment — Methodology Note

*Updated to match the real `reference_codes.csv` / v2 unified schema —
see `impact_links_draft_v2.csv`. The earlier `impact_links_draft.csv` used
invented category labels and is superseded by this version.*

16 draft `impact_link` records connecting the 10 cataloged events to specific
Access/Usage indicators, coded against the actual reference codes:

- **`evidence_basis: empirical`** (6 rows, IMP_0001–0006) — magnitude derived
  from Ethiopia's own before/after observations already in the dataset (e.g.
  `ACC_MM_ACCOUNT` 4.7% → 9.45%, `ACC_OWNERSHIP` 46% → 49%). Where one
  observed delta plausibly reflects two events (Telebirr *and* M-Pesa both
  pushing `ACC_MM_ACCOUNT` up 2021–2024), the delta was split by relative
  scale/tenure — this split is an assumption, not a measurement, so
  `confidence` is set to `estimated` (calculated/interpolated), not `high`.
- **`evidence_basis: literature`** (7 rows) — events too recent to have
  Ethiopian post-period data (M-Pesa/EthSwitch interoperability, EthioPay,
  Fayda) or general documented patterns applied to Ethiopia. `confidence: low`
  throughout — treat these as scenario levers to test, not validated
  estimates.
- **`evidence_basis: theoretical`** (3 rows) — standard economic reasoning
  (price elasticity, FX-liberalization incentives, telecom competition
  effects on subscriptions) with no specific comparable case cited.
- **`evidence_basis: expert`** (1 row, IMP_0015, NFIS-II) — a judgment call
  that this policy's effect isn't separable from the events it enabled,
  rather than a literature- or data-backed estimate.

## Reading the categorical fields

- **`relationship_type`** distinguishes *how* an event acts: `direct` (Telebirr
  → its own mobile-money account rate), `indirect` (mobile-money registration
  → overall account ownership, via an unbanked-conversion mechanism),
  `enabling` (Fayda, NFIS-II — creates conditions for others' effects rather
  than moving an indicator itself), `constraining` (Safaricom's price
  increase, the one `decrease`/`constraining` row).
- **`impact_magnitude`** follows the reference-code thresholds (`negligible`
  <1%, `low` <5%, `medium` 5–15%, `high` >15% *relative* change vs. baseline).
  I added a non-schema `magnitude_estimate_pct` column alongside it so the
  reasoning behind each bucket is visible and re-checkable — drop that column
  before merging if you want to match the reference schema exactly.

## Key modeling decisions worth flagging in your writeup

1. **Registration ≠ Access.** The biggest interpretive call in this table is
   `IMP_0003`/`IMP_0004`: Telebirr and M-Pesa drove huge `ACC_MM_ACCOUNT`
   growth but only a small fraction passes through to `ACC_OWNERSHIP`,
   because most registrants were already banked (Market Nuances sheet D:
   mobile-money-only users ≈0.5%). This is the direct answer to the brief's
   question about why Access grew only +3pp despite 65M+ mobile money
   accounts — treat it as one of your five required EDA insights.
2. **NFIS-II (`IMP_0015`) is deliberately not point-estimated.** It's a
   multi-year policy umbrella acting *through* the other events rather than
   an independent shock. Recommend a period/regime dummy in the regression
   instead of a magnitude, to avoid double-counting with Telebirr/Fayda
   effects.
3. **The 2024-2025-launched events (Fayda, M-Pesa/EthSwitch interop,
   EthioPay, FX liberalization) have no Ethiopian post-period data yet.**
   Their rows are forward-looking assumptions that do the real work in your
   2026-2027 forecast scenarios — worth a dedicated "unvalidated, high-impact"
   callout in the Task 3 writeup, and good candidates for the
   optimistic/pessimistic scenario spread in Task 4.
4. **`EVT_0006` (P2P surpasses ATM) was excluded from this table** — it's a
   milestone/outcome, not a driver, so it has no causal `impact_link`. It's
   still useful as a validation checkpoint for your Usage-pillar model.
5. **Lags** range 3-30 months and roughly track how directly the effect
   converts: registration/usage effects (Telebirr → digital payments) lag
   less than survey-capture effects (registration → *next* Findex round's
   account-ownership figure), which is inherently ~2-3 years given Findex's
   3-year cadence.

## Limitations

- Magnitudes for the `empirical` rows are back-solved from only two survey
  points (2021, 2024) with two overlapping events in between — this is a
  decomposition assumption, not a regression result, which is why
  `confidence` is `estimated` rather than `high`. If you can find
  quarterly/annual Telebirr and M-Pesa user-count series, re-derive these
  splits properly rather than trusting the tenure-based split used here.
- `literature`/`theoretical` rows have no cited source for a specific number
  — they're directionally reasonable but the magnitudes should be treated as
  priors to sensitivity-test in Task 4, not facts to report in Task 2.
- `impact_magnitude` buckets were computed as relative % change vs. the
  nearest available baseline observation where one exists; for indicators
  with no pre-event baseline in the dataset (`USG_DIGITAL_PAYMENT`,
  `ACC_MOBILE_PEN`), the bucket is a qualitative judgment rather than a
  computed ratio — flagged per-row in `notes`.
- This table (16 rows) is larger than the 14 the brief mentions; that's fine
  for a draft — trim/merge as you cross-check against the real 56-record file.
- `magnitude_estimate_pct` and `source_type`/`original_text`/`collected_by`/
  `collection_date`/`notes` are not in `reference_codes.csv` but match the
  Task 1 brief's "document your additions" requirement — keep them if your
  actual master CSV has room for them, otherwise move into a companion log.
