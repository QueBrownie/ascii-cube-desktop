#!/usr/bin/env python3
"""
Spinning ASCII wireframe cube.
Designed to run inside xwinwrap as a desktop background.

Usage:
    python3 cube.py               # run in current terminal
    xwinwrap ... -- xterm -into WID -bg black -e python3 cube.py
"""

import colorsys
import curses
import math
import time

# ── Rotation helpers ───────────────────────────────────────────────────────────

def rot_x(v, a):
    x, y, z = v
    c, s = math.cos(a), math.sin(a)
    return (x, y * c - z * s, y * s + z * c)

def rot_y(v, a):
    x, y, z = v
    c, s = math.cos(a), math.sin(a)
    return (x * c + z * s, y, -x * s + z * c)

def rot_z(v, a):
    x, y, z = v
    c, s = math.cos(a), math.sin(a)
    return (x * c - y * s, x * s + y * c, z)

# ── Projection ─────────────────────────────────────────────────────────────────

def project(v, w, h, fov=4.5, dist=5.0):
    x, y, z = v
    z += dist
    if abs(z) < 0.001:
        z = 0.001
    f = fov / z
    # Terminals are ~2x taller per cell than wide — compensate on y
    sx = int(x * f * (w / 9)  + w / 2)
    sy = int(y * f * (h / 4.5) + h / 2)
    return sx, sy

# ── Line drawing (Bresenham) ───────────────────────────────────────────────────

def draw_line(scr, x0, y0, x1, y1, char, H, W):
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    while True:
        if 0 <= x0 < W and 0 <= y0 < H:
            try:
                scr.addch(y0, x0, char)
            except curses.error:
                pass
        if x0 == x1 and y0 == y1:
            break
        e2 = err * 2
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy

def edge_char(x0, y0, x1, y1):
    """Pick the ASCII character that best matches the edge angle."""
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    if dy == 0:
        return '-'
    if dx == 0:
        return '|'
    ratio = dx / dy
    if ratio > 2.5:
        return '-'
    if ratio < 0.4:
        return '|'
    return '/' if (x1 - x0) * (y1 - y0) < 0 else '\\'

# ── Cube geometry ──────────────────────────────────────────────────────────────

VERTICES = [
    (-1, -1, -1), ( 1, -1, -1), ( 1,  1, -1), (-1,  1, -1),  # back face
    (-1, -1,  1), ( 1, -1,  1), ( 1,  1,  1), (-1,  1,  1),  # front face
]

EDGES = [
    (0, 1), (1, 2), (2, 3), (3, 0),  # back face
    (4, 5), (5, 6), (6, 7), (7, 4),  # front face
    (0, 4), (1, 5), (2, 6), (3, 7),  # connecting edges
]

# ── Main loop ──────────────────────────────────────────────────────────────────

def hsv_to_curses(h, s=1.0, v=1.0):
    """Convert HSV (0–1 each) to a curses 0–1000 RGB triple."""
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return int(r * 1000), int(g * 1000), int(b * 1000)


def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)

    curses.start_color()
    curses.use_default_colors()

    # Use high color indices so we don't clobber the 16 standard colors
    COLOR_EDGE   = 16
    COLOR_VERTEX = 17

    rgb_supported = curses.can_change_color() and curses.COLORS >= 256
    if rgb_supported:
        curses.init_color(COLOR_EDGE,   0, 1000, 0)   # initial green — overwritten each frame
        curses.init_color(COLOR_VERTEX, 1000, 1000, 1000)
        curses.init_pair(1, COLOR_EDGE,   -1)
        curses.init_pair(2, COLOR_VERTEX, -1)
    else:
        # Fallback: cycle through the 6 basic curses colors manually
        CYCLE = [curses.COLOR_RED, curses.COLOR_YELLOW, curses.COLOR_GREEN,
                 curses.COLOR_CYAN, curses.COLOR_BLUE, curses.COLOR_MAGENTA]
        curses.init_pair(1, curses.COLOR_GREEN, -1)
        curses.init_pair(2, curses.COLOR_WHITE,  -1)

    ax = 0.0   # rotation angle around X
    ay = 0.0   # rotation angle around Y
    az = 0.0   # slow roll around Z

    hue = 0.0          # current hue position (0–1)
    HUE_SPEED = 0.004  # how fast the rainbow cycles

    SPEED_X = 0.018
    SPEED_Y = 0.027
    SPEED_Z = 0.007

    frame = 0

    while True:
        key = stdscr.getch()
        if key in (ord('q'), ord('Q'), 27):  # q or ESC to quit
            break

        # ── Update RGB color ───────────────────────────────────────────────────
        hue = (hue + HUE_SPEED) % 1.0
        if rgb_supported:
            curses.init_color(COLOR_EDGE,   *hsv_to_curses(hue))
            curses.init_color(COLOR_VERTEX, *hsv_to_curses((hue + 0.5) % 1.0))
        else:
            idx = int(hue * len(CYCLE)) % len(CYCLE)
            curses.init_pair(1, CYCLE[idx], -1)

        stdscr.erase()
        H, W = stdscr.getmaxyx()

        # Rotate all vertices
        rotated = []
        for v in VERTICES:
            v = rot_x(v, ax)
            v = rot_y(v, ay)
            v = rot_z(v, az)
            rotated.append(v)

        # Project to screen
        pts = [project(v, W, H) for v in rotated]

        # Draw edges
        for a, b in EDGES:
            x0, y0 = pts[a]
            x1, y1 = pts[b]
            ch = edge_char(x0, y0, x1, y1)
            draw_line(stdscr, x0, y0, x1, y1, ch, H - 1, W)

        # Draw vertices as bright corners
        for sx, sy in pts:
            if 0 <= sx < W and 0 <= sy < H - 1:
                try:
                    stdscr.addch(sy, sx, '+', curses.color_pair(2) | curses.A_BOLD)
                except curses.error:
                    pass

        stdscr.refresh()

        ax += SPEED_X
        ay += SPEED_Y
        az += SPEED_Z
        frame += 1
        time.sleep(1 / 30)


if __name__ == '__main__':
    curses.wrapper(main)
