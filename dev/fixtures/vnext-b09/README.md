# B09 deterministic finish fixture

This fixture is a mechanical contract check, not visual dogfood. It creates one
synthetic 96 x 96 reference and one stage-free `DrawingSession`, then changes only
`finish_intent` while authoring four deliberately different decisions:

- `pose`: a weight-path/selected-contour stroke;
- `subject`: a pocket-to-hand contact/occlusion stroke;
- `form_light`: one broad calibrated value region; and
- `expressive`: one focal rhythm accent.

Run it with:

```bash
PYTHONPATH=skills/img2drawing/src python3 dev/fixtures/vnext-b09/run.py --output /tmp/vnext-b09
```

The trace proves that all decisions use the same session, history, schema, and renderer
identity. It does not claim likeness, unseen-subject robustness, or artistic quality.
