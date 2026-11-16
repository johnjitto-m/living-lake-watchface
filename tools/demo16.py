"""Living Lake – demos for the next update: festivals, birthdays, drooping / bigger tree, Nilgiri tahr, circling crows,
goal-evening lanterns, optional complications. Everything is drawn on top of the real v1.5 compositor (lake_preview)."""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))           # tools/
_ROOT = _os.path.dirname(_HERE)                                   # repo root
_RES = _ROOT + '/watchface/src/main/res/'                         # the watch face resources
_OUT = _ROOT + '/out/'                                            # previews, videos, mock-ups (not committed)
import math, random, sys
sys.path.insert(0, _HERE); sys.path.insert(0, _HERE)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import lake_preview as LP, landmock as LM, demo4 as D, demo_tn as TN
import lake_art as LA
from landmock import SS, W, P, ov
from layout15 import TREE_X, SIGN

O = _OUT + 'preview/'
BASE = 394                                     # tree foot


def big(fn):
    """run fn on a 4x canvas and composite it onto the 480 image"""
    def f(im, h, night, *a):
        c = ov(); fn(c, h, night, *a); im.alpha_composite(c.resize((480, 480), Image.LANCZOS))
    return f


def glow(c, x, y, r, col, a=120, blur=None):
    g = ov(); ImageDraw.Draw(g).ellipse(P(x - r, y - r, x + r, y + r), fill=col + (a,))
    c.alpha_composite(g.filter(ImageFilter.GaussianBlur((blur or r * 0.5) * SS)))


def phase(h):
    if 5.5 <= h < 7.5: return 'dawn'
    if 7.5 <= h < 16.75: return 'day'
    if 16.75 <= h < 19.0: return 'golden'
    return 'night'


# ------------------------------------------------------------------ festivals
def reflect_burst(c, cx, cy, r, col, seed):
    """the firework's reflection on the open water only (y 300-336), broken by ripples"""
    lay = ov(); D.firework(lay, cx, cy, r, col, seed, refl=False)
    part = lay.crop((0, int((cy - r - 8) * SS), W, int((cy + r + 8) * SS))).transpose(Image.FLIP_TOP_BOTTOM)
    a = np.asarray(part).astype(np.float32); a[..., 3] *= 0.4
    for row in range(0, a.shape[0], 5 * SS): a[row:row + 2 * SS, :, 3] *= 0.15
    part = Image.fromarray(a.astype(np.uint8)).resize((W, int(part.height * 0.4)))
    top = int(302 * SS); part = part.crop((0, 0, W, min(part.height, int(34 * SS))))
    c.alpha_composite(part, (0, top))


BURSTS_DV = [(108, 214, 26, (255, 200, 90), 1), (384, 206, 30, (255, 110, 150), 2)]
BURSTS_NY = [(104, 210, 28, (255, 200, 90), 1), (378, 202, 32, (255, 110, 150), 2), (240, 232, 20, (140, 220, 255), 3)]


def bursts_sky(bl):
    return big(lambda c, h, n: [D.firework(c, x, y, r, col, sd, refl=False) for x, y, r, col, sd in bl])


def bursts_refl(bl):
    return big(lambda c, h, n: [reflect_burst(c, x, y, r, col, sd) for x, y, r, col, sd in bl])


def plank_lights(c, cols):
    """a string of little lights along the top of the battery plank"""
    g = ov(); gd = ImageDraw.Draw(g); b = ov(); bd = ImageDraw.Draw(b); pts = []
    for i, x in enumerate(np.arange(46, 176, 9)):
        yy = 335.5 + 1.8 * math.sin((x - 46) / 9 * math.pi) ** 2
        pts.append((x, yy)); col = cols[i % len(cols)]
        gd.ellipse(P(x - 5, yy - 5, x + 5, yy + 5), fill=col + (110,)); bd.ellipse(P(x - 1.2, yy - 1.2, x + 1.2, yy + 1.2), fill=col + (255,))
    ImageDraw.Draw(c).line([(px * SS, py * SS) for px, py in pts], fill=(40, 30, 26, 255), width=int(0.6 * SS))
    c.alpha_composite(g.filter(ImageFilter.GaussianBlur(3 * SS))); c.alpha_composite(b)


def maha_deepam(c, x=340, y=211):
    """Karthigai Deepam: the great lamp on the highest peak"""
    glow(c, x, y - 4, 30, (255, 170, 70), 110, 12); glow(c, x, y - 4, 12, (255, 210, 120), 170, 4)
    d = ImageDraw.Draw(c)
    d.polygon(P(x - 4, y + 1, x + 4, y + 1, x + 2.6, y - 2, x - 2.6, y - 2), fill=(120, 70, 40, 255))          # the cauldron
    d.polygon(P(x - 2.6, y - 2, x, y - 12, x + 2.6, y - 2), fill=(255, 196, 80, 255))
    d.polygon(P(x - 1.2, y - 2, x, y - 8, x + 1.2, y - 2), fill=(255, 250, 220, 255))


def karthigai(c, h, n):
    for x in np.arange(50, 176, 11): D.diya(c, x, 337.5, 0.5)                                      # agal vilakku on the plank
    for x in (192, 214, 236, 270, 292): D.diya(c, x, 386 + 2 * math.sin(x * 0.07), 0.62)          # and along the shore
    for x in (SIGN['cx'] - 40, SIGN['cx'], SIGN['cx'] + 40): D.diya(c, x, SIGN['top'] - 1, 0.5)   # on top of the sign
    maha_deepam(c)


def deepavali_water(c, h, n):
    for x, y, s in ((196, 312, 0.6), (226, 306, 0.55), (258, 318, 0.7), (214, 328, 0.75), (282, 310, 0.55), (244, 334, 0.8), (186, 336, 0.8)):
        D.diya(c, x, y, s)


def pongal(c, h, n):
    TN.kolam(c, 112, 404); TN.pongal_pot(c, 208, 398)


