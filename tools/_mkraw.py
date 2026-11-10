import struct
d = open('D:/consoles/ns/hayarigami-recomp/build/v0/pk_annexb.bin','rb').read()
seq = open('D:/consoles/ns/hayarigami-recomp/build/v0/spspps.bin','rb').read()
out = bytearray(seq); i = 0; k = 0
while i + 4 <= len(d):
    n = struct.unpack('<I', d[i:i+4])[0]; i += 4
    out += d[i:i+n]; i += n; k += 1
open('D:/consoles/ns/hayarigami-recomp/build/v0/test2.264','wb').write(bytes(out))
print('raw annexb', len(out), 'samples', k)