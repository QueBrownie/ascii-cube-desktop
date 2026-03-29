#!/usr/bin/env bash
# launch_cube.sh
# Embeds the spinning ASCII cube into the root window (desktop background)
# using xwinwrap. Run this from bspwmrc or .xinitrc before starting the WM.
#
# Requirements: xwinwrap, xterm, python3
# xwinwrap is in the AUR: yay -S xwinwrap-git

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CUBE="$SCRIPT_DIR/cube.py"

# Kill any existing cube instance
pkill -f "cube.py" 2>/dev/null

exec xwinwrap \
    -fs \
    -s \
    -sp \
    -b \
    -nf \
    -ov \
    -argb \
    -- xterm \
        -into WID \
        -bg black \
        -fg white \
        -fa "JetBrainsMono Nerd Font Mono" \
        -fs 14 \
        -bc \
        -bw 0 \
        -e python3 "$CUBE"
