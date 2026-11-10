base = "D:/consoles/ns/hayarigami-recomp/"
raw = open(base + "framework/runtime/ov_movie.c", "rb").read()
t = raw.decode("utf-8")
def rep(old, new):
    global t
    assert t.count(old) == 1, (repr(old[:64]), t.count(old))
    t = t.replace(old, new)
rep('AVC;\\n    int stub', 'AVC;\n    int stub')
rep('stub;\\n    m->mf_is_avc', 'stub;\n    m->mf_is_avc')
rep('inbox\\n// Media Foundation', 'inbox\n// Media Foundation')
open(base + 'framework/runtime/ov_movie.c', 'wb').write(t.encode('utf-8'))
print('KMS fixed')