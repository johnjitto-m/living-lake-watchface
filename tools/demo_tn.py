"""Tamil Nadu seasons + festivals for Living Lake."""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))           # tools/
_ROOT = _os.path.dirname(_HERE)                                   # repo root
_RES = _ROOT + '/watchface/src/main/res/'                         # the watch face resources
_OUT = _ROOT + '/out/'                                            # previews, videos, mock-ups (not committed)
import math, random, sys
sys.path.insert(0, _HERE)
from PIL import Image, ImageDraw, ImageFilter
import landmock as LM, waterlife as WL, lakelife as LL, demo4 as D
from landmock import SS, W, P, ov, mist


def konrai_tree(img, ph, y0=334, y1=350, half=34, n=26):
    """golden-shower (konrai) chains hanging down from the canopy"""
    rng = random.Random(12); lay = ov(); d = ImageDraw.Draw(lay)
    for _ in range(n):
        x = 376 + rng.uniform(-half, half); y = rng.uniform(y0, y1); L = rng.uniform(9, 17)
        for k in range(int(L / 1.6)):
            yy = y + k * 1.6; xx = x + math.sin(k * 0.6) * 0.5
            r = 1.2 - k * 0.04
            d.ellipse(P(xx - r, yy - r, xx + r, yy + r), fill=(255, 214, 60, 255) if k % 2 else (240, 186, 40, 255))
    img.alpha_composite(lay)


def clouds(img, dark=False, n=5, seed=8):
    rng = random.Random(seed); lay = ov(); d = ImageDraw.Draw(lay)
    col = (236, 240, 246) if not dark else (176, 184, 196)
    for _ in range(n):
        cx, cy, s = rng.uniform(40, 440), rng.uniform(186, 236), rng.uniform(0.7, 1.2)
        for _ in range(7):
            r = rng.uniform(10, 18) * s; x = cx + rng.uniform(-26, 26) * s; y = cy + rng.uniform(-5, 4) * s
            d.ellipse(P(x - r * 1.6, y - r, x + r * 1.6, y + r * 0.7), fill=col + (200,))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(2.5 * SS)))


def lotus(img, seed=3):
    rng = random.Random(seed); d = ImageDraw.Draw(img)
    spots = [(196, 372), (214, 378), (236, 374), (258, 380), (280, 372), (300, 378), (184, 382), (226, 386)]
    for i, (x, y) in enumerate(spots):
        d.ellipse(P(x - 6, y - 2, x + 6, y + 2), fill=(58, 112, 64, 255))
        d.pieslice(P(x - 6, y - 2, x + 6, y + 2), -20, 20, fill=(44, 88, 52, 255))
        if i % 2 == 0:
            for k, a in enumerate((-0.6, -0.25, 0.1, 0.45)):
                px = x + math.sin(a) * 4; d.polygon(P(px - 1.5, y - 1, px + math.sin(a) * 2, y - 6 - k % 2, px + 1.5, y - 1), fill=(244, 140, 176, 255))
            d.ellipse(P(x - 1.2, y - 3, x + 1.2, y - 1), fill=(255, 220, 120, 255))


def stork(img, x, y, flip=1):
    d = ImageDraw.Draw(img)
    d.line(P(x - 1, y, x - 2, y + 9), fill=(214, 150, 150, 255), width=max(1, int(0.7 * SS)))
    d.line(P(x + 1, y, x + 1.5, y + 9), fill=(214, 150, 150, 255), width=max(1, int(0.7 * SS)))
    d.ellipse(P(x - 6, y - 5, x + 6, y + 1), fill=(246, 246, 240, 255))
    d.polygon(P(x - 6 * flip, y - 3, x - 10 * flip, y - 1, x - 4 * flip, y + 0.5), fill=(240, 150, 170, 255))      # pink tail
    d.line(P(x - 4, y - 1.5, x + 3, y - 1.5), fill=(30, 30, 34, 255), width=max(1, int(1.1 * SS)))                  # black wing band
    d.line(P(x + 4 * flip, y - 3, x + 6 * flip, y - 11), fill=(246, 246, 240, 255), width=max(1, int(1.3 * SS)))
    d.ellipse(P(x + 5 * flip - 1.8, y - 13.5, x + 5 * flip + 1.8, y - 10), fill=(236, 200, 120, 255))
    d.line(P(x + 6 * flip, y - 11.5, x + 11 * flip, y - 8), fill=(240, 200, 80, 255), width=max(1, int(1.1 * SS)))
    WL.ripples(d, SS, x, y + 9, 0.6, n=2, span=1.6, a0=120, rmax=7)


