"""Living Landscape – concept mock-ups: 3 scenes x (day, night) + the tree growth strip."""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))           # tools/
_ROOT = _os.path.dirname(_HERE)                                   # repo root
_RES = _ROOT + '/watchface/src/main/res/'                         # the watch face resources
_OUT = _ROOT + '/out/'                                            # previews, videos, mock-ups (not committed)
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SS = 4
W = 480 * SS
FT = _HERE + '/fonts/inter/'


def F(name, size): return ImageFont.truetype(FT + name, int(size * SS))
def P(*v): return [x * SS for x in v]
def lerp(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(len(a)))
def ov(): return Image.new('RGBA', (W, W), (0, 0, 0, 0))


def vgrad(stops, h=480):
    """stops: [(y, color), ...] in face px -> RGBA image"""
    arr = np.zeros((W, W, 4), np.uint8)
    ys = np.arange(W) / SS
    for c in range(3):
        arr[..., c] = np.interp(ys, [s[0] for s in stops], [s[1][c] for s in stops])[:, None]
    arr[..., 3] = 255
    return Image.fromarray(arr, 'RGBA')


def ridge_pts(y0, amp, seed, freqs=(1.3, 2.9, 6.1, 13.0), x0=-10, x1=490, step=2, peak=None):
    rng = np.random.default_rng(seed)
    ph = rng.random(len(freqs)) * 6.28
    xs = np.arange(x0, x1 + step, step, dtype=float)
    y = np.zeros_like(xs)
    for k, f in enumerate(freqs):
        y += np.sin(xs / 480 * f * 6.28 + ph[k]) / (1 + k * 0.9)
    y += rng.normal(0, 0.04, len(xs)).cumsum() * 0.15
    y = (y - y.min()) / (y.max() - y.min() + 1e-6)
    if peak:                                        # a sharper summit
        px, pw, ph_ = peak
        y += ph_ * np.exp(-((xs - px) / pw) ** 2)
    return list(zip(xs, y0 - y * amp))


def fill_ridge(img, pts, col, bottom=480, grad=None):
    m = Image.new('L', (W, W), 0)
    ImageDraw.Draw(m).polygon([(x * SS, y * SS) for x, y in pts] + [(pts[-1][0] * SS, bottom * SS), (pts[0][0] * SS, bottom * SS)], fill=255)
    layer = vgrad(grad) if grad else Image.new('RGBA', (W, W), col + (255,))
    img.paste(layer, (0, 0), m)
    return m


def disc(img, x, y, r, col, glow, ga=110):
    g = ov(); d = ImageDraw.Draw(g)
    d.ellipse(P(x - r * 4, y - r * 4, x + r * 4, y + r * 4), fill=glow + (ga,))
    img.alpha_composite(g.filter(ImageFilter.GaussianBlur(r * 2.2 * SS)))
    ImageDraw.Draw(img).ellipse(P(x - r, y - r, x + r, y + r), fill=col + (255,))


def stars(img, seed=3, n=90, ymax=260):
    rng = random.Random(seed); st = ov(); d = ImageDraw.Draw(st)
    for _ in range(n):
        x, y = rng.uniform(20, 460), rng.uniform(10, ymax); r = rng.choice((0.5, 0.6, 0.8, 1.1))
        a = rng.randint(120, 255)
        d.ellipse(P(x - r, y - r, x + r, y + r), fill=(255, 250, 235, a))
    img.alpha_composite(st)


def mist(img, y, h, a, col=(255, 255, 255)):
    g = ov(); ImageDraw.Draw(g).rectangle(P(-20, y - h / 2, 500, y + h / 2), fill=col + (a,))
    img.alpha_composite(g.filter(ImageFilter.GaussianBlur(h * 0.45 * SS)))


