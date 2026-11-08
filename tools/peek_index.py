
import json
d = json.load(open(r"D:\consoles\ns\hayarigami-recomp\build\extracted\v0\romfs\index.json"))
print(json.dumps(d["files"][:3], indent=1)[:1200])
print("section:", json.dumps(d["section"])[:300])
print("integrity:", json.dumps(d["integrity"])[:400])
