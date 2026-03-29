#!/usr/bin/env python3
"""
Spinning ASCII wireframe cube.
Designed to run inside xwinwrap as a desktop background.

Usage:
    python3 cube.py               # run in current terminal
    xwinwrap ... -- xterm -into WID -bg black -e python3 cube.py
"""

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

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)

    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)   # edges
    curses.init_pair(2, curses.COLOR_WHITE, -1)   # vertices

    ax = 0.0   # rotation angle around X
    ay = 0.0   # rotation angle around Y
    az = 0.0   # slow roll around Z

    SPEED_X = 0.018
    SPEED_Y = 0.027
    SPEED_Z = 0.007

    while True:
        key = stdscr.getch()
        if key in (ord('q'), ord('Q'), 27):  # q or ESC to quit
            break

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
        time.sleep(1 / 30)


if __name__ == '__main__':
    curses.wrapper(main)
