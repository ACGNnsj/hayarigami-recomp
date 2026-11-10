import sys
base = 'D:/consoles/ns/hayarigami-recomp/'
def load(path):
    with open(base + path, 'rb') as f: raw = f.read()
    crlf = b'\r\n' in raw
    return raw.decode('utf-8').replace('\r\n', '\n'), crlf
def save(path, t, crlf):
    if crlf: t = t.replace('\n', '\r\n')
    with open(base + path, 'wb') as f: f.write(t.encode('utf-8'))
t, crlf = load('tools/_ap2.py')
i = t.find('F1B_OLD')
j = t.find('F1B_NEW')
k = t.find('G3A_OLD')
old_b = t[i:t.find(chr(10), i)]
new_b = "F1B_OLD = '                    got++;\\n                }\\n            }\\n            dt = kern_now_ns() - t0;'"
assert old_b.startswith('F1B_OLD'), old_b[:40]
t = t.replace(old_b, new_b)
old_n = t[j:t.find(chr(10), j)]
new_n = "F1B_NEW = '                    got++;\\n                }\\n            }\\n                failed = e != VPX_CODEC_OK;\\n            }\\n            dt = kern_now_ns() - t0;'"
assert old_n.startswith('F1B_NEW'), old_n[:40]
t = t.replace(old_n, new_n)
save('tools/_ap2.py', t, crlf)
print('ap2 fixed v2')