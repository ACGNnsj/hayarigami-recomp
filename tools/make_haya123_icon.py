#!/usr/bin/env python3
"""Build framework/runtime/xc2.ico for haya123 from tools/haya123logo.jpg (vendored Gematsu key art).
Square crop around the logo lockup (red circle + hiragana + 1.2.3 pack), LANCZOS downscale."""
import os
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'haya123logo.jpg')
OUT = os.path.normpath(os.path.join(HERE, '..', 'framework', 'runtime', 'xc2.ico'))
PREVIEW = os.path.normpath(os.path.join(HERE, '..', 'build', 'v0', 'haya123_icon_preview.png'))
SIZES = [16, 24, 32, 48, 64, 256]
# logo lockup: x 150-1400, y centre ~870 -> 1300x1300 square
BOX = (0, 279, 1592, 1871)

def main():
    im = Image.open(SRC).convert('RGB')
    print('src', im.size)
    sq = im.crop(BOX)
    print('crop', sq.size)
    sq.save(OUT, sizes=[(s, s) for s in SIZES])
    print('wrote', OUT, os.path.getsize(OUT))
    sq.resize((256, 256), Image.LANCZOS).save(PREVIEW)
    print('preview', PREVIEW)

if __name__ == '__main__':
    main()
