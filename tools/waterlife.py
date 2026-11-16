"""Living lake: rowboat + fisherman, jumping fish, ducks, jetty, reeds, lantern. Everything drawn in face px
on a canvas of size 480*K (K = supersample/scale factor)."""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))           # tools/
_ROOT = _os.path.dirname(_HERE)                                   # repo root
_RES = _ROOT + '/watchface/src/main/res/'                         # the watch face resources
_OUT = _ROOT + '/out/'                                            # previews, videos, mock-ups (not committed)
import math, random
from PIL import Image, ImageDraw, ImageFilter

WOOD, WOOD_D = (112, 74, 46), (74, 48, 30)
HAT, SKIN, SHIRT, PANTS = (214, 184, 118), (196, 140, 104), (176, 64, 56), (52, 62, 84)


def _pt(K, *v): return [x * K for x in v]


def ripples(d, K, x, y, age, n=3, span=1.6, col=(255, 255, 255), a0=150, rmax=14):
    """expanding flattened rings; age in seconds since the splash"""
    for i in range(n):
        t = age - i * 0.25
        if t < 0 or t > span: continue
        r = 2 + rmax * (t / span) ** 0.7; a = int(a0 * (1 - t / span))
        d.ellipse(_pt(K, x - r, y - r * 0.28, x + r, y + r * 0.28), outline=col + (a,), width=max(1, int(0.9 * K)))


