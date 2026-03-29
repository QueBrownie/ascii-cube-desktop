#!/usr/bin/env bash
# install.sh — sets up the ascii-cube-desktop on Arch Linux
# Run as your normal user (sudo will be prompted where needed)
#
# GPU passthrough is NOT required. This script gets you a fully working
# cube desktop accessible from your Mac via RDP. Add the GPU later.

set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── Packages ───────────────────────────────────────────────────────────────────

echo "==> Installing packages from official repos..."
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
    ly \
    pipewire \
    pipewire-pulse \
    wireplumber

echo ""
echo "==> Installing AUR packages (requires yay)..."
if ! command -v yay &>/dev/null; then
    echo "ERROR: yay is not installed. Install it first:"
    echo "  git clone https://aur.archlinux.org/yay.git"
    echo "  cd yay && makepkg -si"
    exit 1
fi
yay -S --needed --noconfirm \
    xrdp \
    xorgxrdp \
    pipewire-module-xrdp \
    xwinwrap-git

echo ""

# ── Configs ────────────────────────────────────────────────────────────────────

echo "==> Copying configs..."

mkdir -p ~/.config/bspwm ~/.config/sxhkd ~/.config/picom ~/.config/kitty ~/.config/cube

cp "$REPO_DIR/config/bspwm/bspwmrc"   ~/.config/bspwm/bspwmrc
cp "$REPO_DIR/config/bspwm/sxhkdrc"   ~/.config/sxhkd/sxhkdrc
cp "$REPO_DIR/config/picom/picom.conf" ~/.config/picom/picom.conf
cp "$REPO_DIR/config/kitty/kitty.conf" ~/.config/kitty/kitty.conf

chmod +x ~/.config/bspwm/bspwmrc

# ── Cube ───────────────────────────────────────────────────────────────────────

cp "$REPO_DIR/cube.py"        ~/.config/cube/cube.py
cp "$REPO_DIR/launch_cube.sh" ~/.config/cube/launch_cube.sh
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

# ── xrdp session ───────────────────────────────────────────────────────────────
# Tell xrdp to launch bspwm when a client connects

echo "==> Configuring xrdp session..."

cat > ~/.xsession << 'EOF'
#!/bin/sh
# xrdp session entry point
xsetroot -solid black
unclutter --timeout 1 &
exec bspwm
EOF
chmod +x ~/.xsession

# ── xrdp service ───────────────────────────────────────────────────────────────

echo "==> Enabling xrdp..."
sudo systemctl enable xrdp.service
sudo systemctl enable xrdp-sesman.service

# Add user to the tsusers group required by xrdp
sudo usermod -aG tsusers "$USER"

# ── ly login manager ───────────────────────────────────────────────────────────

echo "==> Enabling ly..."
sudo systemctl enable ly.service

# ── Static IP reminder ─────────────────────────────────────────────────────────

echo ""
echo "==> ACTION REQUIRED: Set a static IP for this VM."
echo "    Edit /etc/systemd/network/20-wired.network or use nmtui."
echo "    You'll need this IP to connect from your Mac."
echo ""

# ── Done ───────────────────────────────────────────────────────────────────────

echo "================================================"
echo "  Install complete."
echo ""
echo "  Remaining steps:"
echo ""
echo "  1. Set a static IP for this VM (see above)"
echo ""
echo "  3. Reboot"
echo "     sudo reboot"
echo ""
echo "  4. On your Mac:"
echo "     - Install Microsoft Remote Desktop (App Store)"
echo "     - Add PC → enter this VM's IP"
echo "     - Enable 'Redirect clipboard' and 'Redirect sound'"
echo "     - Connect → log in via ly → cube desktop"
echo ""
echo "  5. Ctrl+T to open a terminal"
echo ""
echo "  GPU passthrough can be added later — see Notion for Phase 5-7."
echo "================================================"
