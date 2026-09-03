# Render profile and replay

Final output and process replay must depict the same authored drawing with the same
persisted rendering contract.

Use the public session output operations for:
- final PNG rendering;
- rendering at an earlier history cursor;
- timelapse export.

Do not switch renderers, pressure behavior, supersampling, or material parameters between
the final PNG and replay merely to make one artifact look better.

Replay must be end-to-end: include the initial state and the latest authored action. Frame
sampling may be reduced for file size, but it must not cut away the beginning or final
state. Value/fill actions should replay as authored actions rather than exploding into
synthetic micro-steps.

A migrated or resumed session should retain the same render profile before canonical
output is produced.