# ---------------------------------------------------------------- the tree that grows with your steps
def tree(img, bx, by, s, night=False, seed=7, scale=1.0, bloom=None, flies=True, fixed_depth=None):
    """s = step progress 0..1 (>= 1: goal reached, it blooms)"""
    rng = random.Random(seed)
    d = ImageDraw.Draw(img)
    trunk = (70, 48, 34) if not night else (30, 26, 28)
    greens = [(46, 104, 52), (70, 140, 64), (112, 170, 80)] if not night else [(20, 44, 38), (30, 62, 52), (54, 90, 84)]
    s = max(0.0, s)
    if s < 0.1:                                     # a sprout
        k = 0.6 + s * 4
        d.line(P(bx, by, bx, by - 12 * k * scale), fill=(80, 130, 60, 255) if not night else (40, 70, 50, 255), width=int(1.6 * SS))
        for sx in (-1, 1):
            d.ellipse(P(bx + sx * 5 * k * scale - 4 * k * scale, by - 13 * k * scale - 2.2 * k * scale,
                        bx + sx * 5 * k * scale + 4 * k * scale, by - 13 * k * scale + 2.2 * k * scale), fill=greens[2] + (255,))
        return
    g = min(s, 1.0)
    H = (34 + 92 * g) * scale
    depth = fixed_depth if fixed_depth else 2 + int(g * 3.2)
    leaves = []

    def br(x, y, ang, ln, wd, dep):
        x2 = x + math.cos(ang) * ln; y2 = y - math.sin(ang) * ln
        d.line(P(x, y, x2, y2), fill=trunk + (255,), width=max(1, int(wd * SS)))
        d.ellipse(P(x2 - wd / 2, y2 - wd / 2, x2 + wd / 2, y2 + wd / 2), fill=trunk + (255,))
        if dep == 0:
            leaves.append((x2, y2)); return
        n = 2 if dep > 1 or rng.random() < 0.5 else 3
        for i in range(n):
            spread = rng.uniform(0.32, 0.62)
            a = ang + (spread if i == 0 else -spread if i == 1 else rng.uniform(-0.15, 0.15))
            br(x2, y2, a, ln * rng.uniform(0.66, 0.8), wd * 0.66, dep - 1)
        if dep <= 2: leaves.append((x2, y2))

    br(bx, by, math.pi / 2 + rng.uniform(-0.06, 0.06), H * 0.38, (3 + 6 * g) * scale, depth)
    R = (7 + 14 * g) * scale
    fol = ov(); fd = ImageDraw.Draw(fol)
    for layer, col in enumerate(greens):            # dark under-layer, mid, light top-left highlights
        for (x, y) in leaves:
            for _ in range(2 if layer < 2 else 1):
                r = R * rng.uniform(0.55, 0.95) * (1.0 - layer * 0.18)
                ox, oy = rng.uniform(-R * 0.4, R * 0.4) - layer * R * 0.18, rng.uniform(-R * 0.4, R * 0.3) - layer * R * 0.22
                fd.ellipse(P(x + ox - r, y + oy - r, x + ox + r, y + oy + r), fill=col + (255,))
    img.alpha_composite(fol)
    if s >= 1:                                       # goal: it blooms (and fireflies at night)
        d = ImageDraw.Draw(img)
        pet = bloom or ((255, 182, 200) if not night else (255, 214, 226))
        for (x, y) in leaves:
            for _ in range(3):
                px, py = x + rng.uniform(-R * 0.8, R * 0.8), y + rng.uniform(-R * 0.8, R * 0.5)
                d.ellipse(P(px - 1.6 * scale, py - 1.6 * scale, px + 1.6 * scale, py + 1.6 * scale), fill=pet + (255,))
        if night and flies:
            fl = ov(); fd = ImageDraw.Draw(fl)
            for _ in range(14):
                px, py = bx + rng.uniform(-70, 70) * scale, by - rng.uniform(10, H * 1.1)
                fd.ellipse(P(px - 1.3, py - 1.3, px + 1.3, py + 1.3), fill=(255, 230, 120, 255))
            img.alpha_composite(fl.filter(ImageFilter.GaussianBlur(2.5 * SS))); img.alpha_composite(fl)


