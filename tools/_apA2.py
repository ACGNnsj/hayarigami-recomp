rep("                        const char *d = vpx_codec_error_detail(&m->vpx);\n                        rt_log(\"movie: VP9 decode error on a %d-byte frame at %lld us: %s\", p.size, (long long)p.time,",
"                        if (m->mf_is_avc)\n                            rt_log(\"movie: H.264 decode error on a %d-byte frame at %lld us: hr=%#lx\", p.size,\n                                   (long long)p.time, (unsigned long)mf_hr);\n                        else {\n                        const char *d = vpx_codec_error_detail(&m->vpx);\n                        rt_log(\"movie: VP9 decode error on a %d-byte frame at %lld us: %s\", p.size, (long long)p.time,")
rep("d ? d : vpx_codec_err_to_string(e));", "d ? d : vpx_codec_err_to_string(e));\n                            }")
enc = t.replace("\n", "\r\n") if crlf else t
open(base + "framework/runtime/ov_movie.c", "wb").write(enc.encode("utf-8"))
print("apA applied, crlf=" + str(crlf))