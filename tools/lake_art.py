"""Living Lake – renders every bitmap the watch face uses into build/res/drawable + art.json (placements).

Phases: night (base), dawn, day, golden. All art drawn at 4x (1920 px) and downsampled to the 480 px face.
"""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))           # tools/
_ROOT = _os.path.dirname(_HERE)                                   # repo root
_RES = _ROOT + '/watchface/src/main/res/'                         # the watch face resources
_OUT = _ROOT + '/out/'                                            # previews, videos, mock-ups (not committed)
import json, math, os, random, sys
sys.path.insert(0, _HERE)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import landmock as LM, combomock as CM, waterlife as WL, hroptions as HO, signsteps as SG, batjetty2 as BJ
from layout15 import TREE_X, SIGN, PLANK, BLOCKS
from landmock import SS, W, P, ov, vgrad, ridge_pts, fill_ridge, disc, mist

OUT = _RES + 'drawable/'
MAN = {}
PHASES = ('night', 'dawn', 'day', 'golden')
BANK = 396
ONLY = set(sys.argv[1:])


def want(k): return not ONLY or any(k.startswith(o) for o in ONLY)


def down(c): return c.resize((480, 480), Image.LANCZOS)


def save(img480, name, box=None):
    """crop a 480px layer to box (x, y, w, h) or its alpha bbox; record the placement"""
    if box is None:
        bb = img480.split()[3].getbbox() or (0, 0, 1, 1)
        box = (bb[0], bb[1], bb[2] - bb[0], bb[3] - bb[1])
    x, y, w, h = box
    img480.crop((x, y, x + w, y + h)).save(OUT + name + '.png', optimize=True)
    MAN[name] = [x, y, w, h]
    return box


def union(boxes):
    x0 = min(b[0] for b in boxes); y0 = min(b[1] for b in boxes)
    x1 = max(b[2] for b in boxes); y1 = max(b[3] for b in boxes)
    return (x0, y0, x1 - x0, y1 - y0)


def frames(name, render, n, pad=2, box=None):
    ims = [down(render(i)) for i in range(n)]
    if box is None:
        bbs = [im.split()[3].getbbox() for im in ims]
        bbs = [b for b in bbs if b]
        b = union(bbs)
        box = (max(0, b[0] - pad), max(0, b[1] - pad), min(480, b[2] + 2 * pad), min(480, b[3] + 2 * pad))
    for i, im in enumerate(ims): save(im, f'{name}_{i:02d}', box)
    MAN[name] = list(box) + [n]
    return box


def tint_img(img, ph):
    if ph not in ('golden', 'dawn'): return img
    t = np.asarray(img).astype(np.float32); k = (1.05, 0.8, 0.66) if ph == 'golden' else (1.0, 0.86, 0.82)
    for c in range(3): t[..., c] = np.clip(t[..., c] * k[c], 0, 255)
    return Image.fromarray(t.astype(np.uint8))


