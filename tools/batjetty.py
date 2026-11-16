"""Battery on the jetty: painted beam / jetty lamp / water gauge. Day (82 %) and night (15 %)."""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))           # tools/
_ROOT = _os.path.dirname(_HERE)                                   # repo root
_RES = _ROOT + '/watchface/src/main/res/'                         # the watch face resources
_OUT = _ROOT + '/out/'                                            # previews, videos, mock-ups (not committed)
import math, sys
sys.path.insert(0, _HERE)
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import combomock as CM, landmock as LM, lakelife as LL, waterlife as WL, hrmock as HM, hroptions as HO, signsteps as SG
from landmock import SS, W, P, ov, F

def bcol(b): return (110, 220, 120) if b >= 50 else ((255, 190, 70) if b >= 20 else (255, 80, 80))


def jetty2(img, ph, end=128):
    night = ph == 'night'
    w, wd = SG.tint((138, 98, 62), ph), SG.tint((92, 62, 40), ph)
    lay = ov(); d = ImageDraw.Draw(lay)
    for x in range(36, end, 23):
        d.rectangle(P(x - 1.6, 352, x + 1.6, 374), fill=wd + (255,))
        d.rectangle(P(x - 1.6, 374, x + 1.6, 384), fill=wd + (80,))
    d.rectangle(P(4, 349, end + 2, 354), fill=w + (255,))                 # deck
    for x in range(8, end + 2, 6): d.line(P(x, 349, x, 354), fill=wd + (255,), width=max(1, int(0.5 * SS)))
    d.rectangle(P(4, 354, end + 2, 367), fill=SG.tint((112, 78, 48), ph) + (255,))   # front beam
    d.line(P(4, 354, end + 2, 354), fill=wd + (255,), width=int(0.8 * SS))
    img.alpha_composite(lay)


def statics2(img, ph):
    n, g = ph == 'night', ph in ('golden', 'dawn')
    WL.reeds(img, SS, 418, 470, LL.BANK - 16, seed=2, night=n, golden=g)
    WL.reeds(img, SS, 134, 172, LL.BANK - 6, seed=5, night=n, golden=g)
    jetty2(img, ph)


def painted(img, bat, ph):
    f = F('InterDisplay-Bold.otf', 10); s = f'{bat}%'
    d = ImageDraw.Draw(img)
    c = bcol(bat) if ph != 'night' else tuple(int(min(255, v * 0.95)) for v in bcol(bat))
    d.text((88 * SS, 360.6 * SS), s, font=f, fill=c + (255,), anchor='mm', stroke_width=int(0.9 * SS), stroke_fill=(40, 26, 16, 255))


def lamp(img, bat, ph, t=0.0):
    night = ph == 'night'; x, top = 124, 314
    d = ImageDraw.Draw(img); post = SG.tint((70, 60, 56), ph)
    d.rectangle(P(x - 1.3, top, x + 1.3, 350), fill=post + (255,))
    d.rectangle(P(x - 4.5, top - 7, x + 4.5, top), fill=post + (255,))
    d.polygon(P(x - 5.5, top - 7, x, top - 11, x + 5.5, top - 7), fill=post + (255,))
    low = bat < 20
    lc = (255, 90, 80) if low else (255, 222, 150)
    k = max(0.25, bat / 100) if not low else 0.6
    if night or low:
        g = ov(); ImageDraw.Draw(g).ellipse(P(x - 26, top - 30, x + 26, top + 20), fill=lc + (int(110 * k),))
        img.alpha_composite(g.filter(ImageFilter.GaussianBlur(8 * SS)))
        # its reflection on the water
        rl = ov(); rd = ImageDraw.Draw(rl)
        for i in range(9):
            y = 366 + i * 2.2; w_ = 3.2 - i * 0.3
            if w_ > 0: rd.line(P(x - w_, y, x + w_, y), fill=lc + (int(150 * k),), width=max(1, int(0.8 * SS)))
        img.alpha_composite(rl)
    d = ImageDraw.Draw(img)
    d.rectangle(P(x - 3, top - 6, x + 3, top - 1), fill=(lc if (night or low) else (236, 236, 226)) + (255,))
    # plaque on the post
    pl = SG.tint((236, 230, 214), ph) if not night else (60, 56, 52)
    d.rounded_rectangle(P(x - 13, 326, x + 13, 338), radius=1.5 * SS, fill=pl + (255,), outline=post + (255,), width=int(0.8 * SS))
    f = F('InterDisplay-Bold.otf', 9)
    tc = (60, 50, 40) if not night else (255, 226, 180)
    if low: tc = (220, 40, 40) if not night else (255, 110, 100)
    d.text((x * SS, 327.6 * SS), f'{bat}%', font=f, fill=tc + (255,), anchor='ma')


