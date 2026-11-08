
import json
d = json.load(open(r"D:\consoles\ns\hayarigami-recomp\data\expected-latest.json"))
print("exefs:")
for k,v in d["exefs_sha256"].items(): print(" ", k, v)
upd = [f for f in d["romfs"]["files"] if f["from"]=="update"]
print("update files:", len(upd), sum(f["size"] for f in upd))
for f in upd: print(" ", f["size"], f["path"], f["sha256"][:16])
print("total", d["romfs"]["size"], "files", d["romfs"]["file_count"])