# ------------------------------------------------------------------ sky + land
def sky_land(ph):
    top, mid_, hor = CM.SKY[ph]
    far, snow, mid, pines, lake_top, lake_bot, bank = CM.LAND[ph]
    night = ph == 'night'
    sky = vgrad([(0, top), (210, mid_), (292, hor)])
    if night: LM.stars(sky, 9)
    land = ov()
    farp = ridge_pts(286, 78, 11, peak=(176, 30, 0.45))
    fill_ridge(land, farp, far, 300)
    rng = np.random.default_rng(2); SNOWLINE = 238
    bot = [(x, y + min(22, max(0, SNOWLINE - y)) * (0.75 + 0.35 * math.sin(x * 0.9) + rng.uniform(-0.15, 0.15))) for x, y in farp]
    sm = Image.new('L', (W, W), 0)
    ImageDraw.Draw(sm).polygon([(x * SS, y * SS) for x, y in farp] + [(x * SS, y * SS) for x, y in reversed(bot)], fill=255)
    land.paste(Image.new('RGBA', (W, W), snow + (255,)), (0, 0), sm)
    mist(land, 272, 24, 55 if ph == 'day' else 32, (255, 255, 255) if not night else (120, 130, 170))
    fill_ridge(land, ridge_pts(292, 40, 23), mid, 300)
    pm = ridge_pts(300, 16, 31, freqs=(3, 11, 37, 61), step=1.5)
    pm = [(x, y - (6 if int(x) % 7 < 2 else 0)) for x, y in pm]
    fill_ridge(land, pm, pines, 302)
    above = land.copy()
    m = Image.new('L', (W, W), 0); ImageDraw.Draw(m).rectangle(P(0, 300, 480, 480), fill=255)
    land.paste(vgrad([(300, lake_top), (400, lake_bot)]), (0, 0), m)
    refl = above.crop((0, 200 * SS, W, 302 * SS)).transpose(Image.FLIP_TOP_BOTTOM)
    a = np.asarray(refl).astype(np.float32); a[..., 3] *= 0.45 * np.linspace(1, 0, a.shape[0])[:, None]
    land.alpha_composite(Image.fromarray(a.astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8 * SS)), (0, 300 * SS))
    wl = ov(); d = ImageDraw.Draw(wl); r = random.Random(4)
    for _ in range(40):
        y = r.uniform(304, BANK + 6); x = r.uniform(40, 440); l = r.uniform(8, 40)
        d.line(P(x, y, x + l, y), fill=(255, 255, 255, 50 if not night else 26), width=SS)
    land.alpha_composite(wl)
    fill_ridge(land, ridge_pts(BANK, 24, 41, freqs=(1.1, 2.3, 5)), bank, 480)
    g = ph in ('golden', 'dawn')
    WL.reeds(land, SS, 418, 470, BANK - 16, seed=2, night=night, golden=g)
    WL.reeds(land, SS, 40, 70, BANK - 10, seed=5, night=night, golden=g)
    return sky, land, farp


# ------------------------------------------------------------------ the Nilgiri hills (replaces the snowy peaks)
NIL = {   # far, mid, near, tea rows, forest, mist colour, mist alpha
    'day': ((178, 198, 222), (124, 156, 190), (78, 120, 98), (100, 144, 106), (40, 80, 58), (255, 255, 255), 64),
    'dawn': ((194, 178, 208), (148, 136, 174), (90, 100, 112), (108, 120, 124), (38, 52, 58), (255, 236, 236), 50),
    'golden': ((206, 162, 172), (158, 118, 140), (92, 82, 94), (108, 94, 104), (40, 38, 46), (255, 214, 190), 44),
    'night': ((50, 60, 98), (36, 46, 78), (22, 32, 48), (30, 42, 58), (12, 20, 26), (120, 130, 170), 34),
}


def nilgiri_ridges():
    return (ridge_pts(268, 52, 11, freqs=(0.8, 1.7, 3.2)), ridge_pts(284, 40, 23, freqs=(1.0, 2.1, 3.9)),
            ridge_pts(296, 30, 37, freqs=(1.2, 2.5, 4.6)))


