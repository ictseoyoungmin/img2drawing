# Exemplar authoring owner

The canonical authoring owner for the full-body croquis exemplar tree is this
directory: `skills/img2drawing/exemplars/full_body_croquis/`.

`src/img2drawing/data/exemplars/full_body_croquis/` is a packaged derived copy.
Release/smoke tooling must run `compare_exemplar_trees()` and reject any hash
drift before distributing the packaged copy. Do not hand-edit the packaged
copy to resolve drift.
