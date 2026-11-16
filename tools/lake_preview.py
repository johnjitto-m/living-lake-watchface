"""Living Lake – composite still previews from the built bitmaps, using the same placements and formulas as the XML."""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))           # tools/
_ROOT = _os.path.dirname(_HERE)                                   # repo root
_RES = _ROOT + '/watchface/src/main/res/'                         # the watch face resources
_OUT = _ROOT + '/out/'                                            # previews, videos, mock-ups (not committed)
import json, math, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

B = _RES + ''
A = json.load(open(_HERE + '/art.json'))
LH = 1.21
_c = {}


def L(n):
    if n not in _c: _c[n] = Image.open(B + 'drawable/' + n + '.png').convert('RGBA')
    return _c[n]


def F(n, s): return ImageFont.truetype(B + 'font/' + n + '.ttf', s * 4)


def clamp(v, a, b): return max(a, min(b, v))


SUBPIX = False                                  # video renders: place moving sprites at fractional positions (no 1-px stepping)


def _frac(src, x, y):
    ix, iy = math.floor(x), math.floor(y); fx, fy = x - ix, y - iy
    if fx < 1e-3 and fy < 1e-3: return src, ix, iy
    out = src.transform((src.width + 1, src.height + 1), Image.AFFINE, (1, 0, -fx, 0, 1, -fy), resample=Image.BILINEAR)
    return out, ix, iy


def put(im, name, x=None, y=None, alpha=1.0, box=None):
    bx, by = (box or A[name])[:2]
    x = bx if x is None else x; y = by if y is None else y
    src = L(name)
    if alpha < 1:
        src = src.copy(); src.putalpha(src.split()[3].point(lambda v: int(v * clamp(alpha, 0, 1))))
    if alpha <= 0: return
    if SUBPIX and (x != int(x) or y != int(y)):
        src, ix, iy = _frac(src, x, y); im.alpha_composite(src, (ix, iy))
    else: im.alpha_composite(src, (int(round(x)), int(round(y))))


def put_tf(im, name, x, y, w, h, alpha=1.0, angle=0.0):
    """scaled / rotated placement (mirrors the XML transforms; angle in degrees, clockwise)"""
    if alpha <= 0 or w < 1 or h < 1: return
    src = L(name).resize((max(1, int(round(w))), max(1, int(round(h)))), Image.LANCZOS)
    if angle: src = src.rotate(-angle, resample=Image.BICUBIC, expand=True)
    if alpha < 1: src = src.copy(); src.putalpha(src.split()[3].point(lambda v: int(v * clamp(alpha, 0, 1))))
    cx, cy = x + w / 2, y + h / 2
    if SUBPIX:
        src, ix, iy = _frac(src, cx - src.width / 2, cy - src.height / 2); im.alpha_composite(src, (ix, iy))
    else: im.alpha_composite(src, (int(round(cx - src.width / 2)), int(round(cy - src.height / 2))))


def crow_at(im, u, k):
    """one crow at u seconds into its pass: in from the left edge, one full circle, off to the right (same as the XML)"""
    if u >= 49: return
    CW, CH_ = A['crow'][2], A['crow'][3]; cx, cy, rx, ry = 160, 196, 44, 13
    a = 4.71239 + 2 * math.pi * clamp((u - 13) / 18, 0, 1); e1 = clamp(u / 13, 0, 1); e3 = clamp((u - 31) / 18, 0, 1)
    if u < 13: x, y = -40 + (cx + 40) * e1, cy - ry - 18 + 18 * e1
    elif u < 31: x, y = cx + rx * math.cos(a), cy + ry * math.sin(a)
    else: x, y = cx + 400 * (0.7 * e3 + 0.3 * e3 * e3), cy - ry - 22 * e3 * e3
    circ = 13 <= u < 31; sc = 1 if u < 31 else 1 - 0.35 * e3
    w = 0.5 * CW * k * 0.86 * sc; h = 0.5 * CH_ * k * sc
    put_tf(im, 'crow', x - w / 2, y - h / 2, w, h, 1, 12 * math.cos(a) if circ else 0)


