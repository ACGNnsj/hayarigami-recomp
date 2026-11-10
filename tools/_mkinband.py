import struct
d = open('D:/consoles/ns/hayarigami-recomp/build/v0/pk_annexb.bin','rb').read()
seq = open('D:/consoles/ns/hayarigami-recomp/build/v0/spspps.bin','rb').read()
n = struct.unpack('<I', d[0:4])[0]
first = seq + d[4:4+n]
out = struct.pack('<I', len(first)) + first + d[4+n:]
open('D:/consoles/ns/hayarigami-recomp/build/v0/pk_inband.bin','wb').write(out)
print('inband first sample', len(first))