path = 'D:/consoles/ns/hayarigami-recomp/framework/runtime/ov_movie.c'
t = open(path, encoding='utf-8').read()
def rep(old, new):
    global t
    assert t.count(old) == 1, (repr(old[:60]), t.count(old))
    t = t.replace(old, new)
rep('    int stub, stub_fed;', '    int stub, stub_fed;' + chr(10) + '    unsigned long long fed_in;               // video packets handed to the worker')
rep('        m->pending[m->npending++] = (Pending){index, offset, size, time, flags};', '        m->pending[m->npending++] = (Pending){index, offset, size, time, flags};' + chr(10) + '        m->fed_in++;')
rep('            rt_log("movie: end of stream after %llu frames (decode %.2f ms per frame, max %.2f, %llu errors)",', '            rt_log("movie: end of stream after %llu frames from %llu inputs (decode %.2f ms per frame, max %.2f, %llu errors)",')
rep('                   (unsigned long long)m->st.frames, m->st.frames ? m->st.decode_ns / 1e6 / (double)m->st.frames : 0.0,', '                   (unsigned long long)m->st.frames, m->fed_in, m->st.frames ? m->st.decode_ns / 1e6 / (double)m->st.frames : 0.0,')
open(path, 'w', encoding='utf-8').write(t)
print('fed_in counter ok')