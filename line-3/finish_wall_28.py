"""Artifact assembly: retain the generated addition and exact ancestor pixels.

Run once with record-27 wall.png and the generated wall-v8.png in place.
Uses only committed shared thumbnail helper and Python's standard library.
This is not a dependency of Code Delta.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import zlib

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('thumbnail', ROOT / 'shared/wall-thumbnail/thumbnail.py')
thumbnail = importlib.util.module_from_spec(spec)
spec.loader.exec_module(thumbnail)
ancestor_path = ROOT / 'artifacts/line-3/wall.png'
generated_path = ROOT / 'artifacts/line-3/wall-v8.png'
ancestor_bytes = ancestor_path.read_bytes()
generated_bytes = generated_path.read_bytes()
assert hashlib.sha256(ancestor_bytes).hexdigest() == '1369fe961005002e308a48326693ded86cb30834a9befa5b7cb4d721fd8bb175'
width, height, ancestor = thumbnail.png_rgb(ancestor_path)
gw, gh, generated = thumbnail.png_rgb(generated_path)
assert (width, height) == (gw, gh) == (1254, 1254)
# New head and pebble trails only. The notch excludes the inherited head below/right.
boxes = [(185, 95, 370, 250), (370, 110, 515, 219)]
rows = [bytearray(row) for row in ancestor]
for x0, y0, x1, y1 in boxes:
    for y in range(y0, y1):
        for x in range(x0, x1):
            # No seam at the shared edge; fade only outer edges of the two-part patch.
            horizontal = min(x-185, 514-x)
            vertical = min(y-y0, y1-1-y)
            alpha = min(1, min(horizontal, vertical) / 5)
            for c in range(3):
                rows[y][3*x+c] = round(ancestor[y][3*x+c]*(1-alpha) + generated[y][3*x+c]*alpha)
inside = outside = 0
for y in range(height):
    for x in range(width):
        if rows[y][3*x:3*x+3] != ancestor[y][3*x:3*x+3]:
            if any(x0 <= x < x1 and y0 <= y < y1 for x0, y0, x1, y1 in boxes):
                inside += 1
            else:
                outside += 1
assert inside > 0 and outside == 0


def chunk(kind, data):
    return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind+data))


png = b'\x89PNG\r\n\x1a\n'
png += chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0))
png += chunk(b'IDAT', zlib.compress(b''.join(b'\0'+row for row in rows), 9))
png += chunk(b'IEND', b'')
generated_path.write_bytes(png)
ancestor_path.write_bytes(png)
jpeg = thumbnail.jpeg(thumbnail.resize(width, height, rows, 512))
assert len(jpeg) < 100_000
with (ROOT / 'dist/line-3/28.jpg').open('xb') as stream:
    stream.write(jpeg)
report = {'ancestor_sha256': hashlib.sha256(ancestor_bytes).hexdigest(),
          'generated_before_assembly_sha256': hashlib.sha256(generated_bytes).hexdigest(),
          'wall_sha256': hashlib.sha256(png).hexdigest(), 'format': 'PNG',
          'dimensions': [width, height], 'mode': 'RGB', 'wall_bytes': len(png),
          'addition_boxes_xyxy': boxes, 'changed_pixels_inside_boxes': inside,
          'changed_pixels_outside_boxes': outside,
          'thumbnail': {'path': 'dist/line-3/28.jpg', 'format': 'JPEG',
                        'dimensions': [512, 512], 'bytes': len(jpeg),
                        'sha256': hashlib.sha256(jpeg).hexdigest()},
          'manual_review_pending': True}
(ROOT / 'line-3/visual-checks-28.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report, indent=2))
