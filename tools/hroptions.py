"""Natural mountain lake + birds; six places for the heart rate."""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))           # tools/
_ROOT = _os.path.dirname(_HERE)                                   # repo root
_RES = _ROOT + '/watchface/src/main/res/'                         # the watch face resources
_OUT = _ROOT + '/out/'                                            # previews, videos, mock-ups (not committed)
import math, random, sys
sys.path.insert(0, _HERE)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import combomock as CM, landmock as LM, lakelife as LL, waterlife as WL, hrmock as HM
from landmock import SS, W, P, ov, F

HEART = (255, 92, 110)


def birds(img, K, t=0.0, x0=96, y0=206, n=5, golden=False, night=False):
    """a loose V of small birds, wings at different points of the flap"""
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    col = (46, 52, 66, 235) if not golden else (60, 40, 46, 235)
    rng = random.Random(3)
    for i in range(n):
        side = 1 if i % 2 else -1; k = (i + 1) // 2
        x = x0 + t * 6 - k * 13 + rng.uniform(-2, 2); y = y0 + side * k * 7 + rng.uniform(-1.5, 1.5)
        s = 5.2 - k * 0.5; ph = t * 7 + i * 1.3
        a = s * 0.55 * math.sin(ph)
        for sd in (-1, 1):
            pts = [(x + sd * s, y - a), (x + sd * s * 0.45, y - a * 0.35 - s * 0.22), (x, y)]
            d.line([(px * K, py * K) for px, py in pts], fill=col, width=max(1, int(1.15 * K)), joint='curve')
    img.alpha_composite(lay)


def heart_icon(d, x, y, sc, col=HEART + (255,)):
    pts = [((x + 16 * math.sin(t) ** 3 * sc) * SS, (y - (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) * sc) * SS)
           for t in np.linspace(0, 6.283, 40)]
    d.polygon(pts, fill=col)


def shadow_text(img, x, y, s, f, col=(255, 255, 255, 255), anchor='la', blur=3):
    sh = ov(); ImageDraw.Draw(sh).text((x * SS, y * SS), s, font=f, fill=(0, 0, 0, 170), anchor=anchor)
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur * SS)))
    ImageDraw.Draw(img).text((x * SS, y * SS), s, font=f, fill=col, anchor=anchor)


def bpm_pair(img, cx, y, hr=72, size=17):
    """heart + number centred on cx, text top at y"""
    f = F('InterDisplay-SemiBold.otf', size); s = str(hr)
    tw = f.getlength(s) / SS; hw = size * 0.62
    x0 = cx - (tw + hw + 3) / 2
    shadow_text(img, x0 + hw + 3, y, s, f)
    heart_icon(ImageDraw.Draw(img), x0 + hw / 2, y + size * 0.62, size * 0.02)


# --- the six placements
def o_summit(img, farp):
    sx, sy = HM.summit(farp)
    d = ImageDraw.Draw(img)
    d.line(P(sx, sy - 1, sx, sy - 13), fill=(70, 60, 60, 255), width=int(0.9 * SS))
    d.polygon(P(sx, sy - 13, sx + 8, sy - 10.5, sx, sy - 8), fill=HEART + (255,))
    bpm_pair(img, sx, sy - 34)


def o_sun(img, farp):
    sx, sy = CM.sun_pos(12.33)
    g = ov(); ImageDraw.Draw(g).ellipse(P(sx - 24, sy - 24, sx + 24, sy + 24), outline=(255, 150, 160, 150), width=int(2 * SS))
    img.alpha_composite(g.filter(ImageFilter.GaussianBlur(1.5 * SS)))
    bpm_pair(img, sx, sy + 26, size=15)


def o_ripple(img, farp):
    cx, cy = 112, 334
    g = ov(); d = ImageDraw.Draw(g)
    for k, r in enumerate((10, 19, 29)):
        d.ellipse(P(cx - r, cy - r * 0.3, cx + r, cy + r * 0.3), outline=(255, 255, 255, 170 - k * 45), width=int(1 * SS))
    img.alpha_composite(g)
    bpm_pair(img, cx, cy - 26, size=15)


