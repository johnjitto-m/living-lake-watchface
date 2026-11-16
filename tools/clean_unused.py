"""Remove images in res/drawable that the watch face XML no longer uses (keeps preview.png for the watch face picker)."""
import os, re
HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, '..', 'watchface', 'src', 'main', 'res')
xml = open(os.path.join(RES, 'raw', 'watchface.xml')).read()
used = set(re.findall(r'resource="([^"\[]+)"', xml)) | {'preview'}
gone = []
for f in sorted(os.listdir(os.path.join(RES, 'drawable'))):
    if os.path.splitext(f)[0] not in used:
        os.remove(os.path.join(RES, 'drawable', f)); gone.append(f)
print('removed', len(gone), 'unused images', gone[:12])