# ---- v1.6 calendar + rules (same as the XML)
DEEPAVALI = [(2026, 11, 7), (2026, 11, 8), (2027, 10, 28), (2027, 10, 29), (2028, 10, 16), (2028, 10, 17), (2029, 11, 4), (2029, 11, 5), (2030, 10, 25), (2030, 10, 26)]
KARTHIGAI = [(2026, 11, 24), (2027, 12, 12), (2028, 12, 1), (2029, 11, 20), (2030, 12, 8)]


def festivals(y, m, d, h):
    f = set()
    if m == 1 and 14 <= d <= 17: f.add('pongal')
    if m == 4 and d == 14: f.add('puthandu')
    if (y, m, d) in KARTHIGAI and h >= 17.5: f.add('karthigai')
    if (y, m, d) in DEEPAVALI and (h >= 18 or h < 7): f.add('deepavali')
    if m == 12 and (d == 25 or (d == 24 and h >= 17)): f.add('xmas')
    if (m == 12 and d == 31 and h >= 20) or (m == 1 and d == 1 and h < 1.5): f.add('nye')
    return f


def bursts(im, T, refl=False):
    for name, per, off, x0, xr, y0, yr in (('fw_gold', 3.7, 0, 96, 120, 196, 22), ('fw_pink', 4.6, 1.5, 250, 130, 190, 26), ('fw_blue', 3.1, 2.2, 170, 140, 208, 16)):
        p = ((T + off) % per) / per; n = math.floor((T + off) / per)
        S0 = A[name][2]; size = S0 * (0.3 + 0.7 * clamp(p / 0.3, 0, 1))
        cx = x0 + (n * 137) % xr; cy = y0 + (n * 53) % yr; al = clamp((0.9 - p) / 0.4, 0, 1)
        if refl: put(im, name + '_refl', cx - 30, 306, al * 0.7)
        else: put_tf(im, name, cx - size / 2, cy - size / 2 + 6 * p, size, size, al)


def weights(h):
    dawn = clamp((h - 5.5) / 0.75, 0, 1) if 5.5 <= h < 8.25 else 0
    day = clamp((h - 7.5) / 0.75, 0, 1) if 7.5 <= h < 17.0 else 0
    gold = clamp((h - 16.25) / 0.75, 0, 1) * clamp((19.25 - h) / 0.75, 0, 1) if 16.25 <= h < 19.25 else 0
    return [('night', 1.0), ('dawn', dawn), ('day', day), ('golden', gold)]


def phased(im, fmt, h, **kw):
    for ph, w in weights(h):
        if w > 0: put(im, fmt.format(ph=ph), alpha=w, **kw)


def arc(t): return 240 - 205 * math.cos(math.pi * t), 266 - 78 * clamp(math.sin(math.pi * t), 0, 1) ** 0.55


def text_layer(im4, x, y, w, size, s, font, col, align='CENTER', spacing=0.0, inline=None):
    """PartText: box height = line height, so the ascender sits on the box top; CENTER / START alignment"""
    f = F(font, size); d = ImageDraw.Draw(im4)
    sp = spacing * size * 4
    parts = []                          # (kind, payload, width)
    for kind, val in (inline or [('t', s)]):
        if kind == 't':
            for ch in val: parts.append(('t', ch, f.getlength(ch) + sp))
        else:
            parts.append(('i', val, 11 * 4 + sp))
    tot = sum(p[2] for p in parts) - sp
    xx = (x + w / 2) * 4 - tot / 2 if align == 'CENTER' else x * 4
    for kind, val, wd in parts:
        if kind == 't': d.text((xx, y * 4), val, font=f, fill=col)
        else: im4.alpha_composite(L('heart_small').resize((44, 40), Image.LANCZOS), (int(xx), int(y * 4 + size * 4 * 0.42 - 20 + size * 4 * 0.22)))
        xx += wd


def hud_text(im, fn, shadow=None):
    """draw text at 4x on a layer (optionally with a blurred shadow) and composite"""
    lay = Image.new('RGBA', (1920, 1920), (0, 0, 0, 0)); fn(lay)
    lay = lay.resize((480, 480), Image.LANCZOS)
    if shadow:
        r, a, dy = shadow
        sh = Image.new('RGBA', lay.size, (0, 0, 0, 0)); sh.putalpha(lay.split()[3].point(lambda v: int(v * a)))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(r / 2)), (0, dy))
    im.alpha_composite(lay)


