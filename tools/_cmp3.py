from PIL import Image
import sys
def load(p):
    im = Image.open(p).convert('RGB')
    print(p, im.size)
    return im
a = load('D:/consoles/ns/hayarigami-recomp/build/v0/series2/f05693.png')
b = load('D:/consoles/ns/hayarigami-recomp/build/v0/series2/f08087.png')
c = load('D:/consoles/ns/hayarigami-recomp/build/v0/menu/cn_menu3.png')
import hashlib
# black-pixel fraction per image (luminance < 12)
def blackfrac(im):
    g = im.convert('L')
    h = g.histogram()
    return sum(h[:12]) / (im.size[0]*im.size[1])
print('blackfrac f05693 %.3f f08087 %.3f cn_menu3 %.3f' % (blackfrac(a), blackfrac(b), blackfrac(c)))
# pairwise mean abs diff
def meandiff(x, y):
    hx = x.convert('L'); hy = y.convert('L')
    dx = hx.load(); dy = hy.load()
    n = 0; tot = 0
    for yy in range(0, x.size[1], 4):
        for xx in range(0, x.size[0], 4):
            tot += abs(dx[xx,yy]-dy[xx,yy]); n += 1
    return tot / n
print('diff f05693-f08087 %.1f  f08087-cn_menu3 %.1f' % (meandiff(a,b), meandiff(b,c)))