def thoranam_jetty(c, h, n):
    d = ImageDraw.Draw(c); x0, x1, y = 44, 174, 331.5
    pts = [(x, y + 2.2 * math.sin((x - x0) / (x1 - x0) * math.pi)) for x in np.arange(x0, x1 + 0.1, 2)]
    d.line([(px * SS, py * SS) for px, py in pts], fill=(200, 170, 110, 255), width=max(1, int(0.7 * SS)))
    for i, (px, py) in enumerate(pts[1::2]):
        col = (56, 132, 56) if i % 2 else (84, 160, 64)
        if i % 6 == 3: col = (250, 190, 60)                                                       # a marigold every few leaves
        d.polygon(P(px - 1.8, py, px, py + 7, px + 1.8, py), fill=col + (255,))
    TN.kolam(c, 112, 404)


def xmas_star(c, x, y, r=7):
    glow(c, x, y, r * 2.4, (255, 200, 120), 130, r)
    pts = []
    for k in range(10):
        a = -math.pi / 2 + k * math.pi / 5; rr = r if k % 2 == 0 else r * 0.45
        pts.append(((x + rr * math.cos(a)) * SS, (y + rr * math.sin(a)) * SS))
    d = ImageDraw.Draw(c); d.polygon(pts, fill=(255, 214, 120, 255), outline=(200, 110, 50, 255))
    for k in range(5):                                                                              # paper tails
        tx = x - 3 + k * 1.5; d.line(P(tx, y + r * 0.4, tx + (k - 2) * 0.6, y + r + 8 + (k % 2) * 3), fill=(255, 160, 90, 255), width=max(1, int(0.6 * SS)))


def tree_top(k=6, night=True):
    a = np.asarray(Image.open(LP.B + f'drawable/tree_{"night" if night else "day"}_{k}.png'))[..., 3]
    ys = np.where(a.max(axis=1) > 60)[0]; x0, y0 = LP.A[f'tree_night_{k}'][:2]
    return y0 + ys[0]


def christmas(c, h, n):
    plank_lights(c, [(255, 80, 70), (90, 220, 110), (255, 210, 90), (110, 170, 255)])
    xmas_star(c, TREE_X, tree_top(6) - 4, 5)
    xmas_star(c, SIGN['cx'] - SIGN['W'] / 2 - 6, SIGN['top'] - 4, 7)                              # the paper star hung on the sign


def nye(c, h, n): plank_lights(c, [(255, 196, 90)])


# ------------------------------------------------------------------ birthday
def balloons(c, x0=174, y0=331):
    rng = random.Random(4)
    cols = [(236, 84, 96), (250, 190, 60), (90, 170, 230), (130, 200, 120), (230, 120, 200)]
    tops = [(158, 268), (176, 262), (192, 274), (168, 284), (186, 290)]
    d = ImageDraw.Draw(c)
    for (bx, by), col in zip(tops, cols):
        pts = [(x0 + (bx - x0) * t + math.sin(t * 6 + bx) * 1.2, y0 + (by + 10 - y0) * t) for t in np.linspace(0, 1, 30)]
        d.line([(px * SS, py * SS) for px, py in pts], fill=(240, 240, 235, 200), width=max(1, int(0.5 * SS)))
    for (bx, by), col in zip(tops, cols):
        d.ellipse(P(bx - 6.5, by - 8, bx + 6.5, by + 8), fill=col + (255,))
        d.polygon(P(bx - 1.5, by + 10, bx, by + 7.5, bx + 1.5, by + 10), fill=col + (255,))
        hl = ov(); ImageDraw.Draw(hl).ellipse(P(bx - 4, by - 6, bx - 1, by - 1.5), fill=(255, 255, 255, 150))
        c.alpha_composite(hl.filter(ImageFilter.GaussianBlur(0.6 * SS)))
        d = ImageDraw.Draw(c)


def ribbon(c, text, y=200):
    """a cloth ribbon in the sky carrying the calendar text"""
    f = LP.F('lake_text', 13); tw = ImageDraw.Draw(c).textlength(text, font=f) / SS + 0.12 * 13 * (len(text) - 1)
    w = tw + 34; x0 = 240 - w / 2; x1 = 240 + w / 2
    sh = ov(); ImageDraw.Draw(sh).rounded_rectangle(P(x0, y - 9, x1, y + 11), radius=3 * SS, fill=(0, 0, 0, 70))
    c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(3 * SS)))
    d = ImageDraw.Draw(c); cream, fold = (252, 244, 228), (214, 196, 170)
    for s in (-1, 1):                                                                               # swallow-tail ends
        ex = x0 if s < 0 else x1
        d.polygon(P(ex - s * 2, y - 6, ex + s * 12, y - 6, ex + s * 7, y + 1, ex + s * 12, y + 8, ex - s * 2, y + 8), fill=fold + (255,))
    d.rounded_rectangle(P(x0 + 4, y - 9, x1 - 4, y + 9), radius=2 * SS, fill=cream + (255,))
    # a tiny cake
    cx = x0 + 15; d.rectangle(P(cx - 4.5, y - 1, cx + 4.5, y + 5), fill=(236, 120, 130, 255)); d.rectangle(P(cx - 4.5, y - 2, cx + 4.5, y), fill=(255, 250, 240, 255))
    d.line(P(cx, y - 2, cx, y - 6), fill=(110, 170, 230, 255), width=max(1, int(0.8 * SS))); d.ellipse(P(cx - 0.9, y - 8.6, cx + 0.9, y - 6), fill=(255, 190, 60, 255))
    xx = cx + 9
    for ch in text:
        d.text((xx * SS, (y - 8) * SS), ch, font=f, fill=(92, 60, 40, 255)); xx += d.textlength(ch, font=f) / SS + 0.12 * 13


def birthday(c, h, n): balloons(c)


# ------------------------------------------------------------------ the tree: drooping when behind pace, bigger when grown
def tree_layer(s, night, ph, scale, opt=None):
    c = ov()
    if opt: D.tree2(c, TREE_X, BASE, s, night, seed=5, scale=scale, flies=False, fixed_depth=4, opt=opt)
    else: LM.tree(c, TREE_X, BASE, s, night, seed=5, scale=scale, flies=False, fixed_depth=4)
    return LA.tint_img(c, ph)


