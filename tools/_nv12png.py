import numpy as np
from PIL import Image
w, h = 1920, 1088
d = np.fromfile('D:/consoles/ns/hayarigami-recomp/build/v0/frame200.nv12', dtype=np.uint8)
y = d[:w*h].reshape(h, w)
uv = d[w*h:].reshape(h//2, w//2, 2).astype(np.int16)
u = uv[:,:,0] - 128; v = uv[:,:,1] - 128
u = np.repeat(np.repeat(u, 2, 0), 2, 1); v = np.repeat(np.repeat(v, 2, 0), 2, 1)
yy = y.astype(np.float32)
r = yy + 1.402*v; g = yy - 0.344136*u - 0.714136*v; b = yy + 1.772*u
rgb = np.clip(np.stack([r,g,b], -1), 0, 255).astype(np.uint8)
Image.fromarray(rgb[:1080]).save('D:/consoles/ns/hayarigami-recomp/build/v0/frame200.png')
print('mean', float(yy.mean()), 'min', int(yy.min()), 'max', int(yy.max()))