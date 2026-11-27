# S07 isolated worker comparison — preparation contract

This is a preparation tool, **not** a drawing model, worker runner, artistic judge, or release gate.

Run `python dev/tools/prepare_s07_blind_workers.py --help`. Supply one private PNG reference, one goal Markdown, one JSON budget with `canvas`, `supersample`, `max_actions` and `max_wall_sec`, plus the two pinned wheel/skill ZIP pairs. Expected wheel SHA-256 values are mandatory. This tool does **not** fetch releases, install packages, upload reference files or access repository source at worker time.

It produces `workers/<opaque-code>/` containing precisely `reference.png`, `goal.md`, `budget.json`, `skill.zip`, `runtime.whl`, `worker.json`, plus a separate `evaluator_only.json` with the randomized medium mapping. **Never send the evaluator file to either worker or the blinded reviewer.** Workers require separate contexts, exactly the supplied inputs, the same base goal/budget/reference and their own pinned runtime. The medium-specific sentence intentionally differs to authorize the relevant materials. Do not provide past sessions, extracted coordinates, prior pictures, example answers, source code, or prior evaluator feedback.

After independent runs, mechanically verify resumed checkpoints, observation/action provenance, current PNG, end-to-end GIF and final hashes before blind whole-image and region/crop assessment (face/eyes/expression, hair masses, hands/contact, silhouette and occlusion, line hierarchy, black-white and tone decisions). Keep evaluator-authored residual cause (geometry vs material) and verdict (accept/tie/reject). Worker preparation or mechanical PASS **never** means artistic PASS. Separately compare matched authored paths under graphite/ink; areas and tones are novel material tests, not same-appearance equivalents. Avoid uploading reference/session or derived geometry to Git.

Requires an external fresh agent executor and human/independent visual reviewer. S07 remains NOT_RUN until those artifacts exist. The tool accepts PNG IHDR identity only; it does not inspect image meaning or render pixels.
