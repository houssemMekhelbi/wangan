#!/usr/bin/env python3
"""Generate the WanganAsaNeedle cursor theme (Wangan asa) next to this file.

The pointer is a gauge needle: a white arrow with a dark outline and an amber
tip, so it reads on the night ground and on light pages alike. Links add a
small amber ring; busy is a 270 degree tachometer arc that sweeps in amber up
to its red zone, with the needle following; progress is the arrow with a small
sweeping arc; not-allowed is a ring with a red slash; grab / grabbing are an
outlined / a filled knob. Everything has round caps and joins.

Writes two formats from the same SVGs:
  hyprcursors/ + manifest.hl*   hyprcursor (Hyprland draws it; SVG, any size)
  cursors/                      XCursor 24/32/48 (GTK3, XWayland, anything else)
Shapes not drawn here fall back to Adwaita (index.theme Inherits).
Needs rsvg-convert and hyprcursor-util. Run: python3 build.py
"""

import math
import os
import shutil
import struct
import subprocess
import tempfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NAME = "WanganAsaNeedle"
DARK, WHITE, AMBER, RING, RED, REDZONE = "#0B0D11", "#EEF1F5", "#F2A33A", "#3D4859", "#D41F27", "#5A1A1E"
XSIZES = (24, 32, 48)


def cur(*parts):
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">'
            + "".join(parts) + "</svg>\n")


def stroked(d, color=WHITE, w=1.9, halo=DARK):
    return (f'<path d="{d}" fill="none" stroke="{halo}" stroke-width="{w + 2.4}" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>')


def line(d, color, w):
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round"/>'


def pol(cx, cy, r, a):
    return cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))


def arc_d(cx, cy, r, a0, a1):
    """an arc from angle a0 to a1 (0 = east, clockwise)"""
    (x0, y0), (x1, y1) = pol(cx, cy, r, a0), pol(cx, cy, r, a1)
    return f"M{x0:.2f} {y0:.2f} A{r} {r} 0 {1 if a1 - a0 > 180 else 0} 1 {x1:.2f} {y1:.2f}"


def knob(cx, cy, r, fill):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{DARK}" stroke="{DARK}" stroke-width="2.4"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"/>')


ARROW_D = "M4 2.5 L4 24.5 L9 20.2 L13 29 L16.2 27.5 L12.4 18.9 L18.6 18.3 Z"
ARROW = (f'<path d="{ARROW_D}" fill="{WHITE}" stroke="{DARK}" stroke-width="1.4" stroke-linejoin="round"/>'
         f'<path d="M4 2.5 L4 10 L9 8 Z" fill="{AMBER}" stroke="{DARK}" stroke-width="0.9" stroke-linejoin="round"/>')
FRAMES = 8
A0, A1, ZONE = 135, 405, 365


def busy(cx, cy, r, k, needle=True):
    """frame k of the sweep: the amber arc and the needle climb from idle to the red zone"""
    now = A0 + (A1 - A0) * (k + 1) / FRAMES
    w = max(1.6, r * 0.24)
    out = line(arc_d(cx, cy, r, A0, A1), DARK, w + 2.4) + line(arc_d(cx, cy, r, A0, A1), RING, w)
    out += line(arc_d(cx, cy, r, ZONE, A1), RED if now > ZONE else REDZONE, w)
    out += line(arc_d(cx, cy, r, A0, min(now, ZONE)), AMBER, w)
    if needle:
        x, y = pol(cx, cy, r * 0.72, now)
        out += line(f"M{cx} {cy} L{x:.2f} {y:.2f}", DARK, 3.4) + line(f"M{cx} {cy} L{x:.2f} {y:.2f}", WHITE, 1.7)
        out += f'<circle cx="{cx}" cy="{cy}" r="2.2" fill="{WHITE}" stroke="{DARK}" stroke-width="0.9"/>'
    return out


def heads(pairs):
    return "".join(f'<path d="M{a[0]} {a[1]} L{b[0]} {b[1]}" fill="none" stroke="{DARK}" stroke-width="4.3" stroke-linecap="round"/>' for a, b in pairs) + \
           "".join(f'<path d="M{a[0]} {a[1]} L{b[0]} {b[1]}" fill="none" stroke="{WHITE}" stroke-width="1.9" stroke-linecap="round"/>' for a, b in pairs)


IBEAM = stroked("M11.5 5 H20.5 M16 5 V27 M11.5 27 H20.5", WHITE, 1.8) + f'<circle cx="16" cy="16" r="2.1" fill="{AMBER}" stroke="{DARK}" stroke-width="0.8"/>'
VBEAM = stroked("M5 11.5 V20.5 M5 16 H27 M27 11.5 V20.5", WHITE, 1.8) + f'<circle cx="16" cy="16" r="2.1" fill="{AMBER}" stroke="{DARK}" stroke-width="0.8"/>'

