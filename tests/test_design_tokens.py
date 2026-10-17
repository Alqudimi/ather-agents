from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOKENS = (ROOT / "site/assets/css/tokens.css").read_text(encoding="utf-8")


def block(selector):
    match = re.search(re.escape(selector) + r"\s*\{([^}]*)\}", TOKENS)
    if not match:
        raise AssertionError(f"Theme selector not found: {selector}")
    return {name: value.upper() for name, value in re.findall(r"(--[\w-]+):\s*(#[0-9A-Fa-f]{6})\s*;", match.group(1))}


def contrast(foreground, background):
    def luminance(color):
        channels = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        channels = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in channels]
        return sum(c * w for c, w in zip(channels, (0.2126, 0.7152, 0.0722)))
    a, b = luminance(foreground), luminance(background)
    return (max(a, b) + 0.05) / (min(a, b) + 0.05)


class DesignTokenTests(unittest.TestCase):
    def test_light_mode_text_and_ui_contrast(self):
        light = block(':root,\n:root[data-theme="light"]')
        self.assertGreaterEqual(contrast(light["--brand-indigo"], "#FFFFFF"), 4.5)
        self.assertGreaterEqual(contrast(light["--text-link"], light["--surface-page"]), 4.5)
        self.assertGreaterEqual(contrast(light["--text-accent"], light["--surface-page"]), 4.5)
        self.assertGreaterEqual(contrast(light["--border-default"], light["--surface-page"]), 3.0)

    def test_dark_mode_text_and_ui_contrast(self):
        dark = block(':root[data-theme="dark"]')
        self.assertGreaterEqual(contrast("#FFFFFF", dark["--brand-indigo"]), 4.5)
        self.assertGreaterEqual(contrast(dark["--text-link"], dark["--surface-page"]), 4.5)
        self.assertGreaterEqual(contrast(dark["--text-accent"], dark["--surface-page"]), 4.5)
        self.assertGreaterEqual(contrast(dark["--border-default"], dark["--surface-page"]), 3.0)


if __name__ == "__main__":
    unittest.main()
