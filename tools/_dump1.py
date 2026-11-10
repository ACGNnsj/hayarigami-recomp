import io
p="D:/consoles/ns/hayarigami-recomp/framework/runtime/ov_movie.c"
s=io.open(p,encoding="utf-8",newline="").read()
i=s.index("void movie_note_media_bytes")
print(repr(s[i:i+1200]))