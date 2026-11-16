"""Heart rate merged into the mountains + battery arc on the right edge."""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))           # tools/
_ROOT = _os.path.dirname(_HERE)                                   # repo root
_RES = _ROOT + '/watchface/src/main/res/'                         # the watch face resources
_OUT = _ROOT + '/out/'                                            # previews, videos, mock-ups (not committed)
import math, sys
sys.path.insert(0, _HERE)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import combomock as CM, landmock as LM, lakelife as LL, waterlife as WL
from landmock import SS, W, P, ov, F

HEART = (255, 92, 110)


def ecg_ridge():
    """far range shaped like a heartbeat: P bump, Q dip, tall R summit, S dip, T hill (+ smaller beats either side)"""
    xs = np.arange(-10, 492, 1.5)
    rng = np.random.default_rng(3)
    y = 262 + np.cumsum(rng.normal(0, 0.2, len(xs))) * 0.25 + 1.2 * np.sin(xs / 41)
    def beat(xc, k):
        return k * (-12 * np.exp(-((xs - (xc - 70)) / 15) ** 2) + 7 * np.exp(-((xs - (xc - 20)) / 6) ** 2)
                    - 50 * np.exp(-((xs - xc) / 12) ** 2) + 9 * np.exp(-((xs - (xc + 17)) / 6) ** 2)
                    - 20 * np.exp(-((xs - (xc + 62)) / 19) ** 2))
    y = y + beat(200, 1.0)
    return list(zip(xs, y))


def summit(farp, x0=120, x1=360):
    return min(((x, y) for x, y in farp if x0 < x < x1), key=lambda p: p[1])


def ridge_glow(img, farp, night, pulse_x, beat_k=1.0):
    """thin glowing line along the ridge + a bright pulse travelling along it"""
    pts = [(x * SS, (y - 0.6) * SS) for x, y in farp]
    line = ov(); ImageDraw.Draw(line).line(pts, fill=HEART + (150 if night else 110,), width=int(1.3 * SS), joint='curve')
    glow = line.filter(ImageFilter.GaussianBlur(3 * SS))
    img.alpha_composite(glow); img.alpha_composite(line)
    # the pulse: a short bright segment around pulse_x
    seg = [(x, y) for x, y in farp if abs(x - pulse_x) < 26]
    if len(seg) > 1:
        pl = ov(); d = ImageDraw.Draw(pl)
        for i in range(len(seg) - 1):
            a = int(255 * (1 - abs(seg[i][0] - pulse_x) / 26) * beat_k)
            d.line([(seg[i][0] * SS, (seg[i][1] - 0.6) * SS), (seg[i + 1][0] * SS, (seg[i + 1][1] - 0.6) * SS)], fill=(255, 220, 226, a), width=int(2.2 * SS))
        img.alpha_composite(pl.filter(ImageFilter.GaussianBlur(4 * SS))); img.alpha_composite(pl)


def summit_bpm(img, farp, hr):
    sx, sy = summit(farp)
    f = F('InterDisplay-SemiBold.otf', 17); s = str(hr)
    tw = f.getlength(s); hw = 11 * SS
    x0 = sx * SS - (tw + hw + 3 * SS) / 2; y0 = (sy - 30) * SS
    sh = ov(); d = ImageDraw.Draw(sh)
    d.text((x0 + hw + 3 * SS, y0), s, font=f, fill=(0, 0, 0, 170))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(3 * SS)))
    d = ImageDraw.Draw(img)
    d.text((x0 + hw + 3 * SS, y0), s, font=f, fill=(255, 255, 255, 255))
    hx, hy = x0 / SS + 5.5, sy - 30 + 10
    pts = [((hx + 16 * math.sin(t) ** 3 * 0.34) * SS, (hy - (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) * 0.34) * SS)
           for t in np.linspace(0, 6.283, 40)]
    d.polygon(pts, fill=HEART + (255,))
    # a tiny marker line down to the summit
    d.line(P(sx, sy - 8, sx, sy - 2), fill=(255, 255, 255, 200), width=int(1 * SS))


