"""Minimal stage-agnostic session facade for the vNext workflow.

The facade owns session metadata and persistence, while ``AgentDrawingSession``
and ``CanvasHistory`` remain the single authoritative drawing implementation.
The compatibility stage below is intentionally opaque: it exists only because
the shared legacy action/history representation still has a stage field. Public
vNext methods never expose or branch on it.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import threading
import uuid
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from PIL import Image

from ..core.action import AgentDrawingSession, DrawingAction, sha256_file
from ..core.ir import StrokeIR
from ..core.session import RENDERER_ID, TOOLSET_ID, sha256_obj
from ..inspection import InspectionSheet, Registration, drawing_state_hash
from ..render.pillow_pencil_contact import render
from ..render.presets import default_grade_name
from .correction import CorrectionRecord, ResidualRecord


SESSION_SCHEMA = "img2drawing.vnext.session.v2"
RENDERER_VERSION = "vnext-stage-free-1"
SEED_DOMAIN = "vnext-stage-free"
_COMPAT_STAGE = "__vnext_compat__"
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _portable(value: Any) -> Any:
    """Convert values used by the session boundary to JSON-native data.

    Path values are reduced to names. Checkpoint payloads therefore carry
    identity and portable references, never machine-local display paths.
    """

    if isinstance(value, Path):
        return value.name
    if hasattr(value, "to_dict"):
        return _portable(value.to_dict())
    if isinstance(value, Mapping):
        return {str(key): _portable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_portable(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise TypeError(f"value is not JSON portable: {type(value).__name__}")


def _action_id(history: Any, requested: str | None) -> str:
    if requested is not None:
        result = str(requested).strip()
        if not result:
            raise ValueError("action_id must be non-empty")
        return result
    return f"vnext-{len(history.actions) + 1:06d}"


def _tool_payload(tool: str | Mapping[str, Any], grade: str | None, overrides: Mapping[str, Any] | None) -> dict[str, Any]:
    if isinstance(tool, Mapping):
        payload = deepcopy(dict(tool))
        preset = payload.get("preset")
        if not preset:
            raise ValueError("tool mapping requires a preset")
        if grade is not None:
            payload["grade"] = str(grade)
        if overrides is not None:
            payload["overrides"] = deepcopy(dict(overrides))
        return payload
    payload = {
        "preset": str(tool),
        "grade": default_grade_name() if grade is None else str(grade),
    }
    if overrides:
        payload["overrides"] = deepcopy(dict(overrides))
    return payload


class DrawingSession:
    """The minimal vNext drawing session.

    ``CanvasHistory`` is authoritative. The public facade exposes only drawing
    capabilities and portable lifecycle state; it has no current stage, stage
    registry, review manifest, or stage transition.
    """

    def __init__(
        self,
        *,
        session_id: str,
        subject: Path,
        output_dir: Path,
        agent_session: AgentDrawingSession,
        metadata: dict[str, Any] | None = None,
        observations: list[dict[str, Any]] | None = None,
        inspection_history: list[dict[str, Any]] | None = None,
        residuals: list[dict[str, Any]] | None = None,
        corrections: list[dict[str, Any]] | None = None,
        finish_metadata: dict[str, Any] | None = None,
        checkpoint_path: Path | None = None,
        subject_sha256: str | None = None,
    ):
        self.session_id = str(session_id)
        if not self.session_id.strip():
            raise ValueError("session_id must be non-empty")
        self.subject = Path(subject)
        self.output_dir = Path(output_dir)
        self._agent = agent_session
        self.metadata = deepcopy(metadata or {})
        self._observations = deepcopy(observations or [])
        self._inspection_history = deepcopy(inspection_history or [])
        self._residuals = deepcopy(residuals or [])
        self._corrections = deepcopy(corrections or [])
        self._finish_metadata = None if finish_metadata is None else deepcopy(finish_metadata)
        self._lock = threading.RLock()
        self._subject_sha256 = subject_sha256 or sha256_file(self.subject)
        self._checkpoint_path = checkpoint_path or self.output_dir / "session.checkpoint.json"

    @classmethod
    def create(
        cls,
        *,
        subject: str | Path,
        output_dir: str | Path,
        session_id: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> "DrawingSession":
        subject_path = Path(subject)
        if not subject_path.is_file():
            raise FileNotFoundError(subject_path)
        with Image.open(subject_path) as image:
            width, height = image.size
        if width <= 0 or height <= 0:
            raise ValueError("subject image must have positive dimensions")
        output = Path(output_dir)
        session = cls(
            session_id=session_id or f"vnext-{uuid.uuid4().hex[:12]}",
            subject=subject_path,
            output_dir=output,
            agent_session=AgentDrawingSession(width, height, metadata={"vnext": True}),
            metadata=deepcopy(dict(metadata or {})),
        )
        session._write_checkpoint(session._checkpoint_path)
        return session

    @classmethod
    def resume(
        cls,
        checkpoint: str | Path,
        *,
        subject: str | Path | None = None,
        output_dir: str | Path | None = None,
    ) -> "DrawingSession":
        checkpoint_path = Path(checkpoint)
        payload = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        if payload.get("schema") != SESSION_SCHEMA:
            raise ValueError(f"unsupported vNext session schema: {payload.get('schema')!r}")
        renderer = payload.get("renderer") or {}
        if (
            renderer.get("id") != RENDERER_ID
            or str(renderer.get("version")) != RENDERER_VERSION
            or renderer.get("seed_domain") != SEED_DOMAIN
        ):
            raise ValueError("vNext renderer identity/version mismatch")
        toolset = payload.get("toolset") or {}
        if toolset.get("id") != TOOLSET_ID or str(toolset.get("version")) != "1":
            raise ValueError("vNext toolset identity/version mismatch")

        subject_record = payload.get("subject") or {}
        subject_path = Path(subject) if subject is not None else checkpoint_path.parent / str(subject_record.get("name", ""))
        if not subject_path.is_file():
            raise FileNotFoundError(subject_path)
        actual_subject_hash = sha256_file(subject_path)
        if actual_subject_hash != str(subject_record.get("sha256", "")).lower():
            raise ValueError("checkpoint subject sha256 does not match supplied subject")

        canvas = payload.get("canvas") or {}
        agent_payload = {
            "schema": "img2drawing.agent_drawing_session.v1",
            "history": deepcopy(payload["history"]),
            "executed_action_ids": list(payload.get("executed_action_ids", ())),
        }
        agent = AgentDrawingSession.from_dict(agent_payload)
        if agent.width != int(canvas.get("width", -1)) or agent.height != int(canvas.get("height", -1)):
            raise ValueError("checkpoint canvas dimensions do not match history")
        expected = payload.get("digests") or {}
        state = cls._stage_free_projection(agent.current_ir())
        if expected.get("drawing_state_hash") != drawing_state_hash(state):
            raise ValueError("checkpoint drawing state digest mismatch")
        if expected.get("action_log_sha256") != sha256_obj([a.to_dict() for a in agent.history.actions]):
            raise ValueError("checkpoint action log digest mismatch")

        observations = deepcopy(payload.get("observations") or [])
        cls._validate_observation_records(observations)
        observation_ids = {record["observation_id"] for record in observations}
        for action in agent.history.actions:
            provenance = action.provenance or {}
            observation_id = provenance.get("observation_id")
            if observation_id and observation_id != "vnext-unobserved" and observation_id not in observation_ids:
                raise ValueError(f"checkpoint references unknown observation_id: {observation_id}")
        inspection_history = deepcopy(payload.get("inspection_history") or [])
        cls._validate_inspection_history(inspection_history)
        residuals = deepcopy(payload.get("residuals") or [])
        cls._validate_residual_records(residuals, observations, inspection_history)
        corrections = deepcopy(payload.get("corrections") or [])
        cls._validate_correction_records(
            corrections,
            residuals,
            observations,
            inspection_history,
            agent.history.actions,
        )

        if output_dir is None:
            artifact_root = str((payload.get("artifacts") or {}).get("inspection_root", "."))
            if Path(artifact_root).is_absolute():
                raise ValueError("checkpoint inspection_root must be relative")
            destination = (checkpoint_path.parent / artifact_root).resolve()
        else:
            destination = Path(output_dir)
        cls._verify_inspection_artifacts(destination, inspection_history)
        return cls(
            session_id=str(payload["session_id"]),
            subject=subject_path,
            output_dir=destination,
            agent_session=agent,
            metadata=deepcopy(payload.get("metadata") or {}),
            observations=observations,
            inspection_history=inspection_history,
            residuals=residuals,
            corrections=corrections,
            finish_metadata=deepcopy(payload.get("finish_metadata")),
            checkpoint_path=checkpoint_path if output_dir is None else destination / "session.checkpoint.json",
            subject_sha256=actual_subject_hash,
        )

    @staticmethod
    def _stage_free_projection(ir: StrokeIR) -> StrokeIR:
        projection = deepcopy(ir)
        for stroke in projection.strokes:
            # The legacy stage slot is compatibility provenance, not vNext state.
            stroke.stage = None
        return projection

    def _snapshot(self) -> StrokeIR:
        return self._stage_free_projection(self._agent.current_ir())

    def _assert_subject_current(self) -> None:
        if sha256_file(self.subject) != self._subject_sha256:
            raise ValueError("subject changed after session creation")

    @staticmethod
    def _validate_observation_records(records: Sequence[Mapping[str, Any]]) -> None:
        seen: set[str] = set()
        for record in records:
            observation_id = str(record.get("observation_id", "")).strip()
            if not observation_id:
                raise ValueError("observation record requires non-empty observation_id")
            if observation_id in seen:
                raise ValueError(f"duplicate observation_id: {observation_id}")
            if not _SHA256.fullmatch(str(record.get("digest", ""))):
                raise ValueError(f"observation record requires digest: {observation_id}")
            seen.add(observation_id)

    @staticmethod
    def _validate_inspection_history(records: Sequence[Mapping[str, Any]]) -> None:
        seen: set[str] = set()
        for record in records:
            inspection_id = str(record.get("inspection_id", ""))
            if len(inspection_id) != 6 or not inspection_id.isdigit():
                raise ValueError("inspection history requires six-digit inspection_id")
            if inspection_id in seen:
                raise ValueError(f"duplicate inspection_id: {inspection_id}")
            manifest = str(record.get("manifest", ""))
            manifest_parts = manifest.split("/")
            if (
                len(manifest_parts) < 3
                or any(part in {"", ".", ".."} for part in manifest_parts)
                or manifest_parts[-2] != inspection_id
                or manifest_parts[-1] != "inspection.json"
            ):
                raise ValueError(f"inspection manifest is not immutable: {record.get('manifest')!r}")
            for key in ("drawing_state_hash", "drawing_artifact_sha256"):
                if not _SHA256.fullmatch(str(record.get(key, ""))):
                    raise ValueError(f"inspection history requires {key}")
            seen.add(inspection_id)

    @staticmethod
    def _validate_residual_records(
        records: Sequence[Mapping[str, Any]],
        observations: Sequence[Mapping[str, Any]] = (),
        inspections: Sequence[Mapping[str, Any]] = (),
    ) -> None:
        seen: set[str] = set()
        observation_ids = {str(record.get("observation_id")) for record in observations}
        inspection_by_id = {str(record.get("inspection_id")): record for record in inspections}
        for raw in records:
            record = ResidualRecord.from_dict(raw)
            if record.residual_id in seen:
                raise ValueError(f"duplicate residual_id: {record.residual_id}")
            if observations and record.observation_id not in observation_ids:
                raise ValueError(f"residual references unknown observation_id: {record.observation_id}")
            if inspections:
                before = inspection_by_id.get(record.before_inspection_id)
                if before is None:
                    raise ValueError(f"residual references unknown before inspection: {record.residual_id}")
                if before["drawing_state_hash"] != record.before_drawing_state_hash:
                    raise ValueError(f"residual before digest mismatch: {record.residual_id}")
                if record.after_inspection_id is not None:
                    after = inspection_by_id.get(record.after_inspection_id)
                    if after is None or after["drawing_state_hash"] != record.after_drawing_state_hash:
                        raise ValueError(f"residual after digest mismatch: {record.residual_id}")
            seen.add(record.residual_id)

    @staticmethod
    def _validate_correction_records(
        records: Sequence[Mapping[str, Any]],
        residuals: Sequence[Mapping[str, Any]],
        observations: Sequence[Mapping[str, Any]] = (),
        inspections: Sequence[Mapping[str, Any]] = (),
        actions: Sequence[Any] = (),
    ) -> None:
        residual_by_id = {}
        for raw in residuals:
            parsed = ResidualRecord.from_dict(raw)
            residual_by_id[parsed.residual_id] = parsed
        observation_ids = {str(record.get("observation_id")) for record in observations}
        inspection_by_id = {str(record.get("inspection_id")): record for record in inspections}
        action_by_id = {
            str((action.provenance or {}).get("action_id", "")).strip(): (position, action)
            for position, action in enumerate(actions)
            if str((action.provenance or {}).get("action_id", "")).strip()
        }
        seen: set[str] = set()
        for raw in records:
            record = CorrectionRecord.from_dict(raw)
            if record.correction_id in seen:
                raise ValueError(f"duplicate correction_id: {record.correction_id}")
            residual = residual_by_id.get(record.residual_id)
            if residual is None:
                raise ValueError(f"correction references unknown residual_id: {record.residual_id}")
            if record.observation_id != residual.observation_id:
                raise ValueError(f"correction observation mismatch: {record.correction_id}")
            if observations and record.observation_id not in observation_ids:
                raise ValueError(f"correction references unknown observation_id: {record.observation_id}")
            if inspections:
                before = inspection_by_id.get(record.before_inspection_id)
                after = inspection_by_id.get(record.after_inspection_id)
                if before is None or before["drawing_state_hash"] != record.before_drawing_state_hash:
                    raise ValueError(f"correction before digest mismatch: {record.correction_id}")
                if after is None or after["drawing_state_hash"] != record.after_drawing_state_hash:
                    raise ValueError(f"correction after digest mismatch: {record.correction_id}")
            if actions:
                for action_id in record.action_ids:
                    action_entry = action_by_id.get(action_id)
                    if action_entry is None:
                        raise ValueError(f"correction references unknown action_id: {action_id}")
                    position, action = action_entry
                    if position < record.before_history_cursor:
                        raise ValueError(f"correction action predates residual: {action_id}")
                    action_observation = (action.provenance or {}).get("observation_id")
                    if action_observation not in (None, "vnext-unobserved", record.observation_id):
                        raise ValueError(f"correction action observation mismatch: {action_id}")
            seen.add(record.correction_id)

    @staticmethod
    def _verify_inspection_artifacts(
        root: Path, records: Sequence[Mapping[str, Any]]
    ) -> None:
        root = root.resolve()
        for record in records:
            manifest_path = (root / str(record["manifest"])).resolve()
            try:
                manifest_path.relative_to(root)
            except ValueError as exc:
                raise ValueError("inspection manifest escapes the session output directory") from exc
            if not manifest_path.is_file():
                raise FileNotFoundError(manifest_path)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if manifest.get("drawing_state_hash") != record["drawing_state_hash"]:
                raise ValueError(f"inspection state digest mismatch: {manifest_path}")
            if manifest.get("drawing_artifact_sha256") != record["drawing_artifact_sha256"]:
                raise ValueError(f"inspection artifact digest mismatch: {manifest_path}")
            raw_name = str((manifest.get("artifacts") or {}).get("raw_drawing", ""))
            raw_path = (manifest_path.parent / raw_name).resolve()
            try:
                raw_path.relative_to(manifest_path.parent.resolve())
            except ValueError as exc:
                raise ValueError("inspection raw artifact escapes its immutable directory") from exc
            if not raw_path.is_file() or sha256_file(raw_path) != record["drawing_artifact_sha256"]:
                raise ValueError(f"inspection raw artifact digest mismatch: {raw_path}")

    @property
    def width(self) -> int:
        return self._agent.width

    @property
    def height(self) -> int:
        return self._agent.height

    @property
    def history_cursor(self) -> int:
        return self._agent.history.cursor

    @property
    def checkpoint_path(self) -> Path:
        return self._checkpoint_path

    @property
    def inspection_history(self) -> tuple[dict[str, Any], ...]:
        return tuple(deepcopy(self._inspection_history))

    @property
    def observation_history(self) -> tuple[dict[str, Any], ...]:
        """Return defensive copies of the short agent-authored observations."""

        return tuple(deepcopy(self._observations))

    @property
    def residual_history(self) -> tuple[ResidualRecord, ...]:
        """Return the Agent-authored residual memory as immutable records."""

        return tuple(ResidualRecord.from_dict(record) for record in deepcopy(self._residuals))

    @property
    def correction_history(self) -> tuple[CorrectionRecord, ...]:
        """Return explicit correction records with their fresh evidence bindings."""

        return tuple(CorrectionRecord.from_dict(record) for record in deepcopy(self._corrections))

    @property
    def finish_metadata(self) -> dict[str, Any] | None:
        return None if self._finish_metadata is None else deepcopy(self._finish_metadata)

    def current_ir(self) -> StrokeIR:
        with self._lock:
            return self._snapshot()

    def drawing_state_hash(self) -> str:
        with self._lock:
            return drawing_state_hash(self._snapshot())

    def _checkpoint_payload(self) -> dict[str, Any]:
        self._assert_subject_current()
        snapshot = self._snapshot()
        history = self._agent.history.to_dict()
        return {
            "schema": SESSION_SCHEMA,
            "session_id": self.session_id,
            "renderer": {"id": RENDERER_ID, "version": RENDERER_VERSION, "seed_domain": SEED_DOMAIN},
            "toolset": {"id": TOOLSET_ID, "version": "1"},
            "canvas": {"width": self.width, "height": self.height},
            "subject": {"name": self.subject.name, "sha256": self._subject_sha256},
            "metadata": _portable(self.metadata),
            "history": _portable(history),
            "executed_action_ids": sorted(self._agent.executed_action_ids),
            "observations": _portable(self._observations),
            "inspection_history": _portable(self._inspection_history),
            "residuals": _portable(self._residuals),
            "corrections": _portable(self._corrections),
            "finish_metadata": _portable(self._finish_metadata),
            "digests": {
                "action_log_sha256": sha256_obj([a.to_dict() for a in self._agent.history.actions]),
                "drawing_state_hash": drawing_state_hash(snapshot),
            },
            "artifacts": {
                "checkpoint": self._checkpoint_path.name,
                "inspection_root": _relative_reference(self.output_dir, self._checkpoint_path.parent),
            },
        }

    def _write_checkpoint(self, path: Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = self._checkpoint_payload()
        temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
        try:
            temporary.write_text(
                json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True, allow_nan=False),
                encoding="utf-8",
            )
            os.replace(temporary, path)
        finally:
            if temporary.exists():
                temporary.unlink()
        return path

    def checkpoint(self, path: str | Path | None = None) -> Path:
        with self._lock:
            destination = self._checkpoint_path if path is None else Path(path)
            previous = self._checkpoint_path
            self._checkpoint_path = destination
            try:
                return self._write_checkpoint(destination)
            except Exception:
                self._checkpoint_path = previous
                raise

    def _commit(self, action: DrawingAction | Iterable[DrawingAction]) -> Any:
        actions = [action] if isinstance(action, DrawingAction) else list(action)
        if not actions:
            return []
        with self._lock:
            with self._agent.transaction(label="vnext-mutation"):
                results = [self._agent.execute(item) for item in actions]
                self._write_checkpoint(self._checkpoint_path)
            return results[0] if isinstance(action, DrawingAction) else results

    def _provenance(
        self,
        *,
        observation_id: str | None,
        source_observation: str | None,
        reason: str | None = None,
    ) -> tuple[str, str, str | None]:
        with self._lock:
            known_observations = {record["observation_id"] for record in self._observations}
            if observation_id is None:
                observation_id = self._observations[-1]["observation_id"] if self._observations else "vnext-unobserved"
            elif str(observation_id) not in known_observations:
                raise ValueError(f"unknown observation_id: {observation_id}")
        if source_observation is None:
            source_observation = "agent-authored vNext drawing action"
        return str(observation_id), str(source_observation), None if reason is None else str(reason)

    def _draw_action(
        self,
        points: Sequence[Sequence[float]],
        *,
        action_id: str | None = None,
        stroke_id: str | None = None,
        role: str = "structure",
        part: str | None = None,
        confidence: float = 1.0,
        layer: int = 0,
        pressure: Sequence[float] | None = None,
        tool: str | Mapping[str, Any] = "construction_pencil",
        grade: str | None = None,
        tool_overrides: Mapping[str, Any] | None = None,
        observation_id: str | None = None,
        source_observation: str | None = None,
        metadata: Mapping[str, Any] | None = None,
        kind: str = "draw_stroke",
        target_stroke_id: str | None = None,
        reason: str | None = None,
        revision_of: str | None = None,
    ) -> DrawingAction:
        oid, source, normalized_reason = self._provenance(
            observation_id=observation_id,
            source_observation=source_observation,
            reason=reason,
        )
        return DrawingAction(
            action_id=_action_id(self._agent.history, action_id),
            kind=kind,
            stage=_COMPAT_STAGE,
            role=str(role),
            part=None if part is None else str(part),
            points=tuple((float(point[0]), float(point[1])) for point in points),
            target_stroke_id=target_stroke_id,
            stroke_id=stroke_id,
            confidence=float(confidence),
            layer=int(layer),
            tool=_tool_payload(tool, grade, tool_overrides),
            pressure=None if pressure is None else tuple(float(value) for value in pressure),
            observation_id=oid,
            source_observation=source,
            reason=normalized_reason,
            revision_of=revision_of,
            metadata=None if metadata is None else deepcopy(dict(metadata)),
        )

    def draw(
        self,
        points: Sequence[Sequence[float]],
        *,
        action_id: str | None = None,
        stroke_id: str | None = None,
        role: str = "structure",
        part: str | None = None,
        confidence: float = 1.0,
        layer: int = 0,
        pressure: Sequence[float] | None = None,
        tool: str | Mapping[str, Any] = "construction_pencil",
        grade: str | None = None,
        tool_overrides: Mapping[str, Any] | None = None,
        observation_id: str | None = None,
        source_observation: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> str:
        action = self._draw_action(
            points,
            action_id=action_id,
            stroke_id=stroke_id,
            role=role,
            part=part,
            confidence=confidence,
            layer=layer,
            pressure=pressure,
            tool=tool,
            grade=grade,
            tool_overrides=tool_overrides,
            observation_id=observation_id,
            source_observation=source_observation,
            metadata=metadata,
        )
        return str(self._commit(action))

    def draw_many(self, strokes: Iterable[Any], **defaults: Any) -> list[str | None]:
        actions: list[DrawingAction] = []
        for item in strokes:
            values = dict(defaults)
            if isinstance(item, Mapping):
                values.update(item)
                points = values.pop("points")
            else:
                points = item
            if values.get("action_id") is None:
                values["action_id"] = f"vnext-{len(self._agent.history.actions) + len(actions) + 1:06d}"
            actions.append(self._draw_action(points, **values))
        return list(self._commit(actions))

    def replace_stroke(
        self,
        target_stroke_id: str,
        points: Sequence[Sequence[float]],
        *,
        reason: str,
        action_id: str | None = None,
        stroke_id: str | None = None,
        role: str = "structure",
        part: str | None = None,
        confidence: float = 1.0,
        layer: int = 0,
        pressure: Sequence[float] | None = None,
        tool: str | Mapping[str, Any] = "construction_pencil",
        grade: str | None = None,
        tool_overrides: Mapping[str, Any] | None = None,
        observation_id: str | None = None,
        source_observation: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> str:
        action = self._draw_action(
            points,
            action_id=action_id,
            stroke_id=stroke_id,
            role=role,
            part=part,
            confidence=confidence,
            layer=layer,
            pressure=pressure,
            tool=tool,
            grade=grade,
            tool_overrides=tool_overrides,
            observation_id=observation_id,
            source_observation=source_observation,
            metadata=metadata,
            kind="replace_stroke",
            target_stroke_id=str(target_stroke_id),
            reason=reason,
            revision_of=str(target_stroke_id),
        )
        return str(self._commit(action))

    def replace_segment(
        self,
        target_stroke_id: str,
        start_index: int,
        end_index: int,
        points: Sequence[Sequence[float]],
        *,
        reason: str,
        action_id: str | None = None,
        pressure: Sequence[float] | None = None,
        lock_boundaries: bool = True,
        observation_id: str | None = None,
        source_observation: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> str:
        oid, source, normalized_reason = self._provenance(
            observation_id=observation_id,
            source_observation=source_observation,
            reason=reason,
        )
        action = DrawingAction(
            action_id=_action_id(self._agent.history, action_id),
            kind="replace_segment",
            stage=_COMPAT_STAGE,
            points=tuple((float(point[0]), float(point[1])) for point in points),
            target_stroke_id=str(target_stroke_id),
            pressure=None if pressure is None else tuple(float(value) for value in pressure),
            observation_id=oid,
            source_observation=source,
            reason=normalized_reason,
            revision_of=str(target_stroke_id),
            metadata=None if metadata is None else deepcopy(dict(metadata)),
            segment_start=int(start_index),
            segment_end=int(end_index),
            lock_boundaries=bool(lock_boundaries),
        )
        return str(self._commit(action))

    def soft_lift(
        self,
        target_stroke_id: str,
        *,
        action_id: str | None = None,
        tool: str | Mapping[str, Any] = "soft_eraser",
        grade: str | None = None,
        tool_overrides: Mapping[str, Any] | None = None,
        strength: float | None = None,
        observation_id: str | None = None,
        source_observation: str | None = None,
        reason: str | None = None,
    ) -> str:
        oid, source, normalized_reason = self._provenance(
            observation_id=observation_id,
            source_observation=source_observation,
            reason=reason,
        )
        metadata = {} if strength is None else {"strength": float(strength)}
        action = DrawingAction(
            action_id=_action_id(self._agent.history, action_id),
            kind="soft_lift",
            stage=_COMPAT_STAGE,
            target_stroke_id=str(target_stroke_id),
            tool=_tool_payload(tool, grade, tool_overrides),
            observation_id=oid,
            source_observation=source,
            reason=normalized_reason,
            metadata=metadata,
        )
        self._commit(action)
        # Eraser actions do not create a replacement stroke, so expose their
        # canonical history ID for correction provenance.
        return action.action_id

    def delete_stroke(
        self,
        target_stroke_id: str,
        *,
        action_id: str | None = None,
        tool: str | Mapping[str, Any] = "hard_eraser",
        grade: str | None = None,
        tool_overrides: Mapping[str, Any] | None = None,
        observation_id: str | None = None,
        source_observation: str | None = None,
        reason: str | None = None,
    ) -> str:
        oid, source, normalized_reason = self._provenance(
            observation_id=observation_id,
            source_observation=source_observation,
            reason=reason,
        )
        action = DrawingAction(
            action_id=_action_id(self._agent.history, action_id),
            kind="delete_stroke",
            stage=_COMPAT_STAGE,
            target_stroke_id=str(target_stroke_id),
            tool=_tool_payload(tool, grade, tool_overrides),
            observation_id=oid,
            source_observation=source,
            reason=normalized_reason,
        )
        self._commit(action)
        return action.action_id

    def observe(self, observation: Any, *, observation_id: str | None = None) -> str:
        payload = _portable(observation)
        digest = sha256_obj(payload)
        record_id = (
            f"observation-{len(self._observations) + 1:04d}"
            if observation_id is None
            else str(observation_id).strip()
        )
        if not record_id.strip():
            raise ValueError("observation_id must be non-empty")
        with self._lock:
            if any(record["observation_id"] == record_id for record in self._observations):
                raise ValueError(f"duplicate observation_id: {record_id}")
            record = {
                "observation_id": record_id,
                "cursor": self.history_cursor,
                "digest": digest,
                "payload": payload,
            }
            before = deepcopy(self._observations)
            self._observations.append(record)
            try:
                self._write_checkpoint(self._checkpoint_path)
            except Exception:
                self._observations = before
                raise
        return record_id

    def _inspection_record(self, inspection_id: str) -> dict[str, Any]:
        requested = str(inspection_id).strip()
        for record in self._inspection_history:
            if str(record.get("inspection_id")) == requested:
                return deepcopy(record)
        raise ValueError(f"unknown inspection_id: {requested}")

    def record_residual(
        self,
        residual: ResidualRecord | None = None,
        **fields: Any,
    ) -> str:
        """Anchor one Agent-selected residual to the current inspection snapshot.

        Pass a ``ResidualRecord`` or its fields.  When fields are supplied, the
        before-state digest is derived from ``before_inspection_id`` rather than trusted
        from the caller.  Recording a concern after the drawing has already changed is
        rejected as stale.
        """

        if residual is not None and fields:
            raise TypeError("record_residual accepts a ResidualRecord or keyword fields, not both")
        with self._lock:
            if residual is None:
                values = dict(fields)
                before_id = values.get("before_inspection_id")
                if before_id is None:
                    raise TypeError("record_residual requires before_inspection_id")
                before = self._inspection_record(str(before_id))
                values.setdefault("residual_id", f"residual-{len(self._residuals) + 1:04d}")
                values["before_drawing_state_hash"] = before["drawing_state_hash"]
                values.setdefault("before_history_cursor", self.history_cursor)
                residual = ResidualRecord(**values)
            if not isinstance(residual, ResidualRecord):
                raise TypeError("record_residual requires a ResidualRecord")
            if residual.status != "open":
                raise ValueError("only open residuals can be recorded")
            before = self._inspection_record(residual.before_inspection_id)
            if before["drawing_state_hash"] != residual.before_drawing_state_hash:
                raise ValueError("residual before evidence digest does not match inspection")
            if self.drawing_state_hash() != residual.before_drawing_state_hash:
                raise ValueError("residual evidence is stale; inspect the current drawing first")
            if residual.observation_id not in {record["observation_id"] for record in self._observations}:
                raise ValueError(f"unknown observation_id: {residual.observation_id}")
            if any(record.get("residual_id") == residual.residual_id for record in self._residuals):
                raise ValueError(f"duplicate residual_id: {residual.residual_id}")
            payload = residual.to_dict()
            self._residuals.append(payload)
            try:
                self._write_checkpoint(self._checkpoint_path)
            except Exception:
                self._residuals.pop()
                raise
            return residual.residual_id

    def record_correction(
        self,
        residual_id: str,
        *,
        action_ids: Iterable[str],
        after_inspection_id: str,
        rationale: str,
        decision: str = "keep",
        correction_id: str | None = None,
    ) -> CorrectionRecord:
        """Bind explicit history actions to fresh after-inspection evidence.

        ``decision="revise"`` records an attempt while leaving the residual open.  The
        default ``keep`` marks it resolved only after the Agent supplies a current
        inspection whose digest differs from the before snapshot.
        """

        requested = str(residual_id).strip()
        with self._lock:
            index = next(
                (i for i, record in enumerate(self._residuals) if record.get("residual_id") == requested),
                None,
            )
            if index is None:
                raise ValueError(f"unknown residual_id: {requested}")
            residual = ResidualRecord.from_dict(self._residuals[index])
            if residual.status != "open":
                raise ValueError(f"residual is already resolved: {requested}")
            before = self._inspection_record(residual.before_inspection_id)
            after = self._inspection_record(after_inspection_id)
            if before["drawing_state_hash"] != residual.before_drawing_state_hash:
                raise ValueError("residual before inspection no longer matches its record")
            if self.drawing_state_hash() != after["drawing_state_hash"]:
                raise ValueError("after inspection is stale; inspect the current drawing first")
            if after["drawing_state_hash"] == residual.before_drawing_state_hash:
                raise ValueError("correction requires a changed after drawing state")

            requested_actions = (action_ids,) if isinstance(action_ids, str) else tuple(action_ids)
            actions: dict[str, tuple[int, Any]] = {}
            stroke_refs: dict[str, list[tuple[int, str]]] = {}
            for position, action in enumerate(self._agent.history.actions):
                action_id = str((action.provenance or {}).get("action_id", "")).strip()
                if not action_id:
                    continue
                actions[action_id] = (position, action)
                # History actions use the target/source id at the payload level
                # and may assign a fresh generated id to the nested stroke.  Both
                # are useful caller references; the cursor filter below prevents
                # a pre-residual source stroke from being selected accidentally.
                stroke_ids = []
                payload_stroke_id = action.payload.get("stroke_id")
                if payload_stroke_id is not None:
                    stroke_ids.append(payload_stroke_id)
                stroke = action.payload.get("stroke") or {}
                nested_stroke_id = stroke.get("stroke_id")
                if nested_stroke_id is not None:
                    stroke_ids.append(nested_stroke_id)
                for stroke_id in dict.fromkeys(str(stroke_id) for stroke_id in stroke_ids):
                    stroke_refs.setdefault(stroke_id, []).append((position, action_id))
            normalized_actions: list[str] = []
            for requested_action in requested_actions:
                requested_id = str(requested_action).strip()
                if not requested_id:
                    raise ValueError("correction action_ids must be non-empty")
                action_id = requested_id
                candidates = stroke_refs.get(requested_id, ())
                eligible = [item for item in candidates if item[0] >= residual.before_history_cursor]
                # Construction marks are themselves action IDs.  Once that
                # mark has been revised, prefer the latest eligible action
                # carrying the same target stroke instead of rejecting the
                # original pre-residual action as stale.
                if action_id not in actions or (
                    actions[action_id][0] < residual.before_history_cursor and eligible
                ):
                    if eligible:
                        action_id = eligible[-1][1]
                if action_id not in actions:
                    raise ValueError(f"correction references unknown action_id: {requested_id}")
                normalized_actions.append(action_id)
                position, action = actions[action_id]
                if position < residual.before_history_cursor:
                    raise ValueError(f"correction action predates residual: {requested_id}")
                provenance = action.provenance or {}
                action_observation = provenance.get("observation_id")
                if action_observation not in (None, "vnext-unobserved", residual.observation_id):
                    raise ValueError(f"correction action observation mismatch: {requested_id}")
            if len(set(normalized_actions)) != len(normalized_actions):
                raise ValueError("correction action_ids must be unique")

            correction = CorrectionRecord(
                correction_id=correction_id or f"correction-{len(self._corrections) + 1:04d}",
                residual_id=residual.residual_id,
                observation_id=residual.observation_id,
                before_inspection_id=residual.before_inspection_id,
                before_drawing_state_hash=residual.before_drawing_state_hash,
                before_history_cursor=residual.before_history_cursor,
                action_ids=tuple(normalized_actions),
                after_inspection_id=str(after_inspection_id),
                after_drawing_state_hash=after["drawing_state_hash"],
                decision=decision,
                rationale=rationale,
            )
            if any(record.get("correction_id") == correction.correction_id for record in self._corrections):
                raise ValueError(f"duplicate correction_id: {correction.correction_id}")
            updated = residual
            if correction.decision == "keep":
                updated = replace(
                    residual,
                    status="resolved",
                    after_inspection_id=correction.after_inspection_id,
                    after_drawing_state_hash=correction.after_drawing_state_hash,
                )
            before_residuals = deepcopy(self._residuals)
            before_corrections = deepcopy(self._corrections)
            self._residuals[index] = updated.to_dict()
            self._corrections.append(correction.to_dict())
            try:
                self._write_checkpoint(self._checkpoint_path)
            except Exception:
                self._residuals = before_residuals
                self._corrections = before_corrections
                raise
            return correction

    def resolve_residual(
        self,
        residual_id: str,
        *,
        action_ids: Iterable[str],
        after_inspection_id: str,
        rationale: str,
        correction_id: str | None = None,
    ) -> CorrectionRecord:
        """Resolve a residual after the Agent accepts fresh visual evidence."""

        return self.record_correction(
            residual_id,
            action_ids=action_ids,
            after_inspection_id=after_inspection_id,
            rationale=rationale,
            decision="keep",
            correction_id=correction_id,
        )

    def inspect(
        self,
        *,
        registration: Registration | None = None,
        rois: Sequence[Any] = (),
        subject_dim: float = 0.35,
        grid: Any = None,
        guides: Sequence[Any] = (),
        measurements: Sequence[Any] = (),
        out_dir: str | Path | None = None,
        supersample: int = 3,
    ) -> InspectionSheet:
        """Render and inspect one authoritative snapshot atomically.

        The method intentionally has no ``drawing`` or ``drawing_state_hash``
        parameter. Both are produced from the same snapshot under the session
        lock, then handed to the single B02+B03 inspection implementation.
        """

        with self._lock:
            self._assert_subject_current()
            snapshot = self._snapshot()
            if out_dir is None:
                destination = self.output_dir / "inspections"
            else:
                requested_output = Path(out_dir)
                destination = requested_output if requested_output.is_absolute() else self.output_dir / requested_output
            _portable_artifact(destination, self.output_dir)
            destination.mkdir(parents=True, exist_ok=True)
            inspection_id = self._next_inspection_id(destination)
            final_dir = destination / inspection_id
            temporary_dir = destination / f".{inspection_id}.{uuid.uuid4().hex}.tmp"
            temporary_dir.mkdir(parents=True, exist_ok=False)
            raw_path = temporary_dir / "raw_drawing.png"
            if registration is None:
                if (self.width, self.height) != _subject_size(self.subject):
                    shutil.rmtree(temporary_dir)
                    raise ValueError("registration is required when subject and canvas sizes differ")
                registration = Registration.identity((self.width, self.height))
            try:
                render(snapshot, raw_path, supersample=int(supersample))
                sheet = InspectionSheet.create(
                    subject=self.subject,
                    drawing=raw_path,
                    drawing_ir=snapshot,
                    registration=registration,
                    rois=rois,
                    subject_dim=subject_dim,
                    grid=grid,
                    guides=guides,
                    measurements=measurements,
                    out_dir=temporary_dir,
                )
                os.replace(temporary_dir, final_dir)
                sheet = replace(sheet, drawing=final_dir / "raw_drawing.png")
            except Exception:
                if temporary_dir.exists():
                    shutil.rmtree(temporary_dir)
                raise

            relative_manifest = _portable_artifact(final_dir / "inspection.json", self.output_dir)
            before_history = deepcopy(self._inspection_history)
            self._inspection_history.append({
                "inspection_id": inspection_id,
                "manifest": relative_manifest,
                "drawing_state_hash": sheet.drawing_state_hash,
                "drawing_artifact_sha256": sheet.drawing_artifact_sha256,
            })
            try:
                self._write_checkpoint(self._checkpoint_path)
            except Exception:
                self._inspection_history = before_history
                if final_dir.exists():
                    shutil.rmtree(final_dir)
                raise
            return sheet

    def _next_inspection_id(self, destination: Path) -> str:
        ids = [
            int(record["inspection_id"])
            for record in self._inspection_history
            if str(record.get("inspection_id", "")).isdigit()
        ]
        candidate = max(ids, default=0) + 1
        while (destination / f"{candidate:06d}").exists():
            candidate += 1
        return f"{candidate:06d}"

    def finish(self, metadata: Mapping[str, Any] | None = None) -> dict[str, Any]:
        with self._lock:
            before = self._finish_metadata
            self._finish_metadata = _portable(dict(metadata or {}))
            try:
                self._write_checkpoint(self._checkpoint_path)
            except Exception:
                self._finish_metadata = before
                raise
            return deepcopy(self._finish_metadata)


def _subject_size(path: Path) -> tuple[int, int]:
    with Image.open(path) as image:
        return image.size


def _portable_artifact(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise ValueError("vNext inspection artifacts must live under the session output directory") from exc


def _relative_reference(path: Path, base: Path) -> str:
    """Return a portable relative reference for a checkpoint-owned path."""

    return Path(os.path.relpath(Path(path).resolve(), Path(base).resolve())).as_posix()


__all__ = ["DrawingSession", "SESSION_SCHEMA"]
