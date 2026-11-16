"""Mountain-lake landscape (scene 1) + open sky with sun / moon (scene 2), across the day."""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))           # tools/
_ROOT = _os.path.dirname(_HERE)                                   # repo root
_RES = _ROOT + '/watchface/src/main/res/'                         # the watch face resources
_OUT = _ROOT + '/out/'                                            # previews, videos, mock-ups (not committed)
import math, random, sys
sys.path.insert(0, _HERE)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import landmock as LM
from landmock import SS, W, P, ov, vgrad, ridge_pts, fill_ridge, disc, stars, mist, tree, hud, circle

SKY = {   # top, middle (y 210), horizon (y 292)
    'night': ((5, 9, 28), (20, 30, 66), (40, 48, 86)),
    'dawn': ((58, 92, 168), (214, 168, 176), (255, 214, 172)),
    'day': ((46, 132, 214), (150, 204, 238), (226, 238, 244)),
    'golden': ((52, 74, 146), (236, 146, 112), (255, 196, 132)),
}
LAND = {  # far, snow, mid, pines, lake top, lake bottom, bank
    'night': ((38, 48, 84), (120, 132, 170), (24, 32, 58), (12, 20, 28), (30, 40, 78), (10, 16, 36), (14, 22, 22)),
    'dawn': ((150, 140, 176), (255, 226, 214), (96, 96, 128), (38, 50, 60), (214, 176, 176), (76, 88, 124), (52, 74, 56)),
    'day': ((150, 172, 200), (240, 244, 250), (96, 128, 150), (40, 78, 66), (150, 196, 226), (70, 130, 172), (62, 104, 58)),
    'golden': ((150, 112, 132), (255, 206, 180), (88, 74, 98), (38, 36, 48), (232, 158, 120), (72, 70, 104), (48, 58, 44)),
}


def phase(h):
    if h < 5.5 or h >= 19.5: return 'night'
    if h < 8: return 'dawn'
    if h < 16.5: return 'day'
    return 'golden'


def sun_pos(h):
    """sun 6:00 -> 18:00, moon 18:00 -> 6:00 along the same low arc under the date"""
    t = ((h - 6) % 12) / 12
    return 240 - 205 * math.cos(math.pi * t), 266 - 78 * math.sin(math.pi * t) ** 0.55


LAST = {}


