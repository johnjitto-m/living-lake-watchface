"""Demos for Living Lake: seasons, the message bottle, festivals on the lake, the drooping tree."""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))           # tools/
_ROOT = _os.path.dirname(_HERE)                                   # repo root
_RES = _ROOT + '/watchface/src/main/res/'                         # the watch face resources
_OUT = _ROOT + '/out/'                                            # previews, videos, mock-ups (not committed)
import math, random, sys
sys.path.insert(0, _HERE)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import landmock as LM, combomock as CM, lakelife as LL, waterlife as WL, hrmock as HM, hroptions as HO, signsteps as SG, batjetty2 as BJ
from landmock import SS, W, P, ov, ridge_pts

FT = LM.FT


# ------------------------------------------------------------------ a tree with seasons and moods
def tree2(img, bx, by, s, night=False, seed=7, scale=1.0, bloom=None, flies=True, fixed_depth=None, opt=None):
    o = opt or {}
    if not o: return LM.tree(img, bx, by, s, night, seed, scale, bloom, flies, fixed_depth)
    rng = random.Random(seed); d = ImageDraw.Draw(img)
    trunk = (70, 48, 34) if not night else (30, 26, 28)
    greens = o.get('leaves') or ([(46, 104, 52), (70, 140, 64), (112, 170, 80)] if not night else [(20, 44, 38), (30, 62, 52), (54, 90, 84)])
    droop, bare = o.get('droop', 0.0), o.get('bare', False)
    g = min(max(s, 0.12), 1.0)
    H = (34 + 92 * g) * scale
    depth = 4
    leaves, tips = [], []

    def br(x, y, ang, ln, wd, dep):
        if droop:                                  # outer branches sag towards the ground
            k = droop * (0.15 + 0.28 * (4 - dep) / 4)
            ang = ang + k if ang > math.pi / 2 else ang - k
        x2 = x + math.cos(ang) * ln; y2 = y - math.sin(ang) * ln
        d.line(P(x, y, x2, y2), fill=trunk + (255,), width=max(1, int(wd * SS)))
        d.ellipse(P(x2 - wd / 2, y2 - wd / 2, x2 + wd / 2, y2 + wd / 2), fill=trunk + (255,))
        tips.append((x, y, x2, y2, wd))
        if dep == 0:
            leaves.append((x2, y2)); return
        n = 2 if dep > 1 or rng.random() < 0.5 else 3
        for i in range(n):
            spread = rng.uniform(0.32, 0.62)
            a = ang + (spread if i == 0 else -spread if i == 1 else rng.uniform(-0.15, 0.15))
            br(x2, y2, a, ln * rng.uniform(0.66, 0.8), wd * 0.66, dep - 1)
        if dep <= 2: leaves.append((x2, y2))

    br(bx, by, math.pi / 2 + rng.uniform(-0.06, 0.06), H * 0.38, (3 + 6 * g) * scale, depth)
    R = (7 + 14 * g) * scale * (0.82 if droop else 1.0)
    if bare:                                       # winter: snow resting on the branches
        sn = ov(); sd = ImageDraw.Draw(sn)
        for (x, y, x2, y2, wd) in tips:
            if wd > 0.6: sd.line(P(x, y - wd * 0.6, x2, y2 - wd * 0.6), fill=(250, 252, 255, 230), width=max(1, int(wd * 0.55 * SS)))
        img.alpha_composite(sn)
        return leaves
    fol = ov(); fd = ImageDraw.Draw(fol)
    for layer, col in enumerate(greens):
        for (x, y) in leaves:
            for _ in range(2 if layer < 2 else 1):
                r = R * rng.uniform(0.55, 0.95) * (1.0 - layer * 0.18)
                ox = rng.uniform(-R * 0.4, R * 0.4) - layer * R * 0.18
                oy = rng.uniform(-R * 0.4, R * 0.3) - layer * R * 0.22 + droop * R * 0.35
                fd.ellipse(P(x + ox - r, y + oy - r, x + ox + r, y + oy + r), fill=col + (255,))
    img.alpha_composite(fol)
    if o.get('petals'):
        d = ImageDraw.Draw(img)
        for (x, y) in leaves:
            for _ in range(4):
                px, py = x + rng.uniform(-R * 0.8, R * 0.8), y + rng.uniform(-R * 0.8, R * 0.5)
                d.ellipse(P(px - 1.5 * scale, py - 1.5 * scale, px + 1.5 * scale, py + 1.5 * scale), fill=o['petals'] + (255,))
    if droop:                                      # a few dry leaves on the grass under it
        d = ImageDraw.Draw(img)
        for _ in range(7):
            px, py = bx + rng.uniform(-28, 28), by + rng.uniform(-1, 4)
            d.ellipse(P(px - 1.6, py - 0.8, px + 1.6, py + 0.8), fill=(150, 140, 70, 255))
    return leaves


