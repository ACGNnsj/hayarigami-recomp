
import json, re, collections
imp = json.load(open(r"D:\consoles\ns\hayarigami-recomp\data\imports.json"))
allimp = sorted(set(imp["main"]) | set(imp["subsdk0"]))

def split_ns(name):
    if not name.startswith("_ZN"): return None, name
    s = name[3:]
    parts = []
    while s and s[0].isdigit():
        m = re.match(r"(\d+)", s)
        n = int(m.group(1)); s = s[m.end():]
        if len(s) < n: break
        parts.append(s[:n]); s = s[n:]
        if parts and parts[0] == "nn" and len(parts) >= 2:
            # stop at function name if next segment looks like a name followed by E
            if s.startswith("E"): break
    return "::".join(parts), s

c = collections.Counter()
for x in allimp:
    ns, rest = split_ns(x)
    if ns is None:
        c["(host/libc/nvn)"] += 1
    else:
        c[ns] += 1
print("total imports", len(allimp))
for k, v in c.most_common(60): print(f"{v:5d}  {k}")
nvn = [x for x in allimp if x.startswith("nvn") or x.startswith("_ZN2nv")]
print("NVN API functions:", len(nvn))
print("sample:", nvn[:15])
