# A3 — Runtime physical-isolation audit

Updated: 2026-09-03
Status: **CLOSED**

## Question

Does the packaged source tree communicate the same stage-free product model as the
instruction graph and the `DrawingSession`-centered public API?

A3 distinguishes two different things that happened to share names in older releases:

- the **instruction graph** describes drawing reasoning (`observation`, `construction`,
  `description`, `review`, ...);
- the **runtime package tree** implements capabilities and may retain compatibility code.

The source tree does not need to mirror the instruction graph one-for-one. In particular,
`references/review/` being a current instruction node does not make the historical
`img2drawing.review` runtime package part of the current orchestration path.

## Evidence

The canonical `img2drawing.vnext.session.DrawingSession` imports current capability from
`core`, `inspection`, `render`, and `vnext` modules. It does not import the historical
`stages`, `exemplar`, `review`, `registration`, or `run` modules.

`img2drawing.inspection` already owns the current stage-free registration/measurement
surface used by vNext. The historical top-level `img2drawing.registration` package instead
contains R23-era pose/envelope/head-hair/lower-body/prop comparison contracts.

`img2drawing.legacy.r23` is deliberately lazy. Merely importing the compatibility namespace
does not activate the old orchestration stack. Its legacy export table resolves historical
names to `img2drawing.run`, `img2drawing.stages`, `img2drawing.exemplar`,
`img2drawing.review`, and `img2drawing.registration` only when a caller explicitly asks for
a historical capability.

Resolving `img2drawing.legacy.r23.DrawingRun` activates the historical `run` orchestration
and its stage/exemplar/review dependencies. Historical registration remains even more
narrowly demand-loaded: it is not activated by resolving `DrawingRun` alone and appears only
when a caller explicitly requests an R23 registration capability such as `EnvelopeStation`.
This confirms that the generic historical paths are compatibility-owned rather than eager
parts of the current runtime.

The regression test `dev/tests/test_runtime_physical_isolation.py` freezes these dependency
facts in a fresh interpreter rather than relying on documentation alone.

## Classification

| Runtime path | Classification | Current meaning | A3 decision |
|---|---|---|---|
| `img2drawing.vnext.session` | current implementation | canonical `DrawingSession` orchestration | keep |
| `img2drawing.core` | current shared capability | action/history/fill primitives used by vNext | keep |
| `img2drawing.inspection` | current shared capability | immutable inspection, measurement, current registration | keep |
| `img2drawing.render` | current shared capability | canonical render/replay implementation | keep |
| `img2drawing.observation` | mixed shared namespace | current palette/uncertainty helpers plus historical observation records | keep for now; split only if D/R evidence warrants it |
| `img2drawing.run` | explicit R23 compatibility implementation | historical `DrawingRun` orchestration | quarantine; retirement decision at R03 |
| `img2drawing.stages` | explicit R23 compatibility implementation | Pn stage specs/contracts/registry | quarantine; retirement decision at R03 |
| `img2drawing.exemplar` | explicit R23 compatibility implementation | grammar-exemplar/ablation machinery | quarantine; retirement decision at R03 |
| `img2drawing.review` | explicit R23 compatibility implementation | stage review/pass-memory/reopen/resolved-form machinery | quarantine; do **not** confuse with instruction-graph review guidance |
| `img2drawing.registration` | explicit R23 compatibility implementation | historical subject-structure comparison contracts | quarantine; current registration capability belongs to `img2drawing.inspection` |
| `img2drawing.legacy.r23` | explicit compatibility boundary | lazy adapter and checkpoint migration | keep until bounded retirement decision |

## Why A3 does not rename/delete the old directories now

Moving `stages/`, `exemplar/`, `review/`, `registration/`, and `run.py` into a differently
named directory before dogfood would create a large compatibility-only diff without
improving the current drawing path. Their import paths are still part of the preserved R23
adapter contract, and the current route is already proven not to depend on them.

A cosmetic move would therefore increase migration risk while giving little evidence about
visual quality. Physical deletion or consolidation belongs to **R03**, after fresh D01–D06
validation and the final compatibility-window decision.

A3 instead hardens **ownership and reachability** now:

1. normal root discovery remains `DrawingSession`-centered;
2. canonical vNext imports cannot depend on the R23 orchestration cluster;
3. current registration is owned by `inspection`, not the historical registration package;
4. the old cluster is documented as compatibility implementation, not an alternate workflow;
5. R23 lazy import behavior remains tested at capability granularity.

## Important naming distinction

`review` in the instruction graph means:

`inspect current drawing → name residual → correct responsible premise → inspect again`

The historical `img2drawing.review` Python package means R23 stage reviews, pass memory,
reopen records, resolved-form manifests, identity-finish artifacts, and similar lifecycle
machinery. They share an English word but do not share product ownership.

Likewise, `registration` is not a workflow node in the instruction graph. Alignment and
measurement are bounded inspection capabilities. The current high-level registration type
is therefore correctly discoverable from `img2drawing.inspection`.

## Closure contract

A3 is CLOSED when all of the following hold:

- a clean `import img2drawing` does not import `run`, `stages`, `exemplar`, `review`, or the
  historical `registration` package;
- resolving `DrawingSession` does not import those modules;
- importing `img2drawing.inspection` does not activate the historical registration package;
- importing `img2drawing.legacy.r23` alone remains lazy;
- explicit access to R23 orchestration activates only the historical dependencies it needs;
- explicit access to R23 registration activates the historical registration package on demand;
- current planning docs classify physical retirement as R03 work rather than D01-prep work.

No visual-quality claim is added by A3.

## Next

A4 makes the instruction graph operational by adding explicit
`residual → responsible leaf → upstream premise` routing edges without reintroducing stages.
