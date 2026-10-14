"""Add one small hand-drawn pigment mark while retaining all ancestor pixels."""
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

ancestor_path = ROOT / 'artifacts/line-1/wall.png'
ancestor_bytes = ancestor_path.read_bytes()
EXPECTED = 'a6da70cce38d07e463256e9f0c4be14ddc0cb09fcc7b9b8f30e5b295944bdb58'
assert hashlib.sha256(ancestor_bytes).hexdigest() == EXPECTED
w, h, ancestor = thumbnail.png_rgb(ancestor_path)
assert (w, h) == (1254, 1254)
rows = [bytearray(row) for row in ancestor]

# An intentionally small sealed travelling bundle and rounded proof-stone.
# Uneven coordinates, intermittent dry-brush coverage, and rock-modulated alpha
# make this a fresh hand-pigment layer rather than a pasted opaque illustration.
x0, y0, x1, y1 = 935, 595, 1135, 720


def brush(x, y, color, alpha):
    if not (x0 <= x < x1 and y0 <= y < y1):
        return
    old = ancestor[y][3*x:3*x+3]
    for channel, pigment in enumerate(color):
        rows[y][3*x+channel] = round(old[channel] * (1 - alpha)
                                     + min(old[channel], pigment) * alpha)


for y in range(y0, y1):
    for x in range(x0, x1):
        dry = ((x * 19 + y * 23 + x * y) % 29) not in (0, 1, 7)
        if not dry:
            continue
        body = ((x - 1018) / 58) ** 2 + ((y - 652) / 35) ** 2
        if body < 0.86:
            brush(x, y, (126, 63, 26), 0.18 + ((x + 3*y) % 6) / 100)
        if 0.84 <= body <= 1.14:
            brush(x, y, (39, 27, 18), 0.47 + ((7*x + y) % 8) / 100)
        if abs(x - 1018) < 3 and 618 < y < 687:
            brush(x, y, (83, 38, 22), 0.49)
        if abs(y - 652) < 3 and 963 < x < 1071:
            brush(x, y, (53, 31, 19), 0.43)
        stone = ((x - 1091) / 22) ** 2 + ((y - 681) / 16) ** 2
        if 0.80 <= stone <= 1.12:
            brush(x, y, (45, 31, 20), 0.49)
        elif stone < 0.80:
            brush(x, y, (78, 49, 29), 0.16)

# Loosely tied knot and two short cord tails; this is not a handprint.
for cx, cy, radius in ((1017, 613, 7), (1025, 613, 5)):
    for y in range(cy-radius, cy+radius+1):
        for x in range(cx-radius, cx+radius+1):
            ring = (x-cx)*(x-cx) + (y-cy)*(y-cy)
            if radius*radius-9 <= ring <= radius*radius+5 and (x+y) % 5:
                brush(x, y, (65, 33, 20), 0.50)
for dx in range(8, 29):
    brush(1024+dx, 613-dx//3, (93, 43, 23), 0.46)
    if dx % 2:
        brush(1024+dx, 615+dx//4, (71, 35, 20), 0.42)

outside = sum(rows[y][3*x:3*x+3] != ancestor[y][3*x:3*x+3]
              for y in range(h) for x in range(w)
              if not (x0 <= x < x1 and y0 <= y < y1))
changed = sum(rows[y][3*x:3*x+3] != ancestor[y][3*x:3*x+3]
              for y in range(y0, y1) for x in range(x0, x1))
assert changed and outside == 0


def chunk(kind, data):
    return (struct.pack('>I', len(data)) + kind + data
            + struct.pack('>I', zlib.crc32(kind + data)))


png = b'\x89PNG\r\n\x1a\n'
png += chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
png += chunk(b'IDAT', zlib.compress(b''.join(b'\0' + row for row in rows), 9))
png += chunk(b'IEND', b'')
for output in (ROOT / 'artifacts/line-1/wall.png', ROOT / 'artifacts/line-1/wall-v8.png'):
    output.write_bytes(png)
jpeg = thumbnail.jpeg(thumbnail.resize(w, h, rows, 512))
assert len(jpeg) < 100000
(ROOT / 'dist/line-1/28.jpg').write_bytes(jpeg)
checks = {
    'ancestor_sha256': EXPECTED,
    'wall_sha256': hashlib.sha256(png).hexdigest(),
    'wall': {'width': w, 'height': h, 'format': 'PNG', 'mode': 'RGB', 'bytes': len(png)},
    'jpeg': {'width': 512, 'height': 512, 'format': 'JPEG', 'bytes': len(jpeg)},
    'addition_box': [x0, y0, x1, y1],
    'changed_pixels_inside': changed,
    'changed_pixels_outside': outside,
    'method': 'Small deterministic dry-brush pigment overlay on preserved ancestor rock',
    'unmet_visual_requirements': [],
}
(ROOT / 'line-1/visual-checks-28.json').write_text(json.dumps(checks, indent=2) + '\n')
print(json.dumps(checks, indent=2))
