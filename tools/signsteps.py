"""Heart rate beside the date; steps on a wooden trail sign in the foreground; birds; living lake."""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))           # tools/
_ROOT = _os.path.dirname(_HERE)                                   # repo root
_RES = _ROOT + '/watchface/src/main/res/'                         # the watch face resources
_OUT = _ROOT + '/out/'                                            # previews, videos, mock-ups (not committed)
import math, sys
sys.path.insert(0, _HERE)
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import combomock as CM, landmock as LM, lakelife as LL, waterlife as WL, hrmock as HM, hroptions as HO
from landmock import SS, W, P, ov, F


def tint(c, ph):
    if ph == 'night': return tuple(int(v * 0.38) for v in c)
    if ph in ('golden', 'dawn'): return (min(255, int(c[0] * 1.06)), int(c[1] * 0.84), int(c[2] * 0.7))
    return c


def trail_sign(img, steps, ph, x=240, base=438):
    night = ph == 'night'
    wood, dark, plank = tint((150, 108, 68), ph), tint((92, 62, 40), ph), tint((134, 96, 60), ph)
    lay = ov(); d = ImageDraw.Draw(lay)
    # shadow on the grass
    sh = ov(); ImageDraw.Draw(sh).ellipse(P(x - 40, base - 3, x + 40, base + 4), fill=(0, 0, 0, 80))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(2 * SS)))
    for lx in (x - 26, x + 26):
        d.rectangle(P(lx - 2, base - 30, lx + 2, base), fill=dark + (255,))
    bx0, by0, bx1, by1 = x - 38, base - 50, x + 38, base - 20
    d.rounded_rectangle(P(bx0, by0, bx1, by1), radius=3 * SS, fill=wood + (255,), outline=dark + (255,), width=int(1.3 * SS))
    for yy in (by0 + 10, by0 + 20): d.line(P(bx0 + 2, yy, bx1 - 2, yy), fill=plank + (255,), width=max(1, int(0.6 * SS)))
    for (nx, ny) in ((bx0 + 4, by0 + 4), (bx1 - 4, by0 + 4), (bx0 + 4, by1 - 4), (bx1 - 4, by1 - 4)):
        d.ellipse(P(nx - 0.9, ny - 0.9, nx + 0.9, ny + 0.9), fill=dark + (255,))
    img.alpha_composite(lay)
    if night:   # a small lantern on the post lights the sign
        lx, ly = x + 40, base - 52
        g = ov(); ImageDraw.Draw(g).ellipse(P(x - 44, base - 64, x + 52, base - 10), fill=(255, 190, 100, 60))
        img.alpha_composite(g.filter(ImageFilter.GaussianBlur(10 * SS)))
        d = ImageDraw.Draw(img)
        d.line(P(x + 38, base - 46, lx, ly - 3), fill=dark + (255,), width=int(0.9 * SS))
        d.rectangle(P(lx - 2, ly - 3, lx + 2, ly + 3), fill=(255, 220, 140, 255))
    ink = (255, 244, 226) if not night else (255, 226, 180)
    f = F('InterDisplay-SemiBold.otf', 17); s = f'{steps:,}'
    d = ImageDraw.Draw(img)
    d.text((x * SS, (by0 + 4) * SS), s, font=f, fill=(60, 36, 20, 120), anchor='ma')        # carved edge
    d.text((x * SS, (by0 + 3) * SS), s, font=f, fill=ink + (255,), anchor='ma')
    fl = F('Inter-SemiBold.otf', 7.5); lab = 'STEPS'; sp = 1.8
    tot = sum(fl.getlength(c) for c in lab) / SS + sp * (len(lab) - 1); xx = x - tot / 2
    for c in lab:
        d.text((xx * SS, (by1 - 9.5) * SS), c, font=fl, fill=ink + (210,)); xx += fl.getlength(c) / SS + sp


def date_hr(img, hr):
    f = F('Inter-Medium.otf', 15); sp = 3.2; txt = 'WED  11  NOV'
    wd = sum(f.getlength(c) for c in txt) / SS + sp * (len(txt) - 1)
    wh = 12 + 3 + f.getlength(str(hr)) / SS
    gap = 18; x = 240 - (wd + gap + wh) / 2
    for c in txt:
        HO.shadow_text(img, x, 150, c, f, (255, 255, 255, 225)); x += f.getlength(c) / SS + sp
    x += gap - sp
    HO.heart_icon(ImageDraw.Draw(img), x + 5, 159.5, 0.3)
    HO.shadow_text(img, x + 13, 150, str(hr), f)


def face(h, hhmm, steps, s, life, bat, hr, birds_at):
    img, night, ph = LL.base(h, s)
    LL.statics(img, SS, ph)
    life(img, SS, ph)
    if birds_at: HO.birds(img, SS, 0.0, x0=birds_at[0], y0=birds_at[1], golden=ph == 'golden')
    trail_sign(img, steps, ph, x=318, base=420)
    img.alpha_composite(HM.hud2(hhmm, '', steps, 15000, bat, steps_text=False, steps_arc=False))
    date_hr(img, hr)
    return LM.circle(img)


if __name__ == '__main__':
    rows = [(12.33, '12:20', 6900, 0.46, LL.noon_life, 82, 72, (372, 208), 'Noon'),
            (17.33, '17:20', 12100, 0.8, LL.golden_life, 46, 96, (150, 214), 'Golden hour'),
            (21.5, '21:30', 15240, 1.02, LL.night_life, 15, 64, None, 'Night · goal reached')]
    sheet = Image.new('RGB', (480 * 3 + 48, 480 + 70), (14, 14, 18))
    dr = ImageDraw.Draw(sheet); LF = ImageFont.truetype(LM.FT + 'Inter-SemiBold.otf', 22)
    for i, (h, hhmm, steps, s, life, bat, hr, b, lab) in enumerate(rows):
        out = face(h, hhmm, steps, s, life, bat, hr, b)
        sheet.paste(out, (12 + i * 492, 12), out)
        tw = dr.textlength(lab, font=LF); dr.text((12 + i * 492 + 240 - tw / 2, 500), lab, font=LF, fill=(214, 220, 200))
    sheet.save(_OUT + 'mockups/steps-sign.png')
    z = Image.new('RGB', (3 * 400 + 48, 246), (14, 14, 18))
    for i in range(3):
        c = sheet.crop((12 + i * 492 + 240, 12 + 300, 12 + i * 492 + 460, 12 + 430)).resize((400, 236), Image.LANCZOS)
        z.paste(c, (12 + i * 412, 5))
    z.save(_OUT + 'mockups/steps-sign-closeup.png'); print('ok')
