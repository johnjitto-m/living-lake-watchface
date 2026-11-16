"""lake_reflect.ttf: the clock font flipped upside down (a reflection), foreshortened, with a water ripple baked
into the outlines. The ripple only depends on height, so it runs continuously across all digits.
Advance widths and kerning are untouched, so the reflection lines up exactly under the real time."""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))           # tools/
_ROOT = _os.path.dirname(_HERE)                                   # repo root
_RES = _ROOT + '/watchface/src/main/res/'                         # the watch face resources
_OUT = _ROOT + '/out/'                                            # previews, videos, mock-ups (not committed)
import math
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen

SRC = _RES + 'font/lake_time.ttf'
OUT = _RES + 'font/lake_reflect.ttf'
SQUASH = 0.62          # foreshortening on the water
LAMBDA = 170.0         # ripple wavelength (font units)
A_NEAR, A_FAR = 6.0, 26.0


def flatten(rec):
    """RecordingPen value -> list of closed polylines"""
    out, cur, start = [], [], None
    def lin(p0, p1, step=24.0):
        n = max(1, int(math.hypot(p1[0] - p0[0], p1[1] - p0[1]) / step))
        return [(p0[0] + (p1[0] - p0[0]) * k / n, p0[1] + (p1[1] - p0[1]) * k / n) for k in range(1, n + 1)]
    for op, args in rec:
        if op == 'moveTo':
            cur = [args[0]]; start = args[0]
        elif op == 'lineTo':
            cur += lin(cur[-1], args[0])
        elif op == 'qCurveTo':
            pts = list(args)
            if pts[-1] is None: pts = pts[:-1]; pts.append(pts[0])         # closed all-off-curve contour (rare)
            on, offs = pts[-1], pts[:-1]
            p0 = cur[-1]
            segs = []
            for i, c in enumerate(offs):
                end = on if i == len(offs) - 1 else ((c[0] + offs[i + 1][0]) / 2, (c[1] + offs[i + 1][1]) / 2)
                segs.append((c, end))
            for c, end in segs:
                for k in range(1, 9):
                    t = k / 8
                    cur.append(((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t * t * end[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t * t * end[1]))
                p0 = end
        elif op == 'curveTo':
            p0 = cur[-1]; c1, c2, end = args
            for k in range(1, 13):
                t = k / 12
                cur.append(tuple((1 - t) ** 3 * p0[j] + 3 * (1 - t) ** 2 * t * c1[j] + 3 * (1 - t) * t * t * c2[j] + t ** 3 * end[j] for j in range(2)))
        elif op in ('closePath', 'endPath'):
            if cur:
                cur += lin(cur[-1], start)
                out.append(cur)
            cur = []
    return out


f = TTFont(SRC)
gs = f.getGlyphSet(); cmap = f.getBestCmap()
names = [cmap[ord(c)] for c in '0123456789:']
H = max(f['glyf'][n].yMax for n in names if hasattr(f['glyf'][n], 'yMax'))
TOP = H * SQUASH


def warp(x, y):
    yr = (H - y) * SQUASH                                  # flipped: the digit's foot touches the water at the top
    far = 1 - yr / TOP                                     # 0 at the waterline, 1 at the far end
    amp = A_NEAR + (A_FAR - A_NEAR) * max(0.0, far)
    return x + amp * math.sin(2 * math.pi * yr / LAMBDA + 0.6), yr


for n in names:
    rec = DecomposingRecordingPen(gs); gs[n].draw(rec)
    pen = TTGlyphPen(None)
    for poly in flatten(rec.value):
        pts = [warp(x, y) for x, y in poly]
        pts = pts[::-1]                                    # flipping reverses winding; restore it
        pen.moveTo(pts[0])
        for p in pts[1:]: pen.lineTo(p)
        pen.closePath()
    g = pen.glyph(); g.recalcBounds(f['glyf'])
    f['glyf'][n] = g
    adv, _ = f['hmtx'][n]
    f['hmtx'][n] = (adv, getattr(g, 'xMin', 0))
for rec in f['name'].names:
    if rec.nameID in (1, 3, 4, 6, 16):
        s = rec.toUnicode().replace('Inter Display', 'Lake Reflect').replace('InterDisplay', 'LakeReflect')
        rec.string = s
f.save(OUT)
print('reflect font ok, H =', H, 'top =', round(TOP))
