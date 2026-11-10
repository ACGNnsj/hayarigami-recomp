p = "D:/consoles/ns/hayarigami-recomp/tools/_apBDE.py"
t = open(p, encoding="utf-8").read()
a = t[t.find("Q1LINE"):]
print(repr(t.split(chr(10))[16]))