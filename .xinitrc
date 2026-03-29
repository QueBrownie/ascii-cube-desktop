#!/bin/sh
# .xinitrc — started by `startx`
# Copy this to ~/.xinitrc

# Set a plain black root window (fallback, cube will draw over it)
xsetroot -solid black

# Hide the mouse cursor when idle (requires unclutter)
unclutter --timeout 1 &

# Start bspwm (bspwmrc handles picom + cube launch)
exec bspwm
