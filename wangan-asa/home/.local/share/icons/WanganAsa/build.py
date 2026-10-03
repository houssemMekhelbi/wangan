#!/usr/bin/env python3
"""Generate the WanganAsa icon theme next to this file (Wangan asa).

scalable/  64-unit SVGs, all round. Folders are bayside-blue instrument plates:
           a deeper back plate with a rounded tab, a front plate with a lit
           upper edge, one amber index mark, a row of LCD dots along the bottom
           and one white mark for the special folders. Documents are white spec
           sheets with a blue header pill and one mark for their type (amber on
           PDF and executables, blue on images and code). Devices are panel
           boxes with an amber lamp. The trash is a round bin with an amber handle.
16/        sidebar size: plain round-capped line icons in the muted colour.
Anything not drawn here falls through to Adwaita.
Run: python3 build.py   (then gtk-update-icon-cache runs by itself)
"""

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NAME = "WanganAsa"

GROUND, PANEL, RAISED, LINE, RING = "#E4E8EE", "#F2F4F8", "#D5DCE7", "#B7C0CD", "#A9B3C2"
BLUE, DEEP, LIT, AMBER, RED = "#2A5FC4", "#1D4794", "#8AAEF5", "#F2A33A", "#D41F27"
WHITE, SHEET, SHEET_EDGE, INK, RULE = "#FFFFFF", "#FFFFFF", "#B7C0CD", "#2A3240", "#6B7587"
SILVER = "#4E596B"
SIDE = "#4E596B"


def svg64(body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64">{body}</svg>\n'


def write(rel, content, names):
    for name in names:
        path = ROOT / rel / f"{name}.svg"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)


def stroke(d, color=WHITE, w=2.6):
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>'


# ---- folders: instrument plates --------------------------------------------------------
MARKS = {
    None: "",
    "home": f'<path d="M24 50 V41 L32 33 L40 41 V50 Z" fill="{WHITE}" stroke="{WHITE}" stroke-width="3" stroke-linejoin="round"/><rect x="30" y="43" width="4" height="8" rx="2" fill="{BLUE}"/>',
    "documents": "".join(stroke(f"M23 {y} H{x}", WHITE, 2.8) for y, x in ((34, 41), (41, 41), (48, 35))),
    "downloads": stroke("M32 31 V45 M26 40 L32 46 L38 40 M25 51 H39"),
    "music": stroke("M28 47 V33 L39 31 V45") + f'<circle cx="25.5" cy="47.5" r="3.2" fill="{WHITE}"/><circle cx="36.5" cy="45.5" r="3.2" fill="{WHITE}"/>',
    "pictures": f'<path d="M22 50 L29 40 L33.5 45.5 L37 42 L43 50 Z" fill="{WHITE}" stroke="{WHITE}" stroke-width="2" stroke-linejoin="round"/><circle cx="40" cy="34" r="3" fill="{WHITE}"/>',
    "videos": f'<path d="M28 33 L41 41 L28 49 Z" fill="{WHITE}" stroke="{WHITE}" stroke-width="3" stroke-linejoin="round"/>',
    "desktop": f'<rect x="22" y="32" width="20" height="14" rx="3" fill="none" stroke="{WHITE}" stroke-width="2.4"/>' + stroke("M27 51 H37", WHITE, 2.4),
    "templates": f'<rect x="23" y="32" width="18" height="18" rx="5" fill="none" stroke="{WHITE}" stroke-width="2.4" stroke-dasharray="3.4 3.4" stroke-linecap="round"/>',
    "share": stroke("M26 41.5 L38 35 M26 41.5 L38 48.5", WHITE, 1.8) + "".join(f'<circle cx="{x}" cy="{y}" r="3.4" fill="{WHITE}"/>' for x, y in ((26, 41.5), (38, 34.5), (38, 48.5))),
    "remote": stroke("M32 32 a9 9.5 0 1 0 0.01 0 M23 41.5 H41 M32 32 C27 36.5 27 46.5 32 51 M32 32 C37 36.5 37 46.5 32 51", WHITE, 1.7),
}