# ------------------------------------------------------------------ scene pieces
def falling_leaves(img, seed=4, n=14, col=((214, 110, 46), (236, 160, 70), (170, 70, 40))):
    rng = random.Random(seed); d = ImageDraw.Draw(img)
    for i in range(n):
        if i < n // 2: x, y = rng.uniform(330, 430), rng.uniform(300, 392)
        else: x, y = rng.uniform(150, 330), rng.uniform(340, 392)             # floating on the water
        a = rng.uniform(0, math.pi); c = rng.choice(col)
        pts = [(x + 2.2 * math.cos(a + k * math.pi / 2) * (1 if k % 2 == 0 else 0.45), y + 2.2 * math.sin(a + k * math.pi / 2) * (1 if k % 2 == 0 else 0.45)) for k in range(4)]
        d.polygon([(px * SS, py * SS) for px, py in pts], fill=c + (255,))


def spring_flowers(img, seed=6):
    rng = random.Random(seed); d = ImageDraw.Draw(img)
    for _ in range(46):
        x = rng.uniform(70, 440); y = rng.uniform(LL.BANK + 2, 440)
        c = rng.choice(((255, 255, 255), (255, 214, 90), (255, 160, 190), (200, 170, 255)))
        r = rng.uniform(0.9, 1.5)
        d.ellipse(P(x - r, y - r, x + r, y + r), fill=c + (255,))


def winter_overlay(img, ph='day'):
    """snow on the middle hills, the pines and the bank; a colder lake"""
    lay = ov(); d = ImageDraw.Draw(lay)
    mid = ridge_pts(292, 40, 23)
    snow = (236, 240, 248) if ph != 'night' else (150, 160, 190)
    bot = [(x, y + 2.2 + 1.6 * math.sin(x * 0.9) + 1.2 * math.sin(x * 2.3)) for x, y in mid]
    d.polygon([(x * SS, y * SS) for x, y in mid] + [(x * SS, y * SS) for x, y in reversed(bot)], fill=snow + (150,))
    rng = random.Random(9)
    for _ in range(160):
        x = rng.uniform(0, 480); y = rng.uniform(288, 300)
        d.ellipse(P(x - 0.8, y - 0.6, x + 0.8, y + 0.6), fill=snow + (200,))
    img.alpha_composite(lay)
    ice = ov(); ImageDraw.Draw(ice).rectangle(P(0, 300, 480, LL.BANK + 8), fill=(220, 232, 244, 46))
    img.alpha_composite(ice)
    bank = ov(); bm = Image.new('L', (W, W), 0)
    ImageDraw.Draw(bm).polygon([(x * SS, y * SS) for x, y in ridge_pts(LL.BANK, 24, 41, freqs=(1.1, 2.3, 5))] + [(490 * SS, 480 * SS), (-10 * SS, 480 * SS)], fill=255)
    bank.paste(Image.new('RGBA', (W, W), ((236, 240, 246) if ph != 'night' else (96, 104, 128)) + (228,)), (0, 0), bm)
    img.alpha_composite(bank)


