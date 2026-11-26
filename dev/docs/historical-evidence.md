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
## Development checkout cleanup (2026-11-27)

Second immutable anchor: `1895e0b1ff5d38e27cb66a7fb5e5e25e36bc412b`.
[Retired evidence index](retired-evidence.json) records 430 files and 112959292 bytes across seven
obsolete evidence/release directories and four obsolete R22/R23 build scripts. The original
Git tree and release tags are unchanged. These are no longer files in the development checkout.

The original source is available at the [pre-cleanup Git tree](https://github.com/ictseoyoungmin/img2drawing/tree/1895e0b1ff5d38e27cb66a7fb5e5e25e36bc412b).
Historical documents may name an old relative path; resolve it against the pinned tree, not
today's checkout. For example, recover selected evidence to an external location:

```sh
git archive --format=zip --output=historical-croquis.zip 1895e0b1ff5d38e27cb66a7fb5e5e25e36bc412b dev/dogfood/croquis-sniper-girl
```

Current source, compact regression fixtures (including the v11 pixel goldens), independent
QA protocols, published release records and curated showcase are unchanged. Historical S10,
S14 and R23 checks read the pinned commit or use a temporary external snapshot, so their
assertions remain active without storing old outputs twice. Full-history CI already fetches
the required commit. A source ZIP need not contain these historical outputs to install the skill.

The maximum tracked relative path is now guarded at 100 UTF-16 code units (including old
unchanged files); Windows extraction can still fail if the chosen destination prefix is too
long. This is a checkout/ZIP reduction, not a promise that a full-history clone shrinks.

## Policy for new work

- Never commit private references, solution sessions or repeated frame packs.
- Keep outputs in ignored qa-results or private-qa (or an external directory); small source
  fixtures and compact textual reports are preferred. Generated action histories, GIFs,
  canonical render manifests and run packs are not new tracked artifacts.
- The CI growth guard compares current tracked files with the immutable v1.2.1 tree. Existing
  historical bytes are grandfathered only while identical; new/changed large blobs and generated
  output paths fail. New dev binary evidence is limited to 2 MiB total, with a 512 KiB per-file
  limit. A future change to this policy requires explicit review.
- Exact archive blob and subtree identities, counts and sizes are verified against both pinned
  Git trees; retired paths, including new files in retired directories, must stay absent.
  No historical visual verdict is upgraded by this cleanup.

Skill API guide before/after (UTF-8): 22720 → 20502 bytes. Detailed optional
toolkit operation belongs to the existing specialty leaves, not a growing mandatory guide.