def nilgiri_land(ph):
    top, mid_, hor = CM.SKY[ph]
    lake_top, lake_bot, bank = CM.LAND[ph][4:7]
    far_c, mid_c, near_c, tea_c, forest_c, mc, ma = NIL[ph]
    night = ph == 'night'
    sky = vgrad([(0, top), (210, mid_), (292, hor)])
    if night: LM.stars(sky, 9)
    land = ov()
    farp, midp, nearp = nilgiri_ridges()
    top_c = tuple(int(f + (h_ - f) * 0.45) for f, h_ in zip(far_c, hor))          # a faint, most-distant range
    fill_ridge(land, ridge_pts(258, 46, 51, freqs=(0.6, 1.4, 2.7)), top_c, 300)
    mist(land, 252, 22, int(ma * 0.7), mc)
    fill_ridge(land, farp, far_c, 300)
    mist(land, 264, 26, ma, mc)
    fill_ridge(land, midp, mid_c, 300)
    mist(land, 284, 18, int(ma * 0.8), mc)
    nm = fill_ridge(land, nearp, near_c, 302)
    rows = ov(); rd = ImageDraw.Draw(rows)                       # tea rows on the near hills (left)
    for k in range(1, 12):
        rd.line([(x * SS, (y + k * 3.0) * SS) for x, y in nearp], fill=tea_c + (255,), width=max(1, int(0.9 * SS)))
    a = np.minimum(np.asarray(nm), np.asarray(rows.split()[3])).astype(np.float32)
    a *= np.clip((300 - np.arange(W)[None, :] / SS) / 90, 0, 1)
    rows.putalpha(Image.fromarray(a.astype(np.uint8))); land.alpha_composite(rows)
    fl = ov(); fd = ImageDraw.Draw(fl); r_ = random.Random(31)   # shola canopy + a few tall eucalyptus at the water
    x = -6
    while x < 486:
        r = r_.uniform(2.6, 5.2); fd.ellipse(P(x - r, 301 - r * 1.5, x + r, 302), fill=forest_c + (255,)); x += r * 1.3
    for _ in range(9):
        x = r_.uniform(10, 470); hgt = r_.uniform(12, 20)
        fd.line(P(x, 302, x, 302 - hgt), fill=forest_c + (255,), width=max(1, int(0.8 * SS)))
        fd.ellipse(P(x - 2.4, 302 - hgt - 3, x + 2.4, 302 - hgt * 0.45), fill=forest_c + (255,))
    land.alpha_composite(fl)
    above = land.copy()
    m = Image.new('L', (W, W), 0); ImageDraw.Draw(m).rectangle(P(0, 300, 480, 480), fill=255)
    land.paste(vgrad([(300, lake_top), (400, lake_bot)]), (0, 0), m)
    refl = above.crop((0, 200 * SS, W, 302 * SS)).transpose(Image.FLIP_TOP_BOTTOM)
    a = np.asarray(refl).astype(np.float32); a[..., 3] *= 0.45 * np.linspace(1, 0, a.shape[0])[:, None]
    land.alpha_composite(Image.fromarray(a.astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8 * SS)), (0, 300 * SS))
    wl = ov(); d = ImageDraw.Draw(wl); r = random.Random(4)
    for _ in range(40):
        y = r.uniform(304, BANK + 6); x = r.uniform(40, 440); l = r.uniform(8, 40)
        d.line(P(x, y, x + l, y), fill=(255, 255, 255, 50 if not night else 26), width=SS)
    land.alpha_composite(wl)
    fill_ridge(land, ridge_pts(BANK, 24, 41, freqs=(1.1, 2.3, 5)), bank, 480)
    g = ph in ('golden', 'dawn')
    WL.reeds(land, SS, 418, 470, BANK - 16, seed=2, night=night, golden=g)
    WL.reeds(land, SS, 40, 70, BANK - 10, seed=5, night=night, golden=g)
    return sky, land, farp


def stars_twinkle():
    c = ov(); d = ImageDraw.Draw(c); rng = random.Random(21)
    for _ in range(22):
        x, y = rng.uniform(30, 450), rng.uniform(14, 230); r = rng.choice((0.9, 1.1, 1.3))
        d.ellipse(P(x - r, y - r, x + r, y + r), fill=(255, 252, 240, 255))
    g = c.filter(ImageFilter.GaussianBlur(1.5 * SS)); out = ov(); out.alpha_composite(g); out.alpha_composite(c)
    return out


# ------------------------------------------------------------------ sun, moon and their reflection
def sun_img(low):
    c = ov()
    disc(c, 240, 240, 14, (255, 236, 200) if low else (255, 250, 228), (255, 170, 110) if low else (255, 236, 180), 130 if low else 110)
    return c