def pelican(img, x, y):
    d = ImageDraw.Draw(img)
    d.ellipse(P(x - 8, y - 4, x + 6, y + 2), fill=(240, 238, 232, 255))
    d.line(P(x + 3, y - 2, x + 5, y - 9), fill=(240, 238, 232, 255), width=max(1, int(1.6 * SS)))
    d.ellipse(P(x + 3, y - 12, x + 7.5, y - 8), fill=(240, 238, 232, 255))
    d.polygon(P(x + 7, y - 10.5, x + 15, y - 8, x + 7, y - 7.4), fill=(244, 196, 90, 255))
    d.line(P(x - 7, y + 2.5, x + 6, y + 2.5), fill=(255, 255, 255, 110), width=max(1, int(0.6 * SS)))


def kolam(img, cx=318, cy=432):
    lay = ov(); d = ImageDraw.Draw(lay)
    for i in range(-3, 4):
        for j in range(-1, 2):
            if abs(i) + abs(j) * 2 <= 4: d.ellipse(P(cx + i * 7 - 0.9, cy + j * 4 - 0.6, cx + i * 7 + 0.9, cy + j * 4 + 0.6), fill=(255, 255, 255, 255))
    for k in range(16):
        a = k / 16 * 2 * math.pi
        x1, y1 = cx + math.cos(a) * 24, cy + math.sin(a) * 7
        x2, y2 = cx + math.cos(a + 0.4) * 12, cy + math.sin(a + 0.4) * 3.5
        d.line(P(x1, y1, x2, y2), fill=(255, 255, 255, 230), width=max(1, int(0.8 * SS)))
    d.ellipse(P(cx - 25, cy - 7.6, cx + 25, cy + 7.6), outline=(255, 255, 255, 230), width=max(1, int(0.8 * SS)))
    for k, c in enumerate(((236, 70, 90), (250, 180, 40), (80, 170, 90), (90, 120, 230))):
        a = k / 4 * 2 * math.pi + 0.4
        d.ellipse(P(cx + math.cos(a) * 17 - 2, cy + math.sin(a) * 5 - 1.2, cx + math.cos(a) * 17 + 2, cy + math.sin(a) * 5 + 1.2), fill=c + (255,))
    img.alpha_composite(lay)


def pongal_pot(img, x=226, y=414):
    d = ImageDraw.Draw(img)
    for sx in (-7, 0, 7): d.ellipse(P(x + sx - 3, y - 1, x + sx + 3, y + 3), fill=(120, 110, 100, 255))
    g = ov(); ImageDraw.Draw(g).ellipse(P(x - 8, y - 6, x + 8, y + 3), fill=(255, 150, 50, 160))
    img.alpha_composite(g.filter(ImageFilter.GaussianBlur(2 * SS)))
    d = ImageDraw.Draw(img)
    d.ellipse(P(x - 9, y - 18, x + 9, y), fill=(184, 92, 52, 255))
    d.rectangle(P(x - 5, y - 21, x + 5, y - 16), fill=(170, 84, 48, 255))
    d.line(P(x - 8, y - 11, x + 8, y - 11), fill=(240, 196, 60, 255), width=max(1, int(1.2 * SS)))   # turmeric string
    for k, (dx, dy) in enumerate(((-4, -23), (0, -25), (4, -23), (-6, -20), (6, -20))):
        d.ellipse(P(x + dx - 3, y + dy - 2, x + dx + 3, y + dy + 2.2), fill=(252, 250, 240, 255))
    d.polygon(P(x - 5, y - 20, x - 7, y - 13, x - 3.5, y - 18), fill=(252, 250, 240, 255))      # boiling over
    for sx, lean in ((x - 20, -0.12), (x + 20, 0.12)):                                          # sugarcane
        top = (sx + lean * 60, y - 60)
        d.line(P(sx, y + 2, *top), fill=(110, 60, 90, 255), width=int(2.4 * SS))
        for k in range(1, 6):
            yy = y + 2 - k * 11; xx = sx + lean * (k * 11)
            d.line(P(xx - 1.6, yy, xx + 1.6, yy), fill=(200, 190, 140, 255), width=max(1, int(0.8 * SS)))
        for a in (-0.9, -0.3, 0.4, 1.0):
            d.line(P(top[0], top[1], top[0] + math.sin(a) * 16, top[1] - math.cos(a) * 9 + 6), fill=(90, 160, 70, 255), width=max(1, int(1.1 * SS)))