# ---------------------------------------------------------------- data layer (same on every scene)
def hud(img, hhmm, date, steps, goal, hr, bat, night, accent):
    sh = ov(); d = ImageDraw.Draw(sh)
    ft, fd, fs, fn = F('InterDisplay-Light.otf', 92), F('Inter-Medium.otf', 15), F('Inter-Medium.otf', 14), F('InterDisplay-Medium.otf', 24)
    def ctext(dd, y, s, f, col, sp=0):
        if sp:
            ws = [f.getlength(c) for c in s]; tot = sum(ws) + sp * SS * (len(s) - 1); x = W / 2 - tot / 2
            for c, w_ in zip(s, ws): dd.text((x, y * SS), c, font=f, fill=col); x += w_ + sp * SS
        else:
            dd.text((W / 2 - f.getlength(s) / 2, y * SS), s, font=f, fill=col)
    for dd, col in ((d, (0, 0, 0, 120),),):
        pass
    ctext(d, 50, hhmm, ft, (0, 0, 0, 150)); ctext(d, 152, date, fd, (0, 0, 0, 170), 3.2)
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5 * SS)))
    d = ImageDraw.Draw(img)
    ctext(d, 48, hhmm, ft, (255, 255, 255, 255))
    ctext(d, 150, date, fd, (255, 255, 255, 225), 3.2)
    # steps: a thin arc along the bottom, the number in the middle
    p = min(1, steps / goal)
    r = 222 * SS; box = [W / 2 - r, W / 2 - r, W / 2 + r, W / 2 + r]
    d.arc(box, 128, 52 + 360, fill=(255, 255, 255, 60), width=int(3 * SS)) if False else None
    d.arc(box, 52, 128, fill=(255, 255, 255, 70), width=int(3 * SS))
    d.arc(box, 128 - (128 - 52) * p, 128, fill=accent + (255,), width=int(3 * SS))
    s = f'{steps:,}'
    sw = fn.getlength(s)
    sh = ov(); d2 = ImageDraw.Draw(sh); d2.text((W / 2 - sw / 2, 404 * SS), s, font=fn, fill=(0, 0, 0, 170))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(4 * SS)))
    d = ImageDraw.Draw(img)
    d.text((W / 2 - sw / 2, 402 * SS), s, font=fn, fill=(255, 255, 255, 255))
    ctext(d, 432, 'STEPS', F('Inter-Medium.otf', 10), (255, 255, 255, 170), 2.4)
    # heart rate (left) and battery (right): small and quiet
    for x, label, val, icon in ((78, 'BPM', str(hr), 'heart'), (402, 'BATTERY', f'{bat}%', 'bat')):
        sh = ov(); d2 = ImageDraw.Draw(sh)
        vw = fs.getlength(val)
        d2.text((x * SS - vw / 2, 238 * SS), val, font=F('InterDisplay-Medium.otf', 18), fill=(0, 0, 0, 170))
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(3 * SS)))
        d = ImageDraw.Draw(img)
        f18 = F('InterDisplay-Medium.otf', 18); vw = f18.getlength(val)
        d.text((x * SS - vw / 2, 236 * SS), val, font=f18, fill=(255, 255, 255, 255))
        fl = F('Inter-Medium.otf', 8.5); lw = fl.getlength(label) + 1.6 * SS * (len(label) - 1)
        xx = x * SS - lw / 2
        shl = ov(); dl = ImageDraw.Draw(shl); x2 = xx
        for c in label: dl.text((x2, 260 * SS), c, font=fl, fill=(0, 0, 0, 200)); x2 += fl.getlength(c) + 1.6 * SS
        img.alpha_composite(shl.filter(ImageFilter.GaussianBlur(2 * SS))); d = ImageDraw.Draw(img)
        for c in label: d.text((xx, 260 * SS), c, font=fl, fill=(255, 255, 255, 200)); xx += fl.getlength(c) + 1.6 * SS
        if icon == 'heart':
            hx, hy = x, 226
            pts = []
            for k in range(40):
                t = k / 40 * 6.283
                pts.append(((hx + 16 * math.sin(t) ** 3 * 0.32) * SS, (hy - (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) * 0.32) * SS))
            d.polygon(pts, fill=(255, 98, 110, 255))
        else:
            d.rounded_rectangle(P(x - 9, 222, x + 7, 230), radius=1.5 * SS, outline=(255, 255, 255, 220), width=int(1.2 * SS))
            d.rectangle(P(x + 7.5, 224.5, x + 9, 227.5), fill=(255, 255, 255, 220))
            d.rectangle(P(x - 7.5, 223.5, x - 7.5 + 13 * bat / 100, 228.5), fill=(120, 230, 140, 255))


def circle(img):
    m = Image.new('L', (W, W), 0); ImageDraw.Draw(m).ellipse([0, 0, W - 1, W - 1], fill=255)
    out = Image.new('RGBA', (W, W), (0, 0, 0, 0)); out.paste(img, (0, 0), m)
    return out.resize((480, 480), Image.LANCZOS)