def tree_fn(s, scale=0.68, opt=None):
    def f(im, h, night, steps):
        im.alpha_composite(tree_layer(s, night, phase(h), scale, opt).resize((480, 480), Image.LANCZOS))
    return f


def grow_scale(s): return 0.68 + 0.17 * max(0.0, min(1.0, (s - 0.5) / 0.5))   # bigger as it nears the goal: 0.68 -> 0.85


# ------------------------------------------------------------------ goal evening: paper lanterns rise from the lake
LANTERNS = [(214, 304, 1.9), (172, 280, 1.6), (290, 272, 1.55), (236, 248, 1.4), (138, 240, 1.25), (334, 234, 1.2), (196, 214, 1.1), (286, 208, 1.0), (100, 206, 0.9), (382, 198, 0.9)]


def lantern(c, x, y, s):
    glow(c, x, y, 13 * s, (255, 150, 60), 120, 7 * s)
    d = ImageDraw.Draw(c)
    d.polygon(P(x - 4.2 * s, y - 6 * s, x + 4.2 * s, y - 6 * s, x + 3.2 * s, y + 5 * s, x - 3.2 * s, y + 5 * s), fill=(255, 176, 80, 255))
    d.polygon(P(x - 2.6 * s, y - 4.5 * s, x + 2.6 * s, y - 4.5 * s, x + 2 * s, y + 3.5 * s, x - 2 * s, y + 3.5 * s), fill=(255, 220, 140, 255))
    d.ellipse(P(x - 1.4 * s, y + 3 * s, x + 1.4 * s, y + 5.6 * s), fill=(255, 250, 220, 255))
    d.line(P(x - 4.2 * s, y - 6 * s, x + 4.2 * s, y - 6 * s), fill=(220, 120, 60, 255), width=max(1, int(0.6 * SS)))


def lanterns_sky(c, h, n):
    for x, y, s in LANTERNS: lantern(c, x, y, s)


def lanterns_water(c, h, n):
    for x, y, s in LANTERNS[:2]:                                                                   # the low ones shine on the water
        ry = 316 + (y - 292) * 0.4
        g = ov(); gd = ImageDraw.Draw(g)
        for k in range(6): gd.line(P(x - (5 - k * 0.6) * s, ry + k * 2.2, x + (5 - k * 0.6) * s, ry + k * 2.2), fill=(255, 190, 90, 150), width=max(1, int(0.8 * SS)))
        c.alpha_composite(g.filter(ImageFilter.GaussianBlur(0.5 * SS)))


# ------------------------------------------------------------------ Nilgiri tahr on the ridge at dawn
def tahr(c, x, y, s=1.0, flip=1, kid=False, rim=(255, 200, 160)):
    """Nilgiri tahr seen side-on: stocky, short thick neck, short legs; old males are dark chocolate with a pale saddle
    and short horns that curve back close to the head. x, y = the point under its front hooves' midline."""
    X = lambda dx: x + flip * dx * s
    Y = lambda dy: y + dy * s
    body = (62, 48, 40) if not kid else (124, 100, 76)
    leg = (44, 34, 30) if not kid else (100, 80, 62)
    d = ImageDraw.Draw(c)
    def poly(pts, col): d.polygon([(X(px) * SS, Y(py) * SS) for px, py in pts], fill=col + (255,))
    def ell(x0, y0, x1, y1, col): d.ellipse(P(min(X(x0), X(x1)), Y(y0), max(X(x0), X(x1)), Y(y1)), fill=col + (255,))
    # far legs (darker), then near legs
    for lx, knee in ((-6.2, 0.5), (5.6, -0.4)):
        poly([(lx - 0.8, -1), (lx + 0.8, -1), (lx + 0.6 + knee, 3.5), (lx + 0.7, 6.4), (lx - 0.7, 6.4), (lx - 0.6 + knee, 3.5)], (34, 26, 22) if not kid else (86, 68, 54))
    for lx, knee in ((-4.4, -0.5), (7.4, 0.4)):
        poly([(lx - 0.9, -1), (lx + 0.9, -1), (lx + 0.7 + knee, 3.5), (lx + 0.8, 6.5), (lx - 0.8, 6.5), (lx - 0.7 + knee, 3.5)], leg)
        poly([(lx - 0.9, 6.0), (lx + 1.1, 6.0), (lx + 1.2, 7.0), (lx - 1.0, 7.0)], (24, 20, 18))                                     # hooves
    # barrel body, deep chest, rump
    ell(-9, -7, 6, 1.2, body); ell(2, -8.2, 10.4, 1.0, body); ell(-9.6, -6.6, -3.4, 0.4, body)
    if not kid: ell(-4.4, -6.9, 2.2, -4.4, (164, 148, 126))                                                                     # the saddle
    ell(-8, -1.6, 6, 1.6, (48, 38, 32) if not kid else (108, 86, 66))                                                           # belly shade
    # short, thick neck + head held level, muzzle tapering
    poly([(6.4, -7.8), (10.6, -10.6), (13.0, -9.6), (12.2, -5.2), (9.0, -1.8), (6.0, -3.0)], body)
    ell(10.2, -12.0, 16.2, -7.6, body)
    poly([(14.6, -11.6), (18.6, -9.9), (18.4, -8.4), (15.0, -7.6)], body)
    ell(17.6, -9.6, 18.8, -8.6, (28, 22, 20))                                                                                  # nose
    ell(13.4, -11.0, 14.5, -9.9, (16, 14, 12))                                                                                 # eye
    poly([(11.4, -11.4), (9.0, -12.6), (9.6, -11.2), (11.2, -10.6)], body)                                                     # ear
    # horns: thick at the base, sweeping back over the neck
    hl = 1.0 if not kid else 0.35
    pts = [(12.8 - 4.6 * hl * t ** 0.9, -11.4 - 2.6 * hl * math.sin(t * 2.0)) for t in np.linspace(0, 1, 12)]
    for i in range(len(pts) - 1):
        w = (1.5 - 1.1 * i / len(pts)) * s * (1 if not kid else 0.8)
        d.line([(X(pts[i][0]) * SS, Y(pts[i][1]) * SS), (X(pts[i + 1][0]) * SS, Y(pts[i + 1][1]) * SS)], fill=(118, 104, 88, 255), width=max(1, int(w * SS)))
    poly([(-9.2, -6.2), (-11.4, -6.6), (-10.0, -4.4)], body)                                                                    # short tail


