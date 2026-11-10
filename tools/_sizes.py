import json
o=json.load(open("build/v0/audmap.json"))
print(o["offs"][:8])