def gauge(img, bat, ph):
    night = ph == 'night'; x, y0, y1 = 140, 316, 372
    lay = ov(); d = ImageDraw.Draw(lay)
    board = (238, 236, 228) if not night else (70, 72, 80)
    mark = (40, 40, 44) if not night else (150, 150, 160)
    d.rectangle(P(x - 4, y0, x + 4, y1), fill=board + (255,))
    for i in range(0, 11):                                   # ticks every 10 %
        yy = y1 - (y1 - y0) * i / 10
        d.line(P(x - 4, yy, x - (0.5 if i % 5 else -1.5), yy), fill=mark + (255,), width=max(1, int(0.7 * SS)))
    fy = y1 - (y1 - y0) * bat / 100
    d.rectangle(P(x + 0.8, fy, x + 3.4, y1), fill=bcol(bat) + (255,))
    d.rectangle(P(x - 5, y0 - 12, x + 5, y0), fill=SG.tint((92, 62, 40), ph) + (255,))
    img.alpha_composite(lay)
    # the lake laps at its foot
    wl = ov(); wd = ImageDraw.Draw(wl)
    wd.rectangle(P(x - 6, 362, x + 6, 374), fill=(80, 130, 170, 140) if not night else (14, 20, 40, 160))
    wd.line(P(x - 7, 362, x + 7, 362), fill=(255, 255, 255, 120 if not night else 50), width=int(0.8 * SS))
    img.alpha_composite(wl)
    f = F('InterDisplay-Bold.otf', 8)
    ImageDraw.Draw(img).text((x * SS, (y0 - 10.6) * SS), f'{bat}', font=f, fill=(255, 244, 226, 255), anchor='ma')
    HO.shadow_text(img, x + 9, y0 - 12, '%', F('Inter-SemiBold.otf', 7), (255, 255, 255, 0)) if False else None


def face(h, hhmm, steps, s, bat, hr, opt, ph_life, birds_at=None):
    img, night, ph = LL.base(h, s)
    statics2(img, ph)
    if ph == 'night':
        WL.boat(img, SS, 168, 368, 1.0, 'moored', night=True); WL.fish_jump(img, SS, 230, 330, 0.42, night=True, big=0.9); WL.fireflies(img, SS, 1.0)
    else:
        WL.fish_jump(img, SS, 300, 336, 0.45); WL.boat(img, SS, 214, 338, 2.0, 'fish'); WL.duck(img, SS, 176, 372, 2.0, 0); WL.duck(img, SS, 196, 377, 2.0, 1)
    if birds_at: HO.birds(img, SS, 0.0, x0=birds_at[0], y0=birds_at[1])
    opt(img, bat, ph)
    SG.trail_sign(img, steps, ph, x=318, base=420)
    img.alpha_composite(HM.hud2(hhmm, '', steps, 15000, bat, steps_text=False, steps_arc=False, bat_arc=False))
    SG.date_hr(img, hr)
    return LM.circle(img)


if __name__ == '__main__':
    opts = [(painted, '1 · Painted on the jetty'), (lamp, '2 · Jetty lamp'), (gauge, '3 · Water gauge')]
    sheet = Image.new('RGB', (480 * 3 + 48, 2 * 492 + 60), (14, 14, 18))
    dr = ImageDraw.Draw(sheet); LF = ImageFont.truetype(LM.FT + 'Inter-SemiBold.otf', 22)
    crops = []
    for i, (fn, lab) in enumerate(opts):
        for j, (h, hhmm, steps, s, bat, hr, b) in enumerate(((12.33, '12:20', 6900, 0.46, 82, 72, (372, 208)), (21.5, '21:30', 15240, 1.02, 15, 64, None))):
            out = face(h, hhmm, steps, s, bat, hr, fn, None, b)
            sheet.paste(out, (12 + i * 492, 12 + j * 492), out)
            crops.append(out.crop((20, 290, 220, 400)).resize((400, 220), Image.LANCZOS))
        tw = dr.textlength(lab, font=LF); dr.text((12 + i * 492 + 240 - tw / 2, 2 * 492 + 16), lab, font=LF, fill=(214, 220, 200))
    sheet.save(_OUT + 'mockups/battery-jetty.png')
    z = Image.new('RGB', (3 * 412 + 12, 2 * 232 + 12), (14, 14, 18))
    for i in range(3):
        for j in range(2):
            c = crops[i * 2 + j]; z.paste(c, (12 + i * 412, 12 + j * 232), c)
    z.save(_OUT + 'mockups/battery-jetty-closeup.png'); print('ok')