def rock(c, x, y, w):
    """a weathered rock outcrop growing out of the ridge (no hard base)"""
    lay = ov(); d = ImageDraw.Draw(lay)
    sh, mid, lit = (92, 80, 98), (118, 102, 118), (190, 156, 150)
    outline = [(x - w, y + 9), (x - w * 0.82, y + 3.5), (x - w * 0.6, y + 1.2), (x - w * 0.42, y - 0.4), (x - w * 0.1, y - 1.1),
               (x + w * 0.18, y - 0.6), (x + w * 0.45, y + 0.6), (x + w * 0.7, y + 2.8), (x + w * 0.9, y + 5.5), (x + w * 1.1, y + 9)]
    d.polygon(P(*sum(outline, ())), fill=mid + (255,))
    d.polygon(P(x - w * 0.42, y - 0.4, x - w * 0.1, y - 1.1, x + w * 0.18, y - 0.6, x + w * 0.05, y + 4, x - w * 0.35, y + 3.4), fill=lit + (230,))   # sunlit facet
    d.polygon(P(x + w * 0.45, y + 0.6, x + w * 0.7, y + 2.8, x + w * 0.9, y + 5.5, x + w * 0.4, y + 6), fill=sh + (255,))                          # shade facet
    for cx_, cy_ in ((x - w * 0.55, y + 4.5), (x + w * 0.2, y + 3.8)):
        d.line(P(cx_, cy_, cx_ + 2.6, cy_ + 2.2), fill=sh + (255,), width=max(1, int(0.6 * SS)))
    m = Image.new('L', lay.size, 0); ImageDraw.Draw(m).rectangle(P(0, 0, 480, y + 5), fill=255)                                  # fade into the hill
    m.paste(Image.linear_gradient('L').resize((W, int(5 * SS))).transpose(Image.FLIP_TOP_BOTTOM), (0, int((y + 5) * SS)))
    lay.putalpha(Image.fromarray(np.minimum(np.asarray(lay.split()[3]), np.asarray(m))))
    c.alpha_composite(lay)


def tahr_scene(c, h, n):
    rock(c, 412, 244, 24)
    tahr(c, 406, 236.5, 0.95, flip=-1)
    tahr(c, 427, 238.6, 0.6, flip=-1, kid=True)


# ------------------------------------------------------------------ crows circling (house crows: grey nape, heavy bill)
def crow(c, x, y, s, tilt=0.0, squash=1.0, flap=0.0):
    """a house crow soaring, seen from below: five splayed 'finger' primaries at each wingtip, rounded-wedge tail,
    heavy bill. tilt = banking angle, squash = foreshortening of the span (0.75..1), flap -1..1 lifts the wings."""
    ca, sa = math.cos(tilt), math.sin(tilt)
    def T(u, v): return ((x + (u * ca - v * sa) * s) * SS, (y + (u * sa + v * ca) * s) * SS)
    def W_(u, v):                                                         # wing point: foreshortened + dihedral when flapping
        k = squash * (1 - 0.12 * abs(flap)); return T(u * k, v - flap * abs(u) * 0.16)
    lay = ov(); d = ImageDraw.Draw(lay); blk = (22, 22, 26, 255)
    lead = [(1.0, -1.9), (5.0, -2.8), (9.0, -2.6), (12.4, -1.8)]
    bases = [(12.6, -1.5), (12.4, -0.7), (12.1, 0.2), (11.7, 1.1), (11.2, 1.9)]
    tips = [(15.8, -2.0), (16.3, -0.7), (16.0, 0.7), (15.2, 1.9), (14.1, 2.8)]
    trail = [(10.6, 2.9), (8.0, 3.3), (4.6, 3.5), (1.2, 2.7)]
    for side in (-1, 1):
        pts = lead[:]
        for k in range(5):
            bx, by = bases[k]; tx, ty = tips[k]
            nx, ny = tx - bx, ty - by; L = math.hypot(nx, ny); px_, py_ = -ny / L * 0.6, nx / L * 0.6
            pts += [(bx - px_ * 0.6, by - py_ * 0.6), (tx - px_ * 0.5, ty - py_ * 0.5), (tx + px_ * 0.4, ty + py_ * 0.4), (bx + px_, by + py_)]
        pts += trail
        d.polygon([W_(side * u, v) for u, v in pts], fill=blk)
    oval = lambda cx, cy, rx, ry: [T(cx + rx * math.cos(t), cy + ry * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 28)]
    d.polygon(oval(0, 0.4, 1.8, 4.4), fill=blk)                                                    # body
    d.polygon(oval(0, -4.9, 1.45, 1.6), fill=blk)                                                  # head
    d.polygon([T(-0.6, -6.1), T(0, -8.3), T(0.6, -6.1)], fill=blk)                                 # heavy bill
    d.polygon([T(-1.1, 3.6), T(-2.7, 8.2), T(-1.3, 8.9), T(0, 9.1), T(1.3, 8.9), T(2.7, 8.2), T(1.1, 3.6)], fill=blk)   # tail
    c.alpha_composite(lay)


CROWS = [(0.3, 1.0, 0.2), (2.4, 0.9, -0.5), (4.3, 0.95, 0.6)]


