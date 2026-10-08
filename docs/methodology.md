# Model definitions

## Data validity

Empty source rows are ignored. A populated row must have an ID, a name, a supported position, numeric age/costs/minutes and all six numeric attributes. Duplicate IDs exclude every affected row. The model checks age bounds, negative values, reversed fee estimates and attributes outside 1–20. Excel data validation prompts for whole numbers; the CSV utility additionally rejects fractional and non-finite input. Pasting can bypass Excel validation, so use the import report.

## Role score

`SUMPRODUCT(attributes, selected weights) / 20 * 100`

The six attributes use the same 1–20 scale. The denominator is the scale maximum, so the theoretical minimum score is 5, not 0. All six attributes are required, even when a chosen weight is zero; this avoids comparing records with different completeness. The default weight profiles are illustrative and editable, not calibrated against match outcomes. A weight error blocks the shortlist rather than silently renormalising.

## Cost

`Upper fee estimate + weekly wage × 52 × contract years`

This is a simplified nominal commitment over the selected contract length, not transfer cash flow or accounting amortisation. The wage input is an estimate, not a contract offer. Screening independently requires upper fee ≤ fee limit and wage ≤ weekly wage limit. There is no aggregate squad budget in this model.

## Eligibility and ranking

Rows must pass validity, settings, active weight validation, position, age, fee, wage and minutes, in that order. `Screen result` records the **first** failing criterion. Its categories are mutually exclusive and reconcile to populated records; they are not counts of every possible reason a player failed.

The live rank is the count of eligible players with a strictly greater score plus the count of equal-score eligible rows up to the current row. This provides a unique stable ordering without newer dynamic-array functions. Equal scores carry no preference beyond source order. Dashboard shows ranks 1–6; Model retains every eligible row.

## Cost/score frontier

Among eligible players, another player dominates a row if:

- their score is higher and their commitment is no greater; **or**
- their score is equal and their commitment is lower.

Two `COUNTIFS` blocks count these disjoint conditions. Zero dominators means `Frontier`. Identical score/cost pairs both remain on the frontier. This is a two-objective comparison; it does not account for every factor a manager might value.

## Why keep the controls simple?

The target position changes the active weights; budgets and evidence thresholds screen the candidates. These are separate decisions. Raising a budget does not raise a player's score. Missing information is not rewarded. The comparison sheet exposes the underlying attributes so that a composite score cannot hide a weak area.

## Extend the analysis responsibly

Bring in a real permitted save export, add the missing football context, and record why each weight was chosen. Evaluate the shortlist against subsequent outcomes before calling the score predictive. Any claimed recruitment benefit would need an actual decision log and comparison, not only a polished dashboard.
