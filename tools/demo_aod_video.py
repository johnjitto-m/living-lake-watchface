"""Demo video: always-on (still water) <-> wake, on a generic watch. 1080x1080, 30 fps, one file per scene, concatenated."""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))           # tools/
_ROOT = _os.path.dirname(_HERE)                                   # repo root
_RES = _ROOT + '/watchface/src/main/res/'                         # the watch face resources
_OUT = _ROOT + '/out/'                                            # previews, videos, mock-ups (not committed)
import math, os, subprocess, sys
sys.path.insert(0, _HERE)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import lake_preview as LP, aod_v13 as AV

OUT = _OUT + 'video/'; os.makedirs(OUT, exist_ok=True)
W, FPS, FACE = 1080, 30, 660
CX, CY = W // 2, 500
FT = _HERE + '/fonts/inter/'
CAP = ImageFont.truetype(FT + 'Inter-SemiBold.otf', 40); SUB = ImageFont.truetype(FT + 'Inter-Regular.otf', 28)


def ease(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)


# ---------------------------------------------------------------- a generic watch (no brand)
def watch_body():
    S = 2; im = Image.new('RGBA', (W * S, W * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    R = FACE // 2
    # strap
    d.rounded_rectangle([(CX - 190) * S, (CY - 560) * S, (CX + 190) * S, (CY + 560) * S], radius=60 * S, fill=(24, 25, 29, 255))
    for y in range(CY - 540, CY + 560, 26): d.line([(CX - 170) * S, y * S, (CX + 170) * S, y * S], fill=(30, 31, 36, 255), width=2 * S)
    # lugs + case + bezel
    d.ellipse([(CX - R - 52) * S, (CY - R - 52) * S, (CX + R + 52) * S, (CY + R + 52) * S], fill=(58, 60, 66, 255))
    d.ellipse([(CX - R - 40) * S, (CY - R - 40) * S, (CX + R + 40) * S, (CY + R + 40) * S], fill=(92, 95, 102, 255))
    d.ellipse([(CX - R - 30) * S, (CY - R - 30) * S, (CX + R + 30) * S, (CY + R + 30) * S], fill=(36, 37, 41, 255))
    d.ellipse([(CX - R - 8) * S, (CY - R - 8) * S, (CX + R + 8) * S, (CY + R + 8) * S], fill=(4, 4, 6, 255))
    for dy in (-120, 120):                                      # two side buttons
        d.rounded_rectangle([(CX + R + 44) * S, (CY + dy - 34) * S, (CX + R + 62) * S, (CY + dy + 34) * S], radius=8 * S, fill=(80, 82, 88, 255))
    im = im.resize((W, W), Image.LANCZOS)
    hl = Image.new('RGBA', (W, W), (0, 0, 0, 0)); ImageDraw.Draw(hl).arc([CX - R - 38, CY - R - 38, CX + R + 38, CY + R + 38], 200, 290, fill=(200, 204, 214, 90), width=6)
    im.alpha_composite(hl.filter(ImageFilter.GaussianBlur(3)))
    return im


BODY = watch_body()
MASK = Image.new('L', (FACE, FACE), 0); ImageDraw.Draw(MASK).ellipse([0, 0, FACE - 1, FACE - 1], fill=255)
BG = Image.new('RGB', (W, W), (12, 13, 16))
g = Image.new('L', (W, W), 0); ImageDraw.Draw(g).ellipse([CX - 520, CY - 520, CX + 520, CY + 520], fill=60)
BG.paste(Image.new('RGB', (W, W), (34, 38, 48)), (0, 0), g.filter(ImageFilter.GaussianBlur(160)))


def compose(face480, caption, sub, scale=1.0, glass=1.0):
    out = BG.copy().convert('RGBA')
    body = BODY
    if scale != 1.0:
        sw = int(W * scale); body = BODY.resize((sw, sw), Image.LANCZOS)
        tmp = Image.new('RGBA', (W, W), (0, 0, 0, 0)); tmp.alpha_composite(body, ((W - sw) // 2, int(CY - CY * scale)))
        body = tmp
    out.alpha_composite(body)
    fs = int(FACE * scale)
    face = face480.convert('RGB').resize((fs, fs), Image.LANCZOS)
    m = MASK.resize((fs, fs), Image.LANCZOS)
    out.paste(face, (CX - fs // 2, int(CY - fs / 2)), m)
    # glass reflection
    gl = Image.new('RGBA', (W, W), (0, 0, 0, 0)); gd = ImageDraw.Draw(gl)
    gd.ellipse([CX - fs // 2, int(CY - fs / 2), CX + fs // 2, int(CY + fs / 2)], outline=(255, 255, 255, int(16 * glass)), width=3)
    gd.chord([CX - fs // 2 + 40, int(CY - fs / 2) + 30, CX + fs // 2 - 40, int(CY + fs / 2) - 30], 205, 250, fill=(255, 255, 255, int(10 * glass)))
    out.alpha_composite(gl.filter(ImageFilter.GaussianBlur(4)))
    d = ImageDraw.Draw(out)
    if caption:
        tw = d.textlength(caption, font=CAP); d.text((CX - tw / 2, 930), caption, font=CAP, fill=(236, 238, 242))
    if sub:
        tw = d.textlength(sub, font=SUB); d.text((CX - tw / 2, 988), sub, font=SUB, fill=(150, 156, 168))
    return out.convert('RGB')


class Face:
    """caches the expensive parts; scene animated at 15 fps"""
    def __init__(self, hh, mm, date, kw):
        self.hh, self.mm, self.date, self.kw = hh, mm, date, kw
        self.hhmm = f'{hh:02d}:{mm:02d}'
        self.t_time, self.t_date, self.t_hr = AV.hud_time(self.hhmm), AV.hud_date(date), AV.hud_hr(kw['hr'])
        self.refl = {dy: AV.reflection(self.hhmm, dy) for dy in range(0, 9)}
        self.scenes = {}

    def scene(self, t):
        k = round(t * 15) / 15
        if k not in self.scenes:
            self.scenes[k] = LP.state(self.hh, self.mm, hud=False, t=k, anim=True, **self.kw)
        return self.scenes[k]

    def frame(self, amb, t):
        a_scene = 1 - ease(amb); a_aod = ease((amb - 0.2) / 0.8)
        dy = round(8 * (1 - (1 - (1 - max(0.0, min(1.0, amb))) ** 0) * 0)) if False else round(8 * (1 - (1 - (1 - min(1.0, max(0.0, amb))) ** 2)))
        im = Image.new('RGBA', (480, 480), (0, 0, 0, 255))
        if a_scene > 0:
            im.alpha_composite(AV.fade(self.scene(t), a_scene)); im.alpha_composite(AV.fade(self.t_hr, a_scene))
        if a_aod > 0: im.alpha_composite(AV.fade(self.refl[min(8, max(0, dy))], a_aod))
        im.alpha_composite(AV.fade(self.t_time, 1 - ease(amb) * (1 - 220 / 255)))
        im.alpha_composite(AV.fade(self.t_date, 1 - ease(amb) * (1 - 170 / 255)))
        return LP.circle(im)


def render(path, n_frames, fn):
    tmp = path[:-4] + '.tmp.mp4'
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{W}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
    for f in range(n_frames): ff.stdin.write(fn(f / FPS).tobytes())
    ff.stdin.close()
    if ff.wait() == 0: os.replace(tmp, path)


def wrist(amb):          # the watch rises a touch as you raise your wrist
    return 0.965 + 0.035 * (1 - ease(amb))


def cycle(face, hold_aod=2.0, awake=4.0, title=''):
    """always-on -> wake -> awake -> always-on -> hold"""
    T1 = hold_aod; T2 = T1 + 1.0; T3 = T2 + awake; T4 = T3 + 1.0; T5 = T4 + 1.2
    def amb_at(t):
        if t < T1: return 1.0
        if t < T2: return 1 - (t - T1)
        if t < T3: return 0.0
        if t < T4: return t - T3
        return 1.0
    def cap(t):
        if t < T1: return ('Always-on', title)
        if t < T2: return ('Raise your wrist', 'the reflection sinks, the lake fades in')
        if t < T3: return ('Awake', 'the lake comes alive')
        if t < T4: return ('Lower your wrist', 'the scene fades, the reflection settles')
        return ('Always-on', title)
    def fn(t):
        amb = amb_at(t); c, s = cap(t)
        return compose(face.frame(amb, t), c, s, wrist(amb))
    return T5, fn


if __name__ == '__main__':
    import sys
    night = Face(21, 30, 'SUN  15  NOV', dict(steps=15240, bat=40, hr=64, moon=3, month=11))
    morning = Face(8, 47, 'SUN  15  NOV', dict(steps=2100, bat=91, hr=70, month=11))
    if 'check' in sys.argv:
        for i, (fc, amb, t) in enumerate(((night, 1.0, 0), (night, 0.5, 2.5), (night, 0.0, 4.0), (morning, 0.0, 3.0))):
            compose(fc.frame(amb, t), 'Raise your wrist', 'the reflection sinks, the lake fades in', wrist(amb)).save(f'/tmp/demo_check_{i}.png')
        print('check ok'); sys.exit()
    parts = []
    dur, fn = cycle(night, title='still water · night')
    render(OUT + 's1.mp4', int(dur * FPS), fn); parts.append('s1.mp4')
    # slow motion replay of the wake (x0.4)
    def slow(t):
        if t < 0.6: amb = 1.0
        elif t < 3.1: amb = 1 - (t - 0.6) / 2.5
        else: amb = 0.0
        return compose(night.frame(amb, 4.0 + t), 'Slow motion ×0.4', 'time and date stay perfectly still', wrist(amb))
    render(OUT + 's2.mp4', int(4.0 * FPS), slow); parts.append('s2.mp4')
    dur, fn = cycle(morning, hold_aod=1.6, awake=4.0, title='still water · morning')
    render(OUT + 's3.mp4', int(dur * FPS), fn); parts.append('s3.mp4')
    with open(OUT + 'list.txt', 'w') as fl:
        for p in parts: fl.write(f"file '{OUT}{p}'\n")
    tmp = OUT + 'living-lake-aod-demo.tmp.mp4'
    r = subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', OUT + 'list.txt', '-c', 'copy', '-movflags', '+faststart', tmp])
    if r.returncode == 0: os.replace(tmp, OUT + 'living-lake-aod-demo.mp4')
    print('video ok')
