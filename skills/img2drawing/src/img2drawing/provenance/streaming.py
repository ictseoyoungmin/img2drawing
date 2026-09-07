from __future__ import annotations

import hashlib, json, os, shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
from PIL import GifImagePlugin, Image, ImageChops

from ..core.session import DrawingSession, sha256_file
from ..render.pillow_pencil_contact import render as pencil_render
from .timelapse import _debug_overlay, _frame_duration_ms, pixel_sha256, select_cursors

STREAMING_SCHEMA = "img2drawing.timelapse.streaming.v1"
CHECKPOINT_SCHEMA = "img2drawing.timelapse.checkpoint.v1"

class ResumeMismatchError(RuntimeError): pass
class SimulatedInterruption(RuntimeError): pass

@dataclass
class StreamingTimelapseExport:
    manifest: dict[str, Any]
    manifest_path: Path
    gif_path: Path
    checkpoint_path: Path
    resumed: bool


def _native(value):
    if isinstance(value, Path): return str(value)
    if isinstance(value, (tuple, list)): return [_native(v) for v in value]
    if isinstance(value, dict): return {str(k): _native(v) for k, v in value.items()}
    return value


def _atomic_json(path: Path, data: dict[str, Any]) -> None:
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, sort_keys=True); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, path)


def _rgb(path: Path) -> Image.Image:
    src = Image.open(path).convert("RGBA"); bg = Image.new("RGBA", src.size, (255,255,255,255)); bg.alpha_composite(src); src.close()
    out = bg.convert("RGB"); bg.close(); return out


def _make_palette(path: Path, colors: int) -> list[int]:
    rgb = _rgb(path); q = rgb.quantize(colors=int(colors), method=Image.Quantize.MAXCOVERAGE); rgb.close()
    pal = list(q.getpalette() or []); q.close(); pal.extend([0] * max(0, 768-len(pal))); return pal[:768]


def _quantize(path: Path, palette: list[int]) -> Image.Image:
    rgb = _rgb(path); template = Image.new("P", (1,1)); template.putpalette(palette)
    out = rgb.quantize(palette=template, dither=Image.Dither.NONE); rgb.close(); template.close(); return out


def _compat(session, mode, every_n, renderer_id, renderer_kwargs, final_kwargs, colors, delta_bbox, debug_overlay):
    return _native({
        "session_id": session.session_id, "action_log_sha256": session.action_hash(), "state_sha256": session.state_hash(),
        "cursor": session.history.cursor, "mode": mode, "every_n": every_n if mode == "every_n" else None,
        "renderer_id": renderer_id, "renderer_kwargs": renderer_kwargs, "final_renderer_kwargs": final_kwargs,
        "colors": int(colors), "delta_bbox": bool(delta_bbox), "debug_overlay": bool(debug_overlay),
    })


def _checkpoint(compat, count, cursor, gif_offset, journal_offset, palette, final_hash, completed=False):
    return {"schema": CHECKPOINT_SCHEMA, "compatibility": compat, "committed_frame_count": int(count),
            "committed_cursor": int(cursor), "gif_byte_offset": int(gif_offset), "journal_byte_offset": int(journal_offset),
            "palette": palette, "palette_sha256": hashlib.sha256(bytes(palette)).hexdigest(),
            "expected_final_pixel_sha256": final_hash, "completed": bool(completed)}


def _truncate(path: Path, offset: int) -> None:
    with open(path, "r+b") as f: f.truncate(int(offset)); f.flush(); os.fsync(f.fileno())


def _journal(path: Path) -> list[dict[str, Any]]:
    if not path.exists(): return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write_frame(handle, current, previous, duration, delta):
    if previous is None or not delta:
        bbox=(0,0,current.width,current.height); frame=current; disposal=1 if delta else 2
    else:
        diff=ImageChops.difference(previous,current); bbox=diff.getbbox(); diff.close(); bbox=bbox or (0,0,1,1); frame=current.crop(bbox); disposal=1
    GifImagePlugin._write_frame_data(handle, frame, (bbox[0],bbox[1]), {"duration":int(duration),"disposal":disposal,"include_color_table":False})
    if frame is not current: frame.close()
    return bbox, current.copy()