def bottle(img, x, y, t=0.0, night=False, tilt=-0.5, glint=True, sc=1.5):
    lay = ov(); d = ImageDraw.Draw(lay)
    glass = (70, 150, 110) if not night else (40, 90, 76)
    ca, sa = math.cos(tilt), math.sin(tilt)
    def R(px, py): px, py = px * sc, py * sc; return ((x + px * ca - py * sa) * SS, (y + px * sa + py * ca) * SS)
    body = [R(-7, -3), R(5, -3.4), R(7, -2), R(7, 2), R(5, 3.4), R(-7, 3), R(-8.2, 0)]
    d.polygon(body, fill=glass + (220,))
    d.polygon([R(7, -1.4), R(11, -1.1), R(11, 1.1), R(7, 1.4)], fill=glass + (220,))
    d.polygon([R(11, -1.3), R(13.4, -1.3), R(13.4, 1.3), R(11, 1.3)], fill=(176, 130, 80, 255))
    d.polygon([R(-4.5, -1.6), R(3.5, -1.6), R(3.5, 1.6), R(-4.5, 1.6)], fill=(250, 240, 214, 255))      # the rolled message
    d.line([R(-5, -2.5), R(3, -2.7)], fill=(255, 255, 255, 200), width=max(1, int(0.8 * SS)))
    img.alpha_composite(lay)
    # waterline: the lower half sits in the lake
    wl = ov(); wd = ImageDraw.Draw(wl)
    wd.ellipse(P(x - 11 * sc, y - 0.5, x + 11 * sc, y + 5 * sc), fill=(90, 140, 180, 120) if not night else (10, 18, 40, 150))
    img.alpha_composite(wl)
    d = ImageDraw.Draw(img)
    WL.ripples(ImageDraw.Draw(img), SS, x, y + 1.5 * sc, 0.5 + t % 1.6, n=2, span=1.6, a0=150 if not night else 70, rmax=12 * sc)
    if glint:
        g = ov(); ImageDraw.Draw(g).ellipse(P(x + 2 * sc, y - 7 * sc, x + 8 * sc, y - 1 * sc), fill=(255, 255, 240, 200))
        img.alpha_composite(g.filter(ImageFilter.GaussianBlur(1.6 * SS)))


def diya(img, x, y, sc=1.0):
    g = ov(); ImageDraw.Draw(g).ellipse(P(x - 14 * sc, y - 18 * sc, x + 14 * sc, y + 6 * sc), fill=(255, 170, 70, 110))
    img.alpha_composite(g.filter(ImageFilter.GaussianBlur(5 * SS)))
    rl = ov(); rd = ImageDraw.Draw(rl)
    for k in range(7):
        yy = y + 3 + k * 2; w = (3 - k * 0.35) * sc
        if w > 0: rd.line(P(x - w, yy, x + w, yy), fill=(255, 190, 90, 170), width=max(1, int(0.8 * SS)))
    img.alpha_composite(rl)
    d = ImageDraw.Draw(img)
    d.chord(P(x - 5 * sc, y - 4 * sc, x + 5 * sc, y + 3 * sc), 0, 180, fill=(170, 80, 40, 255))
    d.polygon(P(x - 1.2 * sc, y - 1 * sc, x, y - 6.5 * sc, x + 1.2 * sc, y - 1 * sc), fill=(255, 214, 110, 255))
    d.ellipse(P(x - 0.6 * sc, y - 3 * sc, x + 0.6 * sc, y - 1.4 * sc), fill=(255, 255, 230, 255))


def jetty_lights(img, cols, y=341, x0=10, x1=170, step=11, sag=2.4):
    g = ov(); gd = ImageDraw.Draw(g); b = ov(); bd = ImageDraw.Draw(b)
    pts = []
    for i, x in enumerate(np.arange(x0, x1, step)):
        yy = y - 6 + sag * math.sin((x - x0) / step * math.pi) ** 2
        pts.append((x, yy)); c = cols[i % len(cols)]
        gd.ellipse(P(x - 6, yy - 6, x + 6, yy + 6), fill=c + (120,))
        bd.ellipse(P(x - 1.3, yy - 1.3, x + 1.3, yy + 1.3), fill=c + (255,))
    ImageDraw.Draw(img).line([(px * SS, py * SS) for px, py in pts], fill=(40, 30, 26, 255), width=int(0.6 * SS))
    for x in (10, 48, 82, 116, 150, 170): ImageDraw.Draw(img).line(P(x, 342, x, 334), fill=(60, 42, 30, 255), width=int(1.2 * SS))
    img.alpha_composite(g.filter(ImageFilter.GaussianBlur(3 * SS))); img.alpha_composite(b)


