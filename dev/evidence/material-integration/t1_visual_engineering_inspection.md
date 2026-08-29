# T1 visual engineering inspection

Date: 2026-08-29

The canonical S10 output and calibration artifacts were inspected at enlarged view
as an engineering artifact check after regeneration.

- `s10-quality-run/identity/calibration_sheet.png` is nonblank and shows the five
  declared sample families: straight, C, S, taper-in and taper-out.
- `s10-quality-run/identity/calibration_sheet_50pct.png` is nonblank and preserves
  the same sample ordering at half dimensions.
- `s10-quality-run/final/drawing.png` is nonblank and the P5/P6 output is readable
  as a single figure with selective identity marks rather than a blank or failed
  render.
- `quality_run_report.json` records the P6-discovered P5 reopen and the runtime-
  derived P6 counts; the final PNG hash matches the report.

This is an artifact/provenance inspection for T1. It is not the independent whole-view
visual acceptance required by G6; that gate remains open for a separate evaluator.
