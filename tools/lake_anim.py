"""Living Lake – animation frames: boat (fishing / rowing / moored / the catch), jumping fish, birds, ducks."""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))           # tools/
_ROOT = _os.path.dirname(_HERE)                                   # repo root
_RES = _ROOT + '/watchface/src/main/res/'                         # the watch face resources
_OUT = _ROOT + '/out/'                                            # previews, videos, mock-ups (not committed)
import json, math, sys
sys.path.insert(0, _HERE); sys.path.insert(0, _HERE)
from PIL import Image
import lake_art as A, waterlife as WL, hroptions as HO
from landmock import SS, ov

A.MAN.update(json.load(open(_HERE + '/art.json')))
ONLY = set(sys.argv[1:])
def want(k): return not ONLY or k in ONLY

from layout15 import FISH_AT, ROW_AT, MOOR_AT, BOAT_SC, DUCK_Y
SC = BOAT_SC


def big_boat(c, at, t, mode, **kw):
    """the boat drawn 1.3x bigger: same drawing at a larger supersample factor"""
    WL.boat(c, SS * SC, at[0] / SC, at[1] / SC, t, mode, **kw)
if want('boat'):
    A.frames('boat_fish', lambda i: (lambda c: (big_boat(c, FISH_AT, i / 8.0, 'fish'), c)[1])(ov()), 48, pad=3)
    A.frames('boat_rowd', lambda i: (lambda c: (big_boat(c, ROW_AT, i / 8.0, 'row'), c)[1])(ov()), 24, pad=3)
    A.frames('boat_rowg', lambda i: (lambda c: (big_boat(c, ROW_AT, i / 8.0, 'row', golden=True), c)[1])(ov()), 24, pad=3)
    A.frames('boat_moor', lambda i: (lambda c: (big_boat(c, MOOR_AT, i / 8.0, 'moored', night=True), c)[1])(ov()), 24, pad=3)
    # the catch plays over the fishing loop, so each frame carries the patch of daytime lake behind it
    bx, by, bw, bh, _ = A.MAN['boat_fish']
    box = (bx - 2, by - 12, bw + 6, bh + 14)
    land = Image.open(A.OUT + 'land_day.png').convert('RGBA'); lx, ly = A.MAN['land_day'][:2]
    sky = Image.open(A.OUT + 'sky_day.png').convert('RGBA')
    def catch(i):
        c = ov(); big_boat(c, FISH_AT, 1.0 + i / 12.0, 'fish', catch=i / 30)
        f = A.down(c); bg = Image.new('RGBA', (480, 480), (0, 0, 0, 0)); bg.paste(sky, (0, 0)); bg.alpha_composite(land, (lx, ly)); bg.alpha_composite(f)
        return bg
    ims = [catch(i) for i in range(31)]
    for i, im in enumerate(ims): A.save(im, f'boat_catch_{i:02d}', box)
    A.MAN['boat_catch'] = list(box) + [31]
    Image.new('RGBA', box[2:], (0, 0, 0, 0)).save(A.OUT + 'catch_blank.png')
if want('fish'):
    # rendered at x0 = 220; the XML moves the whole part. 15 fps: 1.1 s jump + rings fading
    for tag, kw in (('d', {}), ('g', {'golden': True}), ('n', {'night': True})):
        A.frames(f'fish_{tag}', lambda i, kw=kw: (lambda c: (WL.fish_jump(c, SS, 220, 336, i / 16.5, **kw), c)[1])(ov()), 34, box=(180, 300, 100, 48))
    Image.new('RGBA', (100, 48), (0, 0, 0, 0)).save(A.OUT + 'fish_blank.png')
if want('birds'):
    A.frames('birds', lambda i: (lambda c: (HO.birds(c, SS, i / 8 * (2 * math.pi / 7), x0=240, y0=210), c)[1])(ov()), 8, pad=3)
if want('ducks'):
    for ph in ('dawn', 'day', 'golden'):
        def r(ph=ph):
            c = ov(); g = ph != 'day'
            WL.duck(c, SS, 240, DUCK_Y, 0.0, 0, golden=g); WL.duck(c, SS, 260, DUCK_Y + 4, 0.0, 1, golden=g)
            return A.down(c)
        A.save(r(), f'ducks_{ph}', (218, DUCK_Y - 10, 54, 20))
json.dump(A.MAN, open(_HERE + '/art.json', 'w'), indent=0)
print('anim ok', {k: A.MAN[k] for k in ('boat_fish', 'boat_rowd', 'boat_moor', 'boat_catch', 'birds') if k in A.MAN})