def firework(img, cx, cy, r, col, seed, refl=True):
    rng = random.Random(seed)
    lay = ov(); d = ImageDraw.Draw(lay)
    for k in range(34):
        a = k / 34 * 2 * math.pi + rng.uniform(-0.05, 0.05); rr = r * rng.uniform(0.75, 1.0)
        for j in range(5):
            q = 0.35 + j * 0.15
            x, y = cx + math.cos(a) * rr * q, cy + math.sin(a) * rr * q + q * q * 6
            s_ = 0.6 + j * 0.25
            d.ellipse(P(x - s_, y - s_, x + s_, y + s_), fill=col + (int(80 + 35 * j),))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(2.5 * SS))); img.alpha_composite(lay)
    if refl:                                       # its reflection in the lake, broken by ripples
        part = lay.crop((0, int((cy - r - 10) * SS), W, int((cy + r + 10) * SS))).transpose(Image.FLIP_TOP_BOTTOM)
        a_ = np.asarray(part).astype(np.float32); a_[..., 3] *= 0.35
        for row in range(0, a_.shape[0], 6 * SS): a_[row:row + 2 * SS, :, 3] *= 0.2
        part = Image.fromarray(a_.astype(np.uint8)).resize((W, int(part.height * 0.45)))
        top = int((300 + (300 - cy) * 0.15) * SS)
        if top + part.height > 396 * SS: part = part.crop((0, 0, W, 396 * SS - top))
        img.alpha_composite(part, (0, top))


def tree_star(img, x, y):
    g = ov(); ImageDraw.Draw(g).ellipse(P(x - 12, y - 12, x + 12, y + 12), fill=(255, 220, 120, 140))
    img.alpha_composite(g.filter(ImageFilter.GaussianBlur(5 * SS)))
    pts = []
    for k in range(10):
        a = -math.pi / 2 + k * math.pi / 5; r = 5 if k % 2 == 0 else 2.2
        pts.append(((x + r * math.cos(a)) * SS, (y + r * math.sin(a)) * SS))
    ImageDraw.Draw(img).polygon(pts, fill=(255, 226, 120, 255))


def snowfall(img, seed=3, n=60):
    rng = random.Random(seed); d = ImageDraw.Draw(img)
    for _ in range(n):
        x, y = rng.uniform(10, 470), rng.uniform(20, 440); r = rng.uniform(0.8, 1.6)
        d.ellipse(P(x - r, y - r, x + r, y + r), fill=(255, 255, 255, 255))


