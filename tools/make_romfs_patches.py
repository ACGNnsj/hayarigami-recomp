"""Build a RomFS overlay directory from an update tree.

Usage: python tools/make_romfs_patches.py --update <dir> --base <dir> --out <dir>

Every file under --update that --base also has is compared by SHA-256; the ones that
differ are hardlinked into --out (falling back to a copy) and listed in
<out>/manifest.tsv as "path<TAB>size<TAB>sha256<TAB>original-sha256", which is the
format framework/runtime/romfs.c overlay_load() reads.
"""
import argparse
import hashlib
import os
import shutil
import sys


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--update", required=True)
    ap.add_argument("--base", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    lines = []
    added = 0
    for root, _dirs, files in os.walk(args.update):
        for name in files:
            src = os.path.join(root, name)
            rel = os.path.relpath(src, args.update).replace("\\", "/")
            dst = os.path.join(args.out, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            new_sha = sha256(src)
            base = os.path.join(args.base, rel)
            if not os.path.exists(base):
                if os.path.exists(dst):
                    os.remove(dst)
                try:
                    os.link(src, dst)
                except OSError:
                    shutil.copy2(src, dst)
                lines.append("%s\t%d\t%s\t-" % (rel, os.path.getsize(src), new_sha))
                added += 1
                continue
            old_sha = sha256(base)
            if new_sha == old_sha:
                continue
            if os.path.exists(dst):
                os.remove(dst)
            try:
                os.link(src, dst)
            except OSError:
                shutil.copy2(src, dst)
            lines.append("%s\t%d\t%s\t%s" % (rel, os.path.getsize(src), new_sha, old_sha))
            print("overlay: %s (%d bytes)" % (rel, os.path.getsize(src)))
    manifest = os.path.join(args.out, "manifest.tsv")
    with open(manifest, "w", newline="\n") as f:
        f.write("\n".join(lines) + ("\n" if lines else ""))
    print("%d replacement(s), %d new file(s) -> %s" % (len(lines) - added, added, manifest))


if __name__ == "__main__":
    main()
