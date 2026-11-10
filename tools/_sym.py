import sys
d = open(sys.argv[1], "rb").read()
print("size", len(d))
cands = ["FindData", "findData", "csd-0", "csd-1", "GetData", "avcC"]
for c in cands:
    b = c.encode()
    n = 0; i = d.find(b)
    while i >= 0 and n < 6:
        ctx = d[max(0,i-40):i+40]
        print(c, "at", i, repr(ctx[:80]))
        n += 1; i = d.find(b, i + 1)
    if n == 0: print(c, "ABSENT")