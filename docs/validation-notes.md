# Validation record — 8 October 2026

- Formula checks: independent computation from the 36-row CSV matched the six default eligible players, their weighted scores and fee-plus-wage commitments.
- Exception checks: the missing upper fee and both duplicated-ID rows remain excluded; there are three affected records.
- Input perturbations: zero transfer budget produced no eligible players; an invalid active weight total blocked eligibility; a duplicate comparison ID displayed `Select unique ID`. Defaults were restored after each check.
- Frontier check: Remy Vale and Marco Linden are nondominated; Alex Moreau is dominated by Marco, whose score matches at lower commitment.
- Independent engine: LibreOffice recalculated the exported XLSX. Dashboard values were 6 eligible, 36 reviewed, 3 exceptions, scores 75.5 and 73.5 for the leading two rows. No cached formula errors were present on any of the five sheets.
- Visual check: dashboard, comparison, settings, source and model views inspected; native currency formats, chart bindings, labels and exception formatting checked.
- Native features: three editable charts linked to worksheet ranges, two Excel tables, dropdowns and numeric data validation, formula-backed conditional formatting. No macros or external links.
- Microsoft Excel desktop: full interaction not verified. The local application required activation and its open-file workflow did not complete reliably. The workbook has not been certified against every Excel version. The formula set avoids dynamic arrays to keep compatibility broad.
- Tests in CI inspect the saved workbook and independently calculate expectations. They do not open Excel, refresh Power Query or recalculate formulas. The separate engine check above is a release validation, not a claim about CI.

The public workbook is the original formula-bearing XLSX. The independently recalculated copy was used for checking and is not substituted for it.
