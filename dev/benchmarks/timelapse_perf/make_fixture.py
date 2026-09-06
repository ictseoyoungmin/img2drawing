from __future__ import annotations

import json
import math
from pathlib import Path

W, H = 1024, 1536


def line(x0, y0, x1, y1, n=12, p0=.2, p1=.7):
    return [[
        x0 + (x1 - x0) * i / (n - 1),
        y0 + (y1 - y0) * i / (n - 1),
        p0 + (p1 - p0) * i / (n - 1),
    ] for i in range(n)]


def bezier(p0, p1, p2, p3, n=20, pr0=.25, pr1=.75):
    out = []
    for i in range(n):
        t = i / (n - 1)
        u = 1 - t
        x = u**3*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t**3*p3[0]
        y = u**3*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t**3*p3[1]
        out.append([x, y, pr0 + (pr1 - pr0) * t])
    return out


def wave(x0, x1, y, amp, cycles, n=24, p=.55):
    return [[
        x0 + (x1 - x0) * i / (n - 1),
        y + amp * math.sin(2 * math.pi * cycles * i / (n - 1)),
        p * (.75 + .25 * math.sin(math.pi * i / (n - 1))),
    ] for i in range(n)]


def build_fixture():
    strokes = []
    add = lambda kind, label, pts: strokes.append({"kind": kind, "label": label, "points": pts})
    for i in range(8):
        add("construction", f"construction_{i}", line(80, 100+i*32, 430+i*8, 115+i*30, n=10, p0=.12, p1=.30))
    curves = [
        ((90,450),(240,350),(390,650),(520,520)),
        ((130,620),(260,760),(420,490),(560,720)),
        ((560,180),(680,100),(830,300),(930,220)),
        ((540,360),(690,520),(850,260),(950,520)),
    ]
    for i, c in enumerate(curves):
        add("form", f"form_curve_{i}", bezier(*c, n=26, pr0=.25, pr1=.72))
    for i in range(4):
        add("continuous", f"continuous_{i}", bezier((80,820+i*35),(250,760+i*20),(420,920+i*15),(590,850+i*30), n=30, pr0=.50, pr1=.62))
    for i in range(8):
        add("hatch", f"hatch_a_{i}", line(630+i*20,650,540+i*20,830,n=8,p0=.12,p1=.24))
    for i in range(8):
        add("hatch", f"hatch_b_{i}", line(540+i*20,690,670+i*16,825,n=8,p0=.12,p1=.22))
    for i in range(8):
        add("form", f"wave_{i}", wave(620+i*7,900-i*5,940+i*28,18+(i%3)*7,1.1+(i%2)*.3,n=28,p=.50+.03*i))
    for i in range(4):
        add("accent", f"accent_{i}", bezier((120+i*45,1230),(230+i*35,1170),(340+i*32,1350),(470+i*28,1270),n=18,pr0=.35,pr1=.92))
    for i in range(4):
        pts = line(600+i*60,1260,560+i*72,1460,n=22,p0=.08,p1=.95 if i%2==0 else .60)
        if i % 2:
            pts = list(reversed(pts))
        add("accent", f"taper_{i}", pts)
    assert len(strokes) == 48
    return {"width": W, "height": H, "strokes": strokes}


if __name__ == "__main__":
    out = Path(__file__).with_name("fixture_48.json")
    out.write_text(json.dumps(build_fixture(), indent=2), encoding="utf-8")
    print(out)
