#!/usr/bin/env python3
"""news-image-20261118 entry: copy the pre-built image to the output dir.

Standard library only, no network. Deterministic: the same bytes every run.

Before copying, the source image is validated: it must exist, be at
most 1 MiB, and be a PNG no larger than 1024x1024, its dimensions
read from the PNG IHDR header with struct (no imaging library, so
the program stays standard-library-only). Any failure is a clear
error on stderr with a non-zero exit code, and nothing is copied.
"""
import os
import shutil
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
MAX_BYTES = 1_048_576
MAX_WIDTH = 1024
MAX_HEIGHT = 1024
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def fail(message):
    print(f"error: {message}", file=sys.stderr)
    return 1


def png_dimensions(data):
    """(width, height) from the PNG IHDR chunk, or None if not a PNG."""
    if len(data) < 33 or data[:8] != PNG_SIGNATURE:
        return None
    length, chunk_type = struct.unpack(">I4s", data[8:16])
    if chunk_type != b"IHDR" or length != 13:
        return None
    return struct.unpack(">II", data[16:24])


def main():
    if not os.path.isfile(SRC):
        return fail(f"entry image not found: {SRC}")
    try:
        with open(SRC, "rb") as f:
            data = f.read()
    except OSError as exc:
        return fail(f"cannot read entry image {SRC}: {exc}")
    if len(data) > MAX_BYTES:
        return fail(
            f"entry image is {len(data)} bytes, over the {MAX_BYTES}-byte limit"
        )
    dims = png_dimensions(data)
    if dims is None:
        return fail(f"entry image {SRC} is not a valid PNG file")
    width, height = dims
    if width > MAX_WIDTH or height > MAX_HEIGHT:
        return fail(
            f"entry image is {width}x{height}, "
            f"over the {MAX_WIDTH}x{MAX_HEIGHT} limit"
        )
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    dst = os.path.join(out_dir, "entry.png")
    try:
        os.makedirs(out_dir, exist_ok=True)
        shutil.copyfile(SRC, dst)
    except OSError as exc:
        return fail(f"cannot write output image: {exc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
