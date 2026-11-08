
import os, re, json, collections
root = r"D:\consoles\ns\xc2-recomp\runtime"
blob = []
for dp, dn, fn in os.walk(root):
    for f in fn:
        if f.endswith(('.c','.h','.inc','.cpp','.hpp')):
            blob.append(open(os.path.join(dp,f), encoding='utf-8', errors='ignore').read())
text = "\n".join(blob)
d = json.load(open(r"D:\consoles\ns\hayarigami-recomp\data\imports.json"))
allimp = sorted(set(d["main"]) | set(d["subsdk0"]))

def comps(name):
    if not name.startswith("_ZN"): return None
    s = name[3:]; out=[]
    while s and s[0].isdigit():
        n = int(re.match(r"\d+", s).group(0)); s = s[len(str(n)):]
        if len(s) < n: break
        out.append(s[:n]); s = s[n:]
    return out

buckets = collections.defaultdict(lambda: [0,0])
for x in allimp:
    cc = comps(x)
    if cc is None:
        key = "libc/nvn/nv/movie/multimedia"
    elif cc and cc[0]=="nn" and len(cc)>=3:
        key = "nn::"+cc[1]
    else:
        key = "::".join(cc[:2]) if cc else "?"
    hit = (x in text) or (len(cc or [])>2 and ("%s::%s" % (cc[1], cc[2])) in text)
    buckets[key][0] += 1
    buckets[key][1] += 1 if hit else 0
print(f"{'namespace':28s} imports  seen-in-runtime")
for k,(n,h) in sorted(buckets.items(), key=lambda kv:-kv[1][0]):
    print(f"{k:28s} {n:5d}   {h:5d}")