def thoranam(img, x0=8, x1=176, y=343):
    lay = ov(); d = ImageDraw.Draw(lay)
    d.line(P(x0, y, x1, y), fill=(200, 170, 110, 255), width=max(1, int(0.7 * SS)))
    for x in range(x0 + 3, x1, 5):
        d.polygon(P(x - 1.8, y, x, y + 7.5, x + 1.8, y), fill=(56, 132, 56, 255) if (x // 5) % 2 else (76, 156, 62, 255))
    img.alpha_composite(lay)


def agal_row(img, pts, sc=0.7):
    for x, y in pts: D.diya(img, x, y, sc)


def grade_hot(img):
    """summer: a warmer, hazier light"""
    h = ov(); ImageDraw.Draw(h).rectangle(P(0, 0, 480, 480), fill=(255, 214, 160, 34))
    img.alpha_composite(h)


if __name__ == '__main__':
    O = _OUT + 'mockups/'
    which = sys.argv[1:] or ['seasons', 'festivals']
    golden_tree = dict(leaves=[(88, 110, 44), (150, 160, 58), (220, 196, 60)])
    if 'seasons' in which:
        items = [
            (D.face(12.33, '12:20', 10500, 0.7, tree_opt=golden_tree, land={'day': {6: (122, 132, 66)}},
                    post=lambda im, ph: (konrai_tree(im, ph), grade_hot(im)), birds_at=(372, 208)),
             'Summer · Mar – May', 'hot, hazy light · the konrai tree turns golden'),
            (D.face(12.33, '12:20', 10500, 0.7, land={'day': {6: (58, 124, 56)}}, after_land=lambda im, ph: clouds(im, n=4), birds_at=(372, 214)),
             'Monsoon · Jun – Sep', 'lush and green · clouds drift over the peaks'),
            (D.face(12.33, '12:20', 10500, 0.7, land={'day': {6: (52, 116, 54)}}, after_land=lambda im, ph: clouds(im, dark=True, n=6, seed=3),
                    pre=lambda im, ph: lotus(im)), 'Northeast monsoon · Oct – Dec', 'grey rain clouds · the lake fills, lotus blooms'),
            (D.face(7.25, '07:15', 1800, 0.12, pre=lambda im, ph: (mist(im, 318, 26, 120), mist(im, 350, 20, 90), stork(im, 214, 374), stork(im, 236, 380, -1),
                                                                    pelican(im, 160, 334), pelican(im, 286, 330)), boat=None),
             'Cool season · Dec – Feb', 'misty mornings · storks and pelicans visit the lake'),
        ]
        D.sheet(items, O + 'tn-seasons.png', cols=2)
        D.closeups(items, [(250, 270, 470, 391), (60, 170, 420, 368), (170, 330, 330, 418), (130, 300, 310, 399)], O + 'tn-seasons-closeup.png')
    if 'festivals' in which:
        warm = [(255, 196, 90)]; xmas = [(255, 80, 70), (90, 220, 110), (255, 210, 90), (110, 170, 255)]
        deepam = lambda im, ph: (agal_row(im, [(x, 341) for x in range(14, 178, 12)], 0.55),
                                 agal_row(im, [(x, LL.BANK + 6 + 3 * math.sin(x * 0.05)) for x in range(70, 420, 22)], 0.7))
        def deepavali(im, ph):
            for x, y, s_ in ((196, 326, 0.75), (234, 318, 0.7), (270, 334, 0.85), (212, 348, 0.95), (252, 358, 1.05), (300, 324, 0.7), (190, 368, 1.1), (290, 352, 1.0)):
                D.diya(im, x, y, s_)
            D.firework(im, 120, 226, 26, (255, 200, 90), 1); D.firework(im, 352, 220, 30, (255, 110, 150), 2)
        items = [
            (D.face(10.0, '10:00', 4600, 0.31, pre=lambda im, ph: (pongal_pot(im), kolam(im)), birds_at=(372, 210)), 'Pongal', 'kolam, a pot boiling over, sugarcane'),
            (D.face(11.0, '11:00', 5200, 0.35, tree_opt=golden_tree, post=lambda im, ph: (konrai_tree(im, ph, 348, 360, 22, 16), thoranam(im)), birds_at=(372, 210)),
             'Tamil New Year', 'mango-leaf thoranam · konrai in bloom'),
            (D.face(19.75, '19:45', 11200, 0.75, post=deepam, boat=None), 'Karthigai Deepam', 'rows of agal vilakku on the jetty and shore'),
            (D.face(20.5, '20:30', 12400, 0.85, pre=deepavali, post=lambda im, ph: D.jetty_lights(im, warm), boat=None), 'Deepavali', 'floating diyas · fireworks over the peaks'),
            (D.face(21.0, '21:00', 9800, 0.66, pre=lambda im, ph: D.tree_star(im, 377, 300), post=lambda im, ph: D.jetty_lights(im, xmas)),
             'Christmas', 'coloured lights · a star on the tree'),
            (D.face(23.98, '23:59', 13200, 0.88, pre=lambda im, ph: (D.firework(im, 120, 222, 30, (255, 200, 90), 1), D.firework(im, 352, 214, 34, (255, 110, 150), 2),
                                                                     D.firework(im, 236, 236, 22, (140, 220, 255), 3)), post=lambda im, ph: D.jetty_lights(im, warm)),
             "New Year's Eve", 'fireworks reflected in the lake'),
        ]
        D.sheet(items, O + 'tn-festivals.png', cols=3)
        D.closeups(items[:3], [(180, 340, 360, 439), (0, 290, 220, 411), (0, 300, 300, 465)], O + 'tn-festivals-closeup.png')
    print('ok', which)
