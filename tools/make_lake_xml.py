"""Living Lake – res/raw/watchface.xml (Watch Face Format v2)."""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))           # tools/
_ROOT = _os.path.dirname(_HERE)                                   # repo root
_RES = _ROOT + '/watchface/src/main/res/'                         # the watch face resources
_OUT = _ROOT + '/out/'                                            # previews, videos, mock-ups (not committed)
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
A = json.load(open(os.path.join(HERE, 'art.json')))
import sys; sys.path.insert(0, HERE)
from layout15 import SIGN, PLANK, BLOCKS, BAT_TEXT_X, BOTTLE_AREA, FISH_SPOTS
OUT_XML = os.path.join(HERE, '..', 'watchface/src/main/res/raw/watchface.xml')

LH = 1.2100                                     # Inter line height (ascent + descent) in em
H = '([HOUR_0_23] + [MINUTE] / 60)'
SECF = '(([SECOND] % 60) + [MILLISECOND] / 1000)'
T = '([SECONDS_IN_DAY] + [MILLISECOND] / 1000)'
PI = '3.14159'
TAU = '6.28318'

# phase weights (0..255); night is the base layer underneath everything
A_PH = {
    'dawn': f'(({H} >= 5.5 && {H} < 8.25) ? clamp(({H} - 5.5) / 0.75, 0, 1) * 255 : 0)',
    'day': f'(({H} >= 7.5 && {H} < 17.0) ? clamp(({H} - 7.5) / 0.75, 0, 1) * 255 : 0)',
    'golden': f'(({H} >= 16.25 && {H} < 19.25) ? clamp(({H} - 16.25) / 0.75, 0, 1) * clamp((19.25 - {H}) / 0.75, 0, 1) * 255 : 0)',
}
E_NIGHT = f'{H} >= 19.0 || {H} < 5.5'
E_DAWN = f'{H} >= 5.5 && {H} < 7.5'
E_DAYP = f'{H} >= 7.5 && {H} < 16.75'
E_GOLDP = f'{H} >= 16.75 && {H} < 19.0'
E_PUREDAY = f'{H} >= 8.25 && {H} < 16.25'


def wx(*codes): return '[WEATHER.IS_AVAILABLE] == 1 && (' + ' || '.join(f'[WEATHER.CONDITION] == {c}' for c in codes) + ')'


E_STORM, E_RAIN, E_SNOW, E_FOG, E_CLOUD = wx(9), wx(4, 6, 10, 12), wx(5, 7, 11), wx(3, 13), wx(2, 14)
E_PRECIP = f'({E_RAIN}) || ({E_STORM}) || ({E_SNOW})'
E_DIM = f'({E_CLOUD}) || ({E_FOG})'
E_GOAL = '[STEP_PERCENT] >= 100'
# Tamil Nadu seasons by month
S_SUMMER, S_SW, S_NE, S_COOL = '[MONTH] >= 3 && [MONTH] <= 5', '[MONTH] >= 6 && [MONTH] <= 9', '[MONTH] >= 10', '[MONTH] <= 2'
E_NOTIF = '[UNREAD_NOTIFICATION_COUNT] > 0'

# v1.6: is the tree behind pace? (expected share of the goal grows from 7:00 to 21:00)
EXP = f'clamp(({H} - 7) / 14, 0, 1) * 100'
E_BEHIND = f'{H} >= 10 && [STEP_PERCENT] < 0.6 * {EXP} && [STEP_PERCENT] < 100'
E_TAHR = f'{H} >= 5.5 && {H} < 9.5 && [DAY_OF_YEAR] % 3 == 0'
E_CROWS = f'{H} >= 14.5 && {H} < 17.5 && [DAY_OF_YEAR] % 2 == 1'

CYAN_W = '#fffff4e2'


def esc(e): return e.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
def tf(target, value): return f'<Transform target="{target}" value="{esc(value)}"/>'


def img(name, extra='', box=None):
    x, y, w, h = (box or A[name])[:4]
    return f'<PartImage x="{x}" y="{y}" width="{w}" height="{h}">{extra}<Image resource="{name}"/></PartImage>'


def group(name, inner, x=0, y=0, w=480, h=480, extra=''):
    return f'<Group name="{name}" x="{x}" y="{y}" width="{w}" height="{h}">{extra}{inner}</Group>'


_n = [0]
def cond(pairs, default=''):
    ex = cmp_ = ''
    for n, e, body in pairs:
        _n[0] += 1; nm = f'{n}{_n[0]}'
        ex += f'<Expression name="{nm}"><![CDATA[{e}]]></Expression>'
        cmp_ += f'<Compare expression="{nm}">{body}</Compare>'
    d = f'<Default>{default}</Default>' if default else ''
    return f'<Condition><Expressions>{ex}</Expressions>{cmp_}{d}</Condition>'


