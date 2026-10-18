#!/usr/bin/env python3
"""Strictly structural checks. This cannot judge clarity or truth."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
ARTICLE_ROOT = ROOT / "articles"
required = ("title:", "slug:", "type:", "entries:", "time_policy:", "status:", "published_at:", "verified_at:")
bad = []
count = 0
for path in sorted(ARTICLE_ROOT.glob("*/article.md")):
    count += 1
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---\n") or "\n---\n" not in content[4:]:
        bad.append(f"{path}: frontmatter missing")
        continue
    front, body = content[4:].split("\n---\n", 1)
    for field in required:
        if not re.search(rf"(?m)^{re.escape(field)}", front):
            bad.append(f"{path}: {field} missing")
    if not re.search(r"(?m)^# .+", body):
        bad.append(f"{path}: H1 missing")
    if re.search(r"(?m)^status: draft\s*$", front):
        if "published_at: null" not in front:
            bad.append(f"{path}: draft cannot have publication date")
    else:
        if "verified_at: null" in front:
            bad.append(f"{path}: published article needs verified_at")
    refs = re.findall(r"!\[[^\]]+\]\(([^)]+)\)", body)
    for ref in refs:
        if "://" in ref:
            continue
        target = (path.parent / ref.split("#")[0]).resolve()
        if not target.is_relative_to(path.parent.resolve()) or not target.is_file():
            bad.append(f"{path}: missing image {ref}")
    for image in (path.parent / "assets").glob("*.svg"):
        if f"assets/{image.name}" not in body:
            bad.append(f"{path}: orphan figure {image.name}")
if count == 0:
    bad.append("no articles")
if bad:
    print("\n".join(bad), file=sys.stderr)
    raise SystemExit(1)
print(f"editorial-check: {count} articles, structural checks passed; semantic review required")
