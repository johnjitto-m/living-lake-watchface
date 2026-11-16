"""Living Lake v1.6+ art: a bigger grown tree + drooping variants, the Nilgiri tahr, a soaring crow, a paper sky lantern
and (v1.7) the smooth bird flock. Writes into build/res/drawable and merges placements into art.json."""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))           # tools/
_ROOT = _os.path.dirname(_HERE)                                   # repo root
_RES = _ROOT + '/watchface/src/main/res/'                         # the watch face resources
_OUT = _ROOT + '/out/'                                            # previews, videos, mock-ups (not committed)
import json, math, random, sys
sys.path.insert(0, _HERE); sys.path.insert(0, _HERE)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import lake_art as A, landmock as LM, demo4 as D, demo_tn as TN
import demo16 as X
from layout15 import TREE_X, SIGN
from landmock import SS, W, P, ov

A.MAN.update(json.load(open(_HERE + '/art.json')))
PH = A.PHASES


class A2:                                     # (copied from lake_art2, which renders on import)
    KONRAI = {'night': [(30, 44, 30), (52, 62, 40), (84, 86, 50)]}
    KONRAI_DAY = [(88, 110, 44), (150, 160, 58), (220, 196, 60)]

    @staticmethod
    def chains(img, leaves, n, night, seed=12, long=1.0):
        rng = random.Random(seed); d = ImageDraw.Draw(img)
        c1, c2 = ((255, 214, 60), (240, 186, 40)) if not night else ((120, 104, 40), (100, 86, 34))
        for _ in range(n):
            x, y = rng.choice(leaves); x += rng.uniform(-6, 6); y += rng.uniform(0, 8)
            L = rng.uniform(7, 14) * long
            for k in range(int(L / 1.5)):
                yy = y + k * 1.5; xx = x + math.sin(k * 0.6) * 0.4; r = 1.05 - k * 0.03
                d.ellipse(P(xx - r, yy - r, xx + r, yy + r), fill=(c1 if k % 2 else c2) + (255,))
BASE = A.BANK - 2
ONLY = set(sys.argv[1:])
def want(k): return not ONLY or k in ONLY


def gs(s): return 0.68 + 0.17 * max(0.0, min(1.0, (s - 0.5) / 0.5))       # the tree grows bigger as it nears the goal


def darken(img, k=(0.36, 0.40, 0.52)):
    a = np.asarray(img).astype(np.float32)
    for c in range(3): a[..., c] *= k[c]
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))


def phase_set(day_img, night_img=None):
    """day art -> {night, dawn, day, golden}"""
    return {'day': day_img, 'dawn': A.tint_img(day_img, 'dawn'), 'golden': A.tint_img(day_img, 'golden'),
            'night': night_img if night_img is not None else darken(day_img)}


def save_set(name, sets):
    for ph, im in sets.items(): A.save(A.down(im) if im.width > 480 else im, f'{name}_{ph}')


