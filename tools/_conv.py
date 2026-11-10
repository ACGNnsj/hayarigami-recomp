import struct
d = open('D:/consoles/ns/hayarigami-recomp/build/v0/packets.bin','rb').read()
out = bytearray(); i = 0; k = 0
while i + 4 <= len(d):
    n = struct.unpack('>I', d[i:i+4])[0]; i += 4
    s = d[i:i+n]; i += n
    j = 0; ab = bytearray()
    while j + 4 <= len(s):
        m = struct.unpack('>I', s[j:j+4])[0]; j += 4
        if m == 0 or j + m > len(s): break
        ab += b'\x00\x00\x00\x01' + s[j:j+m]; j += m
    out += struct.pack('<I', len(ab)) + bytes(ab); k += 1
open('D:/consoles/ns/hayarigami-recomp/build/v0/pk_annexb.bin','wb').write(bytes(out))
print('samples', k, 'first', struct.unpack('<I', out[0:4])[0])