def hud2(hhmm, date, steps, goal, bat, accent=(120, 220, 255), steps_text=True, steps_arc=True, bat_arc=True):
    """time, date, steps arc (bottom) and battery arc (right edge)"""
    o = ov(); d = ImageDraw.Draw(o)
    ft, fd, fn = F('InterDisplay-Light.otf', 92), F('Inter-Medium.otf', 15), F('InterDisplay-Medium.otf', 24)
    def ctext(dd, y, s, f, col, sp=0, cx=240):
        ws = [f.getlength(c) for c in s]; tot = sum(ws) + sp * SS * (len(s) - 1); x = cx * SS - tot / 2
        for c, w_ in zip(s, ws): dd.text((x, y * SS), c, font=f, fill=col); x += w_ + sp * SS
    sh = ov(); ds = ImageDraw.Draw(sh)
    ctext(ds, 50, hhmm, ft, (0, 0, 0, 150)); ctext(ds, 152, date, fd, (0, 0, 0, 170), 3.2)
    if steps_text: ctext(ds, 404, f'{steps:,}', fn, (0, 0, 0, 170));
    o.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5 * SS)))
    d = ImageDraw.Draw(o)
    ctext(d, 48, hhmm, ft, (255, 255, 255, 255)); ctext(d, 150, date, fd, (255, 255, 255, 225), 3.2)
    r = 222 * SS; box = [W / 2 - r, W / 2 - r, W / 2 + r, W / 2 + r]
    # steps: bottom
    p = min(1, steps / goal)
    if steps_arc:
        d.arc(box, 52, 128, fill=(255, 255, 255, 70), width=int(3 * SS))
        d.arc(box, 128 - 76 * p, 128, fill=accent + (255,), width=int(3 * SS))
    if steps_text: ctext(d, 402, f'{steps:,}', fn, (255, 255, 255, 255)); ctext(d, 432, 'STEPS', F('Inter-Medium.otf', 10), (255, 255, 255, 190), 2.4)
    # battery: right edge, fills from the bottom up; green > amber < 50 % > red < 20 %
    col = (120, 230, 140) if bat >= 50 else ((255, 196, 80) if bat >= 20 else (255, 90, 90))
    if bat_arc:
        d.arc(box, -36, 36, fill=(255, 255, 255, 70), width=int(3 * SS))
        d.arc(box, 36 - 72 * bat / 100, 36, fill=col + (255,), width=int(3 * SS))
    return o


def face(h, hhmm, steps, s, life, far_fn, pulse_x, hr=72, bat=82):
    img, night, ph = LL.base(h, s, far_fn)
    farp = CM.LAST['farp']
    LL.statics(img, SS, ph)
    life(img, SS, ph)
    ridge_glow(img, farp, night, pulse_x)
    summit_bpm(img, farp, hr)
    img.alpha_composite(hud2(hhmm, 'WED  11  NOV', steps, 15000, bat))
    return LM.circle(img)


if __name__ == '__main__':
    rows = [(12.33, '12:20', 6900, 0.46, LL.noon_life, 82, 330, 'Noon'), (17.33, '17:20', 12100, 0.8, LL.golden_life, 46, 90, 'Golden hour'),
            (21.5, '21:30', 15240, 1.02, LL.night_life, 15, 300, 'Night')]
    sheet = Image.new('RGB', (480 * 3 + 48, 480 + 70), (14, 14, 18))
    dr = ImageDraw.Draw(sheet); LF = ImageFont.truetype(LM.FT + 'Inter-SemiBold.otf', 22)
    for i, (h, hhmm, steps, s, life, bat, px, lab) in enumerate(rows):
        out = face(h, hhmm, steps, s, life, ecg_ridge, px, bat=bat)
        sheet.paste(out, (12 + i * 492, 12), out)
        tw = dr.textlength(lab, font=LF); dr.text((12 + i * 492 + 240 - tw / 2, 500), lab, font=LF, fill=(214, 220, 200))
    sheet.save(_OUT + 'mockups/heartbeat-lake.png'); print('ok')
