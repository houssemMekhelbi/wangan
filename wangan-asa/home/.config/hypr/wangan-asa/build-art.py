#!/usr/bin/env python3
"""Generate the Wangan asa art: everything that is an image rather than CSS.

  ~/.config/hypr/wangan-asa/wallpaper.svg, wallpaper.png   1920x1080: long-exposure light trails on
        an elevated expressway curve over the bay (left-hand traffic: red leaves, white
        and amber arrive), at dawn. The road is laid out on a ground plane and projected
        through a pinhole camera, so the trails taper by themselves. The left of the
        picture is kept calm for windows.
  ~/.config/hypr/wangan-asa/lock-arc.png      the lock's dial without sweep and needle (what the lock
        shows until ~/.local/bin/wangan-lock-arc has rendered the current time)
  ~/.config/hypr/wangan-asa/lock-field.png    400x54 the password capsule with the blue crescent
  ~/.config/waybar/wangan-asa/ws-<slot>-<state>.png   26x36 gear knobs 1-10 in five states: odd gears
        above the neutral rail, even gears below it
  ~/.config/waybar/wangan-asa/ws.css          the rules that pick them (imported by style.css)
  ~/.config/gtk-3.0/wangan-asa/crumb-dot.png  Thunar path separator

Deterministic; edit and re-run (needs rsvg-convert and the theme's fonts):  python3 build-art.py
"""

import math
import os
import random
import subprocess
import sys
from pathlib import Path

CONF = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
HYPR = CONF / "hypr/wangan-asa"
BAR = CONF / "waybar/wangan-asa"
GTK = CONF / "gtk-3.0/wangan-asa"

GROUND, PANEL, SEL, LINE, RING, MUTED, TEXT = "#E4E8EE", "#F2F4F8", "#D5DCE7", "#B7C0CD", "#A9B3C2", "#4E596B", "#10151D"
LCD, BLUE, BLUE_T, RAILC, AMBER_FILL, ON_AMBER, RED_FILL = "#DDE3EB", "#2A5FC4", "#1F4FA8", "#9DB4E0", "#F2A33A", "#10151D", "#D41F27"

# wallpaper colours per variant
WALL = dict(
    yoru=dict(sky=("#05070C", "#080C17", "#0E1730", "#1A2848", "#0A0E17", "#080B12", "#06080C"), horizon="#1A2848", band="#3A5590",
              water="#06080C", water_op=0.55, sky_far="#0D1320", sky_near="#07090F", lights=1.0, ripple="#5B8DEF", ripple_op=1.0,
              wall="#1B222D", wall2="#171D26", wall_near="#0E1218", top="#4A5670", dash="#C9D2E0", dash_op=0.20, edge_op=0.14,
              road=("#1A1F29", "#141922", "#0D1016"), pole="#2C3646", pier="#0A0D12", lamp="#FFE2B0", halo=1.0, glow=1.0,
              trail_white="#EEF1F5", sodium=0.26, cityblue=0.26, vig="#000", vig_op=0.62, calm="#05070A", grain=0.10, haze=0.20),
    asa=dict(sky=("#9FB4D6", "#BCCBE3", "#E2DCE0", "#F6D3B2", "#C3CEDC", "#B7C3D3", "#A9B6C8"), horizon="#F6D3B2", band="#F3C9A6",
             water="#C3CEDC", water_op=0.0, sky_far="#A3B0C6", sky_near="#8C9AB2", lights=0.35, ripple="#FFFFFF", ripple_op=3.0,
             wall="#98A3B4", wall2="#8C97A9", wall_near="#7C8798", top="#E6EBF2", dash="#F7F9FC", dash_op=0.70, edge_op=0.50,
             road=("#B9C1CD", "#A9B2C0", "#949EAE"), pole="#5E6A7C", pier="#AAB6C8", lamp="#FFF1D6", halo=0.35, glow=0.55,
             trail_white="#FFF6E6", sodium=0.34, cityblue=0.0, vig="#5B6B85", vig_op=0.28, calm="#E4E8EE", grain=0.05, haze=0.30),
)
K = WALL["asa"]


def render(svg, out, keep=False):
    out.parent.mkdir(parents=True, exist_ok=True)
    src = out.with_suffix(".svg")
    src.write_text(svg)
    subprocess.run(["rsvg-convert", "-o", str(out), str(src)], check=True)
    if not keep:
        src.unlink()


