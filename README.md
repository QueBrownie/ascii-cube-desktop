# ascii-cube-desktop

A minimal Linux desktop environment. The entire UI is a spinning ASCII cube.

```
         +--------+
        /|       /|
       / |      / |
      +--------+  |
      |  +-----|--+
      | /      | /
      |/       |/
      +--------+
```

- **Desktop:** spinning ASCII wireframe cube, nothing else
- **`Ctrl+T`** opens a terminal — the only entry point to the system
- No taskbar, dock, panel, launcher, or icons

---

## Stack

| Layer | Tool |
|-------|------|
| OS | Arch Linux (minimal) |
| Display Server | X11 |
| Window Manager | bspwm |
| Hotkey Daemon | sxhkd |
| Compositor | picom |
| Terminal | kitty |
| Cube renderer | Python 3 + curses |
| Desktop renderer | xwinwrap |
| Login Manager | ly |
| Font | JetBrainsMono Nerd Font |

---

## Install

### 1. Install Arch Linux (minimal)

Use the [Arch installation guide](https://wiki.archlinux.org/title/Installation_guide). Stop after a working base system with a user account — no desktop environment.

### 2. Clone this repo

```bash
git clone https://github.com/QueBrownie/ascii-cube-desktop.git
cd ascii-cube-desktop
```

### 3. Run the installer

```bash
chmod +x install.sh
./install.sh
```

### 4. Install xwinwrap (AUR)

xwinwrap is not in the official repos:

```bash
# With yay
yay -S xwinwrap-git

# Or manually
git clone https://aur.archlinux.org/xwinwrap-git.git
cd xwinwrap-git && makepkg -si
```

### 5. Reboot and start

```bash
reboot
# Log in via ly, then:
startx
```

---

## Usage

| Key | Action |
|-----|--------|
| `Ctrl+T` | Open terminal |
| `Super+Q` | Close window |
| `Super+F` | Toggle fullscreen |
| `Super+M` | Toggle monocle (one window, full screen) |
| `Super+1–5` | Switch workspace |
| `Super+Shift+1–5` | Move window to workspace |
| `Super+H/J/K/L` | Focus window (vim directions) |
| `Super+Shift+H/J/K/L` | Move window |
| `Super+Alt+Q` | Quit bspwm |

---

## File Structure

```
ascii-cube-desktop/
├── cube.py               # ASCII spinning cube (Python + curses)
├── launch_cube.sh        # Wraps cube in xwinwrap as desktop bg
├── install.sh            # Installs packages + copies configs
├── .xinitrc              # X session startup
└── config/
    ├── bspwm/
    │   ├── bspwmrc       # WM config — no bars, minimal borders
    │   └── sxhkdrc       # All keybindings
    ├── picom/
    │   └── picom.conf    # Compositor (transparency only)
    └── kitty/
        └── kitty.conf    # Terminal (black + green colorscheme)
```

---

## Customisation

### Change cube speed
Edit `SPEED_X`, `SPEED_Y`, `SPEED_Z` in `cube.py`.

### Change cube color
Edit the `fg` color in `launch_cube.sh` (the `xterm -fg` argument).
Default: `#00ff41` (matrix green).

### Change terminal colorscheme
Edit `config/kitty/kitty.conf`.

### Strip window borders entirely
In `config/bspwm/bspwmrc`, set `border_width 0`.

---

## How the cube works

`cube.py` defines 8 vertices and 12 edges of a unit cube. Each frame:

1. Rotate all vertices using X, Y, Z rotation matrices
2. Project 3D points to 2D screen coordinates (perspective projection)
3. Draw each edge using Bresenham's line algorithm, picking the ASCII character (`-`, `|`, `/`, `\`) that best matches the edge angle
4. Draw vertex intersections as `+`
5. Sleep 1/30s and repeat

The cube runs inside `xterm` which is embedded into the root window via `xwinwrap`, making it the desktop background.

Reference for the 3D math: [donut.c explainer](https://www.a1k0n.net/2011/07/20/donut-math.html)
