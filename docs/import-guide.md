# Importing a shortlist

The workbook is version-independent because it accepts an explicit canonical table, not a game save. Export capabilities and column names vary by Football Manager version and platform. Do not assume an older Ctrl+P/HTML workflow works in every edition.

1. Obtain a player list from your edition's supported export route, or copy the visible values into a CSV. Use your own permitted data. Preserve the original file.
2. Map its columns to the exact headers and order in `data/demo_players.csv`. Assign a stable unique ID to every player. Keep the mapping with the original export.
3. Explicitly map positions to `Centre-back`, `Midfielder`, `Striker` or `Wide forward`. A mapping is an analytical choice, not proof of positional familiarity. Goalkeepers and other roles are outside this version's scope.
4. Use **GBP** fees and **GBP per week** wages. Enter lower and upper fee estimates separately. Do not infer exchange rates, convert annual pay without recording the assumption, or turn a displayed valuation into an asking price without qualification.
5. Enter minutes for one consistent season/competition scope. Use integer attributes from 1 to 20. Masked attribute ranges such as `12–15` stay unknown until scouted; do not use their midpoint as observed data.
6. Validate with `python src/prepare_csv.py YOUR_FILE.csv --output local-data/normalized.csv --report local-data/quality-report.json`. Python 3.10+; no packages are required.
7. Read the quality report. All records are retained. Invalid/unknown numeric input becomes blank in the normalised file and is flagged; the original stays untouched. Over 60 records causes an explicit error rather than silently truncating the list.
8. In a copy of the workbook, clear only the **values** in `Players!A2:N61`, then paste the 14 data columns as values starting at A2. Do not paste CSV headers into row 2, delete rows, overwrite Model, or overwrite validation/formatting.
9. Set calculation to Automatic and check Model before using the shortlist. The comparison ID dropdown covers all 60 slots (`Players!A2:A61`); select a populated, unique ID.

## Input dictionary

| Columns | Unit / rule |
|---|---|
| Player ID, Player | Non-empty, stable unique ID and display name |
| Position group | Exactly one supported group |
| Age | Whole years, 15–50 |
| Fee low GBP, Fee high GBP | Nonnegative whole pounds; high must be at least low |
| Wage GBP/week | Nonnegative whole pounds per week |
| Minutes | Nonnegative whole minutes in one consistent observation period |
| Finishing, Passing, Tackling, Positioning, Pace, Work rate | Whole 1–20 attributes; blanks represent unknown |

Zero transfer fee is allowed for a genuine free transfer. A blank transfer fee is unknown and excludes the player. The parser accepts values such as `£1.2m` and `£15K`, but the workbook uses typed whole-pound values. Currency symbols, ranges and units are not automatically guessed.

`local-data/` is excluded from version control. Publish only data you are entitled to share. The supplied demonstration data is fictional and may be reused.