# ---- wallpaper -------------------------------------------------------------------
def wallpaper():
    global glow_w, glow_r, core
    W, H = 1920, 1080
    F, CX, HOR, CAM = 1150.0, 900.0, 520.0, 13.0          # focal length px, principal point, horizon, camera height m
    AMBER, RED, BLUE, WHITE = "#F2A33A", "#E5252A", "#2A5FC4", K["trail_white"]
    rnd = random.Random(11)

    # ---- centre line: near straight heading right, a long left-hand bend, a far straight leaving to the left
    TH0, S1, R, TH1 = 0.50, 46.0, 118.0, -1.47
    pts, x, z, th, s, ds = [], 1.0, 9.0, TH0, 0.0, 1.0
    while s < 900:
        pts.append((x, z, th))
        if s > S1 and th > TH1:
            th -= ds / R
        x += math.sin(th) * ds; z += math.cos(th) * ds; s += ds


    def proj(X, Y, Z):
        return CX + F * X / Z, HOR + F * (CAM - Y) / Z


    def edge(u, Y=0.0, s0=0, s1=None):
        """screen points of the line at lateral offset u (m, + = right of travel away from camera), height Y"""
        out = []
        for (x, z, th) in pts[s0:s1]:
            X, Z = x + math.cos(th) * u, z - math.sin(th) * u
            if Z < 4:
                continue
            out.append((*proj(X, Y, Z), Z))
        return out


    def ribbon(u, w, Y=0.0, s0=0, s1=None, minpx=1.1):
        a, b = [], []
        uf = u if callable(u) else (lambda k, _u=u: _u)
        for k, (x, z, th) in enumerate(pts[s0:s1]):
            u = uf(k + s0)
            for side, acc in ((-1, a), (1, b)):
                Zc = z - math.sin(th) * u
                if Zc < 4:
                    continue
                ww = max(w, minpx * Zc / F)
                uu = u + side * ww / 2
                X, Z = x + math.cos(th) * uu, z - math.sin(th) * uu
                if Z < 4:
                    continue
                acc.append(proj(X, Y, Z))
        if len(a) < 2 or len(b) < 2:
            return ""
        return "M" + " L".join(f"{px:.1f},{py:.1f}" for px, py in a + b[::-1]) + " Z"


    def strip(u0, Y0, u1, Y1):
        a, b = edge(u0, Y0), edge(u1, Y1)
        return "M" + " L".join(f"{px:.1f},{py:.1f}" for px, py, _ in a + b[::-1]) + " Z"


    HALF = 12.4      # half width of the deck: 3 lanes + shoulder each way, median 1.2 m
    road = strip(-HALF, 0, HALF, 0)
    walls = "".join(f'<path d="{strip(u, 0, u, 1.05)}" fill="{c}"/>' for u, c in ((HALF, K["wall"]), (0.6, K["wall2"]), (-0.6, K["wall2"])))
    wall_near = f'<path d="{strip(-HALF, 0, -HALF, 1.05)}" fill="{K["wall_near"]}"/>'
    tops = "".join(f'<path d="{ribbon(u, 0.10, 1.05, minpx=0.9)}" fill="{K["top"]}" opacity="{o}"/>' for u, o in ((HALF, 0.8), (0.0, 0.7), (-HALF, 0.55)))
    # lane dashes
    dashes = ""
    for u in (-8.3, -4.8, 4.8, 8.3):
        for k in range(0, 420, 12):
            dashes += f'<path d="{ribbon(u, 0.16, 0.0, k, k + 5, minpx=0.0)}" fill="{K["dash"]}" opacity="{K["dash_op"]}"/>'
    for u in (-11.4, -1.4, 1.4, 11.4):
        dashes += f'<path d="{ribbon(u, 0.14, 0.0, minpx=0.0)}" fill="{K["dash"]}" opacity="{K["edge_op"]}"/>'

    # ---- trails. Left-hand traffic: the carriageway on the left (u<0) leaves (red), the one on the right comes toward us (white/amber)
    glow_w, glow_r, core = "", "", ""
    def smooth(t):
        t = min(1.0, max(0.0, t)); return t * t * (3 - 2 * t)
    def car(u, tint, red, op, change=None):
        global glow_w, glow_r, core
        half = rnd.uniform(0.62, 0.78)
        Y = 0.85 if red else 0.65
        w = rnd.uniform(0.09, 0.16) if red else rnd.uniform(0.10, 0.22)
        for side in (-1, 1):
            if change:
                k0, du = change
                uf = lambda k, _b=u + side * half, _k0=k0, _du=du: _b + _du * smooth((k - _k0) / 70.0)
            else:
                uf = u + side * half
            d = ribbon(uf, w, Y)
            dg = ribbon(uf, w * 3.4, Y, minpx=3.0)
            hot = ribbon(uf, w * 0.35, Y, minpx=0.6)
            if red:
                glow_r += f'<path d="{dg}" fill="{RED}" opacity="{op * 0.85 * K["glow"]:.2f}"/>'
                core += f'<path d="{d}" fill="{tint}" opacity="{op:.2f}"/><path d="{hot}" fill="#FFB0A6" opacity="{op * 0.8:.2f}"/>'
            else:
                glow_w += f'<path d="{dg}" fill="{AMBER if tint != WHITE else "#F3C88C"}" opacity="{op * 0.75 * K["glow"]:.2f}"/>'
                core += f'<path d="{d}" fill="{tint}" opacity="{op:.2f}"/>'
    reds = [(-10.1, 0.95, None), (-9.4, 0.45, None), (-6.9, 0.8, None), (-6.2, 1.0, (120, 3.4)), (-3.3, 0.55, None), (-2.7, 0.9, None)]
    for u, op, ch in reds:
        car(u, rnd.choice(("#FF4A40", "#FF3B33", "#FF5E52")), True, op, ch)
    whites = [(2.8, 1.0, None), (3.5, 0.5, None), (6.2, 0.9, None), (7.0, 0.6, (90, 3.2)), (9.7, 1.0, None), (10.4, 0.45, None)]
    for i, (u, op, ch) in enumerate(whites):
        car(u, (WHITE, "#FFD79A", WHITE, "#FFE9C8", WHITE, "#FFC978")[i], False, op, ch)

    # ---- reflector posts on the barriers, sodium lamps on the median
    posts, post_glow = "", ""
    for u, col in ((HALF, WHITE), (0.0, AMBER), (-HALF, WHITE)):
        for k in range(4, 760, 7):
            x, z, th = pts[k]
            X, Z = x + math.cos(th) * u, z - math.sin(th) * u
            if Z < 6:
                continue
            px, py = proj(X, 1.15, Z)
            if not (-20 < px < W + 20):
                continue
            r = max(0.75, F * 0.075 / Z)
            posts += f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r:.2f}" fill="{col}" opacity="{min(1.0, 0.45 + 12 / Z):.2f}"/>'
            if Z < 120:
                post_glow += f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r * 3:.2f}" fill="{col}" opacity="0.35"/>'
    lamps, halos, pools, poles = "", "", "", ""
    for k in range(52, 860, 34):
        x, z, th = pts[k]
        ub, ul = HALF + 0.3, HALF - 3.2                     # pole on the outer barrier, arm reaching over the slow lane
        Xb, Zb = x + math.cos(th) * ub, z - math.sin(th) * ub
        Xl, Zl = x + math.cos(th) * ul, z - math.sin(th) * ul
        if Zb < 8:
            continue
        bx, by = proj(Xb, 0.9, Zb); tx_, ty_ = proj(Xb, 10.2, Zb); px, py = proj(Xl, 10.6, Zl)
        if not (-200 < px < W + 200):
            continue
        r = max(0.9, F * 0.16 / Zl)
        pw = max(0.8, F * 0.14 / Zb)
        poles += f'<path d="M{bx:.1f},{by:.1f} L{tx_:.1f},{ty_:.1f} L{px:.1f},{py:.1f}" fill="none" stroke="{K["pole"]}" stroke-width="{pw:.2f}" stroke-linejoin="round"/>'
        halos += f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{max(11.0, F * 4.6 / Zl):.1f}" fill="url(#halo)"/>'
        lamps += f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="{r * 1.6:.2f}" ry="{max(0.8, r * 0.7):.2f}" fill="{K["lamp"]}"/>'
        gx, gy = proj(Xl, 0, Zl)
        pools += f'<ellipse cx="{gx:.1f}" cy="{gy:.1f}" rx="{F * 8 / Zl:.1f}" ry="{max(1.5, F * CAM * 8 / (Zl * Zl)):.1f}" fill="url(#pool)"/>'

    # ---- piers under the far viaduct, where the deck crosses the bay
    piers = ""
    for k in range(330, 820, 34):
        x, z, th = pts[k]
        px, py = proj(x, -0.8, z)
        _, py2 = proj(x, -16, z)
        wpx = F * 3.2 / z
        piers += f'<rect x="{px - wpx / 2:.1f}" y="{py:.1f}" width="{wpx:.1f}" height="{py2 - py:.1f}" fill="{K["pier"]}"/>'
    deck = f'<path d="{strip(-HALF, -0.2, -HALF, -1.9)}" fill="{K["pier"]}"/>'

    # ---- skyline: two layers of plain blocks, a few lit windows, aviation lights
    def skyline(seed, base, hmin, hmax, fill, x0=-20, x1=W + 20, damp=None):
        r = random.Random(seed)
        out, lights, x = "", "", x0
        while x < x1:
            w = r.choice((r.uniform(14, 26), r.uniform(30, 60), r.uniform(30, 60), r.uniform(60, 100)))
            h = r.uniform(hmin, hmax) * (r.choice((0.5, 0.7, 1.0, 1.0, 1.5)))
            if damp:
                h *= damp(x)
            out += f'<rect x="{x:.0f}" y="{base - h:.0f}" width="{w + 1:.0f}" height="{h + 2:.0f}" fill="{fill}"/>'
            if h > 60 and r.random() < 0.7:
                lights += f'<circle cx="{x + w / 2:.0f}" cy="{base - h - 3:.0f}" r="1.5" fill="{RED}" opacity="0.85"/>'
            for _ in range(int(w * h / 420)):
                wx, wy = x + r.uniform(3, w - 3), base - r.uniform(4, max(5, h - 4))
                lights += f'<rect x="{wx:.0f}" y="{wy:.0f}" width="2" height="2" fill="{r.choice(("#F2C98A", "#F2C98A", "#BFD2F5", "#F2A33A"))}" opacity="{r.uniform(0.12, 0.5) * K["lights"]:.2f}"/>'
            x += w + r.choice((0, 0, 0, 6, 14))
        return out, lights
    damp = lambda x: 0.55 + 0.45 * min(1.0, max(0.0, (x - 300) / 900))
    far, far_l = skyline(5, HOR + 4, 30, 90, K["sky_far"], damp=damp)
    near, near_l = skyline(9, HOR + 10, 18, 60, K["sky_near"], damp=damp)
    # reflections of the city in the bay: short vertical streaks
    refl, r = "", random.Random(21)
    for _ in range(170):
        t = r.uniform(0, 1) ** 1.8
        x, y = r.uniform(0, 1700), HOR + 14 + t * 50
        refl += f'<rect x="{x:.0f}" y="{y:.0f}" width="{r.uniform(6, 30) * (0.6 + t):.0f}" height="1" fill="{r.choice(("#F2C98A", "#5B8DEF", "#F2A33A", "#8FA6CC"))}" opacity="{r.uniform(0.06, 0.26) * (1 - 0.6 * t) * K["lights"]:.2f}"/>'

    # far shore on the right of the deck: a dark industrial flat with scattered lights, denser toward the horizon
    for _ in range(260):
        t = r.uniform(0, 1) ** 2.2
        x, y = r.uniform(1050, W), HOR + 13 + t * 230
        if y > HOR + 60 and x < 1320:
            continue
        sz = 1 + (t > 0.35) + (t > 0.7)
        refl += f'<rect x="{x:.0f}" y="{y:.0f}" width="{sz}" height="{sz}" fill="{r.choice(("#F2C98A", "#F2A33A", "#F2A33A", "#BFD2F5"))}" opacity="{r.uniform(0.15, 0.6) * K["lights"]:.2f}"/>'
    for _ in range(60):
        t = r.uniform(0, 1)
        x, y = r.uniform(-100, 1000), HOR + 80 + t * 470
        refl += f'<rect x="{x:.0f}" y="{y:.0f}" width="{r.uniform(30, 140) * (0.5 + t):.0f}" height="1" fill="{K["ripple"]}" opacity="{r.uniform(0.03, 0.09) * K["ripple_op"]:.2f}"/>'

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
    <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">{"".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in zip((0, 0.26, 0.42, 0.482, 0.495, 0.62, 1), K["sky"]))}</linearGradient>
    <radialGradient id="sodium" gradientUnits="userSpaceOnUse" cx="1420" cy="{HOR + 40}" r="760" gradientTransform="translate(0 {HOR * 0.45:.0f}) scale(1 0.55)"><stop offset="0" stop-color="{AMBER}" stop-opacity="{K["sodium"]}"/><stop offset="0.45" stop-color="{AMBER}" stop-opacity="{K["sodium"] * 0.27:.3f}"/><stop offset="1" stop-color="{AMBER}" stop-opacity="0"/></radialGradient>
    <radialGradient id="cityblue" gradientUnits="userSpaceOnUse" cx="520" cy="{HOR}" r="900" gradientTransform="translate(0 {HOR * 0.7:.0f}) scale(1 0.30)"><stop offset="0" stop-color="{BLUE}" stop-opacity="{K["cityblue"]}"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></radialGradient>
    <radialGradient id="halo"><stop offset="0" stop-color="#FFD9A0" stop-opacity="{0.55 * K["halo"]:.2f}"/><stop offset="0.25" stop-color="{AMBER}" stop-opacity="{0.20 * K["halo"]:.2f}"/><stop offset="1" stop-color="{AMBER}" stop-opacity="0"/></radialGradient>
    <radialGradient id="pool"><stop offset="0" stop-color="{AMBER}" stop-opacity="{0.16 * K["halo"]:.2f}"/><stop offset="1" stop-color="{AMBER}" stop-opacity="0"/></radialGradient>
    <linearGradient id="roadfill" gradientUnits="userSpaceOnUse" x1="0" y1="{HOR}" x2="0" y2="{H}"><stop offset="0" stop-color="{K["road"][0]}"/><stop offset="0.3" stop-color="{K["road"][1]}"/><stop offset="1" stop-color="{K["road"][2]}"/></linearGradient>
    <linearGradient id="fadeleft" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="1100" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="0.35" stop-color="#fff" stop-opacity="0.25"/><stop offset="1" stop-color="#fff" stop-opacity="1"/></linearGradient>
    <linearGradient id="hazefade" x1="0" y1="0" x2="1" y2="0"><stop offset="0.25" stop-color="#fff" stop-opacity="0"/><stop offset="0.8" stop-color="#fff" stop-opacity="1"/></linearGradient><mask id="hm"><rect width="{W}" height="{H}" fill="url(#hazefade)"/></mask>
    <linearGradient id="band" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{K["band"]}" stop-opacity="0"/><stop offset="1" stop-color="{K["band"]}" stop-opacity="0.55"/></linearGradient>
    <mask id="m"><rect width="{W}" height="{H}" fill="url(#fadeleft)"/></mask>
    <radialGradient id="vig" gradientUnits="userSpaceOnUse" cx="1250" cy="640" r="1300"><stop offset="0.45" stop-color="{K["vig"]}" stop-opacity="0"/><stop offset="1" stop-color="{K["vig"]}" stop-opacity="{K["vig_op"]}"/></radialGradient>
    <linearGradient id="calm" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{K["calm"]}" stop-opacity="0.55"/><stop offset="0.55" stop-color="{K["calm"]}" stop-opacity="0"/></linearGradient>
    <filter id="b4" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation="4"/></filter>
    <filter id="b14" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation="16"/></filter>
    <filter id="b2" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation="2.2"/></filter>
    <filter id="haze" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.0016 0.006" numOctaves="4" seed="7"/><feColorMatrix values="0 0 0 0 0.95  0 0 0 0 0.64  0 0 0 0 0.23  0 0 0 0.9 -0.36"/></filter>
    <filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed="4"/><feColorMatrix values="0 0 0 0 0.9  0 0 0 0 0.93  0 0 0 0 1  0 0 0 {K["grain"]} 0"/></filter>
    </defs>
    <rect width="{W}" height="{H}" fill="url(#sky)"/>
    <rect width="{W}" height="{HOR + 20}" fill="url(#cityblue)"/>
    <rect width="{W}" height="{H}" fill="url(#sodium)"/>
    <rect width="{W}" height="{HOR + 6}" filter="url(#haze)" opacity="{K["haze"]}" mask="url(#hm)"/>
    <rect y="{HOR + 10}" width="{W}" height="{H - HOR - 10}" fill="{K["water"]}" opacity="{K["water_op"]}"/>
    <rect y="{HOR - 26}" width="{W}" height="32" fill="url(#band)"/>
    {far}<g opacity="0.8">{far_l}</g>
    <rect y="{HOR - 50}" width="{W}" height="60" fill="{K["horizon"]}" opacity="0.30"/>
    {near}{near_l}
    {refl}
    <g mask="url(#m)">
    {piers}{deck}
    <path d="{road}" fill="url(#roadfill)"/>
    {pools}
    {dashes}
    <g filter="url(#b14)" opacity="{0.55 * K["glow"]:.2f}">{glow_w}{glow_r}</g>
    {walls}
    {poles}
    <g filter="url(#b4)">{glow_w}{glow_r}</g>
    {core}
    {tops}
    <g filter="url(#b2)">{post_glow}</g>
    {posts}
    {halos}{lamps}
    {wall_near}
    </g>
    <rect width="{W}" height="{H}" fill="url(#calm)"/>
    <rect width="{W}" height="{H}" fill="url(#vig)"/>
    <rect width="{W}" height="{H}" filter="url(#grain)"/>
    </svg>'''
    render(svg, HYPR / "wallpaper.png", keep=True)


# ---- workspaces: gear knobs --------------------------------------------------------
def workspaces():
    """26x36 per slot and state. The rail runs through every image; odd gears sit above
    it, even gears below. The focused gear glows (baked in: GTK3 shadows stop at the box)."""
    states = {"empty": (MUTED, LCD, LINE), "occupied": (TEXT, SEL, BLUE), "active": (BLUE_T, LCD, BLUE_T),
              "focused": (ON_AMBER, AMBER_FILL, AMBER_FILL), "urgent": ("#FFFFFF", RED_FILL, RED_FILL)}
    css = ["/* Generated by ~/.config/hypr/wangan-asa/build-art.py: the gear knob image for every slot and state. */"]
    for n in range(1, 11):
        cy = 10.5 if n % 2 else 25.5
        for state, (fg, bg, ring) in states.items():
            glow = (f'<circle cx="13" cy="{cy}" r="9.5" fill="{AMBER_FILL}" opacity="0.55" filter="url(#g)"/>' if state == "focused" else "")
            size = 8.5 if n < 10 else 7.2
            svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="26" height="36" viewBox="0 0 26 36">'
                   f'<defs><filter id="g" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.6"/></filter></defs>'
                   f'<rect x="0" y="16" width="26" height="4" fill="{RAILC}"/>{glow}'
                   f'<circle cx="13" cy="{cy}" r="8" fill="{bg}" stroke="{ring}" stroke-width="1"/>'
                   f'<text x="13" y="{cy + size * 0.36:.2f}" text-anchor="middle" font-family="Zen Dots" font-size="{size}" fill="{fg}">{n}</text></svg>')
            render(svg, BAR / f"ws-{n}-{state}.png")
            sel = f"#custom-ws-{n}" if state == "occupied" else f"#custom-ws-{n}.{state}"
            css.append(f'{sel} {{ background-image: url("ws-{n}-{state}.png"); }}')
    (BAR / "ws.css").write_text("\n".join(css) + "\n")


def crumb():
    render(f'<svg xmlns="http://www.w3.org/2000/svg" width="10" height="18" viewBox="0 0 10 18"><circle cx="5" cy="9" r="2" fill="{RING}"/></svg>',
           GTK / "crumb-dot.png")


# ---- lock ------------------------------------------------------------------------
def lock():
    helper = Path.home() / ".local/bin/wangan-lock-arc"
    subprocess.run([sys.executable, str(helper), "--static", str(HYPR / "lock-arc.png")], check=True)
    w, h, r = 400, 54, 27
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
           f'<defs><clipPath id="low"><rect x="0" y="{h - 20}" width="{w}" height="20"/></clipPath></defs>'
           f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="{r - 0.5}" fill="{PANEL}" fill-opacity="0.90" stroke="{LINE}"/>'
           f'<rect x="1.5" y="1.5" width="{w - 3}" height="{h - 3}" rx="{r - 1.5}" fill="none" stroke="{BLUE}" stroke-width="2" clip-path="url(#low)"/>'
           f'<circle cx="26" cy="{h / 2}" r="4.5" fill="{AMBER_FILL}"/></svg>')
    render(svg, HYPR / "lock-field.png")


if __name__ == "__main__":
    wallpaper()
    workspaces()
    crumb()
    lock()
    print("art written under", CONF)