def anim(name, rate, play='ON_VISIBLE', repeat=True, delay=None, thumb=None, before='THUMBNAIL', after='THUMBNAIL', extra='', box=None):
    x, y, w, h = (box or A[name])[:4]; n = A[name][4]
    th = f'<Thumbnail resource="{thumb or f"{name}_00"}"/>'
    rep = ' repeat="TRUE"' if repeat else ''
    dr = f' delayRepeat="{delay}"' if delay is not None else ''
    ims = ''.join(f'<Image resource="{name}_{i:02d}"/>' for i in range(n))
    return (f'<PartAnimatedImage x="{x}" y="{y}" width="{w}" height="{h}">{extra}{th}'
            f'<AnimationController play="{play}" beforePlaying="{before}" afterPlaying="{after}"{rep}{dr}/>'
            f'<SequenceImages loopCount="1" frameRate="{rate}">{ims}</SequenceImages></PartAnimatedImage>')


def rect(x, y, w, h, color, extra=''):
    return f'<PartDraw x="{x}" y="{y}" width="{w}" height="{h}">{extra}<Rectangle x="0" y="0" width="{w}" height="{h}"><Fill color="{color}"/></Rectangle></PartDraw>'


def text(x, y, w, size, body, family, color, align='CENTER', spacing=None, deco=None, extra=''):
    h = round(size * LH)
    ls = f' letterSpacing="{spacing}"' if spacing is not None else ''
    for d in (deco or []): body = f'{d[0]}{body}{d[1]}'
    return (f'<PartText x="{x}" y="{y}" width="{w}" height="{h}">{extra}<Text align="{align}">'
            f'<Font family="{family}" size="{size}" color="{color}"{ls}>{body}</Font></Text></PartText>')


def tmpl(fmt, *exprs): return f'<Template><![CDATA[{fmt}]]>' + ''.join(f'<Parameter expression="{esc(e)}"/>' for e in exprs) + '</Template>'


def shadow(color='#a0000000', r=5, dy=1): return (f'<Shadow color="{color}" offsetX="0" offsetY="{dy}" radius="{r}">', '</Shadow>')


def bconf(cid, on, off=None):
    """a Customize switch: content shown when on (and optionally when off)"""
    o = f'<BooleanOption id="TRUE"><Group name="{cid}_on" x="0" y="0" width="480" height="480">{on}</Group></BooleanOption>'
    if off: o += f'<BooleanOption id="FALSE"><Group name="{cid}_off" x="0" y="0" width="480" height="480">{off}</Group></BooleanOption>'
    return f'<Group name="cfg_{cid}" x="0" y="0" width="480" height="480"><BooleanConfiguration id="{cid}">{o}</BooleanConfiguration></Group>'


def phased(make):
    """night underneath, then dawn / day / golden faded in by the hour"""
    out = group('ph_night', make('night'))
    for ph in ('dawn', 'day', 'golden'):
        out += group(f'ph_{ph}', make(ph), extra=tf('alpha', A_PH[ph]))
    return out


live = []
# ---------------------------------------------------------------- sky, stars, sun and moon
live.append(phased(lambda ph: img(f'sky_{ph}')))
live.append(cond([('st', f'({E_NIGHT}) && !({E_PRECIP}) && !({E_DIM})',
                   img('stars_tw', tf('alpha', f'140 + 115 * sin({SECF} * {TAU} / 5)')))]))

SUN_T = f'(({H} - 6) / 12)'
MOON_T = f'((({H}) + 6) % 24 / 12)'
def arc_x(t): return f'(240 - 205 * cos({PI} * {t}))'
def arc_y(t): return f'(266 - 78 * pow(clamp(sin({PI} * {t}), 0, 1), 0.55))'
LOW = f'(1 - clamp(sin({PI} * {SUN_T}) * 2.2, 0, 1))'


def body(name, size, t, inner, alpha=255):
    pos = tf('x', f'{arc_x(t)} - {size // 2}') + tf('y', f'{arc_y(t)} - {size // 2}')
    return f'<Group name="{name}" x="0" y="0" width="{size}" height="{size}" alpha="{alpha}">{pos}{inner}</Group>'


def sun(alpha):
    return body('sun', 200, SUN_T, img('sun_day', tf('alpha', f'255 * (1 - {LOW})'), box=(0, 0, 200, 200))
                + img('sun_low', tf('alpha', f'255 * {LOW}'), box=(0, 0, 200, 200)), alpha)


def moon(alpha):
    inner = (img('moon_glow', tf('alpha', '(1 - cos([MOON_PHASE_TYPE] * 0.7854)) * 127'), box=(0, 0, 140, 140))
             + cond([(f'mp{k}', f'[MOON_PHASE_TYPE] == {k}', img(f'moon_{k}', box=(58, 58, 24, 24))) for k in range(8)]))
    return body('moon', 140, MOON_T, inner, alpha)


