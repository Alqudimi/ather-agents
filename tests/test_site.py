from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree
import unittest

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"


class SiteParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.links = []
        self.images = []
        self.scripts = []
        self.stylesheets = []
        self.h1_count = 0
        self.title_count = 0
        self.in_h1 = False
        self.in_title = False
        self.title_text = ""

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if tag == "a":
            self.links.append(attrs)
        elif tag == "img":
            self.images.append(attrs)
        elif tag == "script" and attrs.get("src"):
            self.scripts.append(attrs["src"])
        elif tag == "link" and "stylesheet" in attrs.get("rel", "").split():
            self.stylesheets.append(attrs.get("href", ""))
        if tag == "h1":
            self.h1_count += 1
            self.in_h1 = True
        if tag == "title":
            self.title_count += 1
            self.in_title = True

    def handle_endtag(self, tag):
        if tag == "h1":
            self.in_h1 = False
        elif tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title_text += data


class StaticSiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html_path = SITE / "index.html"
        cls.html = cls.html_path.read_text(encoding="utf-8")
        cls.parser = SiteParser()
        cls.parser.feed(cls.html)
        cls.parser.close()

    def test_entry_point_and_accessible_metadata_exist(self):
        self.assertTrue(self.html_path.is_file())
        self.assertTrue(self.parser.title_text.strip())
        self.assertEqual(self.parser.h1_count, 1)
        self.assertIn('lang="ar"', self.html)
        self.assertIn('dir="rtl"', self.html)
        self.assertIn('name="description"', self.html)

    def test_local_resources_and_anchor_targets_exist(self):
        for resource in self.parser.scripts + self.parser.stylesheets:
            parsed = urlsplit(resource)
            if parsed.scheme or parsed.netloc:
                continue
            self.assertTrue((SITE / unquote(parsed.path)).is_file(), resource)
        for image in self.parser.images:
            self.assertIn("alt", image, image)
            parsed = urlsplit(image.get("src", ""))
            if parsed.scheme or parsed.netloc:
                continue
            self.assertTrue((SITE / unquote(parsed.path)).is_file(), image.get("src"))
        for link in self.parser.links:
            href = link.get("href", "")
            parsed = urlsplit(href)
            if parsed.scheme or parsed.netloc:
                continue
            if parsed.path:
                self.assertTrue((self.html_path.parent / unquote(parsed.path)).is_file(), href)
            if parsed.fragment:
                self.assertIn(parsed.fragment, self.parser.ids, href)

    def test_brand_asset_motion_and_interactive_controls_are_present(self):
        self.assertTrue((SITE / "assets/brand/ather-agents-logo.png").is_file())
        self.assertIn("prefers-reduced-motion", (SITE / "assets/css/site.css").read_text(encoding="utf-8"))
        js = (SITE / "assets/js/site.js").read_text(encoding="utf-8")
        for util in ("toArray", "mapRange", "clamp", "wrap"):
            self.assertIn(f"utils.{util}", js)
        self.assertIn("data-theme-toggle", self.html)
        self.assertIn("data-language-toggle", self.html)
        self.assertIn("data-copy-install", self.html)

    def test_pages_support_files_are_well_formed(self):
        self.assertTrue((SITE / "404.html").is_file())
        robots = (SITE / "robots.txt").read_text(encoding="utf-8")
        self.assertIn("Sitemap: https://alqudimi.github.io/ather-agents/sitemap.xml", robots)
        sitemap = ElementTree.parse(SITE / "sitemap.xml")
        locations = [node.text for node in sitemap.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
        self.assertEqual(locations, ["https://alqudimi.github.io/ather-agents/"])

    def test_external_new_tab_links_are_safe(self):
        for link in self.parser.links:
            if link.get("target") == "_blank":
                rel = link.get("rel", "").split()
                self.assertIn("noopener", rel, link.get("href"))
                self.assertIn("noreferrer", rel, link.get("href"))


if __name__ == "__main__":
    unittest.main()
