from PIL import Image
im = Image.open('D:/consoles/ns/hayarigami-recomp/build/v0/atlas4/pass_0590_tex360_768x3200x1_145_vk145_blocks.png').convert('L')
w, h = im.size
print('size', w, h)
px = im.load()
# ink = fraction of dark pixels per block-row
rows = []
for y in range(h):
    dark = 0
    for x in range(0, w, 2):
        if px[x, y] < 100:
            dark += 1
    rows.append(dark / (w // 2))
# print profile in chunks of 20 block-rows
for b in range(0, h, 20):
    seg = rows[b:b+20]
    print('%3d-%3d ' % (b, b+20) + ''.join('#' if v > 0.45 else ('+' if v > 0.3 else ('.' if v > 0.15 else ' ')) for v in seg))