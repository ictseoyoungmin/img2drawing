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
from dataclasses import asdict
from pathlib import Path
from typing import Any

from PIL import Image

from ..render import PENCIL_CONTRACT, RENDERER_CONTRACT_DIGEST, build_patch, is_eraser, load_contact_profile, prepare_stroke

CACHE_SCHEMA = "img2drawing.local.patch-cache.v3"
_DISK_MAGIC = b"IPC1"
_DISK_HEAD = struct.Struct("<4siiIIII32s")  # magic,x,y,w,h,raw_len,comp_len,raw_sha256


class PatchCache:
    """Build and reuse the canonical renderer's per-stroke RGBA patches."""

    def __init__(self, *, width: int, height: int, background, scale: int, supersample: int,
                 graphite, tooth: float, paper_scale: float, paper_seed: int,
                 cache_contract: dict[str, Any] | None = None,
                 persistent_cache_dir: str | Path | None = None):
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
        self.profile = load_contact_profile()
        self.cache_contract = dict(cache_contract or {})
        self._meta = {
            "schema": CACHE_SCHEMA,
            "scale": self.scale,
            "supersample": self.supersample,
            "graphite": self.graphite,
            "tooth": self.tooth,
            "paper_scale": self.paper_scale,
            "paper_seed": self.paper_seed,
            "contact_profile": asdict(self.profile),
            "renderer_identity": list(PENCIL_CONTRACT.identity),
            "renderer_contract_digest": RENDERER_CONTRACT_DIGEST,
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


__all__ = ["CACHE_SCHEMA", "PatchCache"]
