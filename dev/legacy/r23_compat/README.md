# Retired R23 compatibility namespace

This directory records the retirement of the installable `img2drawing.legacy.r23` namespace from the post-v1.0.2 `main` branch.

The compatibility implementation is intentionally **not copied into a second executable tree**. Its exact source remains recoverable from Git history and the immutable v1.0.2 release commit:

- release commit: `6b4a99431bdb402345fd3779cb16ba7ad1648cb7`
- former path: `skills/img2drawing/src/img2drawing/legacy/r23.py`
- former blob SHA: `e8f4ce234bddc5e5481c41fefe4c356c478fd1cb`
- former package marker blob SHA: `e6bcc72f504c1917427769ed4fa079378ee3d23f`
- frozen historical checkpoint schemas: `img2drawing.run_checkpoint.v1`, `.v2`, `.v3`

The v1.0.2 `dev/release/vnext/CONTRACT_FREEZE.json` remains unchanged because it describes what was actually shipped in that release, including the then-present `img2drawing.legacy.r23` compatibility namespace.

Current source must not import from this archive. Historical R23 checkpoints should be handled with the corresponding historical release when migration is required; the current installable package no longer promises the R23 migration namespace.
