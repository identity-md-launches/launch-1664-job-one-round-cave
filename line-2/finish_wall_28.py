#!/usr/bin/env python3
"""Consume generated RGBA pigment from stdin; preserve ancestors outside one addition."""
import base64
import hashlib
import json
from pathlib import Path
import sys
import finish_wall_26 as imageops
ROOT = Path(__file__).resolve().parents[1]
WALL = ROOT / 'artifacts/line-2/wall.png'
SOURCE_SHA256 = '53bd236f05aa1ccd5811f243431c024c9f6377ea76a93c9f2b948564141cea14'
PLACEMENT = (340, 170, 160, 90)
PROMPT = 'Two irregular charcoal arcs enclose a red-ochre pebble with a yellow-ochre sun-ray fan; isolated transparent worn pigment, no text or hands.'


def main():
    source = WALL.read_bytes()
    assert hashlib.sha256(source).hexdigest() == SOURCE_SHA256
    width, height, channels, base = imageops.decode(source)
    assert (width, height, channels) == (1254, 1254, 3)
    chunks = []
    for line in sys.stdin.buffer:
        if line.strip() == b'END':
            break
        chunks.append(line.strip())
    else:
        raise ValueError('missing END marker')
    mark = imageops.decode(base64.b64decode(b''.join(chunks), validate=True))
    imageops.PLACE_X, imageops.PLACE_Y, imageops.PLACE_W, imageops.PLACE_H = PLACEMENT
    result, bounds = imageops.composite(base, mark)
    x, y, w, h = PLACEMENT
    for row, (old, new) in enumerate(zip(base, result)):
        if not y <= row < y+h:
            assert old == new
        else:
            assert old[:x*3] == new[:x*3]
            assert old[(x+w)*3:] == new[(x+w)*3:]
    output = imageops.encode(width, height, result)
    WALL.write_bytes(output)
    (WALL.parent / 'wall-v8.png').write_bytes(output)
    changed = sum(old[i:i+3] != new[i:i+3] for old,new in zip(base,result)
                  for i in range(0,len(old),3))
    checks = {'source_sha256': SOURCE_SHA256, 'output_sha256': hashlib.sha256(output).hexdigest(),
              'format':'PNG', 'dimensions':[width,height], 'placement':PLACEMENT,
              'changed_pixels':changed, 'outside_placement_unchanged':True,
              'insert_alpha_bounds':bounds, 'prompt_summary':PROMPT,
              'unmet_visual_requirements':[]}
    (ROOT / 'line-2/visual-checks-28.json').write_text(json.dumps(checks, indent=2)+'\n')
    print(json.dumps(checks))


if __name__ == '__main__':
    main()
