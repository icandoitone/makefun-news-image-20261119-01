#!/usr/bin/env python3
"""Entry program for make.fun news-image-20261119.

Copies the front-page image this repository ships (entry.png) into the
harness output directory as entry.png. Standard library only, no network,
fully deterministic: the same input bytes always produce the same output.
"""

import os
import struct
import sys

SOURCE_NAME = "entry.png"
OUTPUT_NAME = "entry.png"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1_048_576
MAX_DIMENSION = 1024


def check_png(path: str) -> tuple[int, int, int]:
    """Read the image, confirm it is a whole PNG inside the size limits.

    Returns (width, height, byte size). Raises ValueError on anything that
    would fail the competition gate, so a bad image errors out here
    instead of being submitted.
    """
    with open(path, "rb") as handle:
        data = handle.read()
    if len(data) > MAX_BYTES:
        raise ValueError(f"{path} is {len(data)} bytes, over the 1 MiB cap")
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError(f"{path} is not a PNG file")
    if len(data) < 33 or data[12:16] != b"IHDR":
        raise ValueError(f"{path} has no PNG header chunk")
    width, height = struct.unpack(">II", data[16:24])
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        raise ValueError(f"{path} is {width}x{height}, over the 1024 cap")
    return width, height, len(data)


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, SOURCE_NAME)
    width, height, size = check_png(source)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, OUTPUT_NAME)
    with open(source, "rb") as src, open(target, "wb") as dst:
        while True:
            block = src.read(65536)
            if not block:
                break
            dst.write(block)
    written = os.path.getsize(target)
    if written != size:
        raise ValueError(f"short write: {written} of {size} bytes copied")
    print(f"wrote {target}: {width}x{height} PNG, {written} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
