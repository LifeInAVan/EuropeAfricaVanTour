#!/usr/bin/env python3
"""Remove location (GPS), camera and other metadata from every photo under assets/.

JPEG: drops the EXIF, XMP, IPTC and comment blocks and anything after the end of the
image (iPhone depth maps), without re-compressing; keeps the colour profile.
A photo stored sideways (EXIF orientation) is turned upright first, which re-saves it.
PNG: keeps only the image and colour chunks.

python pipeline/strip_metadata.py            strip in place
python pipeline/strip_metadata.py --check    list photos that still carry metadata; exit 1 if any
python pipeline/strip_metadata.py DIR ...    other folders instead of assets/
"""
import io, os, struct, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)          # repository root: data/, docs/, assets/

KEEP_APP = {0xE0, 0xEE}               # JFIF, Adobe (colour transform); APP2 kept only for ICC
PNG_KEEP = {b"IHDR", b"PLTE", b"IDAT", b"IEND", b"tRNS", b"gAMA", b"cHRM", b"sRGB",
            b"iCCP", b"sBIT", b"pHYs", b"bKGD"}


def label(marker, body):
    if marker == 0xFE: return "comment"
    for start, name in ((b"Exif", "EXIF"), (b"http", "XMP"), (b"Photoshop", "IPTC"), (b"MPF", "extra images")):
        if body.startswith(start): return name
    return "APP%d" % (marker - 0xE0)


def jpeg_clean(data):
    """Return (cleaned bytes, list of what was removed)."""
    assert data[:2] == b"\xff\xd8", "not a JPEG"
    out, removed, i = [data[:2]], [], 2
    while i < len(data):
        if data[i] != 0xFF: raise ValueError("bad marker at %d" % i)
        m = data[i + 1]
        if m == 0xFF: i += 1; continue                         # fill byte
        if 0xD0 <= m <= 0xD7 or m == 0x01: out.append(data[i:i + 2]); i += 2; continue
        if m == 0xD9: out.append(data[i:i + 2]); i += 2; break
        n = struct.unpack(">H", data[i + 2:i + 4])[0]
        seg = data[i:i + 2 + n]
        if m == 0xDA:                                          # start of scan: copy to end of image
            j = i + 2 + n
            while True:
                j = data.index(b"\xff", j)
                if data[j + 1] == 0xD9: break
                j += 1 if data[j + 1] == 0xFF else 2
            out.append(data[i:j + 2]); i = j + 2; break
        drop = (0xE0 <= m <= 0xEF and m not in KEEP_APP
                and not (m == 0xE2 and seg[4:16] == b"ICC_PROFILE\0")) or m == 0xFE
        if drop: removed.append(label(m, seg[4:]))
        else: out.append(seg)
        i += 2 + n
    if i < len(data) and data[i:].strip(b"\0"): removed.append("data after end of image")
    return b"".join(out), removed


def png_clean(data):
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG"
    out, removed, i = [data[:8]], [], 8
    while i < len(data):
        n, kind = struct.unpack(">I4s", data[i:i + 8])
        chunk = data[i:i + 12 + n]
        if kind in PNG_KEEP: out.append(chunk)
        else: removed.append(kind.decode("latin-1"))
        i += 12 + n
        if kind == b"IEND": break
    return b"".join(out), removed


def upright(data):
    """Turn a sideways JPEG upright (re-saves it); None if it is already upright."""
    from PIL import Image, ImageOps
    im = Image.open(io.BytesIO(data))
    if im.getexif().get(0x0112, 1) == 1: return None
    icc = im.info.get("icc_profile")
    buf = io.BytesIO()
    ImageOps.exif_transpose(im).save(buf, "JPEG", quality=95, icc_profile=icc)
    return buf.getvalue()


def main(args):
    check = "--check" in args
    dirs = [a for a in args if a != "--check"] or [os.path.join(ROOT, "assets")]
    dirty = 0
    for d in dirs:
        for base, _, files in os.walk(d):
            for f in sorted(files):
                p = os.path.join(base, f); ext = f.lower().rsplit(".", 1)[-1]
                if ext not in ("jpg", "jpeg", "png"): continue
                data = open(p, "rb").read()
                if ext == "png": clean, removed = png_clean(data)
                else:
                    turned = None if check else upright(data)
                    clean, removed = jpeg_clean(turned or data)
                    if turned: removed.insert(0, "turned upright")
                if not removed: continue
                dirty += 1
                print(("has " if check else "stripped ") + os.path.relpath(p, ROOT) + ": " + ", ".join(removed))
                if not check: open(p, "wb").write(clean)
    print("%d photo(s) %s" % (dirty, "with metadata" if check else "cleaned"))
    return 1 if check and dirty else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