def o_sign(img, farp):
    d = ImageDraw.Draw(img)
    x, base = 84, 394
    d.rectangle(P(x - 1.2, base - 26, x + 1.2, base), fill=(96, 66, 42, 255))
    d.rounded_rectangle(P(x - 22, base - 40, x + 22, base - 22), radius=2 * SS, fill=(150, 108, 68, 255), outline=(96, 66, 42, 255), width=int(1 * SS))
    for yy in (base - 34, base - 28): d.line(P(x - 20, yy, x + 20, yy), fill=(132, 94, 58, 255), width=max(1, int(0.5 * SS)))
    f = F('InterDisplay-SemiBold.otf', 12); s = '72'
    heart_icon(d, x - 9, base - 30.5, 0.24, (200, 50, 60, 255))
    d.text(((x - 2) * SS, (base - 38.5) * SS), s, font=f, fill=(255, 244, 226, 255))


def o_arc(img, farp, hr=72):
    o = ov(); d = ImageDraw.Draw(o)
    r = 222 * SS; box = [W / 2 - r, W / 2 - r, W / 2 + r, W / 2 + r]
    p = max(0, min(1, (hr - 40) / 140))
    d.arc(box, 144, 216, fill=(255, 255, 255, 70), width=int(3 * SS))
    d.arc(box, 144, 144 + 72 * p, fill=HEART + (255,), width=int(3 * SS))
    img.alpha_composite(o)
    bpm_pair(img, 62, 226, size=15)


def o_date(img, farp):
    pass   # drawn in the date line itself (see make())


OPTS = [(o_summit, '1 · Summit marker', 'On the highest peak, like an altitude sign'),
        (o_sun, '2 · With the sun / moon', 'Under the sun or moon; its halo beats with you'),
        (o_ripple, '3 · Lake ripple', 'Floats on the water; rings spread at your pulse'),
        (o_sign, '4 · Wooden sign', 'A little trail sign on the shore'),
        (o_arc, '5 · Left arc', 'Mirrors the battery arc; fills with your BPM'),
        (o_date, '6 · Beside the date', 'Quiet, on the date line')]


def make(fn):
    img, night, ph = LL.base(12.33, 0.46)
    farp = CM.LAST['farp']
    LL.statics(img, SS, ph)
    LL.noon_life(img, SS, ph)
    birds(img, SS, 0.0, x0=372, y0=208)
    fn(img, farp)
    img.alpha_composite(HM.hud2('12:20', 'WED  11  NOV' if fn is not o_date else '', 6900, 15000, 82))
    if fn is o_date:          # one centred line: WED 11 NOV  ·  heart 72
        f = F('Inter-Medium.otf', 15); sp = 3.2
        txt = 'WED  11  NOV'
        wd = sum(f.getlength(c) for c in txt) / SS + sp * (len(txt) - 1)
        wh = 12 + 3 + f.getlength('72') / SS
        gap = 18; x = 240 - (wd + gap + wh) / 2
        for c in txt:
            shadow_text(img, x, 150, c, f, (255, 255, 255, 225)); x += f.getlength(c) / SS + sp
        x += gap - sp
        heart_icon(ImageDraw.Draw(img), x + 5, 159.5, 0.3)
        shadow_text(img, x + 13, 150, '72', f)
    return LM.circle(img)


if __name__ == '__main__':
    cols = 3
    sheet = Image.new('RGB', (480 * cols + 12 * (cols + 1), 2 * (480 + 80) + 12), (14, 14, 18))
    dr = ImageDraw.Draw(sheet); LF = ImageFont.truetype(LM.FT + 'Inter-SemiBold.otf', 22); LS = ImageFont.truetype(LM.FT + 'Inter-Regular.otf', 16)
    for i, (fn, lab, sub) in enumerate(OPTS):
        out = make(fn)
        x, y = 12 + (i % cols) * 492, 12 + (i // cols) * 560
        sheet.paste(out, (x, y), out)
        tw = dr.textlength(lab, font=LF); dr.text((x + 240 - tw / 2, y + 490), lab, font=LF, fill=(214, 220, 200))
        tw = dr.textlength(sub, font=LS); dr.text((x + 240 - tw / 2, y + 520), sub, font=LS, fill=(150, 156, 146))
    sheet.save(_OUT + 'mockups/heartrate-places.png'); print('ok')