E_SUNUP = f'{H} >= 6 && {H} < 18'
live.append(cond([('sp', f'({E_SUNUP}) && !({E_PRECIP})', cond([('sd', E_DIM, sun(90))], sun(255))),
                  ('mn', f'!({E_SUNUP}) && !({E_PRECIP})', cond([('md', E_DIM, moon(90))], moon(255)))]))

# ---------------------------------------------------------------- birds (day, crossing every 2.5 min)
BIRD_P = f'clamp(({T} % 150) / 100, 0, 1)'
def phased_noimg(fmt): return phased(lambda ph: img(fmt.format(ph=ph)))


cl_drift = tf('x', f'8 * sin({T} * 0.004)')
live.append(group('clouds', cond([('crn', f'({E_RAIN}) || ({E_STORM})', cond([('crnn', E_NIGHT, img('cl_rain_night'))], img('cl_rain_day'))),
                                  ('ccl', f'({E_CLOUD}) || ({E_FOG})', phased_noimg('cl_fair_{ph}')),
                                  ('csw', S_SW, phased_noimg('cl_tower_{ph}')),
                                  ('cne', S_NE, phased_noimg('cl_fair_{ph}'))]), extra=cl_drift))

bx, by = A['birds'][:2]
flock = cond([('bd', f'{H} >= 5.75 && {H} < 18.75 && !({E_PRECIP}) && !({E_CROWS})',
               anim('birds', 16, extra=tf('x', f'-80 + {BIRD_P} * 620 - 240 + {bx}') + tf('y', f'{by} - 16 + 10 * sin({T} * 0.05)')))])

# v1.6.1: house crows on some afternoons: they fly in from the left edge, wheel once round a full circle over the hills,
# then fly off to the right and away. A pass takes about 50 s and repeats every 90 s; the three follow one another.
CW, CH_ = A['crow'][2], A['crow'][3]
CCX, CCY, CRX, CRY, CROW_P = 160, 196, 44, 13, 90


def crow(i, delay, k):
    u = f'((({T}) - {delay}) % {CROW_P})'
    e1 = f'clamp({u} / 13, 0, 1)'
    a = f'(4.71239 + {TAU} * clamp(({u} - 13) / 18, 0, 1))'
    e3 = f'clamp(({u} - 31) / 18, 0, 1)'
    X = (f'(({u} < 13) ? (-40 + {CCX + 40} * {e1}) : (({u} < 31) ? ({CCX} + {CRX} * cos({a})) '
         f': ({CCX} + 400 * (0.7 * {e3} + 0.3 * {e3} * {e3}))))')
    Y = (f'(({u} < 13) ? ({CCY - CRY - 18} + 18 * {e1}) : (({u} < 31) ? ({CCY} + {CRY} * sin({a})) '
         f': ({CCY - CRY} - 22 * {e3} * {e3})))')
    on_circle = f'({u} >= 13 && {u} < 31)'
    sc = f'(({u} < 31) ? 1 : (1 - 0.35 * {e3}))'
    w = f'({0.5 * CW * k * 0.86} * {sc})'                                   # v1.7: fixed shape (no per-frame squash) for a steadier glide
    h = f'({0.5 * CH_ * k} * {sc})'
    return (f'<PartImage x="0" y="0" width="{round(0.5 * CW * k)}" height="{round(0.5 * CH_ * k)}">'
            + tf('width', w) + tf('height', h) + tf('x', f'{X} - {w} / 2') + tf('y', f'{Y} - {h} / 2')
            + tf('angle', f'({on_circle} ? 12 * cos({a}) : 0)') + tf('alpha', f'(({u} < 49) ? 255 : 0)')
            + '<Image resource="crow"/></PartImage>')


crows = cond([('cr', f'({E_CROWS}) && !({E_PRECIP})', crow(0, 0, 1.0) + crow(1, 1.6, 0.9) + crow(2, 3.2, 0.95))])
live.append(bconf('life', flock + crows))


# ---------------------------------------------------------------- the land, the lake and the light on it
live.append(phased(lambda ph: img(f'land_{ph}')))
live.append(cond([('sdry', S_SUMMER, phased_noimg('drybank_{ph}'))]))
live.append(bconf('life', cond([('tahr', f'({E_TAHR}) && !({E_PRECIP}) && !({E_FOG})', phased_noimg('tahr_{ph}'))])))


def refl(kind, cx, alpha):
    sx = f'{cx} - 40'
    return (img(f'refl_{kind}', tf('x', sx) + tf('alpha', alpha))
            + img(f'spark_{kind}_a', tf('x', sx) + tf('alpha', f'({alpha}) * (0.5 + 0.5 * sin({SECF} * {TAU} / 3))'))
            + img(f'spark_{kind}_b', tf('x', sx) + tf('alpha', f'({alpha}) * (0.5 - 0.5 * sin({SECF} * {TAU} / 3))')))


