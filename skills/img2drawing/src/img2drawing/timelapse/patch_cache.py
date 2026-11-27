"""Content-addressed stroke-patch cache for exact incremental frames.

Patches are keyed by the prepared stroke plus every renderer input that can change its
pixels. An optional on-disk layer makes warm re-exports fast; it is disposable acceleration
state, never a source of truth, and corrupt entries are rebuilt.
"""

from __future__ import annotations

import hashlib
import json
import os
import struct
import time
import zlib
from collections import OrderedDict
from contextlib import contextmanager
from dataclasses import asdict
from pathlib import Path
from typing import Any

from PIL import Image

from ..render import RENDERER_ID, RENDERER_VERSION, build_patch, is_eraser, load_contact_profile, prepare_stroke
from ..render.contract import CONTACT_WIDTH_CONTRACT, PRESSURE_LIFT_CONTRACT, contract_for_identity, verify_contract_digest

CACHE_SCHEMA = "img2drawing.local.patch-cache.v3"
_DISK_MAGIC = b"IPC1"
_DISK_HEAD = struct.Struct("<4siiIIII32s")  # magic,x,y,w,h,raw_len,comp_len,raw_sha256


class PatchCache:
    """Build and reuse the canonical renderer's per-stroke RGBA patches."""

    def __init__(self, *, width: int, height: int, background, scale: int, supersample: int,
                 graphite, tooth: float, paper_scale: float, paper_seed: int,
                 cache_contract: dict[str, Any] | None = None,
                 persistent_cache_dir: str | Path | None = None,
                 renderer_version: str = RENDERER_VERSION, renderer_contract_digest: str | None = None):
        self.width = int(width)
        self.height = int(height)
        self.background = tuple(int(x) for x in background)
        self.scale = int(scale)
        self.supersample = int(supersample)
        self.factor = float(self.scale * self.supersample)
        self.hi_size = (int(self.width * self.factor), int(self.height * self.factor))
        self.out_size = (int(self.width * self.scale), int(self.height * self.scale))
        self.graphite = tuple(int(x) for x in graphite)
        self.tooth = float(tooth)
        self.paper_scale = float(paper_scale)
        self.paper_seed = int(paper_seed)
        contract = contract_for_identity(RENDERER_ID, renderer_version)
        digest = verify_contract_digest(renderer_contract_digest, renderer_version=renderer_version)
        self.profile = load_contact_profile(contract.renderer_version)
        self.allow_pressure_lift = contract in (PRESSURE_LIFT_CONTRACT, CONTACT_WIDTH_CONTRACT)
        profile_payload = asdict(self.profile)
        if not self.profile.contact_width_control:
            profile_payload.pop("contact_width_control")
        # Preserve the v11 cache key for the unchanged legacy contact profile.
        if not self.profile.opacity_normalized:
            profile_payload.pop("opacity_normalized")
        self.cache_contract = dict(cache_contract or {})
        self._meta = {
            "schema": CACHE_SCHEMA,
            "scale": self.scale,
            "supersample": self.supersample,
            "graphite": self.graphite,
            "tooth": self.tooth,
            "paper_scale": self.paper_scale,
            "paper_seed": self.paper_seed,
            "contact_profile": profile_payload,
            "renderer_identity": list(contract.identity),
            "renderer_contract_digest": digest,
            "session_contract": self.cache_contract,
        }
        self.patch_cache: dict[str, tuple[tuple[int, int], Image.Image]] = {}
        self.object_cache: dict[int, tuple[object, tuple[tuple[int, int], Image.Image]]] = {}
        self.stats = {"cache_hits": 0, "cache_misses": 0, "patch_build_wall_sec": 0.0,
                      "object_cache_hits": 0, "object_cache_misses": 0}
        self.persistent_cache_dir = None if persistent_cache_dir is None else Path(persistent_cache_dir)
        if self.persistent_cache_dir is not None:
            self.persistent_cache_dir.mkdir(parents=True, exist_ok=True)
        self.persistent = {"disk_hits": 0, "disk_misses": 0, "disk_corrupt": 0, "read_sec": 0.0,
                           "write_sec": 0.0, "bytes_read": 0, "bytes_written": 0}

    def _fingerprint(self, stroke) -> str:
        blob = json.dumps({"stroke": asdict(stroke), "meta": self._meta}, ensure_ascii=False,
                          sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()

    def _build_patch(self, stroke):
        if is_eraser(stroke):
            raise RuntimeError("ordered spatial eraser reached the fast patch cache after eligibility gating")
        bounds, layer = build_patch(
            stroke, factor=self.factor, hi_size=self.hi_size, tooth=self.tooth,
            paper_scale=self.paper_scale, paper_seed=self.paper_seed,
            graphite=self.graphite, profile=self.profile,
        )
        return (bounds[0], bounds[1]), layer

    # -- persistent layer -------------------------------------------------

    def _disk_path(self, key: str) -> Path:
        assert self.persistent_cache_dir is not None
        return self.persistent_cache_dir / key[:2] / f"{key}.pcz"

    def _read_disk(self, key: str):
        path = self._disk_path(key)
        if not path.exists():
            self.persistent["disk_misses"] += 1
            return None
        t0 = time.perf_counter()
        try:
            data = path.read_bytes()
            if len(data) < _DISK_HEAD.size:
                raise ValueError("short cache")
            magic, x, y, w, h, raw_len, comp_len, digest = _DISK_HEAD.unpack_from(data, 0)
            if magic != _DISK_MAGIC or w <= 0 or h <= 0 or raw_len != w * h * 4:
                raise ValueError("bad cache header")
            comp = data[_DISK_HEAD.size:_DISK_HEAD.size + comp_len]
            if len(comp) != comp_len:
                raise ValueError("truncated cache")
            raw = zlib.decompress(comp)
            if len(raw) != raw_len or hashlib.sha256(raw).digest() != digest:
                raise ValueError("cache checksum mismatch")
            layer = Image.frombytes("RGBA", (w, h), raw)
            self.persistent["disk_hits"] += 1
            self.persistent["bytes_read"] += len(data)
            return ((x, y), layer)
        except Exception:
            self.persistent["disk_corrupt"] += 1
            return None
        finally:
            self.persistent["read_sec"] += time.perf_counter() - t0

    def _write_disk(self, key: str, patch) -> None:
        (x, y), layer = patch
        path = self._disk_path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = layer.tobytes()
        comp = zlib.compress(raw, 1)
        blob = _DISK_HEAD.pack(_DISK_MAGIC, int(x), int(y), layer.width, layer.height, len(raw), len(comp),
                               hashlib.sha256(raw).digest()) + comp
        tmp = path.with_name(path.name + f".{os.getpid()}.tmp")
        t0 = time.perf_counter()
        try:
            tmp.write_bytes(blob)
            os.replace(tmp, path)
            self.persistent["bytes_written"] += len(blob)
        finally:
            if tmp.exists():
                try:
                    tmp.unlink()
                except OSError:
                    pass
            self.persistent["write_sec"] += time.perf_counter() - t0

    # -- lookup ------------------------------------------------------------

    def patch_for(self, stroke):
        """Return ``((x, y), rgba_layer)`` for an authored stroke."""

        prepared = prepare_stroke(stroke, None, self.profile)
        key = self._fingerprint(prepared)
        hit = self.patch_cache.get(key)
        if hit is not None:
            self.stats["cache_hits"] += 1
            return hit
        if self.persistent_cache_dir is not None:
            disk = self._read_disk(key)
            if disk is not None:
                self.patch_cache[key] = disk
                self.stats["cache_hits"] += 1
                return disk
        t0 = time.perf_counter()
        patch = self._build_patch(prepared)
        self.stats["patch_build_wall_sec"] += time.perf_counter() - t0
        self.patch_cache[key] = patch
        self.stats["cache_misses"] += 1
        if self.persistent_cache_dir is not None:
            self._write_disk(key, patch)
        return patch

    def patch_for_fast(self, stroke):
        """Like ``patch_for`` but memoized on object identity for borrowed replay strokes."""

        oid = id(stroke)
        hit = self.object_cache.get(oid)
        if hit is not None and hit[0] is stroke:
            self.stats["object_cache_hits"] += 1
            return hit[1]
        self.stats["object_cache_misses"] += 1
        patch = self.patch_for(stroke)
        self.object_cache[oid] = (stroke, patch)
        return patch

    def close(self) -> None:
        seen: set[int] = set()
        for _, layer in self.patch_cache.values():
            if id(layer) in seen:
                continue
            seen.add(id(layer))
            layer.close()
        self.patch_cache.clear()
        self.object_cache.clear()


# Mixed ink uses an isolated, bounded in-memory cache. It has no on-disk
# patches and cannot accidentally reuse a graphite or another profile's entry.
class InkPatchCache:
    DEFAULT_MAX_BYTES = 32 * 1024 * 1024
    MAX_ENTRIES = 256

    def __init__(self, profile, *, supersample=None, max_bytes=DEFAULT_MAX_BYTES):
        from ..render.contract import validate_mixed_raster_budget
        if not profile.is_mixed_media:
            raise ValueError("ink patch cache requires a mixed profile")
        if type(max_bytes) is not int or not 0 <= max_bytes <= self.DEFAULT_MAX_BYTES:
            raise ValueError("invalid ink patch cache byte budget")
        self.profile = profile
        self.supersample = profile.supersample if supersample is None else supersample
        self.factor = validate_mixed_raster_budget(
            profile.canvas_width,profile.canvas_height,self.supersample,profile.output_scale)
        self.hi_size = (profile.canvas_width*self.factor,profile.canvas_height*self.factor)
        self.out_size = (profile.canvas_width*profile.output_scale,profile.canvas_height*profile.output_scale)
        self.background = profile.background_rgba
        self.max_bytes = max_bytes
        self._entries = OrderedDict()
        self._bytes = 0
        self._closed = False
        self._scope = (profile.digest(),self.factor,self.hi_size)
        self.stats = {"cache_hits":0,"cache_misses":0,"patch_build_wall_sec":0.,
                      "evictions":0,"oversize_uncached":0,"cache_bytes":0,
                      "peak_cache_bytes":0,"max_cache_bytes":max_bytes}
        self.persistent = {"mode":"memory-only","disk_hits":0,"disk_misses":0,
                           "disk_corrupt":0,"read_sec":0.,"write_sec":0.,
                           "bytes_read":0,"bytes_written":0}

    def key(self, mark):
        return (self._scope,mark.digest())

    @contextmanager
    def patch(self, mark, *, key=None):
        from ..render.ink import build_ink_patch
        if self._closed:
            raise ValueError("ink patch cache is closed")
        self.profile.validate_ink_mark(mark)
        # Caller may reuse a key derived from the same immutable mark in this
        # source. Never accept a key from a different rendering scope.
        key = self.key(mark) if key is None else key
        if key[0] != self._scope:
            raise ValueError("ink patch key belongs to another profile")
        hit=self._entries.get(key)
        if hit is not None:
            self._entries.move_to_end(key)
            self.stats["cache_hits"]+=1
            yield hit[:2]
            return
        start=time.perf_counter()
        bounds,layer=build_ink_patch(mark,factor=self.factor,hi_size=self.hi_size)
        self.stats["patch_build_wall_sec"]+=time.perf_counter()-start
        self.stats["cache_misses"]+=1
        size=layer.width*layer.height*4
        if size>self.max_bytes:
            self.stats["oversize_uncached"]+=1
            try:
                yield bounds,layer
            finally:
                layer.close()
            return
        while self._entries and (self._bytes+size>self.max_bytes or
                                len(self._entries)>=self.MAX_ENTRIES):
            _,(_,image,n)=self._entries.popitem(last=False)
            image.close()
            self._bytes-=n
            self.stats["evictions"]+=1
        self._entries[key]=(bounds,layer,size)
        self._bytes+=size
        self.stats["cache_bytes"]=self._bytes
        self.stats["peak_cache_bytes"]=max(self.stats["peak_cache_bytes"],self._bytes)
        yield bounds,layer

    def close(self):
        for _,image,_ in self._entries.values():
            image.close()
        self._entries.clear()
        self._bytes=0
        self.stats["cache_bytes"]=0
        self._closed=True


__all__ = ["CACHE_SCHEMA", "PatchCache", "InkPatchCache"]
