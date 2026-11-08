
import json, re, collections
d = json.load(open(r"D:\consoles\ns\hayarigami-recomp\data\imports.json"))
allimp = sorted(set(d["main"]) | set(d["subsdk0"]))
print("unique imports:", len(allimp), "| main:", len(d["main"]), "| subsdk0:", len(d["subsdk0"]))

def comps(name):
    if not name.startswith("_ZN"): return None
    s = name[3:]; out=[]
    while s and s[0].isdigit():
        n = int(re.match(r"\d+", s).group(0)); s = s[len(str(n)):]
        if len(s) < n: break
        out.append(s[:n]); s = s[n:]
    return out

c = collections.Counter(); libc=0; unknown=[]
for x in allimp:
    cc = comps(x)
    if cc is None: libc += 1; continue
    if cc and cc[0] == "nn" and len(cc) >= 3:
        c["::".join(cc[:3]) if cc[1] not in ("os","fs","oe","hid","audio","sf") else "nn::"+cc[1]] += 1
    else:
        unknown.append("::".join(cc[:2]) if len(cc)>=2 else x)
print("non-mangled (libc/C++/nvn):", libc)
print("--- nn:: namespaces ---")
nn = {k:v for k,v in c.items() if k.startswith("nn::")}
for k,v in sorted(nn.items(), key=lambda kv:-kv[1]): print(f"{v:4d}  {k}")
print("--- other mangled prefixes ---")
oc = collections.Counter(unknown)
for k,v in oc.most_common(20): print(f"{v:4d}  {k}")