# ------------------------------------------------------------------ the tree: same branches, sagging when you're behind pace
def tree_d(img, bx, by, s, night=False, seed=5, scale=1.0, droop=0.0, fixed_depth=4):
    rng = random.Random(seed); d = ImageDraw.Draw(img)
    trunk = (70, 48, 34) if not night else (30, 26, 28)
    greens = [(46, 104, 52), (70, 140, 64), (112, 170, 80)] if not night else [(20, 44, 38), (30, 62, 52), (54, 90, 84)]
    if droop:
        tired = [(78, 104, 52), (110, 128, 62), (150, 156, 82)] if not night else [(32, 44, 34), (46, 58, 44), (72, 84, 64)]
        greens = [tuple(int(g * (1 - droop) + t * droop) for g, t in zip(gc, tc)) for gc, tc in zip(greens, tired)]
    if s < 0.1:
        LM.tree(img, bx, by, s, night, seed, scale, flies=False); return
    g = min(s, 1.0); H = (34 + 92 * g) * scale; depth = fixed_depth; leaves = []

    def br(x, y, ang, ln, wd, dep):
        if droop and dep < depth:                                    # outer branches sag towards the ground
            k = droop * (0.12 + 0.30 * (depth - dep) / depth)
            ang = ang + k if ang > math.pi / 2 else ang - k
        x2 = x + math.cos(ang) * ln; y2 = y - math.sin(ang) * ln
        d.line(P(x, y, x2, y2), fill=trunk + (255,), width=max(1, int(wd * SS)))
        d.ellipse(P(x2 - wd / 2, y2 - wd / 2, x2 + wd / 2, y2 + wd / 2), fill=trunk + (255,))
        if dep == 0: leaves.append((x2, y2)); return
        n = 2 if dep > 1 or rng.random() < 0.5 else 3
        for i in range(n):
            spread = rng.uniform(0.32, 0.62)
            a = ang + (spread if i == 0 else -spread if i == 1 else rng.uniform(-0.15, 0.15))
            br(x2, y2, a, ln * rng.uniform(0.66, 0.8), wd * 0.66, dep - 1)
        if dep <= 2: leaves.append((x2, y2))

    br(bx, by, math.pi / 2 + rng.uniform(-0.06, 0.06), H * 0.38, (3 + 6 * g) * scale, depth)
    R = (7 + 14 * g) * scale * (1 - 0.14 * droop)
    fol = ov(); fd = ImageDraw.Draw(fol)
    for layer, col in enumerate(greens):
        for (x, y) in leaves:
            for _ in range(2 if layer < 2 else 1):
                r = R * rng.uniform(0.55, 0.95) * (1.0 - layer * 0.18)
                ox, oy = rng.uniform(-R * 0.4, R * 0.4) - layer * R * 0.18, rng.uniform(-R * 0.4, R * 0.3) - layer * R * 0.22 + droop * R * 0.4
                fd.ellipse(P(x + ox - r, y + oy - r, x + ox + r, y + oy + r), fill=col + (255,))
    img.alpha_composite(fol)
    if s >= 1:
        d = ImageDraw.Draw(img); pet = (255, 182, 200) if not night else (255, 214, 226)
        for (x, y) in leaves:
            for _ in range(3):
                px, py = x + rng.uniform(-R * 0.8, R * 0.8), y + rng.uniform(-R * 0.8, R * 0.5)
                d.ellipse(P(px - 1.6 * scale, py - 1.6 * scale, px + 1.6 * scale, py + 1.6 * scale), fill=pet + (255,))
    if droop:                                                        # a few dry leaves under it
        d = ImageDraw.Draw(img); r2 = random.Random(9)
        for _ in range(9):
            px, py = bx + r2.uniform(-30, 30) * scale, by + r2.uniform(-1, 4)
            d.ellipse(P(px - 1.6, py - 0.8, px + 1.6, py + 0.8), fill=((156, 140, 70) if not night else (50, 46, 30)) + (255,))


def tree_img(ph, s, droop=0.0):
    c = ov(); tree_d(c, TREE_X, BASE, s, ph == 'night', scale=gs(s), droop=droop)
    return A.tint_img(c, ph)


