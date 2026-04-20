# Statement Generator (Practice)

Python tool to generate mock savings account statements in PDF format with realistic-looking transactions for UI/demo practice.

## Files

- `statement_generator.py` - main dynamic generator script
- `sample_statement.pdf` - generated sample statement

## Requirements

- Python 3.9+
- `reportlab`

Install if needed:

```bash
pip install reportlab
```

## Generate a statement (A4 portrait)

```bash
python3 statement_generator.py \
  --output sample_statement.pdf \
  --seed 17 \
  --start-date 2026-01-01 \
  --end-date 2026-04-19 \
  --opening-balance 78500 \
  --start-serial 1 \
  --max-balance 80000 \
  --max-txn-per-day 4
```

## Behavior

- Starts serial from `#1` by default.
- First row is always `OPENING BALANCE` (date cell is blank for that row).
- Fixed salary transaction on exact 10th of each month:
  - Description: `NEFT SALARY/ONE IT SOLUTIONS/MONTHLY CREDIT`
  - Credit range: `23,000` to `25,000`
- Date generation is bounded by `--start-date` and `--end-date`.
- Maximum transactions per day is controlled by `--max-txn-per-day` (default `4`), and some days can have `0` transactions.
- Balance cap is enforced (`--max-balance`, default `80,000`) with automatic debit control entries when needed.
- Transaction text is fully black and description wraps inside its own column.
- Outgoing transactions are intentionally more frequent than incoming.
- Merchant-specific realistic amount caps are applied (for example Zepto and Ola are kept in practical ranges).
- PDF image pages:
  - `head.png` on first page before the table
  - `second-last-end.png` on the second-last page
  - `end.png` on the last page

## Data arrays included

The script includes separate arrays/pools for combinations:

- personal names
- UPI handles
- local vendors
- online shopping merchants
- card usage merchants
- employers
- billers
- cities

This is mock data for design/testing only.
