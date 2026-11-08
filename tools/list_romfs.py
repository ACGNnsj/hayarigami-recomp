
import json, sys
d = json.load(open(r"D:\consoles\ns\hayarigami-recomp\build\extracted\v0\romfs\index.json"))
print(list(d.keys()))
files = d.get("files") or d.get("entries")
print("n_files", len(files))
for f in files:
    print(f.get("name"), f.get("size", f.get("length")), f.get("offset", f.get("data_offset")))