def konrai_img(ph, s, droop=0.0):
    c = ov(); night = ph == 'night'
    if s < 0.1:
        LM.tree(c, TREE_X, BASE, s, night, seed=5, scale=0.68, flies=False); return A.tint_img(c, ph)
    leaves = A2.KONRAI.get(ph, A2.KONRAI_DAY)
    if droop: leaves = [tuple(int(v * 0.85 + 30 * 0.15) for v in col) for col in leaves]
    lv = D.tree2(c, TREE_X, BASE, s, night, seed=5, scale=gs(s), flies=False, opt={'leaves': leaves, 'droop': droop} if droop else {'leaves': leaves})
    if s >= 0.3:
        n = int(6 + 22 * min(s, 1.0)) if s < 1 else 40
        if droop: n = max(4, n // 3)
        A2.chains(c, lv, n, night, long=(1.0 if s < 1 else 1.35) * (0.7 if droop else 1))
    return A.tint_img(c, ph)


if want('tree'):
    for kind, fn in (('tree', tree_img), ('treek', konrai_img)):
        for ph in PH:
            ims = [A.down(fn(ph, s)) for s in A.TREE_S]
            drs = [A.down(fn(ph, s, 0.85)) for s in A.TREE_S[:9]]
            b = A.union([im.split()[3].getbbox() for im in ims + drs])
            for k, im in enumerate(ims): A.save(im, f'{kind}_{ph}_{k}', b)
            for k, im in enumerate(drs):
                if k > 0: A.save(im, f'{kind}d_{ph}_{k}', b)                # (stage 0 is a sprout: it never droops)
    print('trees ok', A.MAN['tree_day_9'])

# ------------------------------------------------------------------ Nilgiri tahr (some dawns), the crow, the lantern
if want('wild'):
    c = ov(); X.tahr_scene(c, 6.5, False)
    sets = phase_set(c, darken(c, (0.42, 0.42, 0.55)))
    for ph, im in sets.items(): A.save(A.down(im), f'tahr_{ph}', (372, 216, 80, 40))
    # crow, gliding (drawn at 2x so it stays crisp when the XML scales it)
    c = Image.new('RGBA', (W, W), (0, 0, 0, 0)); X.crow(c, 240, 240, 1.25, 0, 1.0, 0.15)
    im = A.down(c); bb = im.split()[3].getbbox(); A.save(im, 'crow', (bb[0] - 1, bb[1] - 1, bb[2] - bb[0] + 2, bb[3] - bb[1] + 2))
    # paper sky lantern with its glow (biggest size; the XML shrinks it as it rises)
    c = ov(); sc = 2.2
    X.glow(c, 240, 240, 17, (255, 150, 60), 120, 7)
    d = ImageDraw.Draw(c); x, y = 240, 240
    d.polygon(P(x - 4.2 * sc, y - 6 * sc, x + 4.2 * sc, y - 6 * sc, x + 3.2 * sc, y + 5 * sc, x - 3.2 * sc, y + 5 * sc), fill=(255, 176, 80, 255))
    d.polygon(P(x - 2.6 * sc, y - 4.5 * sc, x + 2.6 * sc, y - 4.5 * sc, x + 2 * sc, y + 3.5 * sc, x - 2 * sc, y + 3.5 * sc), fill=(255, 220, 140, 255))
    d.ellipse(P(x - 1.4 * sc, y + 3 * sc, x + 1.4 * sc, y + 5.6 * sc), fill=(255, 250, 220, 255))
    d.line(P(x - 4.2 * sc, y - 6 * sc, x + 4.2 * sc, y - 6 * sc), fill=(220, 120, 60, 255), width=max(1, int(0.6 * SS)))
    im = A.down(c); A.save(im, 'lantern', (240 - 32, 240 - 32, 64, 64))
    print('wild ok', A.MAN['crow'], A.MAN['lantern'])



# ------------------------------------------------------------------ v1.7: a smooth bird flock (seamless flap loop, no drift inside the frames)
N_FLOCK = 16


def flock_frame(i, n=5, x0=240, y0=210):
    c = ov(); lay = ov(); d = ImageDraw.Draw(lay); col = (44, 50, 64, 240); rng = random.Random(3)
    for b in range(n):
        side = 1 if b % 2 else -1; k = (b + 1) // 2
        x = x0 - k * 13 + rng.uniform(-2, 2); y = y0 + side * k * 7 + rng.uniform(-1.5, 1.5)
        s = 5.4 - k * 0.5
        ph = 2 * math.pi * i / N_FLOCK + b * 1.3                       # exactly one flap per loop, each bird at its own point
        a = s * 0.5 * math.sin(ph); lift = 0.6 * math.cos(ph)              # the body rises a touch on the down-stroke
        for sd in (-1, 1):
            pts = [(x + sd * s, y - a - lift), (x + sd * s * 0.45, y - a * 0.35 - s * 0.22 - lift), (x, y - lift)]
            d.line([(px * SS, py * SS) for px, py in pts], fill=col, width=max(1, int(1.35 * SS)), joint='curve')
    c.alpha_composite(lay); return c


if want('flock'):
    A.frames('birds', flock_frame, N_FLOCK, pad=3)
    print('flock ok', A.MAN['birds'])

json.dump(A.MAN, open(_HERE + '/art.json', 'w'), indent=0)
print('art3 ok', len(A.MAN))
