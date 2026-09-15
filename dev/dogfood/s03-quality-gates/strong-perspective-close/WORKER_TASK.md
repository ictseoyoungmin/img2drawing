# S03.1 clean fresh-worker task

This file is the **worker-facing** task packet. It intentionally contains no prior review findings,
expected failure list, corrected coordinates, previous outputs, or evaluator hints.

## Input

Use the exact supplied reference image whose SHA-256 is:

`393e0ca4870079aa1e4723b13847c9d3fcec0750bd659a7827d00d891280a40d`

Use the current `img2drawing` skill and its documented public runtime.

## Task

Complete a reference-driven croquis/drawing of the supplied subject.

Start from structural observation and construction, then continue to a finished drawing rather
than stopping at rough gesture. Preserve enough face, hair, clothing, pose, overlap, and other
visible subject detail that the depicted subject and action are specifically readable from the
reference.

Use linework rather than region fill for the drawing. Sparse line-based value/shadow expression is
allowed when it supports the observed form. Follow the current skill's normal observation,
correction, retirement, and completion guidance.

Do not use image generation, raster painting/repair, pasted reference pixels, or tracing as the
final authoring method. Final authored marks must use the supported img2drawing runtime.

## Required outputs

Preserve and return:

- the complete canonical `session.json` from action 0 through the latest accepted action;
- the final PNG rendered from that session;
- an end-to-end timelapse GIF from action 0 through latest, normally sampled with `every_n=4`, using
  the same pencil-renderer family as the final PNG;
- any ordinary inspection/comparison artifacts the current skill uses during the task;
- a short note naming any visible limitations that remain at completion.

Do not reconstruct a missing action history after the fact. If the canonical history is lost,
report that honestly with the remaining artifacts instead of synthesizing replacement provenance.
