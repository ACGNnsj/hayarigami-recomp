import struct, subprocess
d = open("build/v0/aac_head3.adts","rb").read()
frames = []
pos = 0
while pos + 7 <= len(d):
    assert d[pos] == 0xFF and (d[pos+1] & 0xF6) == 0xF0
    ln = ((d[pos+3] & 3) << 11) | (d[pos+4] << 3) | (d[pos+5] >> 5)
    frames.append(d[pos:pos+ln])
    pos += ln
p = subprocess.Popen(["build/v0/aac_srv.exe"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
tot = 0
for f in frames:
    p.stdin.write(struct.pack("<I", len(f)) + f)
    p.stdin.flush()
    (pl,) = struct.unpack("<I", p.stdout.read(4))
    got = p.stdout.read(pl) if pl else b""
    print("frame", len(f), "->pcm", len(got))
    tot += len(got)
p.stdin.close()
print("total pcm:", tot)
print("srv stderr:", p.stderr.read().decode()[:300])