def moon_disc(k):
    """phase k: 0 new, 2 first quarter, 4 full, 6 last quarter (northern hemisphere view)"""
    R = 10; S = 8; N = int((2 * R + 4) * S)
    yy, xx = np.mgrid[0:N, 0:N].astype(np.float32)
    cx = cy = N / 2
    u = (xx - cx) / (R * S); v = (yy - cy) / (R * S)
    inside = (u * u + v * v) <= 1
    th = k * math.pi / 4
    xt = math.cos(th) * np.sqrt(np.clip(1 - v * v, 0, 1))
    lit = (u > xt) if k <= 4 else (u < -xt)
    if k == 0: lit = np.zeros_like(inside)
    if k == 4: lit = inside
    rgba = np.zeros((N, N, 4), np.float32)
    rgba[..., 0], rgba[..., 1], rgba[..., 2] = 240, 236, 220
    rgba[..., 3] = np.where(inside, np.where(lit, 255, 46), 0)
    im = Image.fromarray(rgba.astype(np.uint8)).resize((2 * R + 4, 2 * R + 4), Image.LANCZOS)
    return im


def moon_glow():
    c = ov(); g = ov(); d = ImageDraw.Draw(g)
    d.ellipse(P(240 - 40, 240 - 40, 240 + 40, 240 + 40), fill=(180, 190, 230, 80))
    c.alpha_composite(g.filter(ImageFilter.GaussianBlur(10 * 2.2 * SS / 2.2)))
    return c


def reflection(kind, seed):
    """glow + sparkle images centred on x = 240 (the XML moves them under the sun / moon)"""
    warm, night = kind == 'warm', kind == 'moon'
    base_c = (210, 216, 240) if night else ((255, 196, 140) if warm else (255, 250, 232))
    L = 70 if (warm or night) else 46; wdt = 16 if (warm or night) else 22
    glow = ov(); gd = ImageDraw.Draw(glow)
    gd.ellipse(P(240 - wdt, 300, 240 + wdt, 300 + L * 2), fill=base_c + (70 if not night else 45,))
    glow = glow.filter(ImageFilter.GaussianBlur(9 * SS))
    sp = []
    for s in (seed, seed + 7):
        c = ov(); d = ImageDraw.Draw(c); rs = random.Random(s)
        for _ in range(16 if (warm or night) else 11):
            y = 303 + (rs.random() ** 1.3) * L
            spread = 3 + (y - 300) * 0.16
            x = 240 + rs.uniform(-spread, spread); ln = rs.uniform(1.5, 5.5) * (1 - (y - 300) / (L * 1.6))
            a_ = int(rs.uniform(110, 210) * (1 - (y - 300) / (L * 1.3)))
            if ln > 0.6 and a_ > 20: d.line(P(x - ln, y, x + ln, y), fill=base_c + (a_,), width=max(1, int(0.9 * SS)))
        sp.append(c)
    # keep it on the water: fade out before the near shore
    def clip(im):
        a = np.asarray(im).astype(np.float32); ys = np.arange(a.shape[0])[:, None] / SS
        a[..., 3] *= np.clip((374 - ys) / 18, 0, 1) * (ys >= 300)
        return Image.fromarray(a.astype(np.uint8))
    return clip(glow), clip(sp[0]), clip(sp[1])


# ------------------------------------------------------------------ jetty, sign, tree
def jetty(ph):
    """the jetty with a taller plank nailed to its front; the painted gauge outlines are baked, the fill + number are live"""
    c = ov(); BJ.jetty_big(c, ph)
    x0, y0, x1, y1 = PLANK
    wood, dark = SG.tint((146, 104, 66), ph), SG.tint((84, 56, 36), ph)
    d = ImageDraw.Draw(c)
    d.rectangle(P(x0, y0, x1, y1), fill=wood + (255,), outline=dark + (255,), width=int(1.4 * SS))
    rng = np.random.default_rng(3)
    for k in range(10):
        yy = y0 + 3 + k * 2.8; xa = rng.uniform(x0, x0 + 50)
        d.line(P(xa, yy, xa + rng.uniform(40, 90), yy), fill=dark + (60,), width=max(1, int(0.5 * SS)))
    for nx in (x0 + 5, x1 - 5):
        for ny in (y0 + 5, y1 - 5): d.ellipse(P(nx - 1.1, ny - 1.1, nx + 1.1, ny + 1.1), fill=dark + (255,))
    pl = ov(); pd = ImageDraw.Draw(pl); b = BLOCKS
    for k in range(5):
        x = b['x0'] + k * (b['w'] + b['gap'])
        pd.rectangle(P(x, b['cy'] - b['h'] / 2, x + b['w'], b['cy'] + b['h'] / 2), outline=(240, 232, 214, 255), width=int(1.1 * SS))
    c.alpha_composite(BJ.worn(pl, seed=3, lo=0.74))
    return c


