# A2 — Public root API audit

Date: 2026-09-03
State: **CLOSED**
Candidate: `0.6.0rc2` · `DrawingSession/0.6.0-vnext`

## Problem

The stage-free docs already told normal workers to use `DrawingSession`, but the package root
advertised a much larger surface: low-level history/action classes, schema constants,
inspection primitives, derived records, mode/style helpers, and aliases. A worker using
`dir(img2drawing)` could reasonably infer that several of those were competing framework
entry points.

The target is PyTorch-like discoverability: normal work should not require reading or
understanding implementation-oriented machinery merely because it is technically importable.

## Audit decision

### Tier 1 — canonical package root

Keep only names needed to begin and express the normal framework route:

```text
__version__
DrawingSession
DrawingIntent
ReferenceAuthority
ReferenceConstraint
ReferenceUnavailableError
RenderProfile
PoseObservation
InitialConstruct
ConstructionMark
observe_pose
author_initial_construct
inspect_initial_construct
```

`DrawingSession` remains the only orchestration object.

### Tier 2 — explicit specialized public namespaces

Keep capabilities available, but do not advertise them at the package root:

| Namespace | Ownership |
|---|---|
| `img2drawing.inspection` | ROI, guides, measurements, inspection primitives |
| `img2drawing.observation` | optional observation/material evidence helpers |
| `img2drawing.vnext` | advanced records, guide objects, schemas, derived authoring records |
| `img2drawing.core` | low-level stroke/history capability used by framework and compatibility code |

Public capability does not imply root placement. These namespaces are libraries used by the
canonical session route, not alternate lifecycles.

### Tier 3 — explicit legacy boundary

R23 orchestration/checkpoint compatibility remains under `img2drawing.legacy.r23`. It is not
part of the normal package-root API.

## Compatibility decision

Do not abruptly break code written against `0.6.0rc1`. Every name removed from the root
advertising surface continues to resolve through a lazy `__getattr__` compatibility map and
emits `DeprecationWarning` directing callers to the owning namespace.

Compatibility aliases are deliberately:

- absent from `img2drawing.__all__`;
- absent from `dir(img2drawing)`;
- not documented as normal imports;
- still importable by old direct callers during the prerelease compatibility window.

This separates **discoverability** from **temporary compatibility**.

## Contract impact

This is an intentional public-surface change, so the package candidate advances from
`0.6.0rc1` to `0.6.0rc2` and `dev/release/vnext/CONTRACT_FREEZE.json` is updated in the same
change.

Unchanged:

- `DrawingSession/0.6.0-vnext` identifier;
- `DrawingSession` methods;
- session/action persistence schemas;
- intent axes and style/mode values;
- canonical `RenderProfile`;
- history ownership;
- R23 checkpoint compatibility.

Changed:

- canonical `img2drawing.__all__`;
- normal `dir(img2drawing)` discovery;
- package version (`0.6.0rc2`);
- support docs and freeze snapshot.

## Mechanical acceptance

A2 closes only when CI proves:

1. canonical root exports equal the audited Tier-1 set;
2. representative pre-rc2 root imports still resolve through warnings;
3. old root names do not reappear in `dir(img2drawing)`;
4. wheel/sdist and clean-install probes agree on version/API/root exports;
5. B18 freeze verification matches the updated snapshot;
6. the historical R23 compatibility validator still passes.

This is an API/discoverability hardening claim, not a visual-quality claim.

## Next bottleneck

A3 audits physical runtime/source isolation. A2 intentionally does **not** move or delete
stage-era/current-path modules; it establishes the public boundary that A3 can now compare
against the actual package layout.
