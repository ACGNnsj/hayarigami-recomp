base = "D:/consoles/ns/hayarigami-recomp/"
p = base + "framework/runtime/fs_host.c"
t = open(p, encoding="utf-8").read()
old = "    if (!read_file(&n, h, 0, buf, HEAD_CAP)) movie_note_media_bytes(buf, (size_t)n);"
new = "    uint32_t rr = read_file(&n, h, 0, buf, HEAD_CAP);" + chr(10) + "    rt_log(\"movie: head of %s -> r=%#x n=%llu\", path, rr, (unsigned long long)n);" + chr(10) + "    if (!rr) movie_note_media_bytes(buf, (size_t)n);"
assert t.count(old) == 1
t = t.replace(old, new)
open(p, "w", encoding="utf-8").write(t)
print('instrumented')