def crows(cx=150, cy=196, rx=42, ry=12, t=0.0):
    def f(c, h, n):
        for a0, sc, flap in CROWS:
            a = a0 + t
            x, y = cx + rx * math.cos(a), cy + ry * math.sin(a)
            near = (math.sin(a) + 1) / 2                                                       # nearer = lower and a touch bigger
            crow(c, x, y, 0.62 * sc * (0.9 + 0.2 * near), tilt=0.3 * math.cos(a), squash=0.78 + 0.22 * abs(math.cos(a)), flap=flap)
    return f


# ------------------------------------------------------------------ optional complications (empty by default)
def slot_text(im, x, y, w, txt, icon=None, align='CENTER'):
    def draw(q):
        tx = x
        if icon:
            icon(q, x, y)
        LP.text_layer(q, tx, y, w, 15, txt, 'lake_text', (255, 255, 255, 230), align=align, spacing=0.06)
    LP.hud_text(im, draw, shadow=(5, 0.63, 1))


def ic_cloud(q, x, y):
    d = ImageDraw.Draw(q); K = 4; cx, cy = x + 6, y + 9
    for ox, oy, r in ((-3, 1, 3.2), (1, -1.5, 4), (4.5, 1, 3)): d.ellipse([(cx + ox - r) * K, (cy + oy - r) * K, (cx + ox + r) * K, (cy + oy + r) * K], fill=(255, 255, 255, 230))
    d.ellipse([(cx - 9) * K, (cy - 6) * K, (cx - 1) * K, (cy + 2) * K], fill=(255, 210, 110, 230))


def ic_cal(q, x, y):
    d = ImageDraw.Draw(q); K = 4
    d.rounded_rectangle([(x + 1) * K, (y + 4) * K, (x + 12) * K, (y + 15) * K], radius=2 * K, outline=(255, 255, 255, 230), width=int(1.3 * K))
    d.line([(x + 1) * K, (y + 7.5) * K, (x + 12) * K, (y + 7.5) * K], fill=(255, 255, 255, 230), width=int(1.3 * K))


SLOTS = [(82, 114), (398, 114)]


def badge_bg(im, filled=True):
    lay = Image.new('RGBA', (1920, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for cx, cy in SLOTS:
        if filled: d.ellipse([(cx - 23) * 4, (cy - 23) * 4, (cx + 23) * 4, (cy + 23) * 4], fill=(12, 24, 46, 78), outline=(255, 255, 255, 120), width=5)
        else:
            for k in range(0, 360, 20): d.arc([(cx - 23) * 4, (cy - 23) * 4, (cx + 23) * 4, (cy + 23) * 4], k, k + 10, fill=(255, 255, 255, 170), width=5)
    im.alpha_composite(lay.resize((480, 480), Image.LANCZOS))


def complications(im):
    badge_bg(im)
    (lx, ly), (rx, ry) = SLOTS
    def draw(q):
        ic_cloud(q, lx - 8, ly - 19); ic_cal(q, rx - 6, ry - 19)
        LP.text_layer(q, lx - 30, ly - 1, 60, 15, '28°', 'lake_text', (255, 255, 255, 235))
        LP.text_layer(q, rx - 30, ry - 1, 60, 15, '4:30', 'lake_text', (255, 255, 255, 235))
    LP.hud_text(im, draw, shadow=(4, 0.5, 1))


def slots_outline(im): badge_bg(im, filled=False)


# ------------------------------------------------------------------ build the sheets
def S(*a, **k): return LP.state(*a, **k)


def cap(fn):
    """state() returns a circle-masked frame; extra HUD bits go on before the mask"""
    return fn


def with_hud_extra(hh, mm, extra, **k):
    k['hud'] = True
    im = LP.state(hh, mm, **k)
    extra(im)
    return im


if __name__ == '__main__':
    which = sys.argv[1:] or ['fest', 'tree', 'wild', 'slots']
    if 'fest' in which:
        dv_sky, dv_refl = bursts_sky(BURSTS_DV), bursts_refl(BURSTS_DV)
        ny_sky, ny_refl = bursts_sky(BURSTS_NY), bursts_refl(BURSTS_NY)
        bday = S(11, 10, steps=5200, bat=78, hr=74, month=11, dow='SAT', day=21, mon='NOV', post=big(birthday))
        rb = ov(); ribbon(rb, "PRIYA'S BIRTHDAY", 202); bday.alpha_composite(LP.circle(rb.resize((480, 480), Image.LANCZOS)))
        items = [
            (S(9, 40, steps=3800, bat=90, hr=70, month=1, dow='THU', day=15, mon='JAN', post=big(pongal)), 'Pongal · 14–17 Jan', 'kolam on the grass, pot boiling over, sugarcane'),
            (S(10, 30, steps=4600, bat=84, hr=72, month=4, dow='TUE', day=14, mon='APR', post=big(thoranam_jetty)), 'Tamil New Year · 14 Apr', 'mango-leaf thoranam on the jetty, kolam'),
            (S(19, 20, steps=11200, bat=60, hr=68, month=11, dow='TUE', day=24, mon='NOV', post=big(karthigai)), 'Karthigai Deepam · 24 Nov', 'agal lamps everywhere, the Maha Deepam on the peak'),
            (S(20, 30, steps=12400, bat=52, hr=70, month=11, dow='SUN', day=8, mon='NOV', sky_fx=dv_sky, pre=lambda im, h, n: (dv_refl(im, h, n), big(deepavali_water)(im, h, n)),
               post=big(lambda c, h, n: plank_lights(c, [(255, 196, 90)]))), 'Deepavali', 'floating diyas, fireworks over the hills'),
            (S(21, 0, steps=9800, bat=48, hr=66, month=12, dow='FRI', day=25, mon='DEC', post=big(christmas)), 'Christmas · 25 Dec', 'paper star on the sign, star on the tree, lights'),
            (S(23, 59, steps=13200, bat=40, hr=74, month=12, dow='THU', day=31, mon='DEC', sky_fx=ny_sky, pre=ny_refl, post=big(nye)), "New Year's Eve", 'fireworks reflected in the lake'),
            (bday, 'A friend\'s birthday', 'balloons on the jetty + their name in the sky'),
        ]
        D.sheet(items, O + 'v16-festivals.png', cols=3)
        D.closeups(items[:3], [(60, 300, 260, 420), (30, 300, 230, 420), (170, 190, 440, 400)], O + 'v16-festivals-closeup.png')
        print('fest ok')
    if 'tree' in which:
        goal = 15000
        items = [
            (S(10, 0, steps=3200, bat=88, hr=70, month=11, tree_fn=tree_fn(0.3)), 'On pace', '10:00 · 3,200 steps · fresh and upright'),
            (S(15, 30, steps=3200, bat=70, hr=72, month=11, tree_fn=tree_fn(0.3, opt=dict(droop=0.8, leaves=[(70, 104, 54), (100, 132, 66), (138, 156, 84)]))),
             'Behind pace', '15:30 · same steps · leaves droop and fade'),
            (S(15, 30, steps=15240, bat=64, hr=72, month=11), 'Goal reached · now (v1.5)', 'the full tree today'),
            (S(15, 30, steps=15240, bat=64, hr=72, month=11, tree_fn=tree_fn(1.02, grow_scale(1.02))), 'Goal reached · bigger', 'about 1.25x the size, in full bloom'),
            (S(19, 40, steps=15240, bat=58, hr=68, month=11, tree_fn=tree_fn(1.02, grow_scale(1.02)), pre=big(lanterns_water), post=big(lanterns_sky)),
             'Goal evening', 'paper lanterns rise from the lake after 6 pm'),
        ]
        D.sheet(items, O + 'v16-tree.png', cols=3)
        print('tree ok')
    if 'wild' in which:
        dawn = S(6, 45, steps=600, bat=97, hr=60, month=11, post=big(tahr_scene))
        day = S(16, 10, steps=9400, bat=66, hr=74, month=11, sky_fx=big(crows()))
        items = [(dawn, 'Nilgiri tahr', 'some dawns, a male and a kid on the ridge'), (day, 'Crows circling', 'house crows wheel slowly over the hills')]
        D.sheet(items, O + 'v16-wildlife.png', cols=2)
        Z = Image.new('RGB', (2 * 572 + 12, 312), (14, 14, 18))
        for i, (im, b) in enumerate(((dawn, (360, 214, 460, 264)), (day, (92, 168, 212, 228)))):
            z = im.crop(b).resize((560, 280), Image.LANCZOS); Z.paste(z, (12 + i * 572, 16), z)
        Z.save(O + 'v16-wildlife-closeup.png')
        print('wild ok')
    if 'slots' in which:
        a = LP.state(12, 20, steps=6900, bat=82, hr=72, month=11)
        b = LP.state(12, 20, steps=6900, bat=82, hr=72, month=11, hud=True)
        # redraw b with the slot outlines (where they would be) and c with them filled
        b2 = b.copy(); slots_outline(b2); b2 = LP.circle(b2)
        c = b.copy(); complications(c); c = LP.circle(c)
        items = [(a, 'Default', 'slots empty: just the lake'), (b2, 'Two optional slots', 'either side of the time (dashed = empty)'), (c, 'Filled', 'e.g. weather + next event')]
        D.sheet(items, O + 'v16-slots.png', cols=3)
        print('slots ok')


# ------------------------------------------------------------------ v2 slots: curved bars along the left and right edges
ARC_R = 222                       # bar radius (bezel inset 18 px)
LEFT_ARC = (164, 222)             # PIL degrees (0 = 3 o'clock, clockwise): lower-left -> upper-left, ends above the battery plank
RIGHT_ARC = (-42, 16)             # upper-right -> lower-right, ends above the steps sign


def curved_text(q, text, size, r, mid, col, spacing=0.14, font='lake_text', K=4):
    """glyphs along a circle around (240, 240), tops facing the bezel; mid = centre angle (PIL degrees)"""
    f = LP.F(font, size)
    advs = [f.getlength(ch) / K + spacing * size for ch in text]; tot = sum(advs) - spacing * size
    a = math.radians(mid) - tot / 2 / r
    for ch, adv in zip(text, advs):
        w = f.getlength(ch); h = size * K * 1.4
        g = Image.new('RGBA', (int(w) + 8, int(h)), (0, 0, 0, 0)); ImageDraw.Draw(g).text((4, 0), ch, font=f, fill=col)
        phi = a + (adv - spacing * size) / 2 / r
        rot = math.degrees(phi) + 90
        g = g.rotate(-rot, resample=Image.BICUBIC, expand=True)
        px, py = (240 + r * math.cos(phi)) * K, (240 + r * math.sin(phi)) * K
        q.alpha_composite(g, (int(px - g.width / 2), int(py - g.height / 2)))
        a += adv / r


def edge_bar(q, span, frac, col, K=4, track=True):
    box = [(240 - ARC_R) * K, (240 - ARC_R) * K, (240 + ARC_R) * K, (240 + ARC_R) * K]
    d = ImageDraw.Draw(q)
    a0, a1 = span
    if track: d.arc(box, a0, a1, fill=(255, 255, 255, 80), width=3 * K)
    if frac:
        if a0 > 90:   d.arc(box, a1 - (a1 - a0) * frac, a1, fill=col + (255,), width=3 * K) if False else d.arc(box, a0, a0 + (a1 - a0) * frac, fill=col + (255,), width=3 * K)   # left fills bottom-up
        else:         d.arc(box, a1 - (a1 - a0) * frac, a1, fill=col + (255,), width=3 * K)   # right fills bottom-up too
    for ang in ((a0, a0 + (a1 - a0) * frac) if frac else ()):                                    # round caps
        pass


def sun_icon(q, cx, cy, K=4):
    d = ImageDraw.Draw(q)
    d.ellipse([(cx - 3.2) * K, (cy - 3.2) * K, (cx + 3.2) * K, (cy + 3.2) * K], fill=(255, 214, 110, 255))
    for k in range(8):
        a = k * math.pi / 4
        d.line([(cx + 4.6 * math.cos(a)) * K, (cy + 4.6 * math.sin(a)) * K, (cx + 6.4 * math.cos(a)) * K, (cy + 6.4 * math.sin(a)) * K], fill=(255, 214, 110, 255), width=int(1.1 * K))


def drop_icon(q, cx, cy, K=4):
    d = ImageDraw.Draw(q)
    d.polygon([(cx * K, (cy - 5.5) * K), ((cx - 3.6) * K, (cy + 0.6) * K), ((cx + 3.6) * K, (cy + 0.6) * K)], fill=(120, 196, 255, 255))
    d.ellipse([(cx - 3.7) * K, (cy - 2.4) * K, (cx + 3.7) * K, (cy + 5) * K], fill=(120, 196, 255, 255))


def edge_slots(im, left=('28°  SUNNY', None, None), right=('WATER  5/8', 5 / 8, (120, 196, 255))):
    def draw(q):
        lt, lf, lc = left; rt, rf, rc = right
        edge_bar(q, LEFT_ARC, lf, lc or (255, 214, 110), track=True)
        edge_bar(q, RIGHT_ARC, rf, rc, track=True)
        # text just inside each bar, with a small icon at its start
        curved_text(q, lt, 13, ARC_R - 14, (LEFT_ARC[0] + LEFT_ARC[1]) / 2 + 3, (255, 255, 255, 235))
        curved_text(q, rt, 13, ARC_R - 14, (RIGHT_ARC[0] + RIGHT_ARC[1]) / 2 + 3, (255, 255, 255, 235))
        la = math.radians((LEFT_ARC[0] + LEFT_ARC[1]) / 2 - 17); ra = math.radians((RIGHT_ARC[0] + RIGHT_ARC[1]) / 2 - 18)
        sun_icon(q, 240 + (ARC_R - 15) * math.cos(la), 240 + (ARC_R - 15) * math.sin(la))
        drop_icon(q, 240 + (ARC_R - 15) * math.cos(ra), 240 + (ARC_R - 15) * math.sin(ra))
    LP.hud_text(im, draw, shadow=(4, 0.6, 1))


def edge_outline(im):
    lay = Image.new('RGBA', (1920, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    box = [(240 - ARC_R) * 4, (240 - ARC_R) * 4, (240 + ARC_R) * 4, (240 + ARC_R) * 4]
    for a0, a1 in (LEFT_ARC, RIGHT_ARC):
        for k in range(int(a0), int(a1), 5): d.arc(box, k, k + 2.5, fill=(255, 255, 255, 190), width=10)
    im.alpha_composite(lay.resize((480, 480), Image.LANCZOS))


if __name__ == '__main__' and 'edges' in sys.argv:
    a = LP.state(12, 20, steps=6900, bat=82, hr=72, month=11)
    b = LP.state(12, 20, steps=6900, bat=82, hr=72, month=11); edge_outline(b); b = LP.circle(b)
    c = LP.state(12, 20, steps=6900, bat=82, hr=72, month=11); edge_slots(c); c = LP.circle(c)
    n = LP.state(21, 30, steps=15240, bat=40, hr=64, moon=3, month=11); edge_slots(n, ('26°  CLEAR', None, None), ('WATER  7/8', 7 / 8, (120, 196, 255))); n = LP.circle(n)
    items = [(a, 'Default', 'bars hidden: just the lake'), (b, 'Where they sit', 'left + right edges (dashed)'),
             (c, 'Filled · day', 'e.g. weather (text) + water (bar)'), (n, 'Filled · night', 'same, at night')]
    D.sheet(items, O + 'v16-edge-slots.png', cols=2)
    print('edges ok')


# ------------------------------------------------------------------ birthday scene (names + dates baked in)
def balloons2(c, night=False, golden=False, x0=174, y0=331, sway=0.0):
    cols = [(236, 84, 96), (250, 190, 60), (90, 170, 230), (130, 200, 120), (230, 120, 200)]
    if night: cols = [tuple(int(v * 0.62) for v in col) for col in cols]
    if golden: cols = [(min(255, int(r * 1.05)), int(g * 0.88), int(b * 0.74)) for r, g, b in cols]
    tops = [(156, 266), (176, 258), (194, 270), (166, 283), (186, 288)]
    tops = [(x + sway * (331 - y) * 0.06, y) for x, y in tops]
    d = ImageDraw.Draw(c)
    for (bx, by), col in zip(tops, cols):                                                      # strings, gently curved
        pts = [(x0 + (bx - x0) * t + math.sin(t * 5 + bx) * 1.4 * (1 - t), y0 + (by + 10.5 - y0) * t) for t in np.linspace(0, 1, 32)]
        d.line([(px * SS, py * SS) for px, py in pts], fill=(236, 236, 230, 190 if not night else 120), width=max(1, int(0.5 * SS)))
    d.ellipse(P(x0 - 1.6, y0 - 1.2, x0 + 1.6, y0 + 1.6), fill=(236, 236, 230, 255))              # the knot on the post
    for (bx, by), col in zip(tops, cols):
        sh = ov(); ImageDraw.Draw(sh).ellipse(P(bx - 6.5, by - 7.5, bx + 7.5, by + 9), fill=(0, 0, 0, 50))
        c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(1.5 * SS)))
        d = ImageDraw.Draw(c)
        d.ellipse(P(bx - 7, by - 8.5, bx + 7, by + 8.5), fill=col + (255,))
        dark = tuple(int(v * 0.78) for v in col)
        rim = ov(); ImageDraw.Draw(rim).ellipse(P(bx - 7, by - 8.5, bx + 7, by + 8.5), outline=dark + (255,), width=int(1.2 * SS))
        c.alpha_composite(rim.filter(ImageFilter.GaussianBlur(0.8 * SS)))
        d = ImageDraw.Draw(c)
        d.polygon(P(bx - 1.6, by + 10.6, bx, by + 8, bx + 1.6, by + 10.6), fill=dark + (255,))   # the tied neck
        hl = ov(); ImageDraw.Draw(hl).ellipse(P(bx - 4.4, by - 6.4, bx - 1.2, by - 1.4), fill=(255, 255, 255, 170 if not night else 90))
        c.alpha_composite(hl.filter(ImageFilter.GaussianBlur(0.7 * SS)))
        d = ImageDraw.Draw(c)


def ribbon2(c, text, y=201, night=False):
    f = LP.F('lake_text', 14); sp = 0.12 * 14
    tw = sum(ImageDraw.Draw(c).textlength(ch, font=f) / SS + sp for ch in text) - sp
    w = tw + 40; x0 = 240 - w / 2 + 6; x1 = 240 + w / 2 + 6
    cream, fold, ink = ((252, 244, 228), (214, 190, 160), (96, 58, 40)) if not night else ((226, 214, 196), (170, 146, 118), (86, 52, 36))
    sh = ov(); ImageDraw.Draw(sh).rounded_rectangle(P(x0 - 10, y - 8, x1 + 10, y + 13), radius=4 * SS, fill=(0, 0, 0, 80))
    c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(3.5 * SS)))
    d = ImageDraw.Draw(c)
    for s in (-1, 1):                                                                          # swallow-tail ends folding behind
        ex = x0 if s < 0 else x1
        d.polygon(P(ex - s * 2, y - 5, ex + s * 14, y - 5, ex + s * 8.5, y + 3, ex + s * 14, y + 11, ex - s * 2, y + 11), fill=fold + (255,))
        d.polygon(P(ex - s * 2, y + 7, ex + s * 3.5, y + 11, ex - s * 2, y + 11), fill=tuple(int(v * 0.8) for v in fold) + (255,))
    d.rounded_rectangle(P(x0 + 2, y - 10, x1 - 2, y + 10), radius=2 * SS, fill=cream + (255,))
    d.line(P(x0 + 4, y - 7.6, x1 - 4, y - 7.6), fill=fold + (160,), width=max(1, int(0.5 * SS)))       # stitched edges
    d.line(P(x0 + 4, y + 7.6, x1 - 4, y + 7.6), fill=fold + (160,), width=max(1, int(0.5 * SS)))
    cx = x0 + 16                                                                                    # a little cake with a candle
    d.rounded_rectangle(P(cx - 5.5, y - 1.5, cx + 5.5, y + 5.5), radius=1 * SS, fill=(236, 120, 134, 255))
    d.rectangle(P(cx - 5.5, y - 2.6, cx + 5.5, y - 0.6), fill=(255, 250, 240, 255))
    for k in range(3): d.ellipse(P(cx - 4 + k * 4 - 0.7, y + 1.6, cx - 4 + k * 4 + 0.7, y + 3), fill=(255, 236, 160, 255))
    d.line(P(cx, y - 2.6, cx, y - 6.6), fill=(110, 170, 230, 255), width=max(1, int(0.9 * SS)))
    glow(c, cx, y - 8, 3, (255, 200, 90), 150, 1.2); d = ImageDraw.Draw(c)
    d.polygon(P(cx - 1, y - 7, cx, y - 10, cx + 1, y - 7), fill=(255, 196, 70, 255))
    xx = cx + 10
    for ch in text:
        d.text((xx * SS, (y - 9.2) * SS), ch, font=f, fill=ink + (255,)); xx += d.textlength(ch, font=f) / SS + sp


