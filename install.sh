#!/usr/bin/env bash
# install.sh — sets up the ascii-cube-desktop on Arch Linux
# Run as your normal user (sudo will be prompted where needed)

set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> Installing packages..."
sudo pacman -S --needed --noconfirm \
    xorg-server \
    xorg-xinit \
    xorg-xsetroot \
    xterm \
    bspwm \
    sxhkd \
    picom \
    kitty \
    python \
    ttf-jetbrains-mono-nerd \
    unclutter \
    ly

echo ""
echo "==> NOTE: xwinwrap must be installed from the AUR."
echo "    If you have yay:  yay -S xwinwrap-git"
echo "    If you have paru: paru -S xwinwrap-git"
echo ""

# ── Copy configs ───────────────────────────────────────────────────────────────

echo "==> Copying configs..."

mkdir -p ~/.config/bspwm ~/.config/picom ~/.config/kitty ~/.config/cube

cp "$REPO_DIR/config/bspwm/bspwmrc"   ~/.config/bspwm/bspwmrc
cp "$REPO_DIR/config/bspwm/sxhkdrc"   ~/.config/bspwm/sxhkdrc
cp "$REPO_DIR/config/picom/picom.conf" ~/.config/picom/picom.conf
cp "$REPO_DIR/config/kitty/kitty.conf" ~/.config/kitty/kitty.conf

# ── Install cube ───────────────────────────────────────────────────────────────

cp "$REPO_DIR/cube.py"        ~/.config/cube/cube.py
cp "$REPO_DIR/launch_cube.sh" ~/.config/cube/launch_cube.sh

chmod +x ~/.config/bspwm/bspwmrc
chmod +x ~/.config/cube/launch_cube.sh

# ── .xinitrc ───────────────────────────────────────────────────────────────────

if [ -f ~/.xinitrc ]; then
    echo "==> ~/.xinitrc already exists — skipping (manual merge may be needed)"
    echo "    Reference: $REPO_DIR/.xinitrc"
else
    cp "$REPO_DIR/.xinitrc" ~/.xinitrc
    chmod +x ~/.xinitrc
    echo "==> ~/.xinitrc installed"
fi

# ── ly login manager ───────────────────────────────────────────────────────────

echo ""
echo "==> Enabling ly display manager..."
sudo systemctl enable ly.service

echo ""
echo "================================================"
echo "  Install complete."
echo ""
echo "  Next steps:"
echo "  1. Install xwinwrap from AUR (see above)"
echo "  2. Reboot — ly will greet you at login"
echo "  3. Log in, then: startx"
echo "  4. Black screen + spinning cube = success"
echo "  5. Ctrl+T to open a terminal"
echo "================================================"