live.append(cond([('rs', f'({E_SUNUP}) && !({E_PRECIP}) && !({E_DIM})',
                   refl('day', arc_x(SUN_T), f'255 * (1 - {LOW})') + refl('warm', arc_x(SUN_T), f'255 * {LOW}')),
                  ('rm', f'!({E_SUNUP}) && !({E_PRECIP}) && !({E_DIM})',
                   refl('moon', arc_x(MOON_T), '(1 - cos([MOON_PHASE_TYPE] * 0.7854)) * 110 + 30'))]))

# ---------------------------------------------------------------- jetty with the painted battery gauge (tap -> battery)
PAINT = {'g': ('#78e278', '[BATTERY_PERCENT] >= 50'), 'a': ('#ffbc40', '[BATTERY_PERCENT] >= 20'), 'r': ('#ff4e46', None)}
BX, BW, BH, GAP, CY = BLOCKS['x0'], BLOCKS['w'], BLOCKS['h'], BLOCKS['gap'], BLOCKS['cy']


def blocks(color):
    out = ''
    for k in range(5):
        x = BX + k * (BW + GAP)
        top = CY - BH / 2
        full = f'<PartDraw x="{x}" y="{int(top)}" width="{BW}" height="{BH + 1}"><Rectangle x="2" y="{round(top - int(top) + 2, 2)}" width="{BW - 4}" height="{BH - 4}"><Fill color="{color}"/></Rectangle></PartDraw>'
        half = f'<PartDraw x="{x}" y="{int(top)}" width="{BW}" height="{BH + 1}"><Rectangle x="2" y="{round(top - int(top) + 2 + (BH - 4) / 2, 2)}" width="{BW - 4}" height="{(BH - 4) / 2}"><Fill color="{color}"/></Rectangle></PartDraw>'
        out += cond([(f'bf{k}', f'[BATTERY_PERCENT] >= {20 * k + 15}', full), (f'bh{k}', f'[BATTERY_PERCENT] >= {20 * k + 5}', half)])
    return out


def bat_text(color):
    return text(BAT_TEXT_X, int(round(CY - 23 * LH / 2 + 0.8)), 70, 23, tmpl('%d%%', '[BATTERY_PERCENT]'), 'lake_black', color, align='START',
                deco=[('<Outline color="#ff28180e" width="2">', '</Outline>')])


paint = cond([('pr', '[BATTERY_PERCENT] < 20', blocks(PAINT['r'][0]) + bat_text(PAINT['r'][0])),
              ('pa', '[BATTERY_PERCENT] < 50', blocks(PAINT['a'][0]) + bat_text(PAINT['a'][0]))],
             blocks(PAINT['g'][0]) + bat_text(PAINT['g'][0]))
jx, jy, jw, jh = A['jetty_night']
live.append(group('jetty', phased(lambda ph: img(f'jetty_{ph}')) + paint + phased(lambda ph: img(f'jwear_{ph}'))
))

# ---------------------------------------------------------------- northeast-monsoon lotus; messages arrive as bottles (tap -> Messages)
live.append(cond([('lot', S_NE, phased_noimg('lotus_{ph}'))]))
BG = BOTTLE_AREA


def rel(name, extra=''):
    x, y, w, h = A[name][:4]
    return f'<PartImage x="{x - BG[0]}" y="{y - BG[1]}" width="{w}" height="{h}">{extra}<Image resource="{name}"/></PartImage>'


def bottle(i, ph, ph0):
    return rel(f'bottle{i}_{ph}', tf('y', f'{A[f"bottle{i}_{ph}"][1] - BG[1]} + 0.9 * sin({SECF} * {TAU} / 3 + {ph0})'))


def bottle_set(ph):
    return (bottle(0, ph, 0) + cond([('b2', '[UNREAD_NOTIFICATION_COUNT] >= 2', bottle(1, ph, 1.1))])
            + cond([('b3', '[UNREAD_NOTIFICATION_COUNT] >= 3', bottle(2, ph, 2.3))]))


rx, ry, rw, rh, _ = A['bottle_rip']
rip = anim('bottle_rip', 8, box=(rx - BG[0], ry - BG[1], rw, rh))
live.append(cond([('msg', E_NOTIF, f'<Group name="bottles" x="{BG[0]}" y="{BG[1]}" width="{BG[2]}" height="{BG[3]}">'
                                   + cond([('bnn', E_NIGHT, bottle_set('night') + f'<Group name="rip_n" x="0" y="0" width="{BG[2]}" height="{BG[3]}" alpha="90">{rip}</Group>')],
                                          bottle_set('day') + rip) + '</Group>')]))

# ---------------------------------------------------------------- the tree grows with your steps (blooms at the goal); konrai in summer
STAGE = 'clamp(floor([STEP_PERCENT] / 12.5), 0, 8)'