def state(hh, mm, steps=6900, goal=15000, bat=82, hr=72, wx=None, moon=4, t=2.0, h24=True, catch=None, dow='WED', day=11, mon='NOV', month=11, notif=0, hud=True, anim=False, new_bat=None, new_sign=None, sky_fx=None, pre=None, tree_fn=None, post=None,
          year=2026, doy=None, cfg=None, edges=None, fx_t=None):
    h = hh + mm / 60
    cfg = dict(dict(hr=True, life=True, fest=True, pace=True), **(cfg or {}))
    doy = doy if doy is not None else (__import__('datetime').date(year, month, day).timetuple().tm_yday)
    T = hh * 3600 + mm * 60 + t
    Tfx = T if fx_t is None else hh * 3600 + mm * 60 + fx_t          # crows + lanterns can run on their own (faster) clock in demos
    fest = set()                                                    # v1.7: festivals removed
    crows_on = 14.5 <= h < 17.5 and doy % 2 == 1 and wx not in ('rain', 'storm', 'snow') and cfg['life']
    fw_on = bool(fest & {'deepavali', 'nye'}) and wx not in ('rain', 'storm', 'snow')
    night = h >= 19.0 or h < 5.5
    precip = wx in ('rain', 'storm', 'snow'); dim = wx in ('cloud', 'fog')
    im = Image.new('RGBA', (480, 480), (0, 0, 0, 255))
    phased(im, 'sky_{ph}', h)
    if night and not precip and not dim: put(im, 'stars_tw', alpha=(140 + 115 * math.sin(t * 2 * math.pi / 5)) / 255)
    sunup = 6 <= h < 18
    st = (h - 6) / 12; mt = ((h + 6) % 24) / 12
    low = 1 - clamp(math.sin(math.pi * st) * 2.2, 0, 1)
    if not precip:
        k = 90 / 255 if dim else 1
        if sunup:
            x, y = arc(st)
            put(im, 'sun_day', x - 100, y - 100, (1 - low) * k); put(im, 'sun_low', x - 100, y - 100, low * k)
        else:
            x, y = arc(mt)
            put(im, 'moon_glow', x - 70, y - 70, (1 - math.cos(moon * 0.7854)) * 127 / 255 * k)
            put(im, f'moon_{moon}', x - 12, y - 12, k)
    summer, sw, ne, cool = 3 <= month <= 5, 6 <= month <= 9, month >= 10, month <= 2
    if wx in ('rain', 'storm'): put(im, 'cl_rain_night' if night else 'cl_rain_day')
    elif wx in ('cloud', 'fog') or ne: phased(im, 'cl_fair_{ph}', h)
    elif sw: phased(im, 'cl_tower_{ph}', h)
    if crows_on:
        for delay, k in ((0, 1.0), (1.6, 0.9), (3.2, 0.95)):
            crow_at(im, (Tfx - delay) % 90, k)
    if fw_on: bursts(im, T)
    if 5.75 <= h < 18.75 and not precip and not crows_on and cfg['life']:
        p = clamp((t * 37 % 150) / 100, 0, 1)
        bx, by = A['birds'][:2]
        put(im, f'birds_{int(t * 16) % 16:02d}', -80 + (0.45 + (t * 6.2 / 620 if anim else 0)) * 620 - 240 + bx, by - 16)
    if sky_fx: sky_fx(im, h, night)
    phased(im, 'land_{ph}', h)
    if summer: phased(im, 'drybank_{ph}', h)
    if 'karthigai' in fest: put(im, 'fe_deepam_peak', alpha=(220 + 35 * math.sin(t * 2 * math.pi / 2.3)) / 255)
    if cfg['life'] and 5.5 <= h < 9.5 and doy % 3 == 0 and not precip and wx != 'fog': phased(im, 'tahr_{ph}', h)
    if not precip and not dim:
        tw = 0.5 + 0.5 * math.sin(t * 2 * math.pi / 3)
        if sunup:
            x = arc(st)[0] - 40
            for kind, a in (('day', 1 - low), ('warm', low)):
                put(im, f'refl_{kind}', x, alpha=a); put(im, f'spark_{kind}_a', x, alpha=a * tw); put(im, f'spark_{kind}_b', x, alpha=a * (1 - tw))
        else:
            x = arc(mt)[0] - 40; a = ((1 - math.cos(moon * 0.7854)) * 110 + 30) / 255
            put(im, 'refl_moon', x, alpha=a); put(im, 'spark_moon_a', x, alpha=a * tw); put(im, 'spark_moon_b', x, alpha=a * (1 - tw))
    # jetty + paint
    phased(im, 'jetty_{ph}', h)
    col = (0x78, 0xe2, 0x78) if bat >= 50 else ((0xff, 0xbc, 0x40) if bat >= 20 else (0xff, 0x4e, 0x46))
    d = ImageDraw.Draw(im, 'RGBA')
    big = im.resize((1920, 1920), Image.LANCZOS) if not new_bat else Image.new('RGBA', (1920, 1920)); bd = ImageDraw.Draw(big)
    from layout15 import BLOCKS, BAT_TEXT_X
    for k in range(5):
        x = BLOCKS['x0'] + k * (BLOCKS['w'] + BLOCKS['gap']); top = BLOCKS['cy'] - BLOCKS['h'] / 2 + 2; bot = BLOCKS['cy'] + BLOCKS['h'] / 2 - 2
        if bat >= 20 * k + 15: bd.rectangle([(x + 2) * 4, top * 4, (x + BLOCKS['w'] - 2) * 4 - 1, bot * 4 - 1], fill=col + (255,))
        elif bat >= 20 * k + 5: bd.rectangle([(x + 2) * 4, (top + bot) / 2 * 4, (x + BLOCKS['w'] - 2) * 4 - 1, bot * 4 - 1], fill=col + (255,))
    bd.text((BAT_TEXT_X * 4, int(round(BLOCKS['cy'] - 23 * LH / 2 + 0.8)) * 4), f'{bat}%', font=F('lake_black', 23), fill=col + (255,), stroke_width=8, stroke_fill=(0x28, 0x18, 0x0e, 255))
    im = big.resize((480, 480), Image.LANCZOS) if not new_bat else im
    if not new_bat: phased(im, 'jwear_{ph}', h)
    else: im = new_bat(im, bat, night, h)
    if 'pongal' in fest: phased(im, 'fe_pongal_{ph}', h)
    if 'puthandu' in fest: phased(im, 'fe_puthandu_{ph}', h)
    if 'deepavali' in fest: put(im, 'fe_diyas', y=A['fe_diyas'][1] + 0.8 * math.sin(t * 2 * math.pi / 3.5)); put(im, 'fe_lights_warm')
    elif 'nye' in fest: put(im, 'fe_lights_warm')
    elif 'xmas' in fest and (h >= 17.5 or h < 6): put(im, 'fe_lights_xmas')
    if fw_on: bursts(im, T, refl=True)
    if ne: phased(im, 'lotus_{ph}', h)
    if notif:
        bp = 'night' if night else 'day'
        for i in range(min(3, notif)): put(im, f'bottle{i}_{bp}')
        put(im, 'bottle_rip_04', box=A['bottle_rip'], alpha=0.35 if night else 1)
    # tree
    pct = steps * 100 / goal
    k = 9 if pct >= 100 else int(clamp(math.floor(pct / 12.5), 0, 8))
    if pre: pre(im, h, night)
    behind = cfg['pace'] and h >= 10 and pct < 0.6 * clamp((h - 7) / 14, 0, 1) * 100 and pct < 100
    kind = 'treek' if summer else 'tree'
    if behind and k > 0: kind += 'd'
    if tree_fn: tree_fn(im, h, night, steps)
    else: phased(im, kind + '_{ph}_' + str(k), h)
    if night and not precip:
        for i in range(3 if pct >= 100 else 2): put(im, f'flies_{i}', alpha=clamp(math.sin(t * 2 * math.pi / 4 + i * 2.1), 0, 1))
    # sign
    ink = (0xff, 0xe2, 0xb4) if night else (0xff, 0xf4, 0xe2)
    # lake life
    if wx != 'storm' and cfg['life']:
        tag = 'n' if night else ('g' if h >= 16.25 else 'd')
        from layout15 import FISH_SPOTS
        fx = FISH_SPOTS[mm % 4] - 220 + A[f'fish_{tag}'][0]
        if not anim: put(im, f'fish_{tag}_{12:02d}', fx, box=A[f'fish_{tag}'])
        else:
            cyc = (t + 0.6) % 11.27
            if cyc < 34 / 15: put(im, f'fish_{tag}_{int(cyc * 15):02d}', fx, box=A[f'fish_{tag}'])
    if not night and not precip and cfg['life']:
        ph = 'dawn' if 5.5 <= h < 7.5 else ('golden' if 16.75 <= h < 19.0 else 'day')
        p = (t * 13 % 420) / 420
        dp = ((T % 420) / 420) if anim else 0.45
        put(im, f'ducks_{ph}', A['ducks_day'][0] - 98 + dp * 130, y=A['ducks_day'][1] + 0.7 * math.sin(t * 2 * math.pi / 3), alpha=clamp((0.5 - abs(dp - 0.5)) * 10, 0, 1) if anim else 1)
    if not (precip and not night) and cfg['life']:
        if 5.5 <= h < 7.5: put(im, f'boat_rowd_{int(t * 8) % 24:02d}', box=A['boat_rowd'])
        elif 7.5 <= h < 16.75:
            if catch is not None: put(im, f'boat_catch_{catch:02d}', box=A['boat_catch'])
            else: put(im, f'boat_fish_{int(t * 8) % 48:02d}', box=A['boat_fish'])
        elif 16.75 <= h < 19.0: put(im, f'boat_rowg_{int(t * 8) % 24:02d}', box=A['boat_rowg'])
        else: put(im, f'boat_moor_{int(t * 8) % 24:02d}', box=A['boat_moor'])
    if not new_sign:
        from layout15 import SIGN
        if night: put(im, 'sign_lantern')
        phased(im, 'sign_{ph}', h)
        hud_text(im, lambda l: text_layer(l, SIGN['cx'] - SIGN['W'] // 2, SIGN['top'] + 4, SIGN['W'], 28, f'{steps:,}', 'lake_semi', ink + (255,)), shadow=(1.6, 0.55, 1))
    if 'karthigai' in fest: put(im, 'fe_lamps', alpha=(225 + 30 * math.sin(t * 2 * math.pi / 1.7)) / 255)
    if 'xmas' in fest:
        if h >= 17.5 or h < 6: put(im, 'fe_star_night')
        else: phased(im, 'fe_star_{ph}', h)
    if pct >= 100 and 18 <= h < 23.5 and not precip:
        for i, (x0, kk) in enumerate([(214, 1.0), (172, 0.85), (290, 0.9), (236, 0.8), (140, 0.75), (330, 0.8), (196, 0.7), (268, 0.75)]):
            pp = ((Tfx + i * 46 / 8) % 46) / 46; sz = 64 * kk * (1 - 0.55 * pp)
            put_tf(im, 'lantern', x0 + 9 * math.sin(Tfx * 0.21 + i) - sz / 2, 318 - 150 * pp - sz / 2, sz, sz, clamp(pp / 0.08, 0, 1) * clamp((1 - pp) / 0.25, 0, 1))
    if cool and not precip:
        w = dict(weights(h))
        for ph in ('dawn', 'day', 'golden'):
            if cfg['life']: put(im, f'coolbirds_{ph}', alpha=w[ph])
        put(im, 'mist_water', alpha=clamp((h - 5.25) / 0.75, 0, 1) * clamp((9.5 - h) / 1.5, 0, 1))
    if summer and not precip:
        hz = Image.new('RGBA', (480, 480), (0xff, 0xd6, 0xa0, int(0x22 * dict(weights(h))['day']))); im.alpha_composite(hz)
    if new_sign: im = new_sign(im, steps, night, h)
    if post: post(im, h, night)
    # weather
    if wx in ('rain', 'storm', 'snow'):
        tint = {'storm': (0x3a, 0x42, 0x50, 0x78), 'rain': (0x4a, 0x54, 0x62, 0x5a), 'snow': (0x70, 0x78, 0x84, 0x46)}[wx]
        im.alpha_composite(Image.new('RGBA', (480, 480), tint))
        if wx != 'snow':
            put(im, f'rain_rip_{int(t * 10) % 12:02d}', box=A['rain_rip'])
            put(im, 'wx_rain', 0, -360 + (t * 240) % 360, box=(0, 0))
        else: put(im, 'wx_snow', 0, -360 + (t * 36) % 360, box=(0, 0))
    if wx == 'fog': put(im, 'wx_fog')
    # time + date / heart rate
    if not hud: return circle(im)
    hh_s = f'{hh:02d}' if h24 else f'{(hh % 12) or 12}'
    hud_text(im, lambda l: text_layer(l, 0, 48, 480, 92, f'{hh_s}:{mm:02d}', 'lake_time', (255, 255, 255, 255)), shadow=(7, 0.6, 1))
    hud_text(im, lambda l: text_layer(l, 0, 150, 480, 15, f'{dow}  {day}  {mon}', 'lake_text', (255, 255, 255, 230), spacing=0.21), shadow=(5, 0.63, 1))
    def hrl(q):
        q.alpha_composite(L('heart_small').resize((44, 40), Image.LANCZOS), (318 * 4, int(150 * 4 + 15 * 4 * 0.64 - 20)))
        ImageDraw.Draw(q).text(((318 + 14) * 4, 150 * 4), f'{hr}' if hr > 0 else '--', font=F('lake_text', 15), fill=(255, 255, 255, 230))
    if cfg['hr']: hud_text(im, hrl, shadow=(5, 0.63, 1))
    if edges:
        import demo16
        demo16.edge_slots(im, *edges)
    return circle(im)


def circle(im):
    m = Image.new('L', (480, 480), 0); ImageDraw.Draw(m).ellipse([0, 0, 479, 479], fill=255)
    out = Image.new('RGBA', (480, 480), (0, 0, 0, 0)); out.paste(im, (0, 0), m)
    return out


def aod():
    import demo_aod2 as D2
    class _F:                              # always-on has no scene
        def scene(self, t): return Image.new('RGBA', (480, 480), (0, 0, 0, 0))
    return D2.frame(_F(), D2.Block('12:20', 'WED  11  NOV', 72), 1.0, 0.0, scene_on=False)


if __name__ == '__main__':
    S = {
        'nov_noon': lambda: state(12, 20, steps=6900, bat=82, hr=72, month=11),
        'nov_bottle': lambda: state(14, 5, steps=8800, bat=74, hr=70, month=11, notif=1),
        'nov_rain': lambda: state(10, 10, steps=4200, bat=64, hr=75, wx='rain', month=11),
        'summer': lambda: state(12, 40, steps=11300, bat=66, hr=78, month=4),
        'monsoon': lambda: state(11, 30, steps=7400, bat=58, hr=74, month=7),
        'cool_dawn': lambda: state(7, 10, steps=900, bat=96, hr=62, month=1, dow='THU', day=15, mon='JAN'),
        'golden': lambda: state(17, 25, steps=12100, bat=46, hr=96, month=11),
        'night_msgs': lambda: state(21, 30, steps=15240, bat=15, hr=64, moon=3, month=11, notif=3),
        'aod': aod,
    }
    which = sys.argv[1:] or list(S)
    os.makedirs(_OUT + 'preview', exist_ok=True)
    ims = {}
    for k in which:
        ims[k] = S[k](); ims[k].save(_OUT + f'preview/{k}.png')
    if 'nov_noon' in ims: ims['nov_noon'].save(B + 'drawable/preview.png')
    cols = 3; rows = math.ceil(len(which) / cols)
    sheet = Image.new('RGB', (cols * 492 + 12, rows * 492 + 12), (14, 14, 18))
    for i, k in enumerate(which): sheet.paste(ims[k], (12 + (i % cols) * 492, 12 + (i // cols) * 492), ims[k])
    sheet.save(_OUT + 'preview/all.png'); print('ok', which)
