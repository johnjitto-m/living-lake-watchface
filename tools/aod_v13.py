"""Living Lake v1.3 previews: the still-water always-on screen and the native ambient transition (simulated)."""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))           # tools/
_ROOT = _os.path.dirname(_HERE)                                   # repo root
_RES = _ROOT + '/watchface/src/main/res/'                         # the watch face resources
_OUT = _ROOT + '/out/'                                            # previews, videos, mock-ups (not committed)
import os, subprocess, sys
sys.path.insert(0, _HERE)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import lake_preview as LP

OUT = _OUT + 'preview/'


def ease_io(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def ease_out(x): x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 2


def layer(fn):
    l = Image.new('RGBA', (480, 480), (0, 0, 0, 0)); fn(l); return l


def fade(l, a):
    l = l.copy(); l.putalpha(l.split()[3].point(lambda v: int(v * max(0.0, min(1.0, a))))); return l


def reflection(hhmm, dy=0):
    l = Image.new('RGBA', (480, 480), (0, 0, 0, 0))
    LP.hud_text(l, lambda q: LP.text_layer(q, 0, 147 + dy, 480, 92, hhmm, 'lake_reflect', (0x6c, 0x72, 0x82, 255)))
    l.alpha_composite(LP.L('aod_water'), (0, 184 + dy) if False else (0, 184))
    return l


def hud_time(hhmm): return layer(lambda l: LP.hud_text(l, lambda q: LP.text_layer(q, 0, 48, 480, 92, hhmm, 'lake_time', (255, 255, 255, 255)), shadow=(7, 0.6, 1)))
def hud_date(txt): return layer(lambda l: LP.hud_text(l, lambda q: LP.text_layer(q, 0, 150, 480, 15, txt, 'lake_text', (255, 255, 255, 230), spacing=0.21), shadow=(5, 0.63, 1)))


def hud_hr(hr):
    def f(l):
        def g(q):
            q.alpha_composite(LP.L('heart_small').resize((44, 40), Image.LANCZOS), (318 * 4, int(150 * 4 + 15 * 4 * 0.64 - 20)))
            ImageDraw.Draw(q).text(((318 + 14) * 4, 150 * 4), str(hr), font=LP.F('lake_text', 15), fill=(255, 255, 255, 230))
        LP.hud_text(l, g, shadow=(5, 0.63, 1))
    return layer(f)


def frame(scene, hhmm, date, hr, amb):
    """amb: 0 = awake, 1 = always-on (the Variant progress)"""
    a_scene = 1 - ease_io(amb)
    a_aod = ease_io((amb - 0.2) / 0.8)
    dy = round(8 * (1 - ease_out(amb)))
    im = Image.new('RGBA', (480, 480), (0, 0, 0, 255))
    im.alpha_composite(fade(scene, a_scene))
    im.alpha_composite(fade(hud_hr(hr), a_scene))
    if a_aod > 0: im.alpha_composite(fade(reflection(hhmm, dy), a_aod))
    im.alpha_composite(fade(hud_time(hhmm), 1 - ease_io(amb) * (1 - 220 / 255)))
    im.alpha_composite(fade(hud_date(date), 1 - ease_io(amb) * (1 - 170 / 255)))
    return LP.circle(im)


if __name__ == '__main__':
    # stills
    sheet = Image.new('RGB', (3 * 492 + 12, 492 + 12), (14, 14, 18))
    for i, (hhmm, date) in enumerate((('21:30', 'SUN  15  NOV'), ('08:47', 'MON  16  NOV'), ('12:05', 'THU  1  JAN'))):
        im = frame(Image.new('RGBA', (480, 480), (0, 0, 0, 0)), hhmm, date, 72, 1.0)
        sheet.paste(im, (12 + i * 492, 12), im)
        if i == 0: im.save(OUT + 'aod-still-water.png')
    sheet.save(OUT + 'aod-still-water-sheet.png')
    # clip: always-on -> wake -> always-on, at night and in the morning (1 s transitions, as the watch allows up to ~1 s)
    FPS, PX = 30, 720
    mask = Image.new('L', (PX, PX), 0); ImageDraw.Draw(mask).ellipse([0, 0, PX - 1, PX - 1], fill=255)
    tmp = OUT + 'aod-v13.tmp.mp4'
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{PX}x{PX}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', tmp], stdin=subprocess.PIPE)
    for hh, mm, date, kw in ((21, 30, 'SUN  15  NOV', dict(steps=15240, bat=40, hr=64, moon=3, month=11)),
                            (8, 47, 'MON  16  NOV', dict(steps=2100, bat=91, hr=70, month=11))):
        hhmm = f'{hh:02d}:{mm:02d}'
        scene = LP.state(hh, mm, hud=False, **kw)
        cache = {}
        for f in range(int(FPS * 5.0)):
            t = f / FPS
            amb = 1.0 if t < 1.0 else (1 - (t - 1.0) if t < 2.0 else (0.0 if t < 3.6 else min(1.0, t - 3.6)))
            key = round(amb, 3)
            if key not in cache: cache[key] = frame(scene, hhmm, date, kw['hr'], amb).resize((PX, PX), Image.LANCZOS).convert('RGB')
            out = Image.new('RGB', (PX, PX), (0, 0, 0)); out.paste(cache[key], (0, 0), mask)
            ff.stdin.write(out.tobytes())
    ff.stdin.close()
    if ff.wait() == 0: os.replace(tmp, OUT + 'aod-v13-transition.mp4')
    strip = Image.new('RGB', (5 * 300, 300), (0, 0, 0))
    scene = LP.state(21, 30, hud=False, steps=15240, bat=40, hr=64, moon=3, month=11)
    for i, amb in enumerate((1.0, 0.75, 0.5, 0.25, 0.0)):
        strip.paste(frame(scene, '21:30', 'SUN  15  NOV', 64, amb).resize((300, 300), Image.LANCZOS).convert('RGB'), (i * 300, 0))
    strip.save(OUT + 'aod-v13-strip.png'); print('ok')