def stages(kind, ph, droop):
    nm = (lambda k: f'{kind}d_{ph}_{k}' if k > 0 else f'{kind}_{ph}_{k}') if droop else (lambda k: f'{kind}_{ph}_{k}')
    return cond([(f'{kind}g', E_GOAL, img(f'{kind}_{ph}_9'))] + [(f'{kind}s{k}', f'{STAGE} == {k}', img(nm(k))) for k in range(8, -1, -1)])


def tree_any(ph, pace):
    def pick(kind): return cond([('bh', E_BEHIND, stages(kind, ph, True))], stages(kind, ph, False)) if pace else stages(kind, ph, False)
    return cond([('kon', S_SUMMER, pick('treek'))], pick('tree'))


live.append(bconf('pace', phased(lambda ph: tree_any(ph, True)), phased(lambda ph: tree_any(ph, False))))
FLY = lambda i: img(f'flies_{i}', tf('alpha', f'255 * clamp(sin({SECF} * {TAU} / 4 + {i * 2.1}), 0, 1)'))
live.append(cond([('ff', f'({E_NIGHT}) && !({E_PRECIP})', FLY(0) + FLY(1) + cond([('fg', E_GOAL, FLY(2))]))]))

# ---------------------------------------------------------------- the trail sign with your steps
# (drawn after the boat, so the boat's reflection never crosses the board)

# ---------------------------------------------------------------- life on the lake
FISH_X = f'(([MINUTE] % 4 == 0) ? {FISH_SPOTS[0]} : (([MINUTE] % 4 == 1) ? {FISH_SPOTS[1]} : (([MINUTE] % 4 == 2) ? {FISH_SPOTS[2]} : {FISH_SPOTS[3]})))'
fx_, fy_ = A['fish_d'][:2]
def fish(tag): return anim(f'fish_{tag}', 15, play='ON_VISIBLE TAP', delay=9, thumb='fish_blank', before='THUMBNAIL', after='THUMBNAIL',
                           extra=tf('x', f'{FISH_X} - 220 + {fx_}'))
fishes = cond([('fv', f'!({E_STORM})', cond([('fn', E_NIGHT, fish('n')), ('fgo', f'{H} >= 16.25', fish('g'))], fish('d')))])

DUCK_P = f'(({T} % 420) / 420)'
dx_, dy_ = A['ducks_day'][:2]
def ducks(ph): return img(f'ducks_{ph}', tf('x', f'{dx_} - 98 + {DUCK_P} * 130') + tf('y', f'{dy_} + 0.7 * sin({SECF} * {TAU} / 3)')
                         + tf('alpha', f'255 * clamp((0.5 - abs({DUCK_P} - 0.5)) * 10, 0, 1)'))
duckies = cond([('dv', f'!({E_NIGHT}) && !({E_PRECIP})', cond([('dd', E_DAWN, ducks('dawn')), ('dg', E_GOLDP, ducks('golden'))], ducks('day')))])

fishing = (anim('boat_fish', 8)
           + cond([('cp', E_PUREDAY, anim('boat_catch', 12, play='TAP', repeat=False, thumb='catch_blank'))]))
boat = cond([('bv', f'!(({E_PRECIP}) && !({E_NIGHT}))',
              cond([('bdw', E_DAWN, anim('boat_rowd', 8)), ('bdy', E_DAYP, fishing), ('bgo', E_GOLDP, anim('boat_rowg', 8))],
                   anim('boat_moor', 8)))])
live.append(bconf('life', fishes + duckies + boat))

# the trail sign on the right edge: big carved number, a lantern lights it at night
steps_txt = lambda col: text(SIGN['cx'] - SIGN['W'] // 2, SIGN['top'] + 4, SIGN['W'], 28, tmpl('%s', 'numberFormat("#,##0", [STEP_COUNT])'), 'lake_semi', col,
                             deco=[shadow('#8c3c2414', 0.8, 1)])
live.append(cond([('sl', E_NIGHT, img('sign_lantern'))]) + phased(lambda ph: img(f'sign_{ph}'))
            + cond([('sn', E_NIGHT, steps_txt('#ffffe2b4'))], steps_txt('#fffff4e2')))


# v1.6: on evenings when you reached your goal, paper lanterns drift up from the lake
def lantern(i, x0, k, per=46):
    p = f'((({T}) + {i * per / 8}) % {per} / {per})'
    sz = f'({round(64 * k)} * (1 - 0.55 * {p}))'
    return (f'<PartImage x="0" y="0" width="{round(64 * k)}" height="{round(64 * k)}">' + tf('width', sz) + tf('height', sz)
            + tf('x', f'{x0} + 9 * sin({T} * 0.21 + {i}) - {sz} / 2') + tf('y', f'318 - 150 * {p} - {sz} / 2')
            + tf('alpha', f'255 * clamp({p} / 0.08, 0, 1) * clamp((1 - {p}) / 0.25, 0, 1)') + '<Image resource="lantern"/></PartImage>')


