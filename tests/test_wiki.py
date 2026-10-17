from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
WIKI = ROOT / "wiki"


class WikiSourceTests(unittest.TestCase):
    def test_home_page_and_sidebar_pages_exist(self):
        self.assertTrue((WIKI / "Home.md").is_file())
        self.assertTrue((WIKI / "_Sidebar.md").is_file())
        self.assertTrue((WIKI / "_Footer.md").is_file())
        pages = {p.stem for p in WIKI.glob("*.md")}
        expected = {"Home", "Installation", "Using-Agents", "Agent-Catalog", "FAQ", "Troubleshooting", "Development", "CI-CD", "Security"}
        self.assertTrue(expected.issubset(pages), expected - pages)

    def test_internal_wiki_page_links_resolve(self):
        for source in WIKI.glob("*.md"):
            text = source.read_text(encoding="utf-8")
            text = re.sub(r"```.*?```", "", text, flags=re.S)
            text = re.sub(r"`[^`]*`", "", text)
            for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                if "/" not in target and not target.endswith((".md", ".html")):
                    self.assertTrue((WIKI / f"{target}.md").is_file(), f"{source}: {target}")


if __name__ == "__main__":
    unittest.main()
