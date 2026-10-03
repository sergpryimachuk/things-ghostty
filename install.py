#!/usr/bin/env python3
"""Install Things using Ghostty's standard theme directory and config discovery."""
import argparse
from datetime import datetime
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
NAMES = ("Things Light", "Things Dark")


def discover_config(xdg, mac_support=None):
    directories = [xdg] + ([mac_support] if mac_support else [])
    files = [directory / name for directory in directories
             for name in ("config.ghostty", "config")]
    # Ghostty loads all existing files in this order; update the last one.
    return next((path for path in reversed(files) if path.is_file()),
                directories[-1] / "config.ghostty")


def update_theme(original, value):
    lines = original.splitlines(keepends=True)
    kept = "".join(line for line in lines if not re.match(r"^\s*theme\s*=", line))
    return kept + ("\n" if kept and not kept.endswith("\n") else "") + f"theme = {value}\n"


def backup(path):
    if path.exists():
        saved = path.with_name(path.name + ".before-things-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
        shutil.copy2(path, saved)
        print(f"Backup: {saved}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, help="Override the configuration file to update")
    args = parser.parse_args()
    xdg = Path(os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")) / "ghostty"
    mac_support = (Path.home() / "Library/Application Support/com.mitchellh.ghostty"
                   if sys.platform == "darwin" else None)
    config = args.config.expanduser().resolve() if args.config else discover_config(xdg, mac_support)
    ghostty = shutil.which("ghostty")
    if not ghostty and sys.platform == "darwin":
        ghostty = "/Applications/Ghostty.app/Contents/MacOS/ghostty"
    if not ghostty:
        parser.error("Ghostty must be installed and available in PATH")
    # Validate source themes before touching the installed files.
    for name in NAMES:
        subprocess.run([ghostty, "+validate-config",
                        f"--config-file={ROOT / 'themes' / name}"], check=True)
    theme_dir = xdg / "themes"
    try:
        theme_dir.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryFile(dir=theme_dir):
            pass
    except PermissionError:
        if not mac_support:
            raise
        theme_dir = mac_support / "themes"
        theme_dir.mkdir(parents=True, exist_ok=True)
        print(f"Standard theme directory is not writable; using absolute paths in {theme_dir}")
    for name in NAMES:
        source, target = ROOT / "themes" / name, theme_dir / name
        if not target.exists() or target.read_bytes() != source.read_bytes():
            backup(target)
            shutil.copy2(source, target)
    value = ("light:Things Light,dark:Things Dark" if theme_dir == xdg / "themes" else
             f"light:{theme_dir / NAMES[0]},dark:{theme_dir / NAMES[1]}")
    original = config.read_text() if config.exists() else ""
    result = update_theme(original, value)
    config.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", dir=config.parent, prefix="things-validation-", delete=False) as handle:
        handle.write(result)
        candidate = Path(handle.name)
    try:
        subprocess.run([ghostty, "+validate-config",
                        f"--config-file={candidate}"], check=True)
        if original != result:
            backup(config)
            candidate.chmod(config.stat().st_mode & 0o777 if config.exists() else 0o600)
            candidate.replace(config)
        print(f"Installed: {config}")
        print("Reload Ghostty with Cmd+Shift+, on macOS or Ctrl+Shift+, on Linux.")
    finally:
        candidate.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
