import io, sys
root = "D:/consoles/ns/hayarigami-recomp/"

def edit(rel, pairs):
    p = root + rel
    s = io.open(p, encoding="utf-8", newline="").read()
    for old, new, cnt in pairs:
        c = s.count(old)
        if c != cnt:
            print("FAIL", rel, "count", c, "expected", cnt, "for", old[:70])
            sys.exit(1)
        s = s.replace(old, new)
    io.open(p, "w", encoding="utf-8", newline="").write(s)
    print("ok", rel)

def crlf(t):
    return t.replace("\n", "\r\n")

old_fn = crlf("""void movie_note_media_bytes(const void *buf, size_t n) {
    const uint8_t *d = buf;
    if (!d || n < 8) return;
    for (size_t i = 4; i + 4 < n; i++) {
        if (memcmp(d + i, "avcC", 4)) continue;
        size_t box = ((size_t)d[i - 4] << 24) | ((size_t)d[i - 3] << 16) | ((size_t)d[i - 2] << 8) | d[i - 1];
        if (box < 8 || i - 4 + box > n) return;
        uint8_t annexb[1024];
        size_t olen = 0;
        if (!mf_avcc_to_annexb(d + i + 4, box - 8, annexb, sizeof annexb, &olen)) return;
        plat_mutex_lock(&hint_mu);
        memcpy(hint_seq, annexb, olen);
        hint_len = olen;
        plat_mutex_unlock(&hint_mu);
        rt_log("movie: the open movie's avcC gives %d bytes of SPS/PPS", (int)olen);
        return;
    }
}""")
new_fn = crlf("""int movie_note_media_bytes(const void *buf, size_t n) {
    const uint8_t *d = buf;
    if (!d || n < 8) return 0;
    for (size_t i = 4; i + 4 < n; i++) {
        if (memcmp(d + i, "avcC", 4)) continue;
        size_t box = ((size_t)d[i - 4] << 24) | ((size_t)d[i - 3] << 16) | ((size_t)d[i - 2] << 8) | d[i - 1];
        if (box < 8 || i - 4 + box > n) return 0;
        uint8_t annexb[1024];
        size_t olen = 0;
        if (!mf_avcc_to_annexb(d + i + 4, box - 8, annexb, sizeof annexb, &olen)) return 0;
        plat_mutex_lock(&hint_mu);
        memcpy(hint_seq, annexb, olen);
        hint_len = olen;
        plat_mutex_unlock(&hint_mu);
        rt_log("movie: the open movie's avcC gives %d bytes of SPS/PPS", (int)olen);
        return 1;
    }
    return 0;
}""")
edit("framework/runtime/ov_movie.c", [(old_fn, new_fn, 1)])

old_nm = crlf("""    uint64_t n = 0;
    uint32_t rr = read_file(&n, h, 0, buf, HEAD_CAP);
    rt_log("movie: head of %s -> r=%#x n=%llu", path, rr, (unsigned long long)n);
    if (!rr) movie_note_media_bytes(buf, (size_t)n);
    free(buf);""")
new_nm = crlf("""    uint64_t n = 0;
    uint32_t rr = read_file(&n, h, 0, buf, HEAD_CAP);
    int got = !rr && movie_note_media_bytes(buf, (size_t)n);
    rt_log("movie: head of %s -> r=%#x n=%llu avcC=%d", path, rr, (unsigned long long)n, got);
    // The update's movies put moov after mdat, so their avcC sits in the tail rather than the head.
    int64_t size = 0;
    if (!got && !file_size(&size, h) && size > (int64_t)HEAD_CAP) {
        uint64_t m = 0;
        uint32_t tr = read_file(&m, h, size - (int64_t)HEAD_CAP, buf, HEAD_CAP);
        got = !tr && movie_note_media_bytes(buf, (size_t)m);
        rt_log("movie: tail of %s -> r=%#x n=%llu avcC=%d", path, tr, (unsigned long long)m, got);
    }
    free(buf);""")
edit("framework/runtime/fs_host.c", [(old_nm, new_nm, 1)])
