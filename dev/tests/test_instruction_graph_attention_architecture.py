from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VERIFIER_PATH = ROOT / "dev" / "tools" / "verify_instruction_graph.py"


def _load_verifier():
    spec = importlib.util.spec_from_file_location("verify_instruction_graph_attention_test", VERIFIER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_cleaned_router_and_index_remain_attention_bounded() -> None:
    module = _load_verifier()
    module.verify_attention_budgets()

    assert module.MAX_SKILL_BYTES == 12_000
    assert module.MAX_INDEX_BYTES == 10_000
    assert module.MAX_ROOT_DIRECT_LEAF_ROUTES == 16


def test_deployable_markdown_routes_are_closed_over_reference_graph() -> None:
    module = _load_verifier()
    module.verify_internal_route_integrity()
    module.verify_index_reachability()


def test_deployable_graph_stays_out_of_development_control_plane() -> None:
    module = _load_verifier()
    module.verify_deployable_control_plane_boundary()


def test_canonical_policy_owners_remain_present_and_routed() -> None:
    module = _load_verifier()
    module.verify_canonical_owner_routes()
