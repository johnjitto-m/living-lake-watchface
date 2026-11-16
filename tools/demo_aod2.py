"""Demo: bigger, centred always-on clock (time + date + reflection) that shrinks and glides up into place on wake."""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))           # tools/
_ROOT = _os.path.dirname(_HERE)                                   # repo root
_RES = _ROOT + '/watchface/src/main/res/'                         # the watch face resources
_OUT = _ROOT + '/out/'                                            # previews, videos, mock-ups (not committed)
import os, subprocess, sys
sys.path.insert(0, _HERE)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import lake_preview as LP, aod_v13 as AV, demo_aod_video as DV

OUT = _OUT + 'video/'
K = 4                                        # supersampling
PIV = (240, 145)                             # pivot of the clock block (its centre in the awake layout)
AOD_SCALE, AOD_DY = 1.22, 83                 # always-on: 22 % bigger, centre moved down to y 228


def ease(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)


def text4(l4, y, size, s, font, col, spacing=0.0):
    LP.text_layer(l4, 0, y, 480, size, s, font, col, spacing=spacing)


def shadowed(l4, r, a):
    sh = Image.new('RGBA', l4.size, (0, 0, 0, 0)); sh.putalpha(l4.split()[3].point(lambda v: int(v * a)))
    out = Image.new('RGBA', l4.size, (0, 0, 0, 0)); out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(r * K / 2)), (0, K)); out.alpha_composite(l4)
    return out


class Block:
    def __init__(self, hhmm, date, hr=72):
        t = Image.new('RGBA', (480 * K, 480 * K), (0, 0, 0, 0)); text4(t, 48, 92, hhmm, 'lake_time', (255, 255, 255, 255))
        d = Image.new('RGBA', (480 * K, 480 * K), (0, 0, 0, 0)); text4(d, 150, 15, date, 'lake_text', (255, 255, 255, 230), 0.21)
        self.time, self.date = shadowed(t, 7, 0.6), shadowed(d, 5, 0.63)
        r = Image.new('RGBA', (480 * K, 480 * K), (0, 0, 0, 0)); text4(r, 147, 92, hhmm, 'lake_reflect', (0x6c, 0x72, 0x82, 255))
        w = LP.L('aod_water'); r.alpha_composite(w.resize((w.width * K, w.height * K), Image.LANCZOS), (0, 184 * K))
        self.refl = r
        h = Image.new('RGBA', (480 * K, 480 * K), (0, 0, 0, 0))                     # the heart rate rides with the date
        h.alpha_composite(LP.L('heart_small').resize((11 * K, 10 * K), Image.LANCZOS), (318 * K, int(150 * K + 15 * K * 0.64 - 5 * K)))
        ImageDraw.Draw(h).text(((318 + 14) * K, 150 * K), str(hr), font=LP.F('lake_text', 15), fill=(255, 255, 255, 230))
        self.hr = shadowed(h, 5, 0.63)

    @staticmethod
    def place(l4, s, dy, slide=0):
        """scale s about the pivot, then move down dy (+ slide for the reflection) -> 480 px"""
        px, py = PIV[0] * K, PIV[1] * K
        # inverse map for PIL: src = (dst - pivot - (0, dy)) / s + pivot
        a = 1 / s
        out = l4.transform(l4.size, Image.AFFINE, (a, 0, px - px * a, 0, a, py - (py + (dy + slide) * K) * a), resample=Image.BICUBIC)
        return out.resize((480, 480), Image.LANCZOS)


def frame(face, block, amb, t, scene_on=True):
    p = ease(amb)
    s = 1 + (AOD_SCALE - 1) * p; dy = AOD_DY * p
    a_scene = 1 - p; a_aod = ease((amb - 0.2) / 0.8)
    im = Image.new('RGBA', (480, 480), (0, 0, 0, 255))
    if a_scene > 0 and scene_on:
        im.alpha_composite(AV.fade(face.scene(t), a_scene))
    if amb < 0.6: im.alpha_composite(AV.fade(Block.place(block.hr, s, dy), ease(1 - amb / 0.6)))
    if a_aod > 0:
        slide = 8 * (1 - (1 - (1 - min(1.0, max(0.0, amb)))) ** 0) if False else 8 * (1 - amb) ** 2
        im.alpha_composite(AV.fade(Block.place(block.refl, s, dy, slide), a_aod))
    im.alpha_composite(AV.fade(Block.place(block.time, s, dy), 1 - p * (1 - 220 / 255)))
    im.alpha_composite(AV.fade(Block.place(block.date, s, dy), 1 - p * (1 - 170 / 255)))
    return LP.circle(im)


if __name__ == '__main__':
    night = DV.Face(21, 30, 'SUN  15  NOV', dict(steps=15240, bat=40, hr=64, moon=3, month=11))
    morning = DV.Face(8, 47, 'MON  16  NOV', dict(steps=2100, bat=91, hr=70, month=11))
    bn, bm = Block('21:30', 'SUN  15  NOV', 64), Block('08:47', 'MON  16  NOV', 70)
    # stills: always-on, mid-transition, awake
    S = Image.new('RGB', (3 * 492 + 12, 492 + 12), (14, 14, 18))
    for i, amb in enumerate((1.0, 0.5, 0.0)):
        im = frame(night, bn, amb, 4.0); S.paste(im, (12 + i * 492, 12), im)
    S.save(_OUT + 'preview/aod-centre-stills.png')
    if 'stills' in sys.argv: print('stills ok'); sys.exit()

    def cycle(face, block, title, hold=2.0, awake=4.0):
        T1 = hold; T2 = T1 + 1.0; T3 = T2 + awake; T4 = T3 + 1.0; T5 = T4 + 1.2
        def amb_at(t):
            if t < T1: return 1.0
            if t < T2: return 1 - (t - T1)
            if t < T3: return 0.0
            if t < T4: return t - T3
            return 1.0
        def cap(t):
            if t < T1: return ('Always-on', title)
            if t < T2: return ('Raise your wrist', 'the clock shrinks and glides up into place')
            if t < T3: return ('Awake', 'the lake comes alive')
            if t < T4: return ('Lower your wrist', 'the clock grows and settles in the centre')
            return ('Always-on', title)
        return T5, (lambda t: DV.compose(frame(face, block, amb_at(t), t), *cap(t), DV.wrist(amb_at(t))))

    parts = []
    dur, fn = cycle(night, bn, 'bigger, centred, reflected on still water')
    DV.render(OUT + 'c1.mp4', int(dur * DV.FPS), fn); parts.append('c1.mp4')
    def slow(t):
        amb = 1.0 if t < 0.6 else (1 - (t - 0.6) / 2.5 if t < 3.1 else 0.0)
        return DV.compose(frame(night, bn, amb, 4.0 + t), 'Slow motion ×0.4', 'shrinks and moves up while the lake fades in', DV.wrist(amb))
    DV.render(OUT + 'c2.mp4', int(4.0 * DV.FPS), slow); parts.append('c2.mp4')
    dur, fn = cycle(morning, bm, 'morning', hold=1.6)
    DV.render(OUT + 'c3.mp4', int(dur * DV.FPS), fn); parts.append('c3.mp4')
    with open(OUT + 'list2.txt', 'w') as f:
        for p in parts: f.write(f"file '{OUT}{p}'\n")
    tmp = OUT + 'centre.tmp.mp4'
    r = subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', OUT + 'list2.txt', '-c', 'copy', '-movflags', '+faststart', tmp])
    if r.returncode == 0: os.replace(tmp, OUT + 'living-lake-aod-centre-demo.mp4')
    print('video ok')
