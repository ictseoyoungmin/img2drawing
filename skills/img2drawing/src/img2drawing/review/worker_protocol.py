from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class AutonomousWorkerPacket:
    schema: str
    stage: dict[str, Any]
    stage_contract: dict[str, Any]
    pass_index: int
    pass_memory: dict[str, Any]
    references: dict[str, Any]
    artifacts: dict[str, Any]
    local_review_api: dict[str, Any]
    canvas_scale_guidance: dict[str, Any]
    checkpoint_resume: dict[str, Any]
    mandatory_review_views: tuple[str, ...]
    autonomous_loop: tuple[str, ...]
    autonomy_policy: tuple[str, ...]
    escalation_policy: tuple[str, ...]
    grammar_cards: tuple[dict[str, Any], ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema":self.schema,
            "stage":self.stage,
            "stage_contract":self.stage_contract,
            "pass_index":self.pass_index,
            "pass_memory":self.pass_memory,
            "references":self.references,
            "artifacts":self.artifacts,
            "local_review_api":self.local_review_api,
            "canvas_scale_guidance":self.canvas_scale_guidance,
            "checkpoint_resume":self.checkpoint_resume,
            "mandatory_review_views":list(self.mandatory_review_views),
            "autonomous_loop":list(self.autonomous_loop),
            "autonomy_policy":list(self.autonomy_policy),
            "escalation_policy":list(self.escalation_policy),
            "grammar_cards":[dict(card) for card in self.grammar_cards],
        }

    def save_json(self,path: str|Path) -> Path:
        p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(
            json.dumps(self.to_dict(),indent=2,ensure_ascii=False,sort_keys=True),
            encoding="utf-8",
        )
        return p

    def save_markdown(self,path: str|Path) -> Path:
        p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
        s=self.stage
        c=self.stage_contract
        m=self.pass_memory
        refs=self.references

        lines=[
            f"# Autonomous worker packet — {s['stage_id']} / pass {self.pass_index}",
            "",
            "## Stage pass memory",
            f"- state: **{m['state']}**",
            f"- prior review count: {m['prior_review_count']}",
        ]

        if m["state"] == "cold_start":
            lines += [
                "- previous decision: _none_",
                "- carried concerns: _none_",
                "- inter-pass correction actions: _none_",
                "",
                "This is the first review pass for this stage. Start from the stage contract and references.",
            ]
        elif m["state"] == "reopen_restart":
            ctx=m.get("reopen_context") or {}
            lines += [
                "- previous decision: _archived / invalidated by reopen_",
                "- carried concerns: _read reopen context below_",
                "",
                "### REOPEN CONTEXT",
                f"- reopen id: `{ctx.get('reopen_id','unknown')}`",
                f"- role: **{ctx.get('role','unknown')}**",
                f"- target stage: `{ctx.get('target_stage','unknown')}`",
                f"- discovered in: `{ctx.get('discovered_in_stage') or 'unspecified'}`",
                f"- reason: {ctx.get('reason','')}",
            ]
            if ctx.get("findings"):
                lines += ["", "#### Findings that caused the reopen"]
                lines += [f"- {x}" for x in ctx["findings"]]
            lines += [
                "",
                "Do not reuse archived downstream judgements as current evidence. Rebuild from the restored authoritative history.",
            ]
        else:
            lines += [
                f"- parent review digest: `{m['previous_review_digest']}`",
                f"- previous decision: **{m['previous_decision']}**",
                "",
                "### Previous remaining concerns",
            ]
            lines += (
                [f"- {x}" for x in m["previous_remaining_concerns"]]
                if m["previous_remaining_concerns"] else ["- _none_"]
            )
            lines += ["", "### Previous reported corrections"]
            lines += (
                [f"- {x}" for x in m["previous_reported_corrections"]]
                if m["previous_reported_corrections"] else ["- _none_"]
            )
            lines += ["", "### Inter-pass actions since the previous review"]
            if m["inter_pass_actions"]:
                for action in m["inter_pass_actions"]:
                    reason=f" — {action['reason']}" if action.get("reason") else ""
                    part=f" / {action['part']}" if action.get("part") else ""
                    lines.append(
                        f"- `{action['action_id']}` {action['kind']}{part}{reason}"
                    )
            else:
                lines.append("- _none_")

            lines += ["", "### Carried concerns for this pass"]
            lines += (
                [f"- {x}" for x in m["carried_concerns"]]
                if m["carried_concerns"] else ["- _none_"]
            )

        lines += [
            "",
            "### Memory policy",
        ]
        lines += [f"- {x}" for x in m["memory_policy"]]

        lines += [
            "",
            "## Frozen stage representation contract",
            f"- contract: `{c['contract_id']}`",
            f"- representation: **{c['representation_name']}**",
            f"- tier: {c['tier']}",
            f"- inherits from: `{c['inherits_from']}`" if c["inherits_from"] else "- inherits from: _none_",
            "",
            "### This stage owns",
        ]
        lines += [f"- {x}" for x in c["owns"]]
        lines += ["", "### Must preserve from earlier stages"]
        lines += [f"- {x}" for x in c["must_preserve"]] if c["must_preserve"] else ["- _none_"]
        lines += ["", "### Allowed representation"]
        lines += [f"- {x}" for x in c["allowed_representation"]]
        lines += ["", "### Forbidden representation"]
        lines += [f"- {x}" for x in c["forbidden_representation"]]
        lines += ["", "### Detail ceiling"]
        lines += [f"- {x}" for x in c["detail_ceiling"]]
        lines += ["", "### Next stage unlocks"]
        lines += [f"- {x}" for x in c["next_stage_unlocks"]] if c["next_stage_unlocks"] else ["- _none; final stage in this contract_"]

        lines += [
            "", "## Reference authority",
            f"- reference mode: **{refs.get('reference_mode','subject_only')}**",
            f"- authority order: `{' > '.join(refs['authority_order'])}`",
            f"- subject reference: `{refs['subject_reference']['path']}` — geometry truth",
        ]
        if refs.get("task_stage_target") is not None:
            lines.append(
                f"- task stage target: `{refs['task_stage_target']['path']}` — same-task stage truth"
            )
        else:
            lines.append("- task stage target: _not provided_")

        lines += [
            "", "### Non-negotiable authority rule",
            "- The stage contract decides representation scope; it does not decide pose correctness.",
            "- The stage reference under `references/stages/` carries this stage's mark-making guidance,"
            " and some stages keep a rendered example beside it. Open one when you want it; never copy"
            " pose, coordinates, perspective or subject proportions from it.",
            "- The subject reference remains geometry truth if references conflict about pose/proportion/perspective.",
            "", "## Intent", s["intent"], "", "## Observe",
        ]
        lines += [f"- {x}" for x in s["observe"]]
        lines += ["", "## Draw"] + [f"- {x}" for x in s["draw"]]
        lines += ["", "## Avoid"] + [f"- {x}" for x in s["avoid"]]
        lines += ["", "## Mandatory review questions"] + [f"- {x}" for x in s["review_questions"]]
        lines += ["", "## Advance only when"] + [f"- {x}" for x in s["advance_when"]]
        lines += ["", "## Suggested inspection intents"] + [f"- {x}" for x in s["suggested_crops"]]
        lines += ["", "## Review artifacts"]
        lines += [f"- {k}: `{v}`" for k,v in self.artifacts.items() if isinstance(v,str)]

        g=self.canvas_scale_guidance
        lines += [
            "", "## Canvas-scale pencil guidance",
            f"- canvas: `{g['canvas'][0]} × {g['canvas'][1]}`",
            f"- recommended width multiplier: **{g['recommended_width_multiplier']}×**",
            f"- minimum visible opacity for this stage: **{g['minimum_visible_opacity']}**",
            f"- minimum visible pressure for this stage: **{g['minimum_visible_pressure']}**",
            "- Guidance only: do not silently rewrite explicit stroke intent.",
            "", "## Checkpoint / resume",
            f"- checkpoint: `{self.checkpoint_resume['checkpoint_path']}`",
            "- `submit_stage_review()` writes a resumable checkpoint automatically.",
            "- Resume with `DrawingRun.resume(output_dir)` after process loss; prepare a fresh review before judging new edits.",
            "", "## Local Review API",
            "Use this when the whole-view comparison leaves a concrete question unresolved.",
            "",
            "```python",
            "local = run.prepare_local_review(",
            '    label="head_face",',
            '    intent="Check face-direction curve and head envelope",',
            "    subject_box=(left, top, right, bottom),",
            "    drawing_box=(left, top, right, bottom),",
            ")",
            "```",
            "",
            "- ROI selection authority: **Agent explicit boxes**.",
            "- Automatic anatomy/landmark detection: **not used**.",
            "- Runtime validates/crops/binds only.",
            "- Each local review also writes a crop-registered subject/drawing overlay and raw absolute-difference view. These are evidence, never a score.",
        ]

        lines += ["", "## Autonomous loop"] + [f"{i+1}. {x}" for i,x in enumerate(self.autonomous_loop)]
        lines += ["", "## Autonomy policy"] + [f"- {x}" for x in self.autonomy_policy]
        lines += ["", "## Escalation policy"] + [f"- {x}" for x in self.escalation_policy]
        lines += ["", "## Bound modular grammar cards"]
        if self.grammar_cards:
            lines += [
                f"- `{card['card_id']}` / `{card['stage']}` — digest `{card['digest']}`"
                for card in self.grammar_cards
            ]
            lines.append(
                "These cards are representation guidance only; subject geometry remains authoritative. "
                "Every authored stroke in this stage retains the bound card id in provenance."
            )
        else:
            lines.append("- _none bound for this condition_")

        p.write_text("\n".join(lines)+"\n",encoding="utf-8")
        return p