# ------------------------------------------------------------------ the face, with hooks
def face(h, hhmm, steps, s, bat=82, hr=72, pre=None, post=None, tree_opt=None, land=None, birds_at=None, boat='auto', after_land=None, sky=None, sky_tint=None):
    saved_tree, saved_land = CM.tree, {k: v for k, v in CM.LAND.items()}
    CM.tree = lambda *a, **k: tree2(*a, opt=tree_opt, **k)
    if land:
        for ph, kv in land.items():
            l = list(CM.LAND[ph])
            for i, v in kv.items(): l[i] = v
            CM.LAND[ph] = tuple(l)
    CM.LAST['sky_hook'] = sky
    saved_sky = dict(CM.SKY)
    if sky_tint:
        for ph_, v in sky_tint.items(): CM.SKY[ph_] = v
    try:
        img, night, ph = LL.base(h, s)
    finally:
        CM.tree = saved_tree; CM.LAND.clear(); CM.LAND.update(saved_land); CM.LAST['sky_hook'] = None; CM.SKY.clear(); CM.SKY.update(saved_sky)
    n, g = ph == 'night', ph in ('golden', 'dawn')
    if after_land: after_land(img, ph)
    WL.reeds(img, SS, 418, 470, LL.BANK - 16, seed=2, night=n, golden=g)
    WL.reeds(img, SS, 40, 70, LL.BANK - 10, seed=5, night=n, golden=g)
    if boat == 'auto':
        if n: WL.boat(img, SS, 206, 370, 1.0, 'moored', night=True)
        elif ph == 'golden': WL.boat(img, SS, 236, 346, 1.0, 'row', golden=True)
        else: WL.boat(img, SS, 226, 338, 2.0, 'fish')
    if pre: pre(img, ph)
    if birds_at: HO.birds(img, SS, 0.0, x0=birds_at[0], y0=birds_at[1], golden=g)
    BJ.jetty_big(img, ph)
    if n: BJ.lantern_glow(img, 136, 356, 80)
    BJ.painted_battery(img, bat, ph)
    if post: post(img, ph)
    SG.trail_sign(img, steps, ph, x=318, base=420)
    img.alpha_composite(HM.hud2(hhmm, '', steps, 15000, bat, steps_text=False, steps_arc=False, bat_arc=False))
    SG.date_hr(img, hr)
    return LM.circle(img)