LANT = ''.join(lantern(i, x0, k) for i, (x0, k) in enumerate([(214, 1.0), (172, 0.85), (290, 0.9), (236, 0.8), (140, 0.75), (330, 0.8), (196, 0.7), (268, 0.75)]))
live.append(cond([('lan', f'({E_GOAL}) && {H} >= 18 && {H} < 23.5 && !({E_PRECIP})', LANT)]))

# ---------------------------------------------------------------- cool season: storks + pelicans (day), mist on the water in the morning
def cool_birds():
    return ''.join(group(f'cb_{ph}', img(f'coolbirds_{ph}'), extra=tf('alpha', A_PH[ph])) for ph in ('dawn', 'day', 'golden'))


live.append(cond([('cool', f'{S_COOL} && !({E_PRECIP})', bconf('life', cool_birds())
                   + img('mist_water', tf('alpha', f'255 * clamp(({H} - 5.25) / 0.75, 0, 1) * clamp((9.5 - {H}) / 1.5, 0, 1)')))]))
live.append(cond([('haze', f'{S_SUMMER} && !({E_PRECIP})', rect(0, 0, 480, 480, '#22ffd6a0', tf('alpha', A_PH['day'])))]))

# ---------------------------------------------------------------- weather
rain_l = f'<PartImage x="0" y="-360" width="480" height="720">{tf("y", f"-360 + ({SECF} * 240) % 360")}<Image resource="wx_rain"/></PartImage>'
snow_l = f'<PartImage x="0" y="-360" width="480" height="720">{tf("y", f"-360 + ({SECF} * 36) % 360")}<Image resource="wx_snow"/></PartImage>'
fog_l = img('wx_fog', tf('x', f'14 * sin({SECF} * 0.10472)'))
flash = rect(0, 0, 480, 480, '#ffffffff', tf('alpha', f'([SECOND] % 7 == 0 && ([MILLISECOND] < 120 || ([MILLISECOND] > 240 && [MILLISECOND] < 340))) ? 150 : 0'))
ripples = anim('rain_rip', 10)
live.append(cond([('ws', E_STORM, rect(0, 0, 480, 480, '#783a4250') + ripples + rain_l + flash),
                  ('wr', E_RAIN, rect(0, 0, 480, 480, '#5a4a5462') + ripples + rain_l),
                  ('wn', E_SNOW, rect(0, 0, 480, 480, '#46707884') + snow_l),
                  ('wf', E_FOG, fog_l)]))

# ---------------------------------------------------------------- heart rate: parked just after the date (inside the scene, so it fades with it)
HR_X = 318
HR_BODY = '<InlineImage resource="heart_small" width="11" height="10"/>'


def clock(color, deco, size=92, y=48, family='lake_time'):
    h24 = text(0, y, 480, size, tmpl('%s:%s', '[HOUR_0_23_Z]', '[MINUTE_Z]'), family, color, deco=deco)
    h12 = text(0, y, 480, size, tmpl('%s:%s', '[HOUR_1_12]', '[MINUTE_Z]'), family, color, deco=deco)     # 12-hour: 9:05, not 09:05
    return cond([('h24', '[IS_24_HOUR_MODE] == 1', h24)], h12)


# ---------------------------------------------------------------- the clock block: time, date, heart rate and the always-on reflection
# Awake it sits at the top. In always-on the whole block grows 22 % and glides to the centre (v4 Variant transitions),
# the heart rate fades out and the time's reflection fades in on still water underneath.
G0, GH = 30, 230                  # block group: y 30..260, pivot at its centre (y 145)
AOD_SCALE, AOD_Y = 1.22, G0 + 83  # centre moves from y 145 to 228


def V(target, value, dur=1.0, interp='EASE_IN_OUT', start=None):
    so = f' startOffset="{start}"' if start is not None else ''
    return f'<Variant mode="AMBIENT" target="{target}" value="{value}" duration="{dur}"{so} interpolation="{interp}"/>'


hr_line = lambda body: text(HR_X, 150 - G0, 90, 15, body, 'lake_text', '#e6ffffff', align='START', spacing=0.12, deco=[shadow('#a0000000', 5, 1)])
heart = (f'<Group name="hr" x="0" y="0" width="480" height="{GH}">' + V('alpha', 0, 0.6)
         + cond([('hr0', '[HEART_RATE] <= 0', hr_line(HR_BODY + '<![CDATA[ --]]>'))], hr_line(HR_BODY + tmpl(' %d', '[HEART_RATE]'))) + '</Group>')
# lake_reflect.ttf: the clock font flipped, foreshortened and rippled (same advances), so it sits exactly under the time
reflection = (f'<Group name="reflection" x="0" y="8" width="480" height="{GH}">' + V('y', 0, 1.0, 'EASE_OUT')
              + clock('#ff6c7282', None, y=147 - G0, family='lake_reflect') + '</Group>')