def confetti(c, seed=3, n=26):
    rng = random.Random(seed); d = ImageDraw.Draw(c)
    cols = [(236, 84, 96), (250, 190, 60), (90, 170, 230), (130, 200, 120), (230, 120, 200)]
    for _ in range(n):
        x, y = rng.uniform(70, 410), rng.uniform(186, 222)
        if abs(x - 240) < 120 and 190 < y < 214: continue
        a = rng.uniform(0, math.pi); l = rng.uniform(1.6, 2.6)
        d.line(P(x - math.cos(a) * l, y - math.sin(a) * l, x + math.cos(a) * l, y + math.sin(a) * l), fill=rng.choice(cols) + (230,), width=max(1, int(1.1 * SS)))


def bday_face(hh, mm, text, night=False, golden=False, day=21, dow='SAT', **k):
    im = LP.state(hh, mm, month=11, dow=dow, day=day, mon='NOV', post=big(lambda c, h, n: balloons2(c, night, golden)), **k)
    lay = ov(); confetti(lay); ribbon2(lay, text, night=night)
    im.alpha_composite(LP.circle(lay.resize((480, 480), Image.LANCZOS)))
    return im


if __name__ == '__main__' and 'bday' in sys.argv:
    m = bday_face(9, 15, "PRIYA'S BIRTHDAY", steps=2100, bat=94, hr=70)
    g = bday_face(17, 40, "PRIYA'S BIRTHDAY", golden=True, steps=10400, bat=52, hr=76)
    n = bday_face(21, 10, "PRIYA'S BIRTHDAY", night=True, steps=13900, bat=38, hr=66)
    two = bday_face(11, 30, "PRIYA & ARUN · BIRTHDAYS", steps=5600, bat=80, hr=72, day=3, dow='THU')
    items = [(m, 'Birthday morning', 'balloons tied to the jetty, their name in the sky'), (g, 'Golden hour', 'same scene, warm light'),
             (n, 'Night', 'balloons in the dark, the ribbon stays readable'), (two, 'Two on one day', 'both names on the ribbon')]
    D.sheet(items, O + 'v16-birthday.png', cols=2)
    z1 = m.crop((120, 180, 360, 300)).resize((480, 240), Image.LANCZOS); z2 = m.crop((140, 250, 240, 350)).resize((240, 240), Image.LANCZOS)
    Z = Image.new('RGB', (480 + 240 + 36, 264), (14, 14, 18)); Z.paste(z1, (12, 12), z1); Z.paste(z2, (504, 12), z2); Z.save(O + 'v16-birthday-closeup.png')
    print('bday ok')
