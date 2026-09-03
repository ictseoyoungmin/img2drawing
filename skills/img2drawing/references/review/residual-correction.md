# Residual correction

A residual is a visible mismatch between the current drawing and its reference authority or
declared intent.

Use the loop:

`inspect current render → name mismatch → rank impact → choose responsible premise → edit → inspect fresh render`

## Residual description

Describe what is wrong as a relationship, not a vague quality label. Prefer:
- “far knee is too low relative to pelvis” over “leg feels off”;
- “hair contour is too round at the jaw handoff” over “head needs detail”;
- “shoe toe points forward but reference turns outward” over “foot is simple.”

## Scope

Use a global correction when pose, mass, balance, scale, or a large silhouette premise is
wrong. Use a local correction only when the parent structure is credible and the mismatch
is genuinely bounded.

Do not route by the noun that looks wrong. A foot residual can belong to the local foot,
the parent leg chain, the ground relation, or contour ownership. When the responsible scope
is uncertain, use `residual-routing.md` to select the smallest leaf that can actually repair
the relationship and to identify when an upstream premise must be reopened.

Fix one to three highest-impact residuals at a time. After every mutation, inspect a fresh
render; do not accept a correction from stale evidence.

A repeated local repair that leaves the same mismatch visible is an escalation signal, not
a request for more local strokes. Re-observe the parent relation and route upstream.

The Agent decides whether the mismatch is resolved. Tooling may record evidence and edits
but must not emit an artistic verdict on the Agent's behalf.
