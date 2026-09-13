from __future__ import annotations

import re
from pathlib import Path

from img2drawing.render.renderer_registry import resolve_renderer


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "skills" / "img2drawing" / "src"
_GENERATION_TAG = re.compile(r"(?:^|_)v\d+(?=_|\.py$)")


def test_src_python_module_filenames_do_not_encode_renderer_generations() -> None:
    offenders = sorted(
        path.relative_to(SRC).as_posix()
        for path in SRC.rglob("*.py")
        if _GENERATION_TAG.search(path.name)
    )
    assert offenders == []


def test_semantic_module_rename_preserves_serialized_renderer_identities() -> None:
    v10 = resolve_renderer("pillow-pencil-contact-v10", "1")
    v11 = resolve_renderer("pillow-pencil-contact-v11", "1")
    assert v10.identity == ("pillow-pencil-contact-v10", "1")
    assert v11.identity == ("pillow-pencil-contact-v11", "1")
    assert v10.module.__name__.endswith(".pillow_pencil_contact_core")
    assert v11.module.__name__.endswith(".pillow_pencil_contact_material")
