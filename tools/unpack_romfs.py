#!/usr/bin/env python3
"""Unpack romfs.bin into a file tree using the index written by extract_romfs.py.

Usage: unpack_romfs.py --romfs build/extracted/v0/romfs --out build/extracted/v0/romfs-tree
"""
import argparse, json, shutil
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--romfs', type=Path, required=True, help='directory holding romfs.bin and index.json')
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--verify', action='store_true', help='size-check every file after writing')
    a = ap.parse_args()
    index = json.loads((a.romfs / 'index.json').read_text())
    a.out.mkdir(parents=True, exist_ok=True)
    total = 0
    with (a.romfs / 'romfs.bin').open('rb') as src:
        for f in index['files']:
            dst = a.out / f['path']
            dst.parent.mkdir(parents=True, exist_ok=True)
            src.seek(f['offset'])
            with dst.open('wb') as out:
                left = f['size']
                while left:
                    chunk = src.read(min(left, 1 << 24))
                    if not chunk:
                        raise SystemExit(f'{f["path"]}: short read with {left} bytes left')
                    out.write(chunk)
                    left -= len(chunk)
            if a.verify and dst.stat().st_size != f['size']:
                raise SystemExit(f'{f["path"]}: size mismatch')
            total += f['size']
            print(f'{f["size"]:>12,}  {f["path"]}', flush=True)
    print(f'{len(index["files"])} files, {total:,} bytes -> {a.out}')


if __name__ == '__main__':
    main()
