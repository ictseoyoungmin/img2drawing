from __future__ import annotations

import argparse
import dataclasses
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from img2drawing.provenance.timelapse import select_cursors
from img2drawing.vnext.intent import DrawingIntent
from img2drawing.vnext.reference_authority import ReferenceAuthority
from img2drawing.vnext.render_profile import RenderProfile
from img2drawing.vnext.session import DrawingSession

from make_fixture import build_fixture


def make_fixture_session(fixture_path: Path | None, supersample: int, work_dir: Path) -> DrawingSession:
    fixture = json.loads(fixture_path.read_text(encoding="utf-8")) if fixture_path is not None else build_fixture()
    w, h = int(fixture["width"]), int(fixture["height"])
    profile = dataclasses.replace(RenderProfile.canonical(w, h), supersample=int(supersample))
    session = DrawingSession.create(
        canvas=(w, h),
        output_dir=work_dir,
        session_id="duplicate-work-analysis",
        intent=DrawingIntent(
            reference_mode="imaginative",
            drawing_mode="free_draw",
            finish_intent="expressive",
            style_profile="pencil_loose",
        ),
        reference_authority=ReferenceAuthority.imaginative(["duplicate-work fixture"]),
        render_profile=profile,
    )
    tool_map = {
        "construction": "construction_pencil",
        "hatch": "construction_pencil",
        "form": "form_pencil",
        "continuous": "continuous_pencil",
        "accent": "accent_pencil",
    }
    for idx, spec in enumerate(fixture["strokes"]):
        session.draw(
            [p[:2] for p in spec["points"]],
            pressure=[p[2] for p in spec["points"]],
            tool=tool_map[spec["kind"]],
            role=spec["kind"],
            part=spec["label"],
            layer=idx,
        )
    return session


def summarize_duplicate_work(session: DrawingSession, *, every_n: int) -> dict:
    profile = session.render_profile
    if profile is None:
        raise ValueError("session has no RenderProfile")
    history = session._agent.history
    cursors = select_cursors(session._agent, "every_n", every_n=every_n)
    per_frame = []
    counts: dict[str, int] = {}
    for cursor in cursors:
        ir = history.state_at(cursor)
        ids = [str(s.stroke_id) for s in ir.strokes]
        per_frame.append({"cursor": cursor, "active_strokes": len(ids)})
        for sid in ids:
            counts[sid] = counts.get(sid, 0) + 1

    # Current exporter independently renders the final cursor after the sampled final frame.
    final_ir = history.state_at(history.cursor)
    for stroke in final_ir.strokes:
        sid = str(stroke.stroke_id)
        counts[sid] = counts.get(sid, 0) + 1

    unique = len(counts)
    total = sum(counts.values())
    w, h = int(profile.canvas_width), int(profile.canvas_height)
    ss = int(profile.supersample)
    sampled_passes = sum(x["active_strokes"] for x in per_frame)
    result = {
        "schema": "img2drawing.timelapse_duplicate_work.v1",
        "session_id": session.session_id,
        "resolution": [w, h],
        "supersample": ss,
        "actions": history.cursor,
        "every_n": every_n,
        "cursors": cursors,
        "sampled_frames": len(cursors),
        "per_frame_active_strokes": per_frame,
        "final_active_strokes": len(final_ir.strokes),
        "unique_strokes": unique,
        "stroke_material_passes_in_sampled_frames": sampled_passes,
        "extra_final_render_stroke_passes": len(final_ir.strokes),
        "total_stroke_material_passes": total,
        "duplicate_stroke_material_passes": total - unique,
        "duplication_factor_vs_unique": total / unique if unique else 0.0,
        "top_repeated": [
            {"stroke_id": sid, "passes": n}
            for sid, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:12]
        ],
        "pixel_work_manifest": len(cursors) * w * h * ss * ss,
        "actual_full_render_calls": len(cursors) + 1,
        "pixel_work_including_duplicate_final": (len(cursors) + 1) * w * h * ss * ss,
    }
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    group = ap.add_mutually_exclusive_group()
    group.add_argument("--fixture", type=Path, default=None)
    group.add_argument(
        "--session",
        type=Path,
        default=None,
        help="Existing vNext session/checkpoint. Subject and inspection artifacts must remain beside it.",
    )
    ap.add_argument("--every-n", type=int, default=4)
    ap.add_argument("--supersample", type=int, default=4, help="Fixture-only RenderProfile override")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    if args.session is not None:
        session = DrawingSession.resume(args.session)
    else:
        session = make_fixture_session(args.fixture, args.supersample, args.out.parent / "analysis-session")

    result = summarize_duplicate_work(session, every_n=args.every_n)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