def folder(kind=None):
    dots = "".join(f'<circle cx="{x}" cy="51" r="{1.1 if i % 3 == 0 else 0.7}" fill="{WHITE}" fill-opacity="0.5"/>' for i, x in enumerate(range(13, 53, 3))) if kind is None else ""
    mark = f'<g transform="translate(32 40) scale(0.84) translate(-32 -41)">{MARKS[kind]}</g>' if kind else ""
    body = (f'<path d="M6 17 a5 5 0 0 1 5 -5 H23 c4 0 4 5.5 8 5.5 H53 a5 5 0 0 1 5 5 V50 a5 5 0 0 1 -5 5 H11 a5 5 0 0 1 -5 -5 Z" fill="{DEEP}"/>'
            f'<rect x="6" y="23.5" width="52" height="31.5" rx="7" fill="{BLUE}"/>'
            + stroke("M12.5 24.5 H51.5", LIT, 1)
            + f'<rect x="27.5" y="26.5" width="9" height="3.6" rx="1.8" fill="{AMBER}"/>' + dots + mark)
    return svg64(body)


FOLDERS = {
    None: ["folder", "inode-directory", "folder-open", "folder-drag-accept", "folder-visiting"],
    "home": ["user-home", "folder-home"],
    "documents": ["folder-documents"],
    "downloads": ["folder-download"],
    "music": ["folder-music"],
    "pictures": ["folder-pictures"],
    "videos": ["folder-videos"],
    "templates": ["folder-templates"],
    "share": ["folder-publicshare"],
    "desktop": ["user-desktop"],
    "remote": ["folder-remote", "network-workgroup"],
}
for kind, names in FOLDERS.items():
    write("scalable/places", folder(kind), names)
    if kind is None:
        write("scalable/mimetypes", folder(kind), names)
for kind, names in FOLDERS.items():
    write("scalable/places", folder(kind), names)
    if kind is None:
        write("scalable/mimetypes", folder(kind), names)


# ---- documents: spec sheets ------------------------------------------------------------
def sheet():
    return (f'<rect x="12.5" y="4.5" width="39" height="55" rx="7" fill="{SHEET}" stroke="{SHEET_EDGE}"/>'
            f'<rect x="18" y="11" width="18" height="4.6" rx="2.3" fill="{BLUE}"/><circle cx="45" cy="13.3" r="1.9" fill="{RULE}" fill-opacity="0.55"/>')


def lines(ys, color=RULE, x0=19, x1=45):
    return "".join(stroke(f"M{x0} {y} H{x0 + 6} M{x0 + 10.5} {y} H{x1 - (7 if i % 2 else 0)}", color, 2.2) for i, y in enumerate(ys))


DOC_MARKS = {
    None: "",
    "text": lines([24, 31, 38, 45, 52]),
    "script": stroke("M20 26 L26 31 L20 36", BLUE) + stroke("M30 37 H42", AMBER) + lines([45, 52]),
    "code": stroke("M27 25 L21 33 L27 41", BLUE) + stroke("M37 25 L43 33 L37 41", BLUE) + lines([50]),
    "exec": f'<circle cx="32" cy="36" r="11" fill="{INK}"/>' + stroke("M32 36 L38.5 29.5", AMBER, 2.6) + f'<circle cx="32" cy="36" r="2.2" fill="{WHITE}"/>',
    "image": (f'<rect x="18" y="22" width="28" height="30" rx="5" fill="{INK}"/>' + stroke("M23 50 C25 41 31 36 42 35", AMBER, 2.2)
              + stroke("M31 50 C33 44 37 40.5 42 40", WHITE, 1.6)),
    "pdf": lines([24, 31, 38]) + f'<rect x="17" y="44" width="30" height="10" rx="5" fill="{AMBER}"/>' + "".join(f'<circle cx="{x}" cy="49" r="1.6" fill="{INK}"/>' for x in (25, 32, 39)),
    "audio": stroke("M19 38 C22 27 25 49 29 38 C33 27 36 49 45 36", BLUE),
    "video": f'<rect x="18" y="22" width="28" height="30" rx="5" fill="{INK}"/><path d="M28 30 L39 37 L28 44 Z" fill="{WHITE}" stroke="{WHITE}" stroke-width="2.4" stroke-linejoin="round"/>',
    "archive": f'<rect x="29" y="18" width="6" height="41" fill="{BLUE}" fill-opacity="0.85"/><rect x="25.5" y="30" width="13" height="10" rx="4" fill="{SHEET}" stroke="{AMBER}" stroke-width="2"/>',
    "grid": stroke("M19 26 H45 M19 34 H45 M19 42 H45 M19 50 H45 M27.5 23 V53 M36.5 23 V53", RULE, 1.6),
    "slide": f'<rect x="18" y="22" width="28" height="18" rx="5" fill="{BLUE}"/>' + stroke("M32 40 V49 M26 50 H38", INK, 2.2),
    "font": stroke("M21 51 L32 25 L43 51 M25 42.5 H39", INK),
}
DOCUMENTS = {
    None: ["application-x-generic", "unknown", "empty"],
    "text": ["text-x-generic", "text-plain", "x-office-document", "text-markdown", "text-x-readme"],
    "script": ["text-x-script", "application-x-shellscript", "text-x-python", "text-x-makefile"],
    "exec": ["application-x-executable", "application-x-sharedlib"],
    "image": ["image-x-generic"],
    "audio": ["audio-x-generic"],
    "video": ["video-x-generic"],
    "archive": ["package-x-generic", "application-x-archive", "application-zip", "application-x-compressed-tar", "application-x-tar"],
    "pdf": ["application-pdf"],
    "code": ["text-html", "application-json", "text-x-csrc", "text-x-c++src", "text-x-javascript"],
    "grid": ["x-office-spreadsheet"],
    "slide": ["x-office-presentation"],
    "font": ["font-x-generic"],
}
for kind, names in DOCUMENTS.items():
    write("scalable/mimetypes", svg64(sheet() + DOC_MARKS[kind]), names)
for kind, names in DOCUMENTS.items():
    write("scalable/mimetypes", svg64(sheet() + DOC_MARKS[kind]), names)


# ---- devices and trash -----------------------------------------------------------------
def box(x, y, w, h, r=8):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{PANEL}" stroke="{SILVER}" stroke-width="1.6"/>'


def led(cx, cy):
    return f'<circle cx="{cx}" cy="{cy}" r="2.8" fill="{AMBER}"/>'


DRIVE = box(8, 21, 48, 23, 11.5) + stroke("M16 32.5 H36", BLUE, 2.4) + led(46, 32.5)
write("scalable/devices", svg64(DRIVE), ["drive-harddisk", "drive-harddisk-system", "drive-multidisk"])
REMOVABLE = f'<rect x="25" y="8" width="14" height="14" rx="4" fill="{RAISED}" stroke="{SILVER}" stroke-width="1.6"/>' + box(18, 20, 28, 37, 9) + led(32, 40)
write("scalable/devices", svg64(REMOVABLE), ["drive-removable-media", "drive-harddisk-usb", "media-removable", "media-flash"])
OPTICAL = (f'<circle cx="32" cy="32" r="21.5" fill="{PANEL}" stroke="{SILVER}" stroke-width="1.6"/>'
           + stroke("M32 18 A14 14 0 1 1 18 32", BLUE, 2.2) + led(32, 32))
write("scalable/devices", svg64(OPTICAL), ["drive-optical", "media-optical"])
COMPUTER = box(9, 10, 46, 32, 8) + stroke("M32 42.5 V52 M23 54 H41", SILVER, 2.2) + led(32, 26)
write("scalable/devices", svg64(COMPUTER), ["computer", "video-display"])
BIN = (f'<rect x="17" y="21" width="30" height="38" rx="8" fill="{RAISED}" stroke="{SILVER}" stroke-width="1.8"/>'
       f'<rect x="12" y="13" width="40" height="7" rx="3.5" fill="{SILVER}"/><rect x="27" y="6.5" width="10" height="5" rx="2.5" fill="{AMBER}"/>'
       + stroke("M26 30 V51 M32 30 V51 M38 30 V51", LIT, 2))
write("scalable/places", svg64(BIN), ["user-trash"])
write("scalable/places", svg64(BIN + f'<circle cx="49" cy="11" r="5" fill="{RED}" stroke="{GROUND}" stroke-width="1.5"/>'), ["user-trash-full"])