def scene(h, s, wx=None, bank_y=372, tree_x=300, far_fn=None):
    ph = phase(h); top, mid_, hor = SKY[ph]
    far, snow, mid, pines, lake_top, lake_bot, bank = LAND[ph]
    night = ph == 'night'
    img = vgrad([(0, top), (210, mid_), (292, hor)])
    sx, sy = sun_pos(h)
    if night:
        stars(img, 9); disc(img, sx, sy, 10, (240, 236, 220), (180, 190, 230), 80)
    else:
        low = ph != 'day'
        disc(img, sx, sy, 14, (255, 236, 200) if low else (255, 250, 228), (255, 170, 110) if low else (255, 236, 180), 130 if low else 110)
    if LAST.get('sky_hook'): LAST['sky_hook'](img, ph)      # clouds live here: in the sky, behind the mountains
    top_l = ov()
    farp = far_fn() if far_fn else ridge_pts(286, 78, 11, peak=(176, 30, 0.45))
    LAST['farp'] = farp
    fill_ridge(top_l, farp, far, 300)
    # snow caps: only on the high parts, a few px deep with a ragged lower edge
    rng = np.random.default_rng(2); SNOWLINE = 238
    bot = [(x, y + min(22, max(0, SNOWLINE - y)) * (0.75 + 0.35 * math.sin(x * 0.9) + rng.uniform(-0.15, 0.15))) for x, y in farp]
    snowm = Image.new('L', (W, W), 0)
    ImageDraw.Draw(snowm).polygon([(x * SS, y * SS) for x, y in farp] + [(x * SS, y * SS) for x, y in reversed(bot)], fill=255)
    top_l.paste(Image.new('RGBA', (W, W), snow + (255,)), (0, 0), snowm)
    mist(top_l, 272, 24, 55 if ph == 'day' else 32, (255, 255, 255) if not night else (120, 130, 170))
    if not far_fn: fill_ridge(top_l, ridge_pts(292, 40, 23), mid, 300)
    pm = ridge_pts(300, 16, 31, freqs=(3, 11, 37, 61), step=1.5)
    pm = [(x, y - (6 if int(x) % 7 < 2 else 0)) for x, y in pm]
    fill_ridge(top_l, pm, pines, 302)
    img.paste(top_l, (0, 0), top_l)
    # lake + reflection of the land and the sky's glow
    m = Image.new('L', (W, W), 0); ImageDraw.Draw(m).rectangle(P(0, 300, 480, 480), fill=255)
    img.paste(vgrad([(300, lake_top), (400, lake_bot)]), (0, 0), m)
    refl = top_l.crop((0, 200 * SS, W, 302 * SS)).transpose(Image.FLIP_TOP_BOTTOM)
    a = np.asarray(refl).astype(np.float32); a[..., 3] *= 0.45 * np.linspace(1, 0, a.shape[0])[:, None]
    img.alpha_composite(Image.fromarray(a.astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8 * SS)), (0, 300 * SS))
    wl = ov(); d = ImageDraw.Draw(wl); rng = random.Random(4)
    for _ in range(40):
        y = rng.uniform(304, bank_y + 6); x = rng.uniform(40, 440); l = rng.uniform(8, 40)
        d.line(P(x, y, x + l, y), fill=(255, 255, 255, 50 if not night else 26), width=SS)
    if sy < 300:                                  # sun / moon reflection: a soft glow + a few scattered sparkles
        warm = ph in ('golden', 'dawn')
        base_c = (210, 216, 240) if night else ((255, 196, 140) if warm else (255, 250, 232))
        glow = ov(); gd = ImageDraw.Draw(glow)
        L = 70 if (warm or night) else 46; wdt = 16 if (warm or night) else 22
        gd.ellipse(P(sx - wdt, 300, sx + wdt, 300 + L * 2), fill=base_c + (70 if not night else 45,))
        img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(9 * SS)))
        rs = random.Random(int(sx))
        for k in range(16 if (warm or night) else 11):
            y = 303 + (rs.random() ** 1.3) * L
            spread = 3 + (y - 300) * 0.16
            x = sx + rs.uniform(-spread, spread); ln = rs.uniform(1.5, 5.5) * (1 - (y - 300) / (L * 1.6))
            a_ = int(rs.uniform(110, 210) * (1 - (y - 300) / (L * 1.3)))
            if ln > 0.6 and a_ > 20: d.line(P(x - ln, y, x + ln, y), fill=base_c + (a_,), width=max(1, int(0.9 * SS)))
    img.alpha_composite(wl)
    fill_ridge(img, ridge_pts(bank_y, 24, 41, freqs=(1.1, 2.3, 5)), bank, 480)
    tl = ov(); tree(tl, tree_x, bank_y - 2, s, night, seed=5, scale=0.68)
    if ph in ('golden', 'dawn'):                   # warm low light on the tree
        t = np.asarray(tl).astype(np.float32); k = (1.05, 0.8, 0.66) if ph == 'golden' else (1.0, 0.86, 0.82)
        for c in range(3): t[..., c] = np.clip(t[..., c] * k[c], 0, 255)
        tl = Image.fromarray(t.astype(np.uint8))
    img.alpha_composite(tl)
    return img, night


if __name__ == '__main__':
    states = [(6.83, '06:50', 300, 0.04, 'Sunrise'), (12.33, '12:20', 6900, 0.46, 'Noon'),
              (17.33, '17:20', 12100, 0.8, 'Golden hour'), (21.5, '21:30', 15240, 1.02, 'Night · goal reached')]
    sheet = Image.new('RGB', (480 * 2 + 36, 2 * (480 + 50) + 12), (14, 14, 18))
    dr = ImageDraw.Draw(sheet); LF = ImageFont.truetype(LM.FT + 'Inter-SemiBold.otf', 22)
    for i, (h, hhmm, steps, s, lab) in enumerate(states):
        img, night = scene(h, s)
        hud(img, hhmm, 'WED  11  NOV', steps, 15000, 72, 82, night, (120, 220, 255))
        out = circle(img)
        x, y = 12 + (i % 2) * 492, 12 + (i // 2) * 530
        sheet.paste(out, (x, y), out)
        tw = dr.textlength(lab, font=LF); dr.text((x + 240 - tw / 2, y + 488), lab, font=LF, fill=(214, 220, 200))
    sheet.save(_OUT + 'mockups/lake-sky-combo.png'); print('ok')
