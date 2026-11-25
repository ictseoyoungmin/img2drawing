# Historical evidence retention and repository size

S06 archive anchor: `1127e673e05799040e802e9fd3a887d7781f2941` (published v1.2.1). No history rewrite, tag change, or deletion of frozen release assets.

The tracked P1/P2/P3 stage-run directories are retired. Source/dependency audit found the P1
portable checkpoint is still read by the current test and v1.0.2 release notes; it is retained,
and the original full P1 text portability test now also checks the frozen Git object.
Other stage-run files are archived at their immutable commit, with per-path Git blob IDs and
sizes in [historical-evidence-archive.json](historical-evidence-archive.json).
253 files totaling 29211911 bytes are removed from the v1.3 working tree.
This reduces checkout payload, not the historical Git object database or full clone history.
The archive remains retrievable via `git archive <source-commit> <directory>`.
Frozen test/release fixtures, showcase assets, and other evidence are kept until a separate
dependency audit proves they can be safely archived.

## Policy for new work

- Never commit private references, solution sessions or repeated frame packs.
- Keep outputs in ignored qa-results or private-qa (or an external directory); small source
  fixtures and compact textual reports are preferred. Generated action histories, GIFs,
  canonical render manifests and run packs are not new tracked artifacts.
- The CI growth guard compares current tracked files with the immutable v1.2.1 tree. Existing
  historical bytes are grandfathered only while identical; new/changed large blobs and generated
  output paths fail. New dev binary evidence is limited to 2 MiB total, with a 512 KiB per-file
  limit. A future change to this policy requires explicit review.
- Exact archive blob identity is verified against the pinned Git tree and removed paths must
  stay absent. No historical visual verdict is upgraded by this cleanup.

Skill API guide before/after (UTF-8): 22720 → 20502 bytes. Detailed optional
toolkit operation belongs to the existing specialty leaves, not a growing mandatory guide.