# name: (frames, hotspot (x, y) in 32-unit space, frame delay ms, aliases)
SHAPES = {
    "left_ptr": ([cur(ARROW)], (4, 3), 0,
                 ["default", "arrow", "top_left_arrow", "left_arrow", "context-menu", "copy", "alias",
                  "dnd-copy", "dnd-link", "dnd-none", "dnd-ask", "help", "question_arrow", "whats_this"]),
    "hand2": ([cur(ARROW, stroked(arc_d(24, 9, 4.4, 0, 359.9), AMBER, 1.9))], (4, 3), 0,
              ["pointer", "hand1", "hand", "pointing_hand", "e29285e634086352946a0e7090d73106"]),
    "xterm": ([cur(IBEAM)], (16, 16), 0, ["text", "ibeam"]),
    "vertical-text": ([cur(VBEAM)], (16, 16), 0, []),
    "watch": ([cur(busy(16, 17, 11.5, k)) for k in range(FRAMES)], (16, 16), 110, ["wait"]),
    "left_ptr_watch": ([cur(ARROW, busy(24, 24, 5.5, k, needle=False)) for k in range(FRAMES)], (4, 3), 110,
                       ["progress", "half-busy", "00000000000000020006000e7e9ffc3f",
                        "08e8e1c95fe2fc01f976f1e063a24ccd", "3ecb610c1bf2410f44200f48c40d3599"]),
    "crosshair": ([cur(stroked("M16 3 V13 M16 19 V29 M3 16 H13 M19 16 H29", WHITE, 1.6), f'<circle cx="16" cy="16" r="1.4" fill="{AMBER}"/>')], (16, 16), 0,
                  ["cross", "tcross", "cell", "plus", "color-picker"]),
    "not-allowed": ([cur(stroked(arc_d(16, 16, 10, 0, 359.9), WHITE, 2.0), stroked("M9 9 L23 23", RED, 2.2))], (16, 16), 0,
                    ["no-drop", "forbidden", "circle", "crossed_circle", "dnd-no-drop"]),
    "grab": ([cur(stroked(arc_d(16, 16, 8.5, 0, 359.9), AMBER, 2.0), f'<circle cx="16" cy="16" r="2" fill="{WHITE}" stroke="{DARK}" stroke-width="0.8"/>')], (16, 16), 0, ["openhand", "hand-grab"]),
    "grabbing": ([cur(knob(16, 16, 8, AMBER), f'<circle cx="16" cy="16" r="2" fill="{DARK}"/>')], (16, 16), 0, ["closedhand", "dnd-move", "hand-grabbing"]),
    "fleur": ([cur(heads([((16, 4), (16, 28)), ((4, 16), (28, 16)), ((12, 8), (16, 3.5)), ((20, 8), (16, 3.5)),
                          ((12, 24), (16, 28.5)), ((20, 24), (16, 28.5)), ((8, 12), (3.5, 16)), ((8, 20), (3.5, 16)),
                          ((24, 12), (28.5, 16)), ((24, 20), (28.5, 16))]))], (16, 16), 0,
              ["move", "all-scroll", "size_all", "4498f0e0c1937ffe01fd06f973665830", "9081237383d90e509aa00f00170e968f"]),
    "sb_h_double_arrow": ([cur(heads([((4, 16), (28, 16)), ((9, 11), (3.5, 16)), ((9, 21), (3.5, 16)),
                                      ((23, 11), (28.5, 16)), ((23, 21), (28.5, 16))]))], (16, 16), 0,
                          ["ew-resize", "col-resize", "e-resize", "w-resize", "h_double_arrow", "left_side",
                           "right_side", "size_hor", "split_h", "14fef782d02440884392942c11205230",
                           "028006030e0e7ebffc7f7070c0600140"]),
    "sb_v_double_arrow": ([cur(heads([((16, 4), (16, 28)), ((11, 9), (16, 3.5)), ((21, 9), (16, 3.5)),
                                      ((11, 23), (16, 28.5)), ((21, 23), (16, 28.5))]))], (16, 16), 0,
                          ["ns-resize", "row-resize", "n-resize", "s-resize", "v_double_arrow", "top_side",
                           "bottom_side", "size_ver", "split_v", "2870a09082c103050810ffdffffe0204",
                           "00008160000006810000408080010102"]),
    "bd_double_arrow": ([cur(heads([((6, 6), (26, 26)), ((6, 13), (5.5, 5.5)), ((13, 6), (5.5, 5.5)),
                                    ((26, 19), (26.5, 26.5)), ((19, 26), (26.5, 26.5))]))], (16, 16), 0,
                        ["nwse-resize", "nw-resize", "se-resize", "top_left_corner",
                         "bottom_right_corner", "size_fdiag", "c7088f0f3e6c8088236ef8e1e3e70000"]),
    "fd_double_arrow": ([cur(heads([((26, 6), (6, 26)), ((26, 13), (26.5, 5.5)), ((19, 6), (26.5, 5.5)),
                                    ((6, 19), (5.5, 26.5)), ((13, 26), (5.5, 26.5))]))], (16, 16), 0,
                        ["nesw-resize", "ne-resize", "sw-resize", "top_right_corner",
                         "bottom_left_corner", "size_bdiag", "fcf1c3c7cd4491d801f1e1c78f100000"]),
}