# ---------------------------------------------------------------- scene 1: mountain lake
def mountain_lake(night, s):
    if not night:
        img = vgrad([(0, (64, 132, 206)), (200, (150, 196, 232)), (292, (214, 232, 240))])
        disc(img, 262, 194, 13, (255, 250, 228), (255, 236, 180), 110)
        far, snow, mid, pines, lake_top, lake_bot, bank = (150, 172, 200), (240, 244, 250), (96, 128, 150), (40, 78, 66), (150, 196, 226), (70, 130, 172), (62, 104, 58)
    else:
        img = vgrad([(0, (6, 10, 30)), (220, (22, 32, 70)), (292, (44, 52, 92))])
        stars(img); disc(img, 300, 198, 9, (240, 236, 220), (180, 190, 230), 70)
        far, snow, mid, pines, lake_top, lake_bot, bank = (38, 48, 84), (120, 132, 170), (24, 32, 58), (12, 20, 28), (30, 40, 78), (10, 16, 36), (14, 22, 22)
    top = ov()
    farp = ridge_pts(282, 120, 11, peak=(250, 40, 0.6))
    fill_ridge(top, farp, far, 300)
    # snow caps: the top part of the far range
    snowm = Image.new('L', (W, W), 0)
    ImageDraw.Draw(snowm).polygon([(x * SS, (y) * SS) for x, y in farp] + [(490 * SS, 205 * SS), (-10 * SS, 205 * SS)], fill=255)
    capm = Image.new('L', (W, W), 0); ImageDraw.Draw(capm).polygon([(x * SS, y * SS) for x, y in farp] + [(490 * SS, 480 * SS), (-10 * SS, 480 * SS)], fill=255)
    cap = Image.fromarray(np.minimum(np.asarray(snowm), np.asarray(capm)))
    top.paste(Image.new('RGBA', (W, W), snow + (255,)), (0, 0), cap)
    mist(top, 270, 26, 60 if not night else 30, (255, 255, 255) if not night else (120, 130, 170))
    fill_ridge(top, ridge_pts(292, 46, 23), mid, 300)
    pm = ridge_pts(300, 18, 31, freqs=(3, 11, 37, 61), step=1.5)
    pm = [(x, y - (6 if int(x) % 7 < 2 else 0)) for x, y in pm]            # spiky pine tops
    fill_ridge(top, pm, pines, 302)
    img.alpha_composite(top.crop((0, 0, W, 302 * SS)).resize((W, 302 * SS)), (0, 0)) if False else None
    img.paste(top, (0, 0), top)
    # lake + reflection
    lake = vgrad([(300, lake_top), (400, lake_bot)])
    m = Image.new('L', (W, W), 0); ImageDraw.Draw(m).rectangle(P(0, 300, 480, 480), fill=255)
    img.paste(lake, (0, 0), m)
    refl = top.crop((0, 200 * SS, W, 302 * SS)).transpose(Image.FLIP_TOP_BOTTOM)
    r_ = Image.new('RGBA', refl.size, (0, 0, 0, 0)); r_.alpha_composite(refl)
    a = np.asarray(r_).astype(np.float32); a[..., 3] *= 0.45
    a[..., 3] *= np.linspace(1, 0, a.shape[0])[:, None]
    img.alpha_composite(Image.fromarray(a.astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8 * SS)), (0, 300 * SS))
    d = ImageDraw.Draw(img)
    rng = random.Random(4)
    for _ in range(40):
        y = rng.uniform(304, 380); x = rng.uniform(40, 440); l = rng.uniform(8, 40)
        d.line(P(x, y, x + l, y), fill=(255, 255, 255, 50 if not night else 26), width=SS)
    if night:
        for k in range(14):
            y = 306 + k * 5; w_ = 10 - k * 0.4
            d.line(P(300 - w_, y, 300 + w_, y), fill=(220, 220, 200, 90), width=SS)
    # foreground bank where the tree grows
    bankp = ridge_pts(372, 24, 41, freqs=(1.1, 2.3, 5))
    fill_ridge(img, bankp, bank, 480)
    tree(img, 300, 370, s, night, seed=5, scale=0.68)
    return img


