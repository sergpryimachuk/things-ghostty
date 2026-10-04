# Things for Ghostty

A terminal adaptation of [Things for Obsidian](https://github.com/colineckert/obsidian-things), by Colin Eckert. Colors come from the installed Things 2.2.4 CSS. The upstream MIT notice is retained in [LICENSE](LICENSE).

![Light and dark palette preview](preview.svg)

## Install

These native steps follow [Ghostty's theme documentation](https://ghostty.org/docs/config/reference#theme). The commands below are for macOS and Linux. Back up any existing `Things Light` and `Things Dark` files in the destination before copying.

```sh
git clone https://github.com/sergpryimachuk/things-ghostty.git
cd things-ghostty
theme_dir="${XDG_CONFIG_HOME:-$HOME/.config}/ghostty/themes"
mkdir -p "$theme_dir"
cp "themes/Things Light" "themes/Things Dark" "$theme_dir/"
```

Open your Ghostty configuration through its settings command. Back up the file before editing, then replace its existing `theme` setting with:

```ini
theme = light:Things Light,dark:Things Dark
```

Ghostty uses `config.ghostty` for new configurations and also loads legacy `config` files. It searches the XDG location on macOS and Linux, plus `~/Library/Application Support/com.mitchellh.ghostty` on macOS. If several files exist, later files override earlier ones. Keep using your existing configuration; there is no need to rename it. See [configuration locations and load order](https://ghostty.org/docs/config#file-location).

Reload with **Cmd+Shift+comma** on macOS or **Ctrl+Shift+comma** on Linux. Confirm the themes are discoverable with `ghostty +list-themes`. If Ghostty is not in your macOS PATH, use `/Applications/Ghostty.app/Contents/MacOS/ghostty`.

### Optional installer

This repository provides a Python 3.9+ convenience script. It automates the native steps and is not provided by Ghostty.

```sh
python3 install.py
```

The installer updates the last existing configuration in Ghostty's documented load order. When no configuration exists, it creates `config.ghostty` in the macOS Application Support directory or the Linux XDG directory. It preserves other preferences, validates the themes and candidate configuration with Ghostty, and makes timestamped backups before changes. To select a custom configuration explicitly:

```sh
python3 install.py --config /absolute/path/config.ghostty
```

The standard theme directory is `$XDG_CONFIG_HOME/ghostty/themes`, or `~/.config/ghostty/themes` when XDG_CONFIG_HOME is unset. If it is not writable on macOS, the script falls back to `~/Library/Application Support/com.mitchellh.ghostty/themes` and selects the themes by absolute path. This handles a root-owned standard theme folder without changing its permissions. Themes in the fallback directory will work but will not appear in `ghostty +list-themes`.

For that fallback or another custom theme directory, use absolute paths in the configuration:

```ini
theme = light:/absolute/path/Things Light,dark:/absolute/path/Things Dark
```

To select a fixed appearance, use `theme = Things Light` or `theme = Things Dark`, or the corresponding absolute path. Explicit color settings override theme colors. Included configuration files can also override your selection; the installer leaves those files intact. Installation does not restart Ghostty or close sessions, so reload after running it.

## Colors and limits

| Role | Light | Dark |
| --- | --- | --- |
| Obsidian editor background | `#ffffff` | `#1c2127` |
| Normal text | `#222222` | `#dadada` |
| Things accent cursor | `#4c8ce6` | `#79a9ec` |
| Selection composite | `#d2e2f9` | `#283c58` |
| Split divider | `#ebedf0` | `#35393e` |

ANSI colors 1 through 6 use Things' Atom syntax red, green, orange/yellow, blue, purple and aqua. Light ANSI yellow uses Atom orange `#986800`, since Things' light variable named `atom-yellow` is red. Bright colors use suitable Things status colors; light green, yellow and cyan retain syntax colors so they remain readable on white. Selection colors flatten Things' 25% blue selection over the editor background, with the light accent also used by Obsidian's dark interactive selection. HSL values are converted to 8-bit sRGB and rounded consistently with the companion themes.

The terminal keeps its font and layout preferences. Ghostty cannot reproduce Obsidian's note typography, sidebar cards or CSS spacing through a color theme. Programs that emit their own truecolor values can override the ANSI palette. Ghostty documents a macOS tab titlebar style issue during light/dark switches; no sessions are restarted to work around it.

## Agent CLI colors

Agent CLIs can select their own colors independently of the terminal theme. If Antigravity CLI `agy` displays pale text on a white Things Light background, open `/config`, choose Color Scheme, and select `terminal`. This lets agy use the Things ANSI palette in both appearances.

For future sessions, set only this value in `~/.gemini/antigravity-cli/settings.json`, keeping your other preferences:

```json
"colorScheme": "terminal"
```

Changing the file applies to new sessions. Use `/config` in a running session to apply the scheme immediately. Previously rendered scrollback can retain its old colors. See [Antigravity CLI display settings](https://antigravity.google/docs/settings?tab=cli#display-and-rendering).

## Validate and undo

Run the installer regression checks with:

```sh
python3 -m unittest discover -s tests -v
```

Validate your active Ghostty configuration with:

```sh
/Applications/Ghostty.app/Contents/MacOS/ghostty +validate-config
```

To undo installation, copy the saved `config.before-things-TIMESTAMP` over the adjacent `config` file, then reload Ghostty. Remove the two installed theme files if no configuration refers to them. Choose your exact backup from the installer output.

The theme files and system-switching configuration passed native Ghostty 1.3.1 validation. The installer checks cover configuration load order, modern and legacy filenames, settings preservation, backups, and repeat installation. [Ghostty's official theme reference](https://ghostty.org/docs/config/reference#theme) documents absolute paths, paired appearances and override precedence. The SVG is a palette illustration, not an application screenshot.
