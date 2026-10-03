"""Check config precedence and real Ghostty installation in temporary folders."""
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('installer', ROOT / 'install.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)
GHOSTTY = shutil.which('ghostty') or '/Applications/Ghostty.app/Contents/MacOS/ghostty'


class InstallerTests(unittest.TestCase):
    def test_config_precedence_and_new_filename(self):
        with tempfile.TemporaryDirectory() as directory:
            xdg, mac = Path(directory) / 'xdg', Path(directory) / 'mac'
            self.assertEqual(installer.discover_config(xdg), xdg / 'config.ghostty')
            self.assertEqual(installer.discover_config(xdg, mac), mac / 'config.ghostty')
            for folder in (xdg, mac):
                folder.mkdir()
                for name in ('config.ghostty', 'config'):
                    path = folder / name
                    path.write_text('')
                    self.assertEqual(installer.discover_config(xdg, mac), path)

    def test_theme_replacement_preserves_other_lines(self):
        text = '# theme = keep this comment\nfont-size = 15\n\ntheme = old\nkeybind = ctrl+x=close_surface'
        expected = '# theme = keep this comment\nfont-size = 15\n\nkeybind = ctrl+x=close_surface\ntheme = light:Things Light,dark:Things Dark\n'
        updated = installer.update_theme(text, 'light:Things Light,dark:Things Dark')
        self.assertEqual(updated, expected)
        self.assertEqual(installer.update_theme(updated, 'light:Things Light,dark:Things Dark'), expected)

    @unittest.skipUnless(Path(GHOSTTY).is_file(), 'Ghostty CLI is required')
    def test_native_install_backup_and_repeat(self):
        with tempfile.TemporaryDirectory() as directory:
            env = dict(os.environ, XDG_CONFIG_HOME=directory)
            config = Path(directory) / 'ghostty/config.ghostty'
            config.parent.mkdir()
            original = '# retained\nfont-size = 15\ntheme = old-theme\n'
            config.write_text(original)
            command = [sys.executable, str(ROOT / 'install.py'), '--config', str(config)]
            subprocess.run(command, env=env, check=True, capture_output=True)
            installed = config.read_text()
            self.assertIn('font-size = 15', installed)
            self.assertIn('theme = light:Things Light,dark:Things Dark', installed)
            backups = list(config.parent.glob('config.ghostty.before-things-*'))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(), original)
            for name in installer.NAMES:
                self.assertEqual((config.parent / 'themes' / name).read_bytes(), (ROOT / 'themes' / name).read_bytes())
            subprocess.run(command, env=env, check=True, capture_output=True)
            self.assertEqual(config.read_text(), installed)
            self.assertEqual(len(list(config.parent.glob('config.ghostty.before-things-*'))), 1)
            discovered = subprocess.run([GHOSTTY, '+list-themes', '--plain'], env=env,
                                        check=True, capture_output=True, text=True).stdout
            for name in installer.NAMES:
                self.assertIn(name, discovered)

    @unittest.skipUnless(Path(GHOSTTY).is_file(), 'Ghostty CLI is required')
    def test_invalid_config_is_not_replaced(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / 'config'
            original = 'invalid-things-test-key = 1\n'
            config.write_text(original)
            result = subprocess.run([sys.executable, str(ROOT / 'install.py'), '--config', str(config)],
                                    env=dict(os.environ, XDG_CONFIG_HOME=directory), capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(config.read_text(), original)
            self.assertFalse(list(config.parent.glob('config.before-things-*')))


if __name__ == '__main__':
    unittest.main()
