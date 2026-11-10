p = 'D:/consoles/ns/hayarigami-recomp/tools/_nv12png.py'
t = open(p, encoding='utf-8').read()
t = t.replace('frame0.nv12', 'frame200.nv12').replace('frame0.png', 'frame200.png')
open(p, 'w', encoding='utf-8').write(t)
print('png path 200')