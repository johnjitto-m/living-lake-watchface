"""Illustrated clouds: flat bases, billowy sunlit tops, shaded undersides, coloured by the time of day."""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))           # tools/
_ROOT = _os.path.dirname(_HERE)                                   # repo root
_RES = _ROOT + '/watchface/src/main/res/'                         # the watch face resources
_OUT = _ROOT + '/out/'                                            # previews, videos, mock-ups (not committed)
import math, random, sys
sys.path.insert(0, _HERE)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from landmock import SS, W, P, ov

PAL = {   # top light, body, underside, rim
    'day':    ((255, 255, 255), (238, 243, 250), (196, 208, 226), (255, 255, 255)),
    'golden': ((255, 228, 204), (238, 188, 176), (176, 120, 146), (255, 206, 150)),
    'dawn':   ((255, 236, 226), (232, 200, 210), (170, 142, 176), (255, 220, 200)),
    'night':  ((118, 128, 160), (78, 88, 120), (40, 48, 80), (176, 186, 220)),
    'rain':   ((196, 204, 216), (160, 168, 184), (112, 120, 138), (210, 216, 226)),
}


def _bumps(cx, base, w, h, rng):
    n = max(4, int(w / 16)); out = []
    for i in range(n):
        u = (i + 0.5) / n - 0.5
        prof = math.exp(-(u / 0.34) ** 2)                 # taller in the middle
        r = h * (0.32 + 0.5 * prof) * rng.uniform(0.85, 1.12)
        x = cx + u * w + rng.uniform(-3, 3)
        y = base - r * (0.55 + 0.25 * prof) + rng.uniform(-2, 2)
        out.append((x, y, r))
        for _ in range(2):                                   # small secondary puffs break up the scallops
            a = rng.uniform(math.pi * 1.1, math.pi * 1.9); rr = r * rng.uniform(0.35, 0.55)
            out.append((x + math.cos(a) * r * 0.8, y + math.sin(a) * r * 0.75, rr))
    return out


def _mask(bumps, base, extra=0.0, dy=0.0, k=1.0):
    m = Image.new('L', (W, W), 0); d = ImageDraw.Draw(m)
    for x, y, r in bumps:
        rr = r * k + extra
        d.ellipse(P(x - rr, y + dy - rr, x + rr, y + dy + rr), fill=255)
    d.rectangle(P(0, base, 480, 480), fill=0)             # flat base
    return m


def _grad(y0, y1, top, body, under):
    ys = np.arange(W)[:, None] / SS
    t = np.clip((ys - y0) / max(1, y1 - y0), 0, 1)
    g = np.zeros((W, 1, 3), np.float32)
    for c in range(3):
        g[..., c] = np.where(t < 0.5, top[c] + (body[c] - top[c]) * (t / 0.5), body[c] + (under[c] - body[c]) * ((t - 0.5) / 0.5))
    return Image.fromarray(np.repeat(g, W, axis=1).astype(np.uint8), 'RGB').convert('RGBA')


def cumulus(img, cx, base, w, h, pal='day', seed=1, alpha=250, sun_dx=-1, bumps=None):
    """one cloud: opaque colour everywhere, shape only in alpha (no dark fringes)"""
    rng = random.Random(seed); top, body, under, rim = PAL[pal]
    b = bumps or _bumps(cx, base, w, h, rng)
    m = _mask(b, base)
    y0 = min(y - r for x, y, r in b)
    col = _grad(y0, base, top, body, under)
    hl = ov(); hd = ImageDraw.Draw(hl)                                  # sunlit caps
    for x, y, r in b:
        rr = r * 0.74
        hd.ellipse(P(x + sun_dx * r * 0.2 - rr, y - r * 0.26 - rr, x + sun_dx * r * 0.2 + rr, y - r * 0.26 + rr), fill=top + (200,))
    col.alpha_composite(hl.filter(ImageFilter.GaussianBlur(2.2 * SS)))
    sh = ov(); ImageDraw.Draw(sh).rectangle(P(cx - w, base - 5, cx + w, base + 2), fill=under + (170,))   # shaded base
    col.alpha_composite(sh.filter(ImageFilter.GaussianBlur(2.0 * SS)))
    a = np.asarray(m.filter(ImageFilter.GaussianBlur(0.6 * SS))).astype(np.float32) * (alpha / 255)
    ys = np.arange(W)[:, None] / SS
    a *= np.clip((base + 0.5 - ys) / 3.0, 0.55, 1)                     # the flat base is a little softer
    col.putalpha(Image.fromarray(a.astype(np.uint8)))
    img.alpha_composite(col)


def towering(img, cx, base, pal='day', seed=5, sun_dx=-1):
    """a monsoon cumulus tower rising behind the peaks"""
    cumulus(img, cx, base, 150, 56, pal, seed, sun_dx=sun_dx)
    cumulus(img, cx + 6, base - 34, 112, 54, pal, seed + 1, sun_dx=sun_dx)
    cumulus(img, cx - 4, base - 66, 80, 46, pal, seed + 2, sun_dx=sun_dx)
    cumulus(img, cx + 4, base - 92, 50, 34, pal, seed + 3, sun_dx=sun_dx)


def stratus(img, y, x0, x1, thick, pal='rain', seed=7, alpha=236):
    """a long grey band with a scalloped underside (northeast-monsoon sky)"""
    rng = random.Random(seed); top, body, under, rim = PAL[pal]
    m = Image.new('L', (W, W), 0); d = ImageDraw.Draw(m)
    x = x0
    while x < x1:
        r = rng.uniform(thick * 0.5, thick * 0.9)
        d.ellipse(P(x - r * 1.8, y - r * 0.8, x + r * 1.8, y + r * 0.7), fill=255)
        x += r * 1.6
    col = _grad(y - thick, y + thick * 0.8, top, body, under)
    a = np.asarray(m.filter(ImageFilter.GaussianBlur(1.0 * SS))).astype(np.float32) * (alpha / 255)
    col.putalpha(Image.fromarray(a.astype(np.uint8)))
    img.alpha_composite(col)


def rain_curtain(img, x0, x1, y0, y1, seed=3, col=(150, 160, 180)):
    rng = random.Random(seed); lay = Image.new('RGBA', (W, W), col + (0,)); d = ImageDraw.Draw(lay)
    for _ in range(int((x1 - x0) * 1.2)):
        x = rng.uniform(x0, x1); l = rng.uniform(20, 60); y = rng.uniform(y0, y0 + 20)
        d.line(P(x, y, x - 4, y + l), fill=col + (rng.randint(40, 90),), width=max(1, int(0.7 * SS)))
    a = np.asarray(lay).astype(np.float32); yy = np.arange(W)[:, None] / SS
    a[..., 3] *= np.clip((y1 - yy) / (y1 - y0), 0, 1)
    img.alpha_composite(Image.fromarray(a.astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8 * SS)))


# ready-made skies (kept clear of the time, the date and the heart rate: x 120-360, y < 182) -------
def fair(img, ph):
    pal = 'day' if ph == 'day' else ph
    cumulus(img, 92, 226, 96, 28, pal, 3); cumulus(img, 396, 214, 104, 32, pal, 4)
    cumulus(img, 252, 250, 64, 18, pal, 6); cumulus(img, 62, 132, 58, 18, pal, 8); cumulus(img, 424, 126, 52, 16, pal, 9)


def tower_bumps(cx, base, seed=5):
    """one tall cumulus: rounded lobes up a column that narrows, flat base only at the bottom"""
    rng = random.Random(seed); out = []
    levels = ((0, 150, 30), (26, 120, 28), (52, 92, 25), (76, 66, 21), (96, 40, 16))
    for i, (dy, w, r0) in enumerate(levels):
        n = max(2, int(w / 26))
        for k in range(n):
            u = (k + 0.5) / n - 0.5
            r = r0 * rng.uniform(0.8, 1.1) * (1 - 0.35 * abs(u) * 2)
            out.append((cx + u * w + rng.uniform(-3, 3) + i * 1.5, base - 10 - dy - r * 0.5 + rng.uniform(-2, 2), r))
            a = rng.uniform(math.pi * 1.1, math.pi * 1.9)
            out.append((out[-1][0] + math.cos(a) * r * 0.8, out[-1][1] + math.sin(a) * r * 0.7, r * rng.uniform(0.35, 0.5)))
    return out


def monsoon(img, ph):
    pal = 'day' if ph == 'day' else ph
    cumulus(img, 404, 266, 0, 0, pal, 5, bumps=tower_bumps(406, 266))
    cumulus(img, 104, 236, 118, 32, pal, 11); cumulus(img, 56, 140, 60, 18, pal, 12)


def ne_monsoon(img, ph):
    stratus(img, 60, -20, 500, 22, 'rain', 7, 210)
    stratus(img, 118, -20, 110, 16, 'rain', 8, 220); stratus(img, 120, 372, 500, 16, 'rain', 13, 220)
    stratus(img, 204, 170, 500, 22, 'rain', 9, 236); stratus(img, 238, -20, 230, 18, 'rain', 10, 236)
    rain_curtain(img, 300, 430, 220, 292); rain_curtain(img, 40, 140, 250, 300, seed=5)


def golden_clouds(img, ph):
    cumulus(img, 104, 230, 112, 30, 'golden', 3, sun_dx=1); cumulus(img, 392, 222, 100, 28, 'golden', 4, sun_dx=1)
    cumulus(img, 62, 130, 60, 18, 'golden', 8, sun_dx=1); stratus(img, 252, 170, 320, 8, 'golden', 12, 200)


def night_clouds(img, ph):
    cumulus(img, 110, 230, 104, 30, 'night', 3); cumulus(img, 392, 218, 110, 32, 'night', 4)
    cumulus(img, 424, 126, 52, 16, 'night', 9)