water = f'<PartImage x="0" y="{184 - G0}" width="480" height="64"><Image resource="aod_water"/></PartImage>'
aod_part = (f'<Group name="aod" x="0" y="0" width="480" height="{GH}" alpha="0">' + V('alpha', 255, 0.8, start=0.2) + reflection + water + '</Group>')
block = (f'<Group name="clock" x="0" y="{G0}" width="480" height="{GH}" pivotX="0.5" pivotY="0.5">'
         + V('y', AOD_Y) + V('scaleX', AOD_SCALE) + V('scaleY', AOD_SCALE)
         + aod_part
         + group('time', clock('#ffffffff', [shadow('#99000000', 7, 1)], y=48 - G0), h=GH, extra=V('alpha', 220))
         + text(0, 150 - G0, 480, 15, f'<Upper>{tmpl("%s  %s  %s", "[DAY_OF_WEEK_S]", "[DAY]", "[MONTH_S]")}</Upper>', 'lake_text', '#e6ffffff',
                spacing=0.21, deco=[shadow('#a0000000', 5, 1)], extra=V('alpha', 170))
         + bconf('hr', heart) + '</Group>')

# ---------------------------------------------------------------- tap areas: only these open anything
def tap(name, x, y, w, h, target):
    return (f'<Group name="{name}" x="{x}" y="{y}" width="{w}" height="{h}"><Launch target="{target}"/>'
            + rect(0, 0, w, h, '#00000000') + '</Group>')


taps = ('<Group name="taps" x="0" y="0" width="480" height="480">'
        + tap('tap_time', 116, 54, 248, 92, 'ALARM')
        + tap('tap_date', 150, 146, 160, 26, 'ALARM')
        + bconf('hr', tap('tap_hr', HR_X - 4, 146, 72, 28, 'HEALTH_HEART_RATE'))
        + tap('tap_battery', PLANK[0], PLANK[1], PLANK[2] - PLANK[0], PLANK[3] - PLANK[1], 'BATTERY_STATUS')
        + cond([('tmsg', E_NOTIF, tap('tap_msg', BG[0], BG[1], BG[2], PLANK[1] - BG[1], 'MESSAGE'))])
        + '</Group>')

# steps: no launch target exists for steps, so an invisible step-count complication sits on the sign; tapping it opens its app
sbx, sby, sbw, sbh = SIGN['cx'] - SIGN['W'] // 2, SIGN['top'], SIGN['W'], SIGN['H']
STEPS_SLOT = (f'<ComplicationSlot slotId="0" name="steps_sign" displayName="Steps sign (tap)" x="{sbx}" y="{sby}" width="{sbw}" height="{sbh}" '
              'supportedTypes="SHORT_TEXT RANGED_VALUE GOAL_PROGRESS EMPTY" isCustomizable="TRUE">'
              '<Variant mode="AMBIENT" target="alpha" value="0"/>'
              '<DefaultProviderPolicy defaultSystemProvider="STEP_COUNT" defaultSystemProviderType="SHORT_TEXT"/>'
              f'<BoundingBox x="0" y="0" width="{sbw}" height="{sbh}"/>'
              + ''.join(f'<Complication type="{t}">' + rect(0, 0, sbw, sbh, '#00000000') + '</Complication>' for t in ('SHORT_TEXT', 'RANGED_VALUE', 'GOAL_PROGRESS'))
              + '<Complication type="EMPTY"></Complication></ComplicationSlot>')

# v1.6: two curved bars along the left and right edges. They hold any complication you pick in Customize
# (a value fills the bar from the bottom up, text runs along the curve), and stay hidden until you do.
ER = 222                                  # bar radius
EDGES = [  # slot id, name, label, slot box, bar (WFF degrees: 0 = 12 o'clock, clockwise), text span, icon angle, accent
    (1, 'edge_left', 'Left edge bar', (12, 84, 84, 222), (254, 312), (266, 307), 260, '#ffffd66e'),     # boxes kept clear of the
    (2, 'edge_right', 'Right edge bar', (388, 84, 80, 222), (48, 106), (60, 100), 54, '#ff78c4ff'),    # heart-rate + bottle taps
]


