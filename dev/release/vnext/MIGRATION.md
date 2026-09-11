# R23 migration boundary

## Current main

Current post-v1.0.2 `main` no longer installs `img2drawing.legacy.r23` or the old R23
run/stage/review orchestration. Do **not** direct current users to import or call
`inspect_checkpoint()` / `migrate_checkpoint()` from that namespace; those instructions are no
longer valid on current main.

Historical R23 source remains recoverable from Git history. Preserved release evidence lives under
`dev/release/r23/`, and the retired runtime-cluster pointer is documented under `dev/legacy/`.

## v1.0.2 historical compatibility

The immutable v1.0.2 release still contained explicit R23 checkpoint inspection/resume/migration
support, and `CONTRACT_FREEZE.json` records that release-time contract. If an old workflow requires
that compatibility path, use the immutable v1.0.2 tag/release rather than assuming current main
still supports it.

A future release of current main must describe R23 support as retired unless a new, explicitly
versioned migration adapter is deliberately introduced. Historical stage progress, reviews,
reopens, or PASS claims never become current `DrawingSession` authority automatically.
