import json
from pathlib import Path
import tempfile
import unittest

from export_zenn import ExportError, build, run


class ZennExporterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / "articles" / "sample-source"
        self.source.mkdir(parents=True)
        (self.root / "zenn.json").write_text(json.dumps({"sample-source": {
            "slug": "sample-source-article", "type": "tech",
            "emoji": "📖", "topics": ["ai"]
        }}), encoding="utf-8")
        (self.source / "article.md").write_text('''---
title: サンプル
slug: sample-source
type: 解説
status: draft
verified_at: null
published_at: null
---

# サンプル

![](assets/figure.svg)

```md
![](assets/external.svg)
```
''', encoding="utf-8")
        (self.source / "assets").mkdir()
        (self.source / "assets" / "figure.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" width="4" height="4"><rect width="4" height="4" fill="red"/></svg>')

    def test_draft_export_and_png(self):
        out = self.root / "stage"
        self.assertEqual(run(self.root, out, False), 0)
        result = (out / "articles/sample-source-article.md").read_text()
        self.assertIn("published: false", result)
        self.assertIn('title: "サンプル"', result)
        self.assertIn("/images/sample-source-article/figure.png", result)
        self.assertIn("```md\n![](assets/external.svg)\n```", result)
        self.assertTrue((out / "images/sample-source-article/figure.png").read_bytes().startswith(b"\x89PNG"))
        self.assertEqual(run(self.root, out, True), 0)
        (out / "articles/sample-source-article.md").write_text("stale")
        self.assertEqual(run(self.root, out, True), 1)
        self.assertEqual(run(self.root, out, False), 0)
        (out / "articles/stale.md").write_text("stale")
        self.assertEqual(run(self.root, out, True), 1)
        self.assertEqual(run(self.root, out, False), 0)
        self.assertFalse((out / "articles/stale.md").exists())

    def test_publishing_requires_dates(self):
        article = self.source / "article.md"
        article.write_text(article.read_text().replace("status: draft", "status: published"))
        with self.assertRaisesRegex(ExportError, "requires ISO date"):
            build(self.root)
        article.write_text(article.read_text().replace("verified_at: null", "verified_at: 2026-10-18").replace("published_at: null", "published_at: 2026-10-18"))
        doc = build(self.root)["articles/sample-source-article.md"].decode()
        self.assertIn("published: true", doc)
        self.assertIn("published_at: 2026-10-18", doc)

    def test_prevent_unsafe_image_reference(self):
        article = self.source / "article.md"
        article.write_text(article.read_text().replace("assets/figure.svg", "../escape.svg"))
        with self.assertRaisesRegex(ExportError, "unsafe image"):
            build(self.root)

    def test_unregistered_source_fails(self):
        (self.root / "zenn.json").write_text("{}")
        with self.assertRaisesRegex(ExportError, "differs from sources"):
            build(self.root)


if __name__ == "__main__":
    unittest.main()
