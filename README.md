# GFH Inventory Audit

Inventory **count audit** for VidaPay stores: import the count sheet and the
store list, match scanned units against expected inventory, compute variances
per store/district, render a status image, and send the report to WhatsApp
groups. A Timesheet variant adds employee timesheet processing.

## Highlights
- Import XLSX for store accounts, employees and excluded IMEIs — each with a
  matching **Download Template** button
- Variance pipeline with per-IMEI matching, excluded-IMEI filters
- District summaries, status image render, WhatsApp reporting
- Timesheet automation variant (`GFH_Inventory_Audit_Timesheet.py`)

## Build
Windows EXE built via GitHub Actions on push.
