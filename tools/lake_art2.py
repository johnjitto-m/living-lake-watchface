"""Living Lake v1.1 art: clouds, Tamil Nadu seasons, notification bottles."""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))           # tools/
_ROOT = _os.path.dirname(_HERE)                                   # repo root
_RES = _ROOT + '/watchface/src/main/res/'                         # the watch face resources
_OUT = _ROOT + '/out/'                                            # previews, videos, mock-ups (not committed)
import json, math, random, sys
sys.path.insert(0, _HERE); sys.path.insert(0, _HERE)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import lake_art as A, landmock as LM, waterlife as WL, clouds2 as C, demo4 as D, demo_tn as TN
from layout15 import TREE_X, BOTTLES
from landmock import SS, W, P, ov, ridge_pts, fill_ridge, mist

A.MAN.update(json.load(open(_HERE + '/art.json')))
PH = A.PHASES; BANK = A.BANK
ONLY = set(sys.argv[1:])
def want(k): return not ONLY or k in ONLY
def save(c, name): return A.save(A.down(c), name)


def tint(c, ph, night_k=0.42):
    if ph == 'night':
        t = np.asarray(c).astype(np.float32); t[..., :3] *= night_k
        return Image.fromarray(np.clip(t, 0, 255).astype(np.uint8))
    return A.tint_img(c, ph)


# ---------------------------------------------------------------- clouds (they sit behind the hills)
C.PAL['rainn'] = ((84, 90, 112), (60, 66, 88), (38, 42, 60), (100, 106, 126))


def rain_decks(img, pal, curtain):
    C.stratus(img, 60, -20, 500, 22, pal, 7, 210)
    C.stratus(img, 118, -20, 110, 16, pal, 8, 220); C.stratus(img, 120, 372, 500, 16, pal, 13, 220)
    C.stratus(img, 204, 170, 500, 22, pal, 9, 236); C.stratus(img, 238, -20, 230, 18, pal, 10, 236)
    C.rain_curtain(img, 300, 430, 220, 292, col=curtain); C.rain_curtain(img, 40, 140, 250, 300, seed=5, col=curtain)


if want('clouds'):
    for ph in PH:
        c = ov(); C.fair(c, ph); save(c, f'cl_fair_{ph}')
        c = ov(); C.monsoon(c, ph); save(c, f'cl_tower_{ph}')
    c = ov(); rain_decks(c, 'rain', (150, 160, 180)); save(c, 'cl_rain_day')
    c = ov(); rain_decks(c, 'rainn', (90, 96, 116)); save(c, 'cl_rain_night')

# ---------------------------------------------------------------- summer: the konrai tree, dry grass, warm haze
KONRAI = {'night': [(30, 44, 30), (52, 62, 40), (84, 86, 50)]}
KONRAI_DAY = [(88, 110, 44), (150, 160, 58), (220, 196, 60)]


def chains(img, leaves, n, night, seed=12, long=1.0):
    rng = random.Random(seed); d = ImageDraw.Draw(img)
    c1, c2 = ((255, 214, 60), (240, 186, 40)) if not night else ((120, 104, 40), (100, 86, 34))
    for _ in range(n):
        x, y = rng.choice(leaves); x += rng.uniform(-6, 6); y += rng.uniform(0, 8)
        L = rng.uniform(7, 14) * long
        for k in range(int(L / 1.5)):
            yy = y + k * 1.5; xx = x + math.sin(k * 0.6) * 0.4; r = 1.05 - k * 0.03
            d.ellipse(P(xx - r, yy - r, xx + r, yy + r), fill=(c1 if k % 2 else c2) + (255,))


def konrai(ph, s):
    c = ov(); night = ph == 'night'
    if s < 0.1:
        LM.tree(c, TREE_X, BANK - 2, s, night, seed=5, scale=0.68, flies=False)
        return A.tint_img(c, ph)
    lv = D.tree2(c, TREE_X, BANK - 2, s, night, seed=5, scale=0.68, flies=False, opt={'leaves': KONRAI.get(ph, KONRAI_DAY)})
    if s >= 0.3:
        n = int(6 + 22 * min(s, 1.0)) if s < 1 else 40
        chains(c, lv, n, night, long=1.0 if s < 1 else 1.35)
    return A.tint_img(c, ph)


DRY = {'day': (150, 146, 80), 'dawn': (122, 106, 80), 'golden': (132, 110, 62), 'night': (26, 28, 22)}


def dry_bank(ph):
    c = ov(); fill_ridge(c, ridge_pts(BANK, 24, 41, freqs=(1.1, 2.3, 5)), DRY[ph], 480)
    WL.reeds(c, SS, 418, 470, BANK - 16, seed=2, night=ph == 'night', golden=True)
    WL.reeds(c, SS, 40, 70, BANK - 10, seed=5, night=ph == 'night', golden=True)
    return c