def jetty_wear(ph):
    """plank-coloured scuffs laid over the live paint"""
    wood = SG.tint((146, 104, 66), ph)
    rng = np.random.default_rng(11)
    w, h = 130, 28
    n = rng.random((h * 4, w * 4))
    n = np.asarray(Image.fromarray((n * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))).astype(np.float32) / 255
    a = np.clip((n - 0.55) * 9, 0, 1) * 200
    rgba = np.zeros((h * 4, w * 4, 4), np.uint8); rgba[..., :3] = wood; rgba[..., 3] = a.astype(np.uint8)
    return Image.fromarray(rgba).resize((w, h), Image.LANCZOS)


def sign_board(ph):
    """the big trail sign on the right edge, without its number (the XML prints the live step count)"""
    cx, top, W_, H_ = SIGN['cx'], SIGN['top'], SIGN['W'], SIGN['H']
    img = ov(); night = ph == 'night'
    wood, dark, plank = SG.tint((152, 110, 70), ph), SG.tint((90, 60, 38), ph), SG.tint((136, 98, 62), ph)
    sh = ov(); ImageDraw.Draw(sh).ellipse(P(cx - 58, top + H_ + 12, cx + 58, top + H_ + 21), fill=(0, 0, 0, 90))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(3 * SS)))
    d = ImageDraw.Draw(img)
    for lx in (cx - 36, cx + 36): d.rectangle(P(lx - 3, top + H_ - 6, lx + 3, top + H_ + 16), fill=dark + (255,))
    x0, x1, y0, y1 = cx - W_ / 2, cx + W_ / 2, top, top + H_
    d.rounded_rectangle(P(x0, y0, x1, y1), radius=5 * SS, fill=wood + (255,), outline=dark + (255,), width=int(1.8 * SS))
    for yy in (y0 + 14, y0 + 28): d.line(P(x0 + 3, yy, x1 - 3, yy), fill=plank + (255,), width=int(0.8 * SS))
    for nx, ny in ((x0 + 6, y0 + 6), (x1 - 6, y0 + 6), (x0 + 6, y1 - 6), (x1 - 6, y1 - 6)):
        d.ellipse(P(nx - 1.3, ny - 1.3, nx + 1.3, ny + 1.3), fill=dark + (255,))
    return img                                                    # (v1.6.2: no 'STEPS' label, the number speaks for itself)


def sign_lantern():
    """night only (its own image, so the day signs never show it): a small lantern hung off the board and its warm glow"""
    cx, top, W_, H_ = SIGN['cx'], SIGN['top'], SIGN['W'], SIGN['H']
    x0 = cx - W_ / 2; dark = SG.tint((90, 60, 38), 'night')
    img = ov(); g = ov(); ImageDraw.Draw(g).ellipse(P(cx - 84, top - 26, cx + 74, top + H_ + 22), fill=(255, 190, 100, 70))
    img.alpha_composite(g.filter(ImageFilter.GaussianBlur(14 * SS)))
    d = ImageDraw.Draw(img); lx, ly = x0 - 5, top - 4
    d.line(P(x0 + 3, top + 4, lx, ly - 3), fill=dark + (255,), width=int(1.2 * SS))
    d.rectangle(P(lx - 3, ly - 4, lx + 3, ly + 4), fill=(255, 220, 140, 255))
    return img


