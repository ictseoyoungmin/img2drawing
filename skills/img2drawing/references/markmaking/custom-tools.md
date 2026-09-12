# Custom tools

Custom tools are for repeated line behavior that existing public presets do not express cleanly.
They are not a reason to modify renderer internals or build an alternative rasterizer.

## Smallest-scope rule

Use the narrowest customization scope that solves the drawing problem:

```text
existing preset fits
  -> preset + per-stroke modifier

one unusual mark only
  -> one-off authored dynamics

special behavior repeats within this artwork
  -> session-local custom tool

behavior recurs across unrelated works with one clear semantic purpose
  -> candidate builtin preset
```

Do not create a global preset merely because one local stroke needed an unusual parameter.

## Session-local custom tool

A session-local custom tool should inherit from the nearest stable public preset, then override only
what materially changes the line language. Keep its purpose semantic and reviewable.

Example intent:

```text
custom:coat-fold-deep
inherits: contour-weighted
purpose: repeated deep jacket folds in this drawing
changes: slightly broader contact, stronger local pressure, shorter terminal release
```

The example is descriptive; use only public customization fields implemented by the runtime.
Do not invent private renderer arguments from this document.

## Replay rule

A custom tool name is not enough for deterministic replay. The session must preserve the resolved
tool state that was actually used, together with any explicitly authored pressure/width/opacity
behavior. A future edit to the preset definition must not silently change historical output.

## Promotion rule

Promote a session-local custom tool to the builtin vocabulary only when:

1. the behavior has recurred across unrelated drawings;
2. the semantic purpose is stable and explainable;
3. the existing preset vocabulary cannot express it without repeated ad-hoc overrides;
4. regression evidence exists for the behavior.

## Runtime boundary

If public customization cannot express a needed mark, record that as a runtime capability gap.
Do not work around it by drawing the final result directly with Pillow, OpenCV, SVG, canvas, or a
private renderer helper. Framework development can then extend the public runtime explicitly.
