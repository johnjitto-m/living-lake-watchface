"""v1.5 layout: steps sign on the right edge, tree to its left, a bigger boat on the right water, life on the left water."""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))           # tools/
_ROOT = _os.path.dirname(_HERE)                                   # repo root
_RES = _ROOT + '/watchface/src/main/res/'                         # the watch face resources
_OUT = _ROOT + '/out/'                                            # previews, videos, mock-ups (not committed)
TREE_X = 252
SIGN = dict(cx=368, top=344, W=112, H=42)          # board 312-424 x 344-386, legs to 402
PLANK = (40, 339, 178, 371)                         # battery plank on the jetty front
BLOCKS = dict(x0=50, w=10, h=19, gap=3, cy=355)     # five painted blocks
BAT_TEXT_X = 119
BOAT_SC = 1.3
FISH_AT, ROW_AT, MOOR_AT = (350, 312), (342, 316), (346, 320)
BOTTLES = [(98, 326, -0.5, 1.3, 0.0), (126, 334, 0.4, 1.05, 0.7), (70, 334, -0.9, 1.0, 1.3)]
BOTTLE_AREA = (48, 306, 104, 44)
FISH_SPOTS = (92, 150, 424, 122)
DUCK_Y = 320                                        # ducks drift across the open middle water