def boat(img, K, x, y, t, mode='fish', night=False, golden=False, catch=None):
    """mode: 'fish' (rod + float), 'row' (oars), 'moored' (empty, tied)"""
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    bob = math.sin(t * 2.0944) * 0.7; y = y + bob
    dim = (lambda c: tuple(int(v * 0.35) for v in c)) if night else ((lambda c: (int(min(255, c[0] * 1.05)), int(c[1] * 0.82), int(c[2] * 0.68))) if golden else (lambda c: c))
    # hull
    hull = [(x - 24, y - 6), (x + 24, y - 6), (x + 19, y + 1), (x - 18, y + 1)]
    d.polygon([(a * K, b * K) for a, b in hull], fill=dim(WOOD) + (255,))
    d.line(_pt(K, x - 24, y - 6, x + 24, y - 6), fill=dim((150, 104, 66)) + (255,), width=int(1.4 * K))
    d.line(_pt(K, x - 20, y - 2.5, x + 21, y - 2.5), fill=dim(WOOD_D) + (255,), width=max(1, int(0.8 * K)))
    if mode != 'moored':
        # the fisherman, sitting at the stern
        fx = x - 8
        d.rounded_rectangle(_pt(K, fx - 3.6, y - 17, fx + 3.6, y - 6), radius=2 * K, fill=dim(SHIRT) + (255,))
        d.ellipse(_pt(K, fx - 2.6, y - 22.5, fx + 2.6, y - 17), fill=dim(SKIN) + (255,))
        d.polygon(_pt(K, fx - 7, y - 20.5, fx, y - 26, fx + 7, y - 20.5), fill=dim(HAT) + (255,))
        if mode == 'fish':
            lift = 0.0 if catch is None else max(0.0, min(1.0, (catch - 0.3) / 0.3))
            tipx, tipy = fx + 30 - 5 * lift, y - 34 - 9 * lift + math.sin(t * 1.0472) * 0.6
            d.line(_pt(K, fx + 3, y - 12, tipx, tipy), fill=dim((60, 44, 30)) + (255,), width=max(1, int(0.9 * K)))
            bx, by = fx + 44, y + 9
            if catch is None or catch < 0.35:
                bite = ((t % 6.0) > 4.6 and (t % 6.0) < 5.2) if catch is None else True
                by2 = by + ((2.2 if catch is None else 2.6 * abs(math.sin(catch * 40))) if bite else math.sin(t * 3.1416) * 0.5)
                d.line(_pt(K, tipx, tipy, bx, by2), fill=(230, 230, 230, 150 if not night else 70), width=max(1, int(0.5 * K)))
                d.ellipse(_pt(K, bx - 1.3, by2 - 1.6, bx + 1.3, by2 + 0.6), fill=(230, 60, 50, 255) if not night else (90, 40, 40, 255))
                ripples(d, K, bx, by + 1, (t % 2.0), n=2, span=2.0, a0=110 if not night else 50, rmax=8)
                if bite: ripples(d, K, bx, by + 1, ((t % 6.0) - 4.6) if catch is None else (catch * 3 % 1.2), n=3, span=1.2, a0=180, rmax=10)
            else:                                   # the catch: a fish comes up on the line and swings by the rod tip
                q = max(0.0, min(1.0, (catch - 0.35) / 0.35))
                fxp = bx + (tipx - 1 - bx) * q; fyp = by + (tipy + 13 - by) * q - 7 * math.sin(q * math.pi)
                sw = math.sin(catch * 30) * (1.6 - q)
                d.line(_pt(K, tipx, tipy, fxp + sw * 0.3, fyp - 3), fill=(230, 230, 230, 170 if not night else 80), width=max(1, int(0.5 * K)))
                ang = math.pi / 2 + sw * 0.35
                ca, sa = math.cos(ang), math.sin(ang)
                body = [(4.6 * math.cos(tt), 1.8 * math.sin(tt)) for tt in [k_ / 18 * 2 * math.pi for k_ in range(18)]]
                tail = [(4.4, 0), (7.4, -2.4), (7.4, 2.4)]
                R_ = lambda p_: ((fxp + sw + p_[0] * ca - p_[1] * sa) * K, (fyp + p_[0] * sa + p_[1] * ca) * K)
                fc = dim((206, 216, 224))
                d.polygon([R_(p_) for p_ in body], fill=fc + (255,)); d.polygon([R_(p_) for p_ in tail], fill=tuple(int(v * 0.85) for v in fc) + (255,))
                if catch < 0.6: ripples(d, K, bx, by + 1, (catch - 0.35) * 4, n=3, span=1.4, a0=190, rmax=11)
        else:   # rowing
            ang = math.sin(t * 2.0944)
            for side in (-1, 1):
                ox, oy = fx + 2 + side * 0.5, y - 10
                ex, ey = ox + 16 + ang * 6, y + 5 + side * 1.5
                d.line(_pt(K, ox, oy, ex, ey), fill=dim((140, 100, 62)) + (255,), width=max(1, int(1.1 * K)))
                if ang > 0.6: ripples(d, K, ex, ey, (t % 3.0) / 3.0, n=2, span=1.0, a0=120, rmax=6)
    if night or golden:   # lantern on a short pole at the bow
        lx, ly = x + 18, y - 16
        d.line(_pt(K, x + 18, y - 6, lx, ly), fill=dim((90, 70, 50)) + (255,), width=max(1, int(0.8 * K)))
        g = Image.new('RGBA', img.size, (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
        flick = 1 + 0.08 * math.sin(t * 8.3776) + 0.05 * math.sin(t * 23.038)
        gd.ellipse(_pt(K, lx - 14 * flick, ly - 14 * flick, lx + 14 * flick, ly + 14 * flick), fill=(255, 190, 90, 90))
        img.alpha_composite(g.filter(ImageFilter.GaussianBlur(6 * K)))
        d.rectangle(_pt(K, lx - 1.6, ly - 1, lx + 1.6, ly + 2.4), fill=(255, 220, 140, 255))
        # its reflection
        rl = Image.new('RGBA', img.size, (0, 0, 0, 0)); rd = ImageDraw.Draw(rl)
        for k in range(8):
            yy = y + 4 + k * 2.2; w = 3.5 - k * 0.35 + math.sin(t * 4.18879 + k) * 0.6
            if w > 0: rd.line(_pt(K, lx - w, yy, lx + w, yy), fill=(255, 200, 110, 150), width=max(1, int(0.8 * K)))
        img.alpha_composite(rl)
    # reflection of boat + man (flipped, faded, wobbling)
    box = (int((x - 30) * K), int((y - 40) * K), int((x + 50) * K), int((y + 1) * K))
    part = lay.crop(box).transpose(Image.FLIP_TOP_BOTTOM)
    a = part.split()[3].point(lambda v: int(v * (0.28 if not night else 0.18)))
    part.putalpha(a)
    img.alpha_composite(part, (box[0] + int(math.sin(t * 2.0944) * K * 0.5), int((y + 1) * K)))
    img.alpha_composite(lay)


def fish_jump(img, K, x0, y0, ph, golden=False, night=False, big=1.0):
    """ph: 0..1 through the jump (~1.1 s); ph < 0: before, ph > 1: rings only (pass age via ph up to 2.4)"""
    top = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(top)
    L = 26 * big; Hh = 20 * big
    col = (200, 214, 222) if not golden else (255, 196, 140)
    if night: col = (190, 196, 214)
    if 0 <= ph <= 1:
        x = x0 + L * ph; y = y0 - Hh * 4 * ph * (1 - ph)
        ang = math.atan2(-Hh * 4 * (1 - 2 * ph), L)
        lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        # body: ellipse + tail, rotated along the path
        pts = []
        for k in range(24):
            tt = k / 24 * 2 * math.pi
            pts.append((5.2 * big * math.cos(tt), 1.9 * big * math.sin(tt)))
        tail = [(-5 * big, 0), (-8.2 * big, -2.6 * big), (-8.2 * big, 2.6 * big)]
        ca, sa = math.cos(ang), math.sin(ang)
        R = lambda p: ((x + p[0] * ca - p[1] * sa) * K, (y + p[0] * sa + p[1] * ca) * K)
        ld.polygon([R(p) for p in pts], fill=col + (255,))
        ld.polygon([R(p) for p in tail], fill=tuple(int(v * 0.85) for v in col) + (255,))
        ld.polygon([R(p) for p in [(1.5 * big, -1.9 * big), (-1.5 * big, -3.2 * big), (-2 * big, -1.7 * big)]], fill=tuple(int(v * 0.8) for v in col) + (255,))
        img.alpha_composite(lay)
        # droplets
        for k in range(6):
            for (sx, a0) in ((x0, ph), (x0 + L, ph - 0.8)):
                if 0 <= a0 <= 0.35:
                    q = a0 / 0.35
                    dx = (k - 2.5) * 2.2 * q; dy = -9 * q * (1 - q) * (1 + (k % 3) * 0.3)
                    d.ellipse(_pt(K, sx + dx - 0.7, y0 + dy - 0.7, sx + dx + 0.7, y0 + dy + 0.7), fill=(255, 255, 255, 220))
    if ph >= 0:
        age = ph * 1.1
        ripples(d, K, x0, y0 + 1, age, n=3, span=1.8, a0=170 if not night else 110, rmax=12)
        if ph > 0.85: ripples(d, K, x0 + L, y0 + 1, age - 0.95, n=3, span=1.8, a0=170 if not night else 110, rmax=13)
    img.alpha_composite(top)


def duck(img, K, x, y, t, i=0, golden=False, night=False):
    top = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(top)
    bob = math.sin(t * 2.1 + i) * 0.4; y += bob
    body = (110, 86, 60) if not night else (40, 40, 48)
    if golden: body = (120, 80, 56)
    head = (40, 96, 70) if not night else (30, 34, 40)
    d.line(_pt(K, x - 5, y + 1.5, x - 16, y + 4.5), fill=(255, 255, 255, 90 if not night else 40), width=max(1, int(0.7 * K)))
    d.line(_pt(K, x - 5, y + 1.5, x - 15, y - 0.5), fill=(255, 255, 255, 70 if not night else 30), width=max(1, int(0.7 * K)))
    d.ellipse(_pt(K, x - 5.5, y - 2.5, x + 4, y + 1.6), fill=body + (255,))
    d.polygon(_pt(K, x - 5.5, y - 1.2, x - 8, y - 3.4, x - 4.5, y - 2.2), fill=body + (255,))
    d.ellipse(_pt(K, x + 1.6, y - 6, x + 5.2, y - 2.4), fill=head + (255,))
    d.polygon(_pt(K, x + 5, y - 4.6, x + 7.6, y - 4.0, x + 5, y - 3.3), fill=(230, 170, 60, 255) if not night else (90, 70, 40, 255))
    img.alpha_composite(top)


def jetty(img, K, night=False, golden=False):
    top = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(top)
    w = (138, 98, 62) if not night else (40, 34, 34)
    if golden: w = (150, 96, 60)
    wd = tuple(int(v * 0.7) for v in w)
    for x in (28, 52, 76, 100):
        d.rectangle(_pt(K, x - 1.3, 356, x + 1.3, 372), fill=wd + (255,))
        d.rectangle(_pt(K, x - 1.3, 372, x + 1.3, 380), fill=wd + (90,))
    d.polygon(_pt(K, 10, 354, 108, 354, 110, 358, 10, 358), fill=w + (255,))
    for x in range(14, 108, 6): d.line(_pt(K, x, 354, x, 358), fill=wd + (255,), width=max(1, int(0.5 * K)))
    img.alpha_composite(top)


def reeds(img, K, x0, x1, base, seed=1, night=False, golden=False, t=0):
    rng = random.Random(seed); d = ImageDraw.Draw(img)
    col = (70, 110, 56) if not night else (20, 32, 30)
    if golden: col = (96, 92, 52)
    for _ in range(int((x1 - x0) * 0.9)):
        x = rng.uniform(x0, x1); h = rng.uniform(8, 20); lean = rng.uniform(-2.5, 2.5) + math.sin(t * 1.3 + x) * 0.8
        d.line(_pt(K, x, base, x + lean, base - h), fill=col + (255,), width=max(1, int(0.9 * K)))
        if rng.random() < 0.25:
            d.ellipse(_pt(K, x + lean - 0.9, base - h - 3.5, x + lean + 0.9, base - h + 0.5), fill=(110, 76, 46, 255) if not night else (30, 26, 26, 255))


def fireflies(img, K, t, n=10, seed=4, area=(150, 300, 460, 380)):
    rng = random.Random(seed)
    g = Image.new('RGBA', img.size, (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    for i in range(n):
        x = rng.uniform(area[0], area[2]) + math.sin(t * 0.7 + i) * 6; y = rng.uniform(area[1], area[3]) + math.cos(t * 0.9 + i * 2) * 4
        a = int(255 * max(0, math.sin(t * 1.6 + i * 1.7)))
        gd.ellipse(_pt(K, x - 1.2, y - 1.2, x + 1.2, y + 1.2), fill=(255, 232, 130, a))
    img.alpha_composite(g.filter(ImageFilter.GaussianBlur(2.2 * K))); img.alpha_composite(g)