if want('summer'):
    for ph in PH:
        ims = [A.down(konrai(ph, s)) for s in A.TREE_S]
        b = A.union([im.split()[3].getbbox() for im in ims])
        for k, im in enumerate(ims): A.save(im, f'treek_{ph}_{k}', b)
        save(dry_bank(ph), f'drybank_{ph}')

# ---------------------------------------------------------------- northeast monsoon: lotus on the lake
if want('lotus'):
    for ph in PH:
        c = ov()                                                        # lotus pads on the left water, peeking out above the jetty
        for x, y, bloom in ((40, 336, True), (62, 338, False), (150, 334, True), (172, 338, False), (110, 338, False), (196, 330, True)):
            d = ImageDraw.Draw(c)
            d.ellipse(P(x - 6, y - 2, x + 6, y + 2), fill=(58, 112, 64, 255)); d.pieslice(P(x - 6, y - 2, x + 6, y + 2), -20, 20, fill=(44, 88, 52, 255))
            if bloom:
                for k, a in enumerate((-0.6, -0.25, 0.1, 0.45)):
                    px = x + math.sin(a) * 4; d.polygon(P(px - 1.5, y - 1, px + math.sin(a) * 2, y - 6 - k % 2, px + 1.5, y - 1), fill=(244, 140, 176, 255))
                d.ellipse(P(x - 1.2, y - 3, x + 1.2, y - 1), fill=(255, 220, 120, 255))
        save(tint(c, ph), f'lotus_{ph}')

# ---------------------------------------------------------------- cool season: storks, pelicans, morning mist
if want('cool'):
    for ph in ('dawn', 'day', 'golden'):
        c = ov(); TN.pelican(c, 100, 322); TN.pelican(c, 154, 328); TN.stork(c, 288, 394); TN.stork(c, 300, 399, -1)
        save(tint(c, ph), f'coolbirds_{ph}')
    c = ov(); mist(c, 318, 26, 120); mist(c, 350, 20, 90); A.save(A.down(c), 'mist_water', (0, 290, 480, 90))

# ---------------------------------------------------------------- the message bottles
if want('bottle'):
    for i, (x, y, tilt, sc, t) in enumerate(BOTTLES):
        for ph, night in (('day', False), ('night', True)):
            c = ov(); D.bottle(c, x, y, t=1.59, night=night, tilt=tilt, glint=not night, sc=sc)
            save(c, f'bottle{i}_{ph}')
    x, y = BOTTLES[0][:2]
    A.frames('bottle_rip', lambda i: (lambda c: (WL.ripples(ImageDraw.Draw(c), SS, x, y + 2, i / 12 * 1.6, n=2, span=1.6, a0=150, rmax=16), c)[1])(ov()),
             12, box=(x - 22, y - 6, 44, 18))

json.dump(A.MAN, open(_HERE + '/art.json', 'w'), indent=0)
print('v1.1 art ok')

# ---------------------------------------------------------------- always-on: the still-water overlay (above the live reflection)
if want('aod'):
    K = 4; Wd, Hd, Y0 = 480, 64, 184
    c = Image.new('RGBA', (Wd * K, Hd * K), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    WL_Y = 191 - Y0
    xs = np.arange(Wd * K) / K
    taper = np.clip(1 - np.abs(xs - 240) / 150, 0, 1) ** 1.6
    glow = np.zeros((Hd * K, Wd * K, 4), np.float32)                       # the waterline: brightest in the middle, fading out
    for yy in range(Hd * K):
        dy = yy / K - WL_Y
        k = math.exp(-(dy / 0.7) ** 2) * 0.85 + (math.exp(-((dy + 2.5) / 3.0) ** 2) * 0.18 if dy < 0 else 0)
        glow[yy, :, 0], glow[yy, :, 1], glow[yy, :, 2] = 132, 142, 162
        glow[yy, :, 3] = 255 * k * taper
    fade = np.zeros((Hd * K, Wd * K, 4), np.float32)                       # the reflection darkens with distance
    yy = np.arange(Hd * K)[:, None] / K
    fade[..., 3] = np.clip((yy - (WL_Y + 3)) / 46, 0, 1) ** 1.2 * 235 * np.ones((1, Wd * K))
    for ly, a in ((WL_Y + 12.5, 150), (WL_Y + 23, 170), (WL_Y + 35, 190)):  # calm lines across the water
        band = np.exp(-((yy - ly) / 0.55) ** 2) * a * np.clip(1 - np.abs(xs - 240) / 190, 0, 1)[None, :] ** 0.4
        fade[..., 3] = np.maximum(fade[..., 3], band)
    over = Image.fromarray(fade.astype(np.uint8)); over.alpha_composite(Image.fromarray(glow.astype(np.uint8)))
    over.resize((Wd, Hd), Image.LANCZOS).save(A.OUT + 'aod_water.png')
    A.MAN['aod_water'] = [0, Y0, Wd, Hd]
    json.dump(A.MAN, open(_HERE + '/art.json', 'w'), indent=0)
    print('aod water ok')