# ---- PNG decode (8-bit RGBA from rsvg-convert) --------------------------------

def load_png(path):
    d = Path(path).read_bytes()
    pos, idat = 8, b""
    while pos < len(d):
        n, t = struct.unpack(">I4s", d[pos:pos + 8])
        body = d[pos + 8:pos + 8 + n]
        pos += 12 + n
        if t == b"IHDR":
            w, h, bd, ct = struct.unpack(">IIBB", body[:10])
            assert bd == 8 and ct == 6, "expected 8-bit RGBA"
        elif t == b"IDAT":
            idat += body
    raw, bpp, stride = zlib.decompress(idat), 4, w * 4
    rows, prev, i = [], bytearray(stride), 0
    for _ in range(h):
        f, line_ = raw[i], bytearray(raw[i + 1:i + 1 + stride])
        i += 1 + stride
        for x in range(stride):
            a = line_[x - bpp] if x >= bpp else 0
            b = prev[x]
            c = prev[x - bpp] if x >= bpp else 0
            if f == 1:
                line_[x] = (line_[x] + a) & 255
            elif f == 2:
                line_[x] = (line_[x] + b) & 255
            elif f == 3:
                line_[x] = (line_[x] + (a + b) // 2) & 255
            elif f == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line_[x] = (line_[x] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        rows.append(bytes(line_))
        prev = line_
    return w, h, rows


def argb_premultiplied(rows):
    out = bytearray()
    for r in rows:
        for x in range(0, len(r), 4):
            R, G, B, A = r[x:x + 4]
            out += struct.pack("<I", (A << 24) | ((R * A // 255) << 16) | ((G * A // 255) << 8) | (B * A // 255))
    return bytes(out)


def xcursor(images):
    """images: list of (nominal, w, h, xhot, yhot, delay, argb). Returns XCursor bytes."""
    ntoc = len(images)
    header = struct.pack("<4sIII", b"Xcur", 16, 0x10000, ntoc)
    pos = 16 + ntoc * 12
    toc, chunks = b"", b""
    for nominal, w, h, xh, yh, delay, px in images:
        toc += struct.pack("<III", 0xFFFD0002, nominal, pos)
        chunk = struct.pack("<IIIIIIIII", 36, 0xFFFD0002, nominal, 1, w, h, xh, yh, delay) + px
        chunks += chunk
        pos += len(chunk)
    return header + toc + chunks


def main():
    for d in ("hyprcursors", "cursors"):
        shutil.rmtree(ROOT / d, ignore_errors=True)
    for f in ROOT.glob("manifest.*"):
        f.unlink()
    (ROOT / "cursors").mkdir()

    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / "work"
        (work / "hyprcursors").mkdir(parents=True)
        (work / "manifest.hl").write_text(
            f"name = {NAME}\ndescription = Wangan asa: a white needle with an amber tip, a tachometer arc when busy\n"
            "version = 0.1\ncursors_directory = hyprcursors\n")
        for shape, (frames, (hx, hy), delay, aliases) in SHAPES.items():
            sd = work / "hyprcursors" / shape
            sd.mkdir()
            meta = [f"resize_algorithm = bilinear", f"hotspot_x = {hx / 32:.4f}", f"hotspot_y = {hy / 32:.4f}"]
            meta += [f"define_override = {a}" for a in aliases]
            images = []
            for k, body in enumerate(frames):
                fname = f"{shape}-{k}.svg"
                (sd / fname).write_text(body)
                meta.append(f"define_size = 0, {fname}" + (f", {delay}" if delay else ""))
                for size in XSIZES:
                    png = Path(tmp) / f"{shape}-{k}-{size}.png"
                    subprocess.run(["rsvg-convert", "-w", str(size), "-h", str(size), "-o", str(png), str(sd / fname)], check=True)
                    w, h, rows = load_png(png)
                    images.append((size, w, h, round(hx * size / 32), round(hy * size / 32), delay or 0, argb_premultiplied(rows)))
            (sd / "meta.hl").write_text("\n".join(meta) + "\n")
            images.sort(key=lambda i: i[0])
            (ROOT / "cursors" / shape).write_bytes(xcursor(images))
            for a in aliases:
                link = ROOT / "cursors" / a
                if not link.exists():
                    os.symlink(shape, link)

        out = Path(tmp) / "out"
        out.mkdir()
        subprocess.run(["hyprcursor-util", "--create", str(work), "--output", str(out)], check=True,
                       stdout=subprocess.DEVNULL)
        built = next(out.iterdir())
        for item in built.iterdir():
            dest = ROOT / item.name
            if item.is_dir():
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, dest)

    (ROOT / "index.theme").write_text(
        f"[Icon Theme]\nName={NAME}\nComment=Wangan asa cursors: white needle with an amber tip, amber ring for links, tachometer arc when busy\nInherits=Adwaita\n")
    print(f"{NAME} written to {ROOT}")


if __name__ == "__main__":
    main()
