"""Painted jetty, better version: bigger, real wood, worn paint, 5-block painted gauge + number."""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))           # tools/
_ROOT = _os.path.dirname(_HERE)                                   # repo root
_RES = _ROOT + '/watchface/src/main/res/'                         # the watch face resources
_OUT = _ROOT + '/out/'                                            # previews, videos, mock-ups (not committed)
import math, sys
sys.path.insert(0, _HERE)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import combomock as CM, landmock as LM, lakelife as LL, waterlife as WL, hrmock as HM, hroptions as HO, signsteps as SG, batjetty as BJ
from landmock import SS, W, P, ov, F

END = 176          # jetty end x
DK, FT0, FT1 = 342, 348, 364      # deck top, fascia top / bottom


def paint_col(b): return (120, 226, 120) if b >= 50 else ((255, 188, 64) if b >= 20 else (255, 78, 70))


def worn(layer, seed=1, lo=0.62):
    """scuff the paint: modulate alpha with fine noise + a few scratches"""
    a = np.asarray(layer.split()[3]).astype(np.float32)
    rng = np.random.default_rng(seed)
    n = rng.random((a.shape[0] // 8 + 1, a.shape[1] // 8 + 1)).astype(np.float32)
    n = np.asarray(Image.fromarray((n * 255).astype(np.uint8)).resize((a.shape[1], a.shape[0]), Image.BILINEAR)).astype(np.float32) / 255
    a *= lo + (1 - lo) * n
    out = layer.copy(); out.putalpha(Image.fromarray(a.astype(np.uint8)))
    return out


def jetty_big(img, ph, t=0.0):
    wood, dark, top = SG.tint((140, 100, 64), ph), SG.tint((84, 56, 36), ph), SG.tint((168, 126, 84), ph)
    lay = ov(); d = ImageDraw.Draw(lay)
    # posts + their reflections and ripples
    for x in (48, 82, 116, 150, END - 3):
        d.rectangle(P(x - 2.4, FT1 - 2, x + 2.4, 376), fill=dark + (255,))
        d.rectangle(P(x - 2.4, 376, x + 2.4, 388), fill=dark + (70,))
        d.ellipse(P(x - 6, 374.5, x + 6, 377.5), outline=(255, 255, 255, 80 if ph != 'night' else 25), width=max(1, int(0.7 * SS)))
    # deck top (seen a little from above) with plank seams
    d.polygon(P(-6, FT0, END + 2, FT0, END - 2, DK, -6, DK), fill=top + (255,))
    for x in range(-4, END, 7): d.line(P(x, DK, x + 1.2, FT0), fill=dark + (200,), width=max(1, int(0.55 * SS)))
    # fascia beam with grain + nails
    d.rectangle(P(-6, FT0, END + 2, FT1), fill=wood + (255,))
    rng = np.random.default_rng(7)
    for k in range(9):
        y = FT0 + 1.5 + k * 1.9 + rng.uniform(-0.3, 0.3)
        x0 = rng.uniform(-6, 40); x1 = x0 + rng.uniform(30, 90)
        d.line(P(x0, y, x1, y + rng.uniform(-0.4, 0.4)), fill=dark + (70,), width=max(1, int(0.5 * SS)))
    d.line(P(-6, FT0, END + 2, FT0), fill=dark + (255,), width=int(0.8 * SS))
    d.line(P(-6, FT1, END + 2, FT1), fill=dark + (255,), width=int(0.8 * SS))
    for x in range(8, END, 38):
        for y in (FT0 + 3, FT1 - 3): d.ellipse(P(x - 0.8, y - 0.8, x + 0.8, y + 0.8), fill=dark + (255,))
    # mooring post + rope at the end
    d.rectangle(P(END - 6, 330, END + 1, FT1), fill=dark + (255,))
    d.ellipse(P(END - 6.5, 328, END + 1.5, 332), fill=SG.tint((110, 76, 50), ph) + (255,))
    rope = SG.tint((206, 184, 140), ph)
    for k in range(3): d.ellipse(P(END - 7.5, 334 + k * 2.2, END + 2.5, 336.6 + k * 2.2), outline=rope + (255,), width=max(1, int(0.8 * SS)))
    img.alpha_composite(lay)


def painted_battery(img, bat, ph):
    night = ph == 'night'
    col = paint_col(bat)
    if night: col = tuple(int(v * 0.92) for v in col)
    pl = ov(); d = ImageDraw.Draw(pl)
    cy = (FT0 + FT1) / 2
    # five painted blocks: 20 % each (a part-filled block shows the remainder)
    bx = 62; bw, bh, gap = 7, 10, 2.4
    for k in range(5):
        x = bx + k * (bw + gap)
        fill = max(0.0, min(1.0, (bat - k * 20) / 20))
        d.rectangle(P(x, cy - bh / 2, x + bw, cy + bh / 2), outline=(240, 232, 214, 255), width=max(1, int(0.8 * SS)))
        if fill > 0: d.rectangle(P(x + 1.2, cy + bh / 2 - 1.2 - (bh - 2.4) * fill, x + bw - 1.2, cy + bh / 2 - 1.2), fill=col + (255,))
    f = F('InterDisplay-Black.otf', 14.5)
    d.text(((bx + 5 * (bw + gap) + 5) * SS, (cy + 0.6) * SS), f'{bat}%', font=f, fill=col + (255,), anchor='lm')
    pl = worn(pl, seed=bat, lo=0.7)
    img.alpha_composite(pl)


def lantern_glow(img, x, y, a=70):
    g = ov(); ImageDraw.Draw(g).ellipse(P(x - 60, y - 30, x + 60, y + 30), fill=(255, 190, 100, a))
    img.alpha_composite(g.filter(ImageFilter.GaussianBlur(14 * SS)))


def face(h, hhmm, steps, s, bat, hr, life, birds_at=None):
    img, night, ph = LL.base(h, s)
    n, g = ph == 'night', ph in ('golden', 'dawn')
    WL.reeds(img, SS, 418, 470, LL.BANK - 16, seed=2, night=n, golden=g)
    WL.reeds(img, SS, 40, 70, LL.BANK - 10, seed=5, night=n, golden=g)
    life(img, ph)
    if birds_at: HO.birds(img, SS, 0.0, x0=birds_at[0], y0=birds_at[1], golden=g)
    jetty_big(img, ph)
    if n: lantern_glow(img, 136, 356, 80)
    painted_battery(img, bat, ph)
    SG.trail_sign(img, steps, ph, x=318, base=420)
    img.alpha_composite(HM.hud2(hhmm, '', steps, 15000, bat, steps_text=False, steps_arc=False, bat_arc=False))
    SG.date_hr(img, hr)
    return LM.circle(img)


def noon(img, ph):
    WL.fish_jump(img, SS, 300, 334, 0.45); WL.boat(img, SS, 226, 338, 2.0, 'fish')
    WL.duck(img, SS, 236, 380, 2.0, 0); WL.duck(img, SS, 256, 384, 2.0, 1)


def golden(img, ph):
    WL.boat(img, SS, 236, 346, 1.0, 'row', golden=True); WL.fish_jump(img, SS, 312, 330, 0.5, golden=True, big=0.9)
    WL.duck(img, SS, 250, 382, 1.0, 0, golden=True)


def night(img, ph):
    WL.boat(img, SS, 206, 370, 1.0, 'moored', night=True); WL.fish_jump(img, SS, 236, 330, 0.42, night=True, big=0.9); WL.fireflies(img, SS, 1.0)


if __name__ == '__main__':
    rows = [(12.33, '12:20', 6900, 0.46, 82, 72, noon, (372, 208), 'Noon · 82%'), (17.33, '17:20', 12100, 0.8, 46, 96, golden, (150, 214), 'Golden hour · 46%'),
            (21.5, '21:30', 15240, 1.02, 15, 64, night, None, 'Night · 15%')]
    sheet = Image.new('RGB', (480 * 3 + 48, 480 + 70), (14, 14, 18))
    dr = ImageDraw.Draw(sheet); LF = ImageFont.truetype(LM.FT + 'Inter-SemiBold.otf', 22)
    z = Image.new('RGB', (3 * 412 + 12, 232 + 12), (14, 14, 18))
    for i, (h, hhmm, steps, s, bat, hr, life, b, lab) in enumerate(rows):
        out = face(h, hhmm, steps, s, bat, hr, life, b)
        sheet.paste(out, (12 + i * 492, 12), out)
        tw = dr.textlength(lab, font=LF); dr.text((12 + i * 492 + 240 - tw / 2, 500), lab, font=LF, fill=(214, 220, 200))
        c = out.crop((30, 300, 230, 410)).resize((400, 220), Image.LANCZOS); z.paste(c, (12 + i * 412, 12), c)
    sheet.save(_OUT + 'mockups/jetty-paint.png'); z.save(_OUT + 'mockups/jetty-paint-closeup.png'); print('ok')
