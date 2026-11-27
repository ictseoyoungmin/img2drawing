"""Layer exchange with a native checkpoint from the same locked session snapshot."""
from __future__ import annotations

from dataclasses import replace
import json
import os
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory

from ..core.digest import sha256_file
from ..render.layer_export import export_layer_pngs, export_openraster


def _require_new(path):
    if path.exists() or path.is_symlink():
        raise FileExistsError(f"layer export destination already exists: {path}")


def _copy_evidence(session, destination):
    """Copy only retained manifests and their declared artifacts, preserving safe paths."""
    root = session.output_dir.resolve()
    records = session.inspection_history
    session._verify_inspection_artifacts(root, records)
    destination.mkdir()
    for record in records:
        relative = Path(record["manifest"])
        source = (root / relative).resolve()
        source.relative_to(root)
        manifest = json.loads(source.read_text(encoding="utf-8"))
        files = [(source, relative)]
        for name in manifest.get("artifacts", {}).values():
            if not isinstance(name, str) or Path(name).is_absolute():
                raise ValueError("inspection artifact must have a relative file name")
            artifact = (source.parent / name).resolve()
            artifact.relative_to(source.parent)
            files.append((artifact, relative.parent / name))
        for original, relative_file in files:
            copied = destination / relative_file
            copied.resolve().relative_to(destination.resolve())
            copied.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(original, copied)


def export_session_layers(session, out, *, format, include_native=True):
    if type(include_native) is not bool:
        raise ValueError("include_native must be boolean")
    target = Path(out)
    if format not in ("png", "ora"):
        raise ValueError("unsupported layer export format")
    if format == "ora" and target.suffix.lower() != ".ora":
        raise ValueError("OpenRaster output must use .ora")
    manifest_target = target / "manifest.json" if format == "png" else target.with_suffix(".layers.json")
    native_target = (target / "session.checkpoint.json" if format == "png"
                     else target.with_suffix(".checkpoint.json"))
    evidence_target = target / "native-evidence" if format == "png" else target.with_suffix(".native")
    for path in (target, manifest_target, *((native_target, evidence_target) if include_native else ())):
        _require_new(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with session._lock, TemporaryDirectory(prefix=".img2drawing-exchange-", dir=target.parent) as temporary:
        snapshot = session.current_ir()
        profile = session._require_render_profile()
        staged = Path(temporary) / target.name
        result = (export_layer_pngs(snapshot, profile, staged) if format == "png"
                  else export_openraster(snapshot, profile, staged))
        if include_native:
            native_path = staged / native_target.name if format == "png" else staged.with_suffix(".checkpoint.json")
            evidence_path = staged / "native-evidence" if format == "png" else staged.with_suffix(".native")
            _copy_evidence(session, evidence_path)
            session._write_checkpoint(native_path)
            payload = json.loads(native_path.read_text(encoding="utf-8"))
            payload["artifacts"] = {"checkpoint": native_target.name,
                                    "inspection_root": evidence_target.name}
            native_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2,
                sort_keys=True, allow_nan=False), encoding="utf-8")
            result.manifest["native_checkpoint"] = {
                "file": native_target.name,
                "sha256": sha256_file(native_path),
                "history_cursor": session.history_cursor,
                "drawing_state_hash": session.drawing_state_hash(),
                "location": "bundle" if format == "png" else "external_sidecar",
                "evidence_root": evidence_target.name,
                "reference_sha256": session._subject_sha256,
            }
        else:
            result.manifest["native_checkpoint"] = None
        # The external ORA receipt owns the sidecar handoff. The archive's own
        # manifest describes its raster contents and never claims a native file inside.
        result.manifest_path.write_text(json.dumps(result.manifest, ensure_ascii=False,
            indent=2, sort_keys=True, allow_nan=False), encoding="utf-8")
        if format == "png":
            # Exclusive directory reservation prevents overwriting a raced destination.
            target.mkdir()
            try:
                for path in staged.iterdir():
                    path.rename(target / path.name)
            except BaseException:
                shutil.rmtree(target)
                raise
        else:
            publications = [(staged, target), (result.manifest_path, manifest_target)]
            if include_native:
                publications.append((native_path, native_target))
                publications.append((evidence_path, evidence_target))
            created = []
            try:
                for source, destination in publications:
                    if source.is_dir():
                        destination.mkdir()
                        created.append(destination)
                        for child in source.iterdir():
                            child.rename(destination / child.name)
                    else:
                        os.link(source, destination)
                        created.append(destination)
            except BaseException:
                for path in created:
                    if path.is_dir():
                        shutil.rmtree(path)
                    else:
                        path.unlink()
                raise
        return replace(result, path=target, manifest_path=manifest_target)