# ---------------------------------------------------------------- scene 2: ocean cliff + lighthouse
def ocean_cliff(night, s):
    if not night:
        img = vgrad([(0, (46, 132, 214)), (220, (150, 204, 238)), (290, (226, 238, 244))])
        disc(img, 262, 194, 13, (255, 250, 228), (255, 236, 180), 110)
        sea_top, sea_bot, isl, head, cliff_top, cliff_face = (86, 156, 200), (24, 84, 136), (112, 146, 160), (84, 110, 92), (104, 146, 70), (128, 108, 86)
    else:
        img = vgrad([(0, (5, 9, 28)), (220, (20, 30, 66)), (290, (40, 48, 86))])
        stars(img, 9); disc(img, 300, 198, 9, (240, 236, 220), (180, 190, 230), 70)
        sea_top, sea_bot, isl, head, cliff_top, cliff_face = (26, 36, 70), (6, 12, 28), (30, 40, 66), (18, 26, 34), (16, 26, 24), (24, 22, 28)
    # sea
    m = Image.new('L', (W, W), 0); ImageDraw.Draw(m).rectangle(P(0, 290, 480, 480), fill=255)
    img.paste(vgrad([(290, sea_top), (420, sea_bot)]), (0, 0), m)
    d = ImageDraw.Draw(img); rng = random.Random(8)
    for k in range(70):
        y = rng.uniform(294, 440); x = rng.uniform(0, 480); l = rng.uniform(4, 22) * (1 + (y - 290) / 80)
        d.line(P(x, y, x + l, y), fill=(255, 255, 255, 70 if not night else 30), width=SS)
    if night:
        for k in range(20):
            y = 294 + k * 5; w_ = 12 - k * 0.45
            d.line(P(300 - w_, y, 300 + w_, y), fill=(220, 220, 200, 90), width=SS)
    # distant island + the headland with a lighthouse
    fill_ridge(img, [(x, y) for x, y in ridge_pts(290, 14, 5, x0=300, x1=430)], isl, 291)
    hp = ridge_pts(292, 40, 12, x0=-10, x1=190)
    hp = [(x, y + max(0, (x - 150)) * 1.2) for x, y in hp]
    fill_ridge(img, hp, head, 296)
    lx = 128; ly = min(y for x, y in hp if 118 < x < 138)
    d = ImageDraw.Draw(img)
    d.polygon(P(lx - 4, ly, lx + 4, ly, lx + 2.6, ly - 30, lx - 2.6, ly - 30), fill=(236, 236, 230, 255) if not night else (60, 64, 76, 255))
    for k in (8, 18): d.rectangle(P(lx - 3.6 + k * 0.05, ly - k - 4, lx + 3.6 - k * 0.05, ly - k), fill=(206, 60, 60, 255) if not night else (70, 30, 36, 255))
    d.rectangle(P(lx - 3, ly - 36, lx + 3, ly - 30), fill=(255, 226, 140, 255) if night else (60, 66, 70, 255))
    if night:
        bm = ov(); bd = ImageDraw.Draw(bm)
        bd.polygon(P(lx, ly - 33, lx + 230, ly - 58, lx + 230, ly - 20), fill=(255, 232, 160, 60))
        img.alpha_composite(bm.filter(ImageFilter.GaussianBlur(4 * SS)))
        disc(img, lx, ly - 33, 3, (255, 240, 190), (255, 220, 140), 120)
    # foreground cliff (right) with grass, where the tree grows
    cp = [(x, y) for x, y in ridge_pts(356, 20, 3, x0=200, x1=490, freqs=(1.5, 3.2, 7))]
    cp = [(200, 480)] + [(x, y + max(0, 250 - x) * 1.6) for x, y in cp]
    m = Image.new('L', (W, W), 0); ImageDraw.Draw(m).polygon([(x * SS, y * SS) for x, y in cp] + [(490 * SS, 480 * SS)], fill=255)
    img.paste(Image.new('RGBA', (W, W), cliff_face + (255,)), (0, 0), m)
    gm = Image.new('L', (W, W), 0); ImageDraw.Draw(gm).polygon([(x * SS, y * SS) for x, y in cp[1:]] + [(490 * SS, 400 * SS), (232 * SS, 400 * SS)], fill=255)
    img.paste(Image.new('RGBA', (W, W), cliff_top + (255,)), (0, 0), gm)
    tree(img, 318, 358, s, night, seed=9, scale=0.68, bloom=(255, 236, 160) if not night else (255, 240, 190))
    return img


