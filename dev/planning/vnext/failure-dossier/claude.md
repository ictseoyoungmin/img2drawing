# Claude failure dossier

Failure mode: **visual truth was found, but R23 inspection and review cost blocked
completion**.

## Evidence

- Source log: external evidence ID `claude-log`
- Source SHA-256: `3fe6d5afdd9fef4621807ff264da2481e81d935e8e60a4fe4655bfb79862f244`
- Run summary and measured findings: lines 1940–1959.
- Cost/tooling findings: lines 1991–2054.
- Cross-check: external evidence ID `r23-assessment`, lines 15–19 and 86–99.

## What happened

The final run record reports: P1 gesture took three passes and advanced; P2 primary
axes took one pass and advanced; work stopped when P3 began. The log also records an
earlier status of more than four hours and more than 60% usage, so the run did not
reach a completed full-body croquis.

The review loop did real useful work. It found, among other things:

- the skull outline cutting off the ear;
- leg centre-path drift of 4–7px and 8–10px;
- both ankles placed at the boot cuff, shortening the legs by 35–50px;
- an elbow placed on the sleeve silhouette;
- a facial centreline 5px away from the measured nose;
- an over-bent spine path;
- a rifle axis drifting 8–12px.

These are concrete, high-impact corrections that would have been missed by a casual
whole-image glance. The log explicitly says the fresh overlay and ROI comparisons
were what exposed them.

## Cost failure

For each pass, the worker describes one full render, eight local reviews, and three
to five additional enlarged boards. P1 alone required reading more than 20 images.
The runtime’s local review images were too small for reliable judgement, and dark
clothing made the unmodified overlay hard to read. The worker therefore created
one-off tooling: a grid, enlarged subject/drawing/contrast-overlay boards, row scans,
pixel samples, and `tmp/inspect_roi.py`.

The bespoke tools improved visual truth but increased review overhead and were not a
portable product contract. The worker stopped before completing the R23 job. This is
the opposite failure from Gemini: not false acceptance, but correct inspection at
unaffordable cost.

## Secondary observations

The log also records a resume/local-review binding surprise
(`prepare_stage_review()` had to be called again), contradictory visibility guidance,
an example image that conflicted with the single-centre-path rule, and no built-in
read-only measurement helpers. These are supporting observations; B00 does not fix
them in runtime.

## B00 disposition

- Keep the measured findings as evidence that overlay, zoom, contrast, and basic
  measurement are high-value capabilities.
- Do not copy the worker’s subject coordinates or temporary scripts into vNext.
- Treat the future Inspection Foundation as the earliest candidate for this bottleneck;
  it must provide one readable sheet with focused ROIs and optional read-only guides.
- Do not add that implementation during B00.

## Authority note

This dossier distinguishes the final run summary from the earlier interruption
status in the same log. It does not claim that Claude completed R23; it records that
the visual review method was informative but too expensive.