def export_timelapse_streaming(
    session_path: str | Path, out_dir: str | Path, *, mode="every_n", every_n=8, resume=False, clean=True,
    colors=64, delta_bbox=True, debug_overlay=False, renderer: Callable[..., None] | None=None,
    renderer_kwargs: dict[str,Any] | None=None, renderer_id: str | None=None, expected_final_path: str | Path | None=None,
    final_renderer_kwargs: dict[str,Any] | None=None, loop=0, _stop_after_frames: int | None=None,
) -> StreamingTimelapseExport:
    """Stream a crash-resumable GIF without retaining or spooling the full frame set."""
    session_path, out_dir = Path(session_path), Path(out_dir)
    cp_path, journal_path = out_dir/"checkpoint.json", out_dir/"frames.journal.jsonl"
    tmp_gif, gif_path, manifest_path = out_dir/"timelapse.tmp.gif", out_dir/("debug_timelapse.gif" if debug_overlay else "timelapse.gif"), out_dir/"manifest.json"
    staging, palette_source = out_dir/".frame.png", out_dir/".palette_source.png"
    render_fn=renderer or pencil_render; kwargs=dict(renderer_kwargs or {}); final_kwargs=dict(kwargs if final_renderer_kwargs is None else final_renderer_kwargs)
    rid=renderer_id or getattr(render_fn,"__module__","renderer")
    session=DrawingSession.load(session_path, verify=True); cursors=select_cursors(session,mode,every_n=every_n)
    compat=_compat(session,mode,every_n,rid,kwargs,final_kwargs,colors,delta_bbox,debug_overlay)
    cp=None; resumed=False
    if resume and cp_path.exists():
        cp=json.loads(cp_path.read_text(encoding="utf-8"))
        if cp.get("schema") != CHECKPOINT_SCHEMA or cp.get("compatibility") != compat: raise ResumeMismatchError("timelapse checkpoint does not match session/export contract")
        resumed=True
    elif clean and out_dir.exists(): shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True,exist_ok=True)

    if cp is None:
        render_fn(session.history.state_at(session.history.cursor), str(palette_source), **final_kwargs)
        final_hash=pixel_sha256(palette_source); palette=_make_palette(palette_source,colors); palette_source.unlink(missing_ok=True)
        journal_path.write_bytes(b""); tmp_gif.write_bytes(b"")
        cp=_checkpoint(compat,0,0,0,0,palette,final_hash); _atomic_json(cp_path,cp)
    else:
        palette=[int(v) for v in cp["palette"]]; final_hash=str(cp["expected_final_pixel_sha256"])
        if cp.get("completed"):
            if not manifest_path.exists(): raise ResumeMismatchError("completed checkpoint exists but manifest.json is missing")
            if not gif_path.exists():
                if tmp_gif.exists(): os.replace(tmp_gif,gif_path)
                else: raise ResumeMismatchError("completed checkpoint has neither final nor temporary GIF")
            return StreamingTimelapseExport(json.loads(manifest_path.read_text(encoding="utf-8")),manifest_path,gif_path,cp_path,True)
        if not tmp_gif.exists() or not journal_path.exists(): raise ResumeMismatchError("checkpoint append files are missing")
        _truncate(tmp_gif,cp["gif_byte_offset"]); _truncate(journal_path,cp["journal_byte_offset"])

    committed=int(cp["committed_frame_count"])
    if committed>len(cursors) or (committed and int(cp["committed_cursor"])!=cursors[committed-1]): raise ResumeMismatchError("checkpoint cursor does not match selected replay frames")
    previous=None
    if committed and delta_bbox:
        cursor=cursors[committed-1]; render_fn(session.history.state_at(cursor),str(staging),**(final_kwargs if cursor==session.history.cursor else kwargs))
        if debug_overlay: _debug_overlay(staging,{"frame_index":committed-1,"cursor":cursor,"action":None})
        previous=_quantize(staging,palette)

    with open(tmp_gif,"r+b") as gf, open(journal_path,"ab") as jf:
        gf.seek(0,os.SEEK_END); jf.seek(0,os.SEEK_END)
        for i in range(committed,len(cursors)):
            cursor=cursors[i]; render_fn(session.history.state_at(cursor),str(staging),**(final_kwargs if cursor==session.history.cursor else kwargs)); action=None if cursor==0 else session.history.actions[cursor-1]
            info={"frame_index":i,"cursor":cursor,"action_seq":None if action is None else action.seq,"logical_time":None if action is None else action.logical_time,
                  "stage":None if action is None else action.stage,"action":None if action is None else action.action,"part":None if action is None else action.part,
                  "role":None if action is None else action.role,"duration_ms":_frame_duration_ms(cursors,i,session),"pixel_sha256":pixel_sha256(staging)}
            if debug_overlay: _debug_overlay(staging,info); info["debug_pixel_sha256"]=pixel_sha256(staging)
            current=_quantize(staging,palette)
            if i==0 and gf.tell()==0:
                for chunk in GifImagePlugin._get_global_header(current,{"loop":int(loop)}): gf.write(chunk)
            bbox,next_previous=_write_frame(gf,current,previous,info["duration_ms"],delta_bbox); current.close()
            if previous is not None: previous.close()
            previous=next_previous; info["gif_bbox"]=list(map(int,bbox))
            gf.flush(); os.fsync(gf.fileno()); gif_offset=gf.tell()
            jf.write((json.dumps(info,ensure_ascii=False,sort_keys=True)+"\n").encode("utf-8")); jf.flush(); os.fsync(jf.fileno()); journal_offset=jf.tell()
            cp=_checkpoint(compat,i+1,cursor,gif_offset,journal_offset,palette,final_hash); _atomic_json(cp_path,cp)
            if _stop_after_frames is not None and i+1>=int(_stop_after_frames): raise SimulatedInterruption(f"simulated interruption after {i+1} committed frames")
        gf.write(b";"); gf.flush(); os.fsync(gf.fileno())
    if previous is not None: previous.close()
    staging.unlink(missing_ok=True)

    frames=_journal(journal_path); final_match=bool(frames) and frames[-1]["pixel_sha256"]==final_hash
    external=None if expected_final_path is None else pixel_sha256(Path(expected_final_path))==final_hash
    manifest={"schema":STREAMING_SCHEMA,
      "session":{"path":str(session_path),"session_id":session.session_id,"action_log_sha256":session.action_hash(),"state_sha256":session.state_hash(),"action_count":len(session.history.actions),"cursor":session.history.cursor},
      "export":{"mode":mode,"every_n":every_n if mode=="every_n" else None,"frame_count":len(frames),"streaming":True,"resume_supported":True,"resumed":resumed,
                "delta_bbox":bool(delta_bbox),"colors":int(colors),"renderer_id":rid,"renderer_kwargs":_native(kwargs),"final_renderer_kwargs":_native(final_kwargs),
                "final_frame_matches_session_state":final_match,"external_final_matches_session_state":external,"frame_spool_used":False},
      "frames":frames,"gif":{"file":gif_path.name,"sha256":sha256_file(tmp_gif)}}
    _atomic_json(manifest_path,manifest)
    _atomic_json(cp_path,_checkpoint(compat,len(frames),cursors[-1],tmp_gif.stat().st_size,journal_path.stat().st_size,palette,final_hash,True))
    os.replace(tmp_gif,gif_path)
    return StreamingTimelapseExport(manifest,manifest_path,gif_path,cp_path,resumed)
