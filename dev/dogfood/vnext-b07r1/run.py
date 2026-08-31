"""Re-author the B08 dogfood value pass through fill_region and measure the cost.

The B08 croquis reached its value family with 1,398 hand-rolled hatch strokes and a
313,391-line canonical session. The drawing is unchanged here; only the way the value
pass is authored changes.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "skills" / "img2drawing" / "src"))

from img2drawing import DrawingSession, PoseObservation  # noqa: E402

SUBJECT = ROOT / "drawings" / "subject.png"

# the same regions the B08 session hatched by hand
JACKET = [(352, 318), (400, 296), (444, 288), (486, 292), (520, 300), (544, 341), (556, 400),
          (568, 462), (578, 502), (589, 546), (589, 585), (600, 618), (611, 656), (602, 691),
          (596, 731), (591, 776), (546, 830), (493, 830), (432, 819), (370, 803), (322, 781),
          (330, 743), (340, 701), (343, 669), (331, 643), (312, 618), (296, 590), (294, 556),
          (297, 502), (300, 456), (304, 410), (322, 362)]
SOCK_F = [(330, 892), (373, 882), (413, 882), (441, 897), (429, 958), (418, 1002), (403, 1060),
          (396, 1102), (391, 1160), (386, 1202), (383, 1242), (337, 1242), (329, 1202),
          (322, 1160), (327, 1102), (336, 1062), (344, 1020), (341, 958)]
SOCK_N = [(494, 942), (540, 934), (578, 936), (600, 944), (597, 1002), (601, 1042), (602, 1102),
          (607, 1162), (609, 1204), (611, 1244), (614, 1288), (560, 1290), (552, 1246),
          (539, 1202), (531, 1142), (532, 1082), (521, 1042), (508, 1000)]
BOOT_F = [(333, 1252), (390, 1247), (397, 1259), (401, 1302), (412, 1334), (436, 1356),
          (448, 1379), (436, 1398), (404, 1407), (366, 1408), (334, 1400), (325, 1382),
          (326, 1348), (329, 1302)]
BOOT_N = [(557, 1296), (619, 1296), (625, 1309), (632, 1352), (650, 1392), (690, 1422),
          (736, 1446), (718, 1466), (662, 1477), (600, 1474), (566, 1456), (557, 1420),
          (555, 1362)]
HOLSTER = [(572, 828), (602, 822), (615, 850), (616, 900), (604, 932), (580, 930), (569, 890)]
BARREL = [(243, 97), (263, 96), (324, 326), (307, 326)]
RECEIVER = [(330, 470), (378, 464), (422, 664), (376, 664)]
STOCK = [(376, 668), (422, 668), (432, 740), (444, 812), (452, 866), (432, 878), (405, 866),
         (398, 812), (388, 740)]

OBS = PoseObservation(
    support_side="near (image-right) leg forward and lower",
    flow="head turns back over the shoulder; torso falls away image-right",
    head_ribcage_pelvis="head rotated back over a three-quarter ribcage",
    shoulder_pelvis="shoulders drop image-right against the pelvis tilt",
    silhouette_keys=("black tactical kit", "bare thigh gap", "slung rifle"),
    ground_relation="both boots on one ground plane",
)


def main(out_dir: Path) -> dict:
    s = DrawingSession.create(subject=SUBJECT, output_dir=out_dir,
                              session_id="b07r1-value-pass", metadata={"dogfood": "B07-R1"})
    oid = s.observe(OBS, observation_id="observation-0001")

    # measured off the subject: jacket sits lighter than the socks and boots,
    # the rifle is the darkest shape and lies in front of everything.
    plan = [
        (JACKET, 120, 74.0, "jacket_tone", [
            {"path": [(524, 344), (542, 420), (554, 500), (562, 560)], "width": 26.0,
             "strength": 0.55, "note": "lit side of the back"},
            {"path": [(366, 352), (342, 404), (330, 464), (330, 578), (338, 614)],
             "width": 10.0, "strength": 0.8, "note": "break between far arm and torso"}]),
        (SOCK_F, 70, 82.0, "far_sock_tone", [
            {"path": [(338, 950), (330, 1120), (336, 1232)], "width": 6.0, "strength": 1.0,
             "note": "rim light down the shin"}]),
        (SOCK_N, 70, 96.0, "near_sock_tone", [
            {"path": [(512, 1000), (534, 1120), (551, 1246)], "width": 6.0, "strength": 1.0,
             "note": "rim light down the shin"}]),
        (BOOT_F, 50, 78.0, "far_boot_tone", [
            {"path": [(361, 1272), (389, 1268)], "width": 5.0, "strength": 1.0},
            {"path": [(365, 1296), (395, 1292)], "width": 5.0, "strength": 1.0},
            {"path": [(370, 1320), (401, 1317)], "width": 5.0, "strength": 1.0}]),
        (BOOT_N, 50, 78.0, "near_boot_tone", [
            {"path": [(601, 1310), (631, 1306)], "width": 5.0, "strength": 1.0},
            {"path": [(604, 1336), (638, 1334)], "width": 5.0, "strength": 1.0},
            {"path": [(609, 1362), (645, 1362)], "width": 5.0, "strength": 1.0}]),
        (HOLSTER, 50, 80.0, "holster_tone", []),
        (BARREL, 35, 15.0, "rifle_barrel_tone", []),
        (RECEIVER, 35, 15.0, "rifle_receiver_tone", []),
        (STOCK, 35, 15.0, "rifle_stock_tone", []),
    ]
    for polygon, value, angle, part, reserved in plan:
        s.fill_region(polygon, value=value, part=part, angle=angle, reserved=reserved,
                      observation_id=oid, reason=f"observed value {value} for {part}")

    ir = s.current_ir()
    text = json.dumps(json.loads(s.checkpoint_path.read_text()), indent=2)
    return {
        "canonical_actions": len(s._agent.history.actions),
        "rendered_strokes": len(ir.strokes),
        "stored_points": sum(len(st.points) for st in ir.strokes),
        "session_lines": len(text.splitlines()),
        "session_bytes": len(text.encode()),
    }


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/tmp/b07r1")
    print(json.dumps(main(out), indent=2))