def sheet(items, path, cols=None, sub=True):
    cols = cols or len(items)
    rows = math.ceil(len(items) / cols)
    S = Image.new('RGB', (cols * 492 + 12, rows * 552 + 12), (14, 14, 18))
    dr = ImageDraw.Draw(S); LF = ImageFont.truetype(FT + 'Inter-SemiBold.otf', 22); LS = ImageFont.truetype(FT + 'Inter-Regular.otf', 16)
    for i, (im, lab, sub_) in enumerate(items):
        x, y = 12 + (i % cols) * 492, 12 + (i // cols) * 552
        S.paste(im, (x, y), im)
        tw = dr.textlength(lab, font=LF); dr.text((x + 240 - tw / 2, y + 488), lab, font=LF, fill=(214, 220, 200))
        tw = dr.textlength(sub_, font=LS); dr.text((x + 240 - tw / 2, y + 516), sub_, font=LS, fill=(150, 156, 146))
    S.save(path)
    return S


def closeups(items, boxes, path):
    Z = Image.new('RGB', (len(items) * 412 + 12, 244), (14, 14, 18))
    for i, ((im, lab, _), b) in enumerate(zip(items, boxes)):
        c = im.crop(b).resize((400, 220), Image.LANCZOS); Z.paste(c, (12 + i * 412, 12), c)
    Z.save(path)


if __name__ == '__main__':
    which = sys.argv[1:] or ['seasons', 'bottle', 'festivals', 'pace']
    O = _OUT + 'mockups/'
    import os; os.makedirs(O, exist_ok=True)

    if 'seasons' in which:
        spring = dict(leaves=[(170, 90, 120), (226, 140, 170), (250, 196, 212)], petals=(255, 240, 246))
        autumn = dict(leaves=[(150, 60, 36), (206, 104, 44), (238, 162, 66)])
        items = [
            (face(12.33, '12:20', 10500, 0.7, tree_opt=spring, land={'day': {6: (88, 146, 66)}}, after_land=lambda im, ph: spring_flowers(im), birds_at=(372, 208)),
             'Spring', 'Mar – May · blossoms, flowers on the grass'),
            (face(12.33, '12:20', 10500, 0.7, birds_at=(372, 208)), 'Summer', 'Jun – Aug · deep green'),
            (face(12.33, '12:20', 10500, 0.7, tree_opt=autumn, land={'day': {6: (104, 112, 58), 3: (48, 72, 52)}},
                  pre=lambda im, ph: falling_leaves(im), birds_at=(372, 208)), 'Autumn', 'Sep – Nov · orange leaves fall on the water'),
            (face(12.33, '12:20', 10500, 0.7, tree_opt=dict(bare=True), after_land=lambda im, ph: winter_overlay(im, ph),
                  land={'day': {1: (252, 252, 255)}}, pre=lambda im, ph: snowfall(im, n=36)), 'Winter', 'Dec – Feb · bare tree, snowy peaks and shore'),
        ]
        sheet(items, O + 'seasons.png', cols=2)
        closeups(items, [(250, 270, 470, 400)] * 4, O + 'seasons-closeup.png')

    if 'bottle' in which:
        items = [
            (face(12.33, '12:20', 6900, 0.46), 'No messages', 'the lake is clear'),
            (face(12.33, '12:20', 6900, 0.46, pre=lambda im, ph: bottle(im, 292, 360)), '1 message', 'a bottle drifts in to the shore · tap to read'),
            (face(21.5, '21:30', 15240, 1.02, bat=40, pre=lambda im, ph: (bottle(im, 270, 352, night=True, sc=1.3), bottle(im, 298, 364, 0.7, night=True, tilt=0.4, sc=1.3),
                                                                            bottle(im, 236, 366, 1.1, night=True, tilt=-0.9, glint=False, sc=1.3))),
             '3+ messages', 'more bottles (up to 3) · they catch the lantern light'),
        ]
        sheet(items, O + 'bottle.png')
        closeups(items, [(200, 300, 360, 388)] * 3, O + 'bottle-closeup.png')

    if 'festivals' in which:
        def diwali(im, ph):
            for x, y, s_ in ((196, 326, 0.75), (234, 318, 0.7), (270, 334, 0.85), (212, 348, 0.95), (252, 358, 1.05), (300, 324, 0.7), (190, 368, 1.1), (290, 352, 1.0), (150, 322, 0.7)):
                diya(im, x, y, s_)
        warm = [(255, 196, 90)]; xmas = [(255, 80, 70), (90, 220, 110), (255, 210, 90), (110, 170, 255)]
        items = [
            (face(20.5, '20:30', 12400, 0.85, pre=diwali, post=lambda im, ph: jetty_lights(im, warm), boat=None), 'Diwali', 'floating diyas · lights along the jetty'),
            (face(21.0, '21:00', 9800, 0.66, tree_opt=dict(bare=True), after_land=lambda im, ph: winter_overlay(im, ph),
                  pre=lambda im, ph: (snowfall(im, n=40), tree_star(im, 377, 324)), post=lambda im, ph: jetty_lights(im, xmas)),
             'Christmas', 'coloured lights · a star on the tree · snow'),
            (face(23.98, '23:59', 13200, 0.88, pre=lambda im, ph: (firework(im, 120, 222, 30, (255, 200, 90), 1), firework(im, 352, 214, 34, (255, 110, 150), 2),
                                                                   firework(im, 236, 236, 22, (140, 220, 255), 3)),
                  post=lambda im, ph: jetty_lights(im, warm)), "New Year's Eve", 'fireworks over the peaks, reflected in the lake'),
        ]
        sheet(items, O + 'festivals.png')
        closeups(items, [(120, 300, 340, 420), (180, 290, 420, 420), (70, 150, 410, 330)], O + 'festivals-closeup.png')

    if 'pace' in which:
        items = [
            (face(10.0, '10:00', 3200, 0.3, birds_at=(372, 208)), 'On pace', '10:00 · 3,200 steps · the tree looks fresh'),
            (face(15.5, '15:30', 3200, 0.3, tree_opt=dict(droop=1.0, leaves=[(78, 98, 46), (112, 126, 58), (150, 156, 76)]), birds_at=(372, 208)),
             'Behind pace', '15:30 · same steps · leaves droop and fade'),
            (face(16.0, '16:00', 7600, 0.55, birds_at=(372, 208)), 'Caught up', 'walk a bit · it perks right back up'),
        ]
        sheet(items, O + 'tree-pace.png')
        closeups(items, [(290, 290, 470, 400)] * 3, O + 'tree-pace-closeup.png')
    print('ok', which)
