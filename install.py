#!/usr/bin/env python3
"""Install themes and select system appearance, preserving other preferences."""
from datetime import datetime
from pathlib import Path
import os
import re
import shutil
import subprocess
import tempfile

root = Path(__file__).resolve().parent
support = Path.home() / "Library/Application Support/com.mitchellh.ghostty"
if os.uname().sysname != "Darwin":
    support = Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))) / "ghostty"
support.mkdir(parents=True, exist_ok=True)
theme_dir = support / "themes"
theme_dir.mkdir(exist_ok=True)
for name in ("Things Light", "Things Dark"):
    target = theme_dir / name
    if target.exists() and target.read_bytes() != (root / "themes" / name).read_bytes():
        shutil.copy2(target, target.with_name(name + ".backup-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f")))
    shutil.copy2(root / "themes" / name, target)

config = support / "config"
original = config.read_text() if config.exists() else ""
choice = f"theme = light:{theme_dir / 'Things Light'},dark:{theme_dir / 'Things Dark'}"
lines = original.splitlines()
result = "\n".join(line for line in lines if not re.match(r"^\s*theme\s*=", line))
result = (result + "\n" if result else "") + choice + "\n"
ghostty = shutil.which("ghostty") or "/Applications/Ghostty.app/Contents/MacOS/ghostty"
with tempfile.NamedTemporaryFile(mode="w", dir=support, prefix="things-validation-", delete=False) as handle:
    handle.write(result)
    candidate = Path(handle.name)
try:
    subprocess.run([ghostty, "+validate-config", f"--config-file={candidate}"], check=True)
    if config.exists() and original != result:
        backup = config.with_name("config.before-things-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
        shutil.copy2(config, backup)
        print(f"Backup: {backup}")
    if original != result:
        candidate.replace(config)
    print(f"Installed: {config}")
    print("Reload Ghostty with Cmd+Shift+, or Ghostty > Reload Configuration.")
finally:
    candidate.unlink(missing_ok=True)
