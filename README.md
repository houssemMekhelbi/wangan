<p align="center"><img src=".github/banner.png" alt="Wangan: the bayshore route, by night and at dawn" width="100%"></p>

<p align="center"><sub>限界突破 genkai toppa · 公道最速 kōdō saisoku · 首都高速 Shuto kōsoku</sub></p>

# ◉ WANGAN 湾岸

The bayshore route of the Shutokō. **Blue** is the body, **amber** the instruments, **red** the redline only. Every shape is round: capsules, LCD windows, pills, gear knobs, the sweep of a light trail. No car, badge or model name appears anywhere.

| | |
|---|---|
| **wangan-yoru** 夜 | the road at 3 a.m., dark |
| **wangan-asa** 朝 | the same road at first light, light |

## ◉ Instruments

| | | |
|---|---|---|
| **ground** | `#0B0D11 / #E4E8EE` | yoru / asa |
| **text** | `#EEF1F5 / #10151D` |  |
| **bayside blue** | `#2A5FC4` | the body |
| **instrument amber** | `#F2A33A` | gauges, attention |
| **redline** | `#D41F27` | the red zone only |
| **paint shift** | `purple → blue → bronze` | the focused border |

## ◉ The dash

- **Windows**: rounding 10, the paint shift on the focused border, a blue glow
- **Waybar**: three capsules with a blue crescent; each module its own LCD window;
  gear-knob workspaces on a rail; eight-cell gauges with a red zone
- **mawaqit**: a lozenge banner with a five-mark prayer dial
- **yawm**: an amber count when due, a red one when overdue; ◉ ○ ●
- **hyprlock**: a 24-hour tachometer that fills to the current time, a red zone from
  22 to 24, the saying in vertical RocknRoll One
- **WanganYoruNeedle / WanganAsaNeedle** cursors (busy is a tach sweep),
  **WanganYoru / WanganAsa** icons, **GTK / Thunar** capsules, **swaync**
- **Terminals**: M PLUS 1 Code 11, an amber block cursor; tmux and zsh as pills
- **Type**: Zen Dots, DotGothic16, RocknRoll One, M PLUS 1p, M PLUS 1 Code, Changa

## ◉ Pre-drive check

- Arch Linux (the package check uses `pacman`)
- Hyprland 0.56 or newer: the configuration is written in Lua
- waybar 0.15 or newer
- the packages in `wangan-yoru/packages.txt` (both variants need the same):

```sh
sudo pacman -S --needed $(grep -v '^#' wangan-yoru/packages.txt)
```

## ◉ On-ramp

> [!WARNING]
> This is a whole desktop, not a colour scheme. It replaces every file listed
> in `wangan-yoru/MANIFEST` or `wangan-asa/MANIFEST`: the Hyprland, waybar, terminal, tmux, GTK and fontconfig
> configuration among them, and the theme line in `~/.zshrc`.
> Everything it replaces is backed up first.

```sh
git clone https://github.com/houssemMekhelbi/wangan.git
cd wangan
./wangan-yoru/restore.sh --dry-run   # show what would change, touch nothing
./wangan-yoru/restore.sh             # apply wangan-yoru
./wangan-asa/restore.sh              # or wangan-asa
```

`restore.sh` then:

1. reports missing packages;
2. backs up every path it is about to replace to `~/themes/.backups/before-<variant>-<timestamp>/`;
3. copies the theme's `home/` over `$HOME` and removes the paths in its `ABSENT`;
4. points `~/.zshrc` at the theme's prompt;
5. applies its `gsettings.txt` and refreshes the font and icon caches;
6. builds the mawaqit-api image if it is missing, enables the user services and
   reloads Hyprland, waybar, hyprpaper, swaync and tmux.

`--files-only` copies the files and gsettings and leaves the services alone.

## ○ Off-ramp

Copy the backup folder back over `$HOME`.

## ○ Prayer times

Prayer times come from [mawaqit.net](https://mawaqit.net) through a local copy of
[mawaqit-api](https://github.com/mrsofiane/mawaqit-api), run by podman on 127.0.0.1.
List your mosques in `~/.config/mawaqit/mosques`, one `<mawaqit.net slug> | <label>`
per line; scroll or right-click the prayer module to switch between them.

## ○ Other routes

This is one of the hattin themes. They share one behaviour (binds, workspaces,
bar modules) and differ only in look. Clone several side by side and run the
`restore.sh` of the one you want: each switch removes what the previous theme
left that the new one does not use.

## ○ Licence

MIT, see [LICENSE](LICENSE). The fonts in `<theme>/home/.local/share/fonts/` are
under the SIL Open Font License; each licence text sits next to its font.
mawaqit-api (`<theme>/home/.local/share/mawaqit-api/`) is MIT, © Sofiane Louchene.
