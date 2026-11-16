"""Living lake mock: stills (noon / golden hour / night) + a 6 s clip of the noon lake."""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))           # tools/
_ROOT = _os.path.dirname(_HERE)                                   # repo root
_RES = _ROOT + '/watchface/src/main/res/'                         # the watch face resources
_OUT = _ROOT + '/out/'                                            # previews, videos, mock-ups (not committed)
import math, subprocess, sys
sys.path.insert(0, _HERE)
from PIL import Image, ImageDraw, ImageFont
import combomock as CM, landmock as LM, waterlife as WL

BANK = 396


def base(h, s, far_fn=None):
    img, night = CM.scene(h, s, bank_y=BANK, tree_x=376, far_fn=far_fn)
    return img, night, CM.phase(h)


def statics(img, K, ph, t=0):
    n, g = ph == 'night', ph in ('golden', 'dawn')
    WL.jetty(img, K, night=n, golden=g)
    WL.reeds(img, K, 418, 470, BANK - 16, seed=2, night=n, golden=g, t=t)
    WL.reeds(img, K, 112, 150, BANK - 6, seed=5, night=n, golden=g, t=t)


def hud_layer(hhmm, steps, night):
    o = LM.ov(); LM.hud(o, hhmm, 'WED  11  NOV', steps, 15000, 72, 82, night, (120, 220, 255))
    return o


def still(h, hhmm, steps, s, life):
    img, night, ph = base(h, s); K = LM.SS
    statics(img, K, ph)
    life(img, K, ph)
    img.alpha_composite(hud_layer(hhmm, steps, night))
    return LM.circle(img)


def noon_life(img, K, ph, t=2.0):
    WL.fish_jump(img, K, 300, 336, 0.45)
    WL.boat(img, K, 206, 338, t, 'fish')
    WL.duck(img, K, 150, 372, t, 0); WL.duck(img, K, 170, 377, t, 1)


def golden_life(img, K, ph, t=1.0):
    WL.boat(img, K, 220, 346, t, 'row', golden=True)
    WL.fish_jump(img, K, 312, 330, 0.5, golden=True, big=0.9)
    WL.duck(img, K, 150, 374, t, 0, golden=True)


def night_life(img, K, ph, t=1.0):
    WL.boat(img, K, 132, 366, t, 'moored', night=True)
    WL.fish_jump(img, K, 104, 330, 0.42, night=True, big=0.9)
    WL.fireflies(img, K, t)


if __name__ == '__main__':
    if 'clip' not in sys.argv:
        sheet = Image.new('RGB', (480 * 3 + 48, 480 + 70), (14, 14, 18))
        dr = ImageDraw.Draw(sheet); LF = ImageFont.truetype(LM.FT + 'Inter-SemiBold.otf', 22)
        for i, (h, hhmm, steps, s, life, lab) in enumerate(((12.33, '12:20', 6900, 0.46, noon_life, 'Noon · fishing'),
                                                              (17.33, '17:20', 12100, 0.8, golden_life, 'Golden hour · rowing home'),
                                                              (21.5, '21:30', 15240, 1.02, night_life, 'Night · moored, lantern on'))):
            out = still(h, hhmm, steps, s, life)
            sheet.paste(out, (12 + i * 492, 12), out)
            tw = dr.textlength(lab, font=LF); dr.text((12 + i * 492 + 240 - tw / 2, 500), lab, font=LF, fill=(214, 220, 200))
        sheet.save(_OUT + 'mockups/lake-life.png'); print('stills ok')
    else:
        # 6 s noon clip: the boat bobs, the float gets a bite, two fish jump, ducks glide
        OUTPX, K = 720, 3
        img0, night, ph = base(12.33, 0.46)
        bg = img0.resize((480 * K, 480 * K), Image.LANCZOS)
        statics(bg, K, ph)
        hud = hud_layer('12:20', 6900, False).resize((480 * K, 480 * K), Image.LANCZOS)
        mask = Image.new('L', (OUTPX, OUTPX), 0); ImageDraw.Draw(mask).ellipse([0, 0, OUTPX - 1, OUTPX - 1], fill=255)
        tmp = _OUT + 'mockups/lake-clip.tmp.mp4'
        ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{OUTPX}x{OUTPX}', '-r', '30', '-i', '-',
                               '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', tmp], stdin=subprocess.PIPE)
        ztmp = _OUT + 'mockups/lake-zoom.tmp.mp4'
        zz = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1080x360', '-r', '30', '-i', '-',
                               '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', ztmp], stdin=subprocess.PIPE)
        FPS, DUR = 30, 6.0
        for f in range(int(FPS * DUR)):
            t = f / FPS
            im = bg.copy()
            WL.fish_jump(im, K, 296, 336, (t - 0.6) / 1.1)
            WL.fish_jump(im, K, 132, 330, (t - 3.3) / 1.1, big=0.85)
            WL.boat(im, K, 206, 338, t, 'fish')
            WL.duck(im, K, 140 + 4 * t, 372, t, 0); WL.duck(im, K, 160 + 4 * t, 377, t, 1)
            im.alpha_composite(hud)
            fr = Image.new('RGB', (OUTPX, OUTPX), (0, 0, 0))
            fr.paste(im.resize((OUTPX, OUTPX), Image.LANCZOS).convert('RGB'), (0, 0), mask)
            ff.stdin.write(fr.tobytes())
            zz.stdin.write(im.crop((60 * K, 300 * K, 420 * K, 420 * K)).resize((1080, 360), Image.LANCZOS).convert('RGB').tobytes())
        ff.stdin.close(); rc = ff.wait()
        zz.stdin.close(); rz = zz.wait()
        if rz == 0:
            import os; os.replace(ztmp, _OUT + 'mockups/lake-life-zoom.mp4'); print('zoom ok')
        if rc == 0:
            import os; os.replace(tmp, _OUT + 'mockups/lake-life-clip.mp4'); print('clip ok')