TREE_S = [0.04, 0.12, 0.24, 0.36, 0.48, 0.6, 0.72, 0.84, 0.96, 1.02]     # stage k shows from 12.5*k % (9 = goal: bloom)


def tree_img(ph, s):
    c = ov()
    LM.tree(c, TREE_X, BANK - 2, s, ph == 'night', seed=5, scale=0.68, flies=False, fixed_depth=4 if s >= 0.1 else None)
    return tint_img(c, ph)


def fireflies(seed):
    c = ov(); d = ImageDraw.Draw(c); rng = random.Random(seed)
    for _ in range(6):
        x, y = rng.uniform(150, 340), rng.uniform(300, 392)
        if rng.random() < 0.5: x, y = rng.uniform(TREE_X - 60, TREE_X + 60), rng.uniform(288, 350)
        d.ellipse(P(x - 1.3, y - 1.3, x + 1.3, y + 1.3), fill=(255, 232, 130, 255))
    out = ov(); out.alpha_composite(c.filter(ImageFilter.GaussianBlur(2.5 * SS))); out.alpha_composite(c.filter(ImageFilter.GaussianBlur(2.5 * SS))); out.alpha_composite(c)
    return out


# ------------------------------------------------------------------ weather
def periodic(draw_one, n, seed):
    """a 480x720 tile whose top and bottom halves are identical (seamless when moved by 360 px)"""
    c = Image.new('RGBA', (960, 720), (0, 0, 0, 0)); d = ImageDraw.Draw(c); rng = random.Random(seed)
    for _ in range(n):
        x, y = rng.uniform(0, 960), rng.uniform(0, 720); a = draw_one(rng)
        for dy in (-720, 0, 720): a(d, x, y + dy)
    c = c.resize((480, 360), Image.LANCZOS)
    out = Image.new('RGBA', (480, 720), (0, 0, 0, 0)); out.paste(c, (0, 0)); out.paste(c, (0, 360))
    return out


def rain_tile():
    def one(rng):
        l = rng.uniform(14, 30); a = rng.randint(70, 140)
        return lambda d, x, y: d.line([(x, y), (x - l * 0.18, y + l)], fill=(220, 230, 245, a), width=2)
    return periodic(one, 90, 5)


def snow_tile():
    def one(rng):
        r = rng.choice((2, 2.5, 3, 4)); a = rng.randint(150, 235)
        return lambda d, x, y: d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, a))
    return periodic(one, 70, 6)


def aod_land():
    """always-on: just the outline of the far range and the shore line, very dim"""
    c = ov(); d = ImageDraw.Draw(c)
    farp, midp, _ = nilgiri_ridges()
    d.line([(x * SS, y * SS) for x, y in farp], fill=(86, 92, 108, 255), width=int(1.3 * SS), joint='curve')
    d.line([(x * SS, y * SS) for x, y in midp], fill=(58, 64, 78, 255), width=int(1.0 * SS), joint='curve')
    d.line(P(40, 300, 440, 300), fill=(52, 58, 70, 255), width=int(1 * SS))
    return c


def clouds():
    c = Image.new('RGBA', (600 * 2, 200 * 2), (0, 0, 0, 0)); d = ImageDraw.Draw(c); rng = random.Random(8)
    for cx, cy, s in ((90, 70, 1.0), (300, 40, 1.3), (500, 90, 0.9), (420, 150, 0.7), (160, 160, 0.6)):
        for _ in range(9):
            r = rng.uniform(18, 34) * s
            x = (cx + rng.uniform(-40, 40) * s) * 2; y = (cy + rng.uniform(-10, 8) * s) * 2
            d.ellipse([x - r * 2, y - r * 1.3, x + r * 2, y + r * 1.3], fill=(250, 250, 252, 120))
    return c.filter(ImageFilter.GaussianBlur(6)).resize((600, 200), Image.LANCZOS)