# ---- 16px sidebar: plain line icons ------------------------------------------------------
SYM = {
    "home": '<path d="M2 8 L8 2.5 L14 8"/><path d="M4 7 V14 H12 V7"/>',
    "desktop": '<rect x="2" y="3" width="12" height="8"/><path d="M6 14 H10"/>',
    "documents": '<path d="M4 2 H10 L13 5 V14 H4 Z"/><path d="M6.5 8 H10.5 M6.5 11 H9.5"/>',
    "downloads": '<path d="M8 2 V11"/><path d="M4 7.5 L8 11.5 L12 7.5"/><path d="M3 14 H13"/>',
    "music": '<path d="M5.5 12.5 V3.5 L12.5 2.5 V11.5"/><circle cx="4" cy="12.5" r="1.6"/><circle cx="11" cy="11.5" r="1.6"/>',
    "pictures": '<path d="M2 13 L6 7 L9 10.5 L11 8.5 L14 13 Z"/><circle cx="11.5" cy="4.5" r="1.2"/>',
    "videos": '<path d="M5 3 V13 L13 8 Z"/>',
    "templates": '<rect x="2.5" y="2.5" width="11" height="11" stroke-dasharray="2.2 2"/>',
    "share": '<circle cx="4" cy="8" r="1.6"/><circle cx="12" cy="3.8" r="1.6"/><circle cx="12" cy="12.2" r="1.6"/><path d="M5.4 7.2 L10.6 4.6 M5.4 8.8 L10.6 11.4"/>',
    "folder": '<path d="M2 4 H6.5 L8 5.5 H14 V13 H2 Z"/>',
    "recent": '<circle cx="8" cy="8" r="6"/><path d="M8 4.5 V8 L10.5 9.5"/>',
    "trash": '<path d="M3 4.5 H13"/><path d="M6 4.5 V2.5 H10 V4.5"/><path d="M4.5 4.5 L5.5 14 H10.5 L11.5 4.5"/>',
    "bookmark": '<path d="M4 2 H12 V14 L8 10.5 L4 14 Z"/>',
    "drive": '<rect x="2" y="5" width="12" height="6"/><path d="M10.5 8 H11.5"/>',
    "removable": '<rect x="4.5" y="5" width="7" height="9"/><path d="M6 5 V2 H10 V5"/>',
    "optical": '<circle cx="8" cy="8" r="6"/><circle cx="8" cy="8" r="1.5"/>',
    "computer": '<rect x="2" y="2.5" width="12" height="8"/><path d="M5 14 H11 M8 10.5 V14"/>',
    "network": '<circle cx="8" cy="8" r="6"/><path d="M2 8 H14 M8 2 C5 5 5 11 8 14 M8 2 C11 5 11 11 8 14"/>',
}


def sym16(key):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none" '
            f'stroke="{SIDE}" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round">{SYM[key]}</svg>\n')


SIDEBAR = {
    "places": {
        "home": ["user-home", "folder-home", "go-home"], "desktop": ["user-desktop"], "documents": ["folder-documents"],
        "downloads": ["folder-download"], "music": ["folder-music"], "pictures": ["folder-pictures"],
        "videos": ["folder-videos"], "templates": ["folder-templates"], "share": ["folder-publicshare"],
        "folder": ["folder", "inode-directory", "folder-open", "folder-drag-accept", "folder-visiting"],
        "recent": ["document-open-recent", "folder-recent"], "trash": ["user-trash", "user-trash-full"],
        "bookmark": ["user-bookmarks", "bookmark-new"], "network": ["folder-remote", "network-workgroup", "network-server"],
    },
    "devices": {
        "drive": ["drive-harddisk", "drive-harddisk-system", "drive-multidisk"],
        "removable": ["drive-removable-media", "drive-harddisk-usb", "media-removable", "media-flash"],
        "optical": ["drive-optical", "media-optical"], "computer": ["computer", "video-display"],
    },
}
for ctx, groups in SIDEBAR.items():
    for key, names in groups.items():
        write(f"16/{ctx}", sym16(key), names)

(ROOT / "index.theme").write_text(f"""[Icon Theme]
Name={NAME}
Comment=Wangan asa: blue instrument plates for folders, white spec sheets for documents, plain 16px line icons
Inherits=Adwaita,hicolor
Example=folder

Directories=16/places,16/devices,scalable/places,scalable/mimetypes,scalable/devices

[16/places]
Size=16
Context=Places
Type=Fixed

[16/devices]
Size=16
Context=Devices
Type=Fixed

[scalable/places]
Size=64
MinSize=20
MaxSize=512
Context=Places
Type=Scalable

[scalable/mimetypes]
Size=64
MinSize=16
MaxSize=512
Context=MimeTypes
Type=Scalable

[scalable/devices]
Size=64
MinSize=20
MaxSize=512
Context=Devices
Type=Scalable
""")
subprocess.run(["gtk-update-icon-cache", "-f", "-t", str(ROOT)], check=False,
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(f"{NAME} icons written to {ROOT}")
