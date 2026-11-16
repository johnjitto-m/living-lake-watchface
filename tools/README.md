# Tools

Python scripts that draw every image, build the fonts and write the watch face XML. You only need them to change the artwork or the behaviour; the finished watch face is already in `watchface/src/main/`.

Requirements: Python 3.10+, `pip install pillow numpy fonttools` (and `xmlschema` if you want to validate). Everything is drawn at 4x and scaled down to the 480 x 480 face.

## Rebuild everything (about 40 seconds)

Run from the repo root, in this order:

```bash
python3 tools/fonts.py            # Inter (tools/fonts/inter) -> subset TrueType fonts lake_*.ttf
python3 tools/reflect_font.py     # lake_reflect.ttf: the clock font mirrored and rippled for the always-on reflection
python3 tools/lake_art.py         # sky, land, sun, moon, water light, jetty, sign, base trees, weather, always-on water
python3 tools/lake_art2.py        # Nilgiri hills, clouds, seasons (konrai, lotus, storks), message bottles
python3 tools/lake_anim.py        # boat, catch, jumping fish, ducks (animation frames)
python3 tools/lake_art3.py        # bigger and drooping trees, tahr, crow, lantern, smooth bird flock
python3 tools/make_lake_xml.py    # res/raw/watchface.xml
python3 tools/clean_unused.py     # drop images the XML no longer uses
python3 tools/lake_preview.py     # renders previews into out/preview/ (and res/drawable/preview.png)
```

Each art script takes optional section names, e.g. `python3 tools/lake_art3.py flock` re-renders only the bird flock. Placements of every image are kept in `tools/art.json`.

## Files

| File | What it does |
|---|---|
| `layout15.py` | Positions of the sign, battery plank, tree, boat, bottles, fish and ducks |
| `make_lake_xml.py` | Writes the whole face: scene layers, phase crossfades, animations, tap areas, the clock block, Customize switches, complication slots |
| `lake_preview.py` | A Python stand-in for the watch renderer, used for previews, screenshots and videos |
| `landmock.py`, `waterlife.py`, `combomock.py`, `clouds2.py`, `signsteps.py`, `hroptions.py`, `demo4.py`, `demo_tn.py`, `lakelife.py`, `batjetty*.py` | Drawing helpers (hills, trees, water, boat, ducks, clouds, sign, jetty, birds) |
| `demo16.py`, `demo_aod2.py`, `aod_v13.py`, `demo_aod_video.py`, `hrmock.py` | Drawing helpers and the always-on transition used by the previews |

## Build the APK

```bash
KEYSTORE=~/my-key.jks KEY_ALIAS=me KS_PASS=secret tools/build_apk.sh
```

Uses `aapt`, `zipalign` and `apksigner` from the Android build tools (`ANDROID_JAR` defaults to the Debian/Ubuntu `android-sdk` path). Sign with **your own** key; the release APK is signed with the author's key, so an APK you build can't update it in place (uninstall first).

Validate the XML against the official schema in [google/watchface](https://github.com/google/watchface) (`specification/documents/4/watchface.xsd`).