def fog():
    c = ov()
    for y, h, a in ((262, 30, 110), (300, 22, 90), (338, 30, 80), (380, 26, 60)): mist(c, y, h, a)
    return c


def rain_ripples(i, n=12):
    c = ov(); d = ImageDraw.Draw(c); rng = random.Random(40)
    for k in range(26):
        x, y = rng.uniform(60, 430), rng.uniform(308, 388); t0 = rng.uniform(0, 1)
        age = ((i / n) - t0) % 1.0
        WL.ripples(d, SS, x, y, age * 1.2, n=2, span=1.2, a0=150, rmax=6 + (y - 300) * 0.06)
    return c


# ------------------------------------------------------------------ main
if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    if os.path.exists(_HERE + '/art.json'): MAN.update(json.load(open(_HERE + '/art.json')))
    if want('sky') or want('land'):
        for ph in PHASES:
            sky, land, farp = nilgiri_land(ph)
            save(down(sky), f'sky_{ph}', (0, 0, 480, 304))
            save(down(land), f'land_{ph}')
            if ph == 'night':
                MAN['_farp'] = [[round(x, 1), round(y, 1)] for x, y in farp[::6]]
        save(down(stars_twinkle()), 'stars_tw')
    if want('sun') or want('moon'):
        save(down(sun_img(False)), 'sun_day', (140, 140, 200, 200)); save(down(sun_img(True)), 'sun_low', (140, 140, 200, 200))
        for k in range(8):
            m = moon_disc(k); m.save(OUT + f'moon_{k}.png'); MAN[f'moon_{k}'] = [0, 0, m.width, m.height]
        save(down(moon_glow()), 'moon_glow', (170, 170, 140, 140))
    if want('refl'):
        for kind, seed in (('day', 1), ('warm', 2), ('moon', 3)):
            g, a, b = reflection(kind, seed)
            save(down(g), f'refl_{kind}', (200, 290, 80, 90)); save(down(a), f'spark_{kind}_a', (200, 290, 80, 90)); save(down(b), f'spark_{kind}_b', (200, 290, 80, 90))
    if want('jetty'):
        for ph in PHASES:
            save(down(jetty(ph)), f'jetty_{ph}')
            jetty_wear(ph).save(OUT + f'jwear_{ph}.png'); MAN[f'jwear_{ph}'] = [44, 341, 130, 28]
    if want('sign'):
        for ph in PHASES: save(down(sign_board(ph)), f'sign_{ph}')
        save(down(sign_lantern()), 'sign_lantern')
    if want('tree'):
        boxes = {}
        for ph in PHASES:
            ims = [down(tree_img(ph, s)) for s in TREE_S]
            b = union([im.split()[3].getbbox() for im in ims])
            for k, im in enumerate(ims): save(im, f'tree_{ph}_{k}', b)
    if want('flies'):
        for i, s in enumerate((3, 9, 17)): save(down(fireflies(s)), f'flies_{i}')
    if want('wx'):
        rain_tile().save(OUT + 'wx_rain.png'); snow_tile().save(OUT + 'wx_snow.png'); clouds().save(OUT + 'wx_clouds.png')
        save(down(fog()), 'wx_fog', (0, 220, 480, 200))
        frames('rain_rip', lambda i: rain_ripples(i), 12, box=(40, 296, 400, 100))
    if want('aod'):
        save(down(aod_land()), 'aod_land')
    if want('heart'):
        h = Image.new('RGBA', (48, 44), (0, 0, 0, 0)); d = ImageDraw.Draw(h)
        pts = [(24 + 16 * math.sin(t) ** 3 * 1.35, 22 - (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) * 1.35) for t in np.linspace(0, 6.283, 60)]
        d.polygon(pts, fill=(255, 92, 110, 255)); h.resize((12, 11), Image.LANCZOS).save(OUT + 'heart_small.png')
    json.dump(MAN, open(_HERE + '/art.json', 'w'), indent=0)
    print('static art ok', len(MAN))
