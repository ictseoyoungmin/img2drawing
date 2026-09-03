# vNext release/control-plane records

This directory contains release, support, migration, and freeze records for maintainers and CI.
They are deliberately outside `skills/img2drawing/`: a deployed Agent Skill should expose only
the operating specification, canonical drawing references, runtime source, package metadata, and
optional curated examples if such examples have actually earned a teaching role.

Files here may describe package versions, public API snapshots, compatibility windows, or
validation freezes. They are repository control-plane records, not drawing guidance and not part
of the distributable skill attention surface.