def build_worker_packet(
    *,
    stage_spec,
    stage_contract,
    pass_memory,
    artifacts,
    references,
    pass_index: int,
    canvas_scale_guidance,
    checkpoint_resume,
    grammar_cards=(),
) -> AutonomousWorkerPacket:
    mandatory=[]
    if references.task_stage_target is not None:
        mandatory += ["task_target_vs_drawing","task_target_split"]
    mandatory += [
        "subject_vs_drawing",
        "subject_split",
        "subject_drawing_overlay",
        "subject_drawing_absdiff",
        "reference_authority_overview",
        "stage-contract boundary review",
        "Agent-selected local reviews when whole view is insufficient",
    ]

    loop=[
        "Read pass memory first. If state is reopen_restart, treat archived target/downstream reviews as invalidated evidence and rebuild from the restored branch.",
        "If carried concerns exist, re-check them before inventing new work.",
        "Read the frozen stage contract before deciding what belongs in this stage.",
        "Observe the subject at whole-body scale first; choose a local ROI only to answer a concrete uncertainty.",
    ]
    if references.task_stage_target is not None:
        loop.append(
            "Inspect the same-task stage target for current-stage expected placement/abstraction without allowing it to override contradictory subject geometry."
        )
    else:
        loop.append(
            "SUBJECT-ONLY MODE: no same-subject stage target exists. Construct the current stage from the subject geometry, frozen StageContract, and verified prior drawing state."
        )
    loop += [
        "Before drawing, reject vocabulary listed in forbidden_representation.",
        "Draw a bounded set of explicit strokes that serve the current stage ownership.",
        "Render the exact current artifact with prepare_stage_review().",
        "If a whole-view question remains unresolved, choose explicit ROI boxes and call prepare_local_review().",
        "Compare fresh evidence against carried concerns and the inter-pass correction actions recorded in pass memory.",
        "Write contract_findings separately from reference/artifact findings and cite useful local_review_ids.",
        "If any important drawing mismatch remains, choose the highest-impact 1–3 issues and revise locally.",
        "After every drawing mutation, prepare fresh stage/local reviews; never reuse stale judgement.",
        "After carried concerns appear cleared, perform one fresh residual-mismatch sweep that is NOT limited to the prior concern list; inspect the whole view and a high-risk ROI before setting remaining_concerns=[] .",
        "Advance only when both the carried-concern recheck and the fresh residual sweep find no important mismatch at the current stage purpose.",
        "If a later stage exposes an earlier foundational error, reopen the earliest responsible stage.",
    ]

    return AutonomousWorkerPacket(
        schema="img2drawing.autonomous_worker_packet.v7",
        stage=stage_spec.worker_brief(),
        stage_contract=stage_contract.to_dict(),
        pass_index=int(pass_index),
        pass_memory=pass_memory.to_dict(),
        references=references.to_dict(),
        artifacts=artifacts.to_dict(),
        local_review_api={
            "method":"DrawingRun.prepare_local_review",
            "selection_authority":"agent_explicit_boxes",
            "auto_detection":False,
            "required_boxes":["subject_box","drawing_box"],
            "task_target_box":"required" if references.task_stage_target is not None else "must_be_omitted",
            "coordinate_space":"source-image pixel coordinates; (left, top, right, bottom), right/bottom exclusive",
            "suggested_intents":list(stage_spec.suggested_crops),
            "rule":"Choose the ROI because of a concrete visual question. Runtime crops/layouts only; it never detects anatomy or decides similarity.",
            "paired_crop_evidence":["subject_drawing_overlay","subject_drawing_absdiff"],
        },
        canvas_scale_guidance=dict(canvas_scale_guidance),
        checkpoint_resume=dict(checkpoint_resume),
        mandatory_review_views=tuple(mandatory),
        autonomous_loop=tuple(loop),
        autonomy_policy=(
            "Do not stop after a pass merely to ask the user whether to continue.",
            "Do not ask the user to approve routine stage transitions; the worker owns the self-review loop.",
            "Use pass memory to continue unresolved work rather than resetting the stage mentally each pass.",
            "Do not treat inter-pass action provenance as proof that a concern was solved.",
            "Do not let the prior concern list become the review boundary; new defects found in the residual sweep can keep the stage at REVISE.",
            "Never use CV/evidence maps or crop automation as semantic authority.",
        ),
        escalation_policy=(
            "Ask the user only when the source reference is missing/unreadable, the requested goal is internally contradictory, or a choice genuinely changes the intended artistic target.",
            "Repeated visual failure is not itself a reason to ask the user; change observation strategy, crop, stroke plan, or reopen the responsible stage first.",
        ),
        grammar_cards=tuple(dict(card) for card in grammar_cards),
    )