# ---------------------------------------------------------------- scene 3: misty tea hills
def tea_hills(night, s):
    if not night:
        img = vgrad([(0, (96, 166, 216)), (210, (188, 222, 232)), (300, (236, 238, 226))])
        disc(img, 262, 194, 13, (255, 250, 228), (255, 236, 180), 110)
        L = [(150, 182, 172), (110, 162, 120), (82, 146, 88), (60, 124, 64)]
        row = [(124, 160, 140), (88, 134, 96), (62, 116, 66), (44, 98, 48)]
        mcol, ma = (255, 255, 255), 90
    else:
        img = vgrad([(0, (8, 12, 32)), (220, (26, 34, 70)), (300, (46, 52, 84))])
        stars(img, 5); disc(img, 300, 198, 9, (240, 236, 220), (180, 190, 230), 70)
        L = [(34, 44, 70), (24, 38, 52), (18, 32, 40), (12, 24, 28)]
        row = [(28, 38, 62), (18, 30, 44), (12, 24, 32), (8, 18, 22)]
        mcol, ma = (120, 132, 176), 45
    bases = [(268, 54, 2), (300, 50, 14), (338, 52, 26), (390, 46, 38)]
    for i, (y0, amp, seed) in enumerate(bases):
        pts = ridge_pts(y0, amp, seed, freqs=(0.9, 1.9, 3.7))
        m = fill_ridge(img, pts, L[i], 480)
        if i >= 1:                                     # curved tea rows following the hill
            rows = ov(); rd = ImageDraw.Draw(rows)
            for k in range(1, 14):
                rd.line([(x * SS, (y + k * (5 + i * 1.6)) * SS) for x, y in pts], fill=row[i] + (255,), width=int((0.9 + i * 0.3) * SS))
            img.paste(rows, (0, 0), Image.fromarray(np.minimum(np.asarray(m), np.asarray(rows.split()[3]))))
        if i < 3: mist(img, y0 + 8, 18, ma, mcol)
        if i == 1:                                     # a small cottage on the middle hill
            cx = 150; cy = [y for x, y in pts if abs(x - cx) < 1.5][0] + 2
            d = ImageDraw.Draw(img)
            d.rectangle(P(cx - 9, cy - 9, cx + 9, cy), fill=(236, 230, 214, 255) if not night else (44, 46, 60, 255))
            d.polygon(P(cx - 12, cy - 9, cx, cy - 18, cx + 12, cy - 9), fill=(170, 70, 60, 255) if not night else (40, 28, 34, 255))
            d.rectangle(P(cx - 3, cy - 6, cx + 2, cy - 2), fill=(255, 210, 120, 255) if night else (90, 110, 120, 255))
            if night: disc(img, cx, cy - 4, 2, (255, 214, 130), (255, 190, 100), 90)
    tree(img, 306, 402, s, night, seed=3, scale=0.72)
    return img


SCENES = [(mountain_lake, 'Mountain lake', (120, 220, 255)), (ocean_cliff, 'Ocean cliff & lighthouse', (255, 214, 120)), (tea_hills, 'Misty tea hills', (150, 230, 130))]

if __name__ == '__main__':
    sheet = Image.new('RGB', (480 * 3 + 48, 480 * 2 + 100 + 250), (14, 14, 18))
    dr = ImageDraw.Draw(sheet); LF = ImageFont.truetype(FT + 'Inter-SemiBold.otf', 24); LS = ImageFont.truetype(FT + 'Inter-Medium.otf', 18)
    for i, (fn, lab, acc) in enumerate(SCENES):
        for j, (night, hhmm, steps, s) in enumerate(((False, '12:20', 6900, 0.46), (True, '21:30', 15240, 1.02))):
            img = fn(night, s)
            hud(img, hhmm, 'WED  11  NOV', steps, 15000, 72, 82, night, acc)
            out = circle(img)
            sheet.paste(out, (12 + i * 492, 12 + j * 492), out)
        tw = dr.textlength(lab, font=LF); dr.text((12 + i * 492 + 240 - tw / 2, 2 * 480 + 40), lab, font=LF, fill=(214, 220, 200))
    # growth strip
    y0 = 2 * 480 + 96
    dr.text((24, y0), 'The tree grows with your steps', font=LF, fill=(214, 220, 200))
    for k, (s, lab) in enumerate(((0.04, '0%'), (0.25, '25%'), (0.5, '50%'), (0.75, '75%'), (1.02, 'Goal'))):
        cell = Image.new('RGBA', (W, W), (0, 0, 0, 0))
        g = vgrad([(0, (120, 180, 220)), (300, (210, 232, 236)), (480, (210, 232, 236))])
        cell.alpha_composite(g)
        ImageDraw.Draw(cell).ellipse(P(60, 380, 420, 520), fill=(70, 120, 64, 255))
        tree(cell, 240, 400, s, False, seed=5, scale=2.2)
        c = circle(cell).resize((170, 170), Image.LANCZOS)
        x = 40 + k * 290
        sheet.paste(c, (x, y0 + 40), c)
        tw = dr.textlength(lab, font=LS); dr.text((x + 85 - tw / 2, y0 + 214), lab, font=LS, fill=(190, 196, 180))
    sheet.save(_OUT + 'mockups/landscape-concepts.png'); print('ok')
