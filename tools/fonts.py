"""Inter (SIL OFL) -> subset TrueType fonts for the watch face (CFF outlines converted to quadratic glyf)."""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))           # tools/
_ROOT = _os.path.dirname(_HERE)                                   # repo root
_RES = _ROOT + '/watchface/src/main/res/'                         # the watch face resources
_OUT = _ROOT + '/out/'                                            # previews, videos, mock-ups (not committed)
from fontTools import subset
from fontTools.ttLib import TTFont, newTable
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen

SRC = _HERE + '/fonts/inter/'
OUT = _RES + 'font/'
FONTS = {'lake_time': 'InterDisplay-Light.otf', 'lake_text': 'Inter-Medium.otf', 'lake_semi': 'InterDisplay-SemiBold.otf', 'lake_black': 'InterDisplay-Black.otf'}
UNI = list(range(0x20, 0x7F)) + list(range(0xA0, 0x180)) + list(range(0x370, 0x3D0)) + list(range(0x400, 0x460)) + [0xB7, 0x2013, 0x2014, 0x2019, 0x2665]


def otf_to_ttf(f):
    order = f.getGlyphOrder(); gs = f.getGlyphSet()
    glyphs = {}
    for g in order:
        tt = TTGlyphPen(gs); gs[g].draw(Cu2QuPen(tt, 1.0, reverse_direction=True)); glyphs[g] = tt.glyph()
    f['loca'] = newTable('loca'); f['glyf'] = glyf = newTable('glyf')
    glyf.glyphOrder = order; glyf.glyphs = glyphs
    del f['CFF ']
    for t in ('VORG', 'CFF2'):
        if t in f: del f[t]
    glyf.compile(f)
    mx = newTable('maxp'); mx.tableVersion = 0x00010000
    for k in ('maxZones', 'maxTwilightPoints', 'maxStorage', 'maxFunctionDefs', 'maxInstructionDefs', 'maxStackElements', 'maxSizeOfInstructions', 'maxComponentElements'):
        setattr(mx, k, 1 if k == 'maxZones' else 0)
    f['maxp'] = mx; mx.compile(f)
    post = f['post']; post.formatType = 2.0; post.extraNames = []; post.mapping = {}; post.glyphOrder = order
    f.sfntVersion = '\x00\x01\x00\x00'
    if 'head' in f: f['head'].glyphDataFormat = 0


for name, src in FONTS.items():
    f = TTFont(SRC + src)
    opts = subset.Options(); opts.layout_features = ['kern', 'liga', 'tnum', 'case']; opts.name_IDs = ['*']; opts.notdef_outline = True
    s = subset.Subsetter(opts); s.populate(unicodes=UNI); s.subset(f)
    otf_to_ttf(f)
    f.save(OUT + name + '.ttf')
    g = TTFont(OUT + name + '.ttf'); print(name, 'glyf' in g, len(g.getGlyphOrder()), round(len(open(OUT + name + '.ttf', 'rb').read()) / 1024), 'KB')