def edge_slot(sid, name, label, box, bar, span, icon_a, accent):
    import math
    bx_, by_, bw_, bh_ = box; a0, a1 = bar
    left = a0 > 180
    def arc(start, end, color, extra=''):
        return (f'<PartDraw x="{-bx_}" y="{-by_}" width="480" height="480"><Arc centerX="240" centerY="240" width="{2 * ER}" height="{2 * ER}" '
                f'startAngle="{start}" endAngle="{end}">{extra}<Stroke color="{color}" thickness="3" cap="ROUND"/></Arc></PartDraw>')
    def fill(frac):
        if left: return arc(a0, a0, accent, tf('endAngle', f'{a0} + {a1 - a0} * {frac}'))           # fills upwards (clockwise on the left)
        return arc(a1, a1, accent, tf('startAngle', f'{a1} - {a1 - a0} * {frac}'))                     # fills upwards on the right
    words = lambda body: (f'<PartText x="{-bx_}" y="{-by_}" width="480" height="480"><TextCircular centerX="240" centerY="240" width="412" height="412" '
                          f'startAngle="{span[0]}" endAngle="{span[1]}" direction="CLOCKWISE" align="CENTER">'
                          f'<Font family="lake_text" size="13" color="#f0ffffff" letterSpacing="0.1"><Shadow color="#c0000000" offsetX="0" offsetY="1" radius="4">{body}</Shadow></Font></TextCircular></PartText>')
    ix = 240 + 207 * math.sin(math.radians(icon_a)) - bx_; iy = 240 - 207 * math.cos(math.radians(icon_a)) - by_
    icon = (f'<PartImage x="{round(ix - 7)}" y="{round(iy - 7)}" width="14" height="14" tintColor="#ffffffff">'
            f'<Image resource="[COMPLICATION.MONOCHROMATIC_IMAGE]"/></PartImage>')
    t2 = lambda: words('<Upper>' + tmpl('%s  %s', '[COMPLICATION.TITLE]', '[COMPLICATION.TEXT]') + '</Upper>')
    ranged = f'clamp(([COMPLICATION.RANGED_VALUE_VALUE] - [COMPLICATION.RANGED_VALUE_MIN]) / clamp([COMPLICATION.RANGED_VALUE_MAX] - [COMPLICATION.RANGED_VALUE_MIN], 0.001, 1000000000), 0, 1)'
    goal = 'clamp([COMPLICATION.GOAL_PROGRESS_VALUE] / clamp([COMPLICATION.GOAL_PROGRESS_TARGET_VALUE], 0.001, 1000000000), 0, 1)'
    track = arc(a0, a1, '#55ffffff'); faint = arc(a0, a1, '#30ffffff')
    return (f'<ComplicationSlot slotId="{sid}" name="{name}" displayName="{label}" x="{bx_}" y="{by_}" width="{bw_}" height="{bh_}" '
            'supportedTypes="RANGED_VALUE GOAL_PROGRESS SHORT_TEXT EMPTY" isCustomizable="TRUE">'
            '<Variant mode="AMBIENT" target="alpha" value="0" duration="0.6" interpolation="EASE_IN_OUT"/>'
            '<DefaultProviderPolicy defaultSystemProvider="EMPTY" defaultSystemProviderType="EMPTY"/>'
            f'<BoundingBox x="0" y="0" width="{bw_}" height="{bh_}"/>'
            f'<Complication type="RANGED_VALUE">{track}{fill(ranged)}{t2()}{icon}</Complication>'
            f'<Complication type="GOAL_PROGRESS">{track}{fill(goal)}{t2()}{icon}</Complication>'
            f'<Complication type="SHORT_TEXT">{faint}{t2()}{icon}</Complication>'
            '<Complication type="EMPTY"></Complication></ComplicationSlot>')


EDGE_SLOTS = ''.join(edge_slot(*e) for e in EDGES)
CONFIGS = ('<UserConfigurations>'
           '<BooleanConfiguration id="hr" displayName="Heart rate" defaultValue="TRUE"/>'
           '<BooleanConfiguration id="life" displayName="Lake life and birds" defaultValue="TRUE"/>'
           '<BooleanConfiguration id="pace" displayName="Tree droops when behind on steps" defaultValue="TRUE"/>'
           '</UserConfigurations>')

xml = f'''<?xml version="1.0" encoding="utf-8"?>
<!-- Living Lake v1.7: a Nilgiri hill lake with Tamil Nadu seasons; that follows the real sun, moon and weather. The tree grows with your steps,
     the jetty paint shows the battery, the date line carries your heart rate. -->
<WatchFace width="480" height="480">
  <Metadata key="CLOCK_TYPE" value="DIGITAL"/>
  <Metadata key="PREVIEW_TIME" value="12:20:00"/>
  {CONFIGS}
  <Scene backgroundColor="#ff000000">
    <Group name="interactive" x="0" y="0" width="480" height="480" alpha="255">
      <Variant mode="AMBIENT" target="alpha" value="0" duration="1.0" interpolation="EASE_IN_OUT"/>
      {"".join(live)}
    </Group>
    {block}
    {taps}
    {STEPS_SLOT}
    {EDGE_SLOTS}
  </Scene>
</WatchFace>
'''
os.makedirs(os.path.dirname(OUT_XML), exist_ok=True)
open(OUT_XML, 'w').write(xml)
print('written', len(xml))
