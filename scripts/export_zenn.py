#!/usr/bin/env python3
"""Export source articles to a standalone Zenn GitHub Connect branch."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SLUG = re.compile(r"^[a-z0-9_-]{12,50}$")
IMAGE = re.compile(r"(!\[[^\]\n]*\]\()([^\)\s]+)(\))")
ALLOWED_IMAGES = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
LIMIT = 3 * 1024 * 1024


class ExportError(ValueError):
    pass


def read_article(path: Path) -> tuple[dict[str, str], str]:
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---\n") or "\n---\n" not in content[4:]:
        raise ExportError(f"{path}: front matter missing")
    head, body = content[4:].split("\n---\n", 1)
    required = {"title", "slug", "type", "status", "verified_at", "published_at"}
    found: dict[str, str] = {}
    for line in head.splitlines():
        match = re.match(r"^([a-z_]+):(?:\s*(.*))?$", line)
        if not match:
            continue
        key, value = match.groups()
        if key in required:
            if key in found:
                raise ExportError(f"{path}: duplicate {key}")
            found[key] = (value or "").strip().strip('"\'')
    if not required.issubset(found):
        raise ExportError(f"{path}: missing {sorted(required - found.keys())}")
    if not found["title"] or not found["slug"]:
        raise ExportError(f"{path}: empty title or slug")
    if found["slug"] != path.parent.name:
        raise ExportError(f"{path}: slug does not match directory")
    if found["status"] not in {"draft", "published"}:
        raise ExportError(f"{path}: invalid status")
    if found["status"] == "published":
        for field in ("verified_at", "published_at"):
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", found[field]):
                raise ExportError(f"{path}: published article requires ISO date {field}")
    return found, body


def render_article(source: Path, info: dict, meta: dict, expected: dict[str, bytes]) -> str:
    slug = meta["slug"]
    body = info["body"]

    def substitute(match: re.Match[str]) -> str:
        ref = match.group(2)
        if re.match(r"^(?:https?://|/images/)", ref):
            return match.group(0)
        if ref.startswith(("/", "#")) or "?" in ref or "#" in ref:
            raise ExportError(f"{source}: unsupported image reference {ref}")
        asset = (source.parent / ref).resolve()
        if not asset.is_relative_to(source.parent.resolve()) or not asset.is_file():
            raise ExportError(f"{source}: missing or unsafe image {ref}")
        suffix = asset.suffix.lower()
        if suffix == ".svg":
            try:
                import cairosvg
            except ImportError as exc:
                raise ExportError("CairoSVG is needed to export SVG assets: pip install -r requirements-zenn.txt") from exc
            raw = cairosvg.svg2png(bytestring=asset.read_bytes())
            name = asset.stem + ".png"
        elif suffix in ALLOWED_IMAGES:
            raw = asset.read_bytes()
            name = asset.name
        else:
            raise ExportError(f"{source}: unsupported image format {suffix}")
        if len(raw) > LIMIT:
            raise ExportError(f"{source}: image exceeds Zenn 3 MiB limit {ref}")
        target = f"images/{slug}/{name}"
        if target in expected and expected[target] != raw:
            raise ExportError(f"{source}: conflicting asset name {name}")
        expected[target] = raw
        return f"{match.group(1)}/images/{slug}/{name}{match.group(3)}"

    # Do not rewrite example Markdown inside fenced code blocks.
    parts = re.split(r"(?m)(^```[^\n]*\n.*?^```\s*$)", body, flags=re.DOTALL)
    for i in range(0, len(parts), 2):
        parts[i] = IMAGE.sub(substitute, parts[i])
    body = "".join(parts)
    published = info["status"] == "published"
    yaml = [
        "---",
        "title: " + json.dumps(info["title"], ensure_ascii=False),
        "emoji: " + json.dumps(meta["emoji"], ensure_ascii=False),
        f"type: {meta['type']}",
        "topics: [" + ", ".join(meta["topics"]) + "]",
        f"published: {'true' if published else 'false'}",
    ]
    if published:
        yaml.append(f"published_at: {info['published_at']}")
    yaml.append("---")
    return "\n".join(yaml) + "\n" + body


def build(root: Path = ROOT) -> dict[str, bytes]:
    sources = sorted((root / "articles").glob("*/article.md"))
    config = json.loads((root / "zenn.json").read_text(encoding="utf-8"))
    if not sources:
        raise ExportError("no source articles")
    actual = {p.parent.name for p in sources}
    if set(config) != actual:
        raise ExportError(f"zenn.json differs from sources (missing={sorted(actual - set(config))}, extra={sorted(set(config) - actual)})")
    expected: dict[str, bytes] = {}
    slugs: set[str] = set()
    for source in sources:
        fields, body = read_article(source)
        meta = config[fields["slug"]]
        slug = meta["slug"]
        if not isinstance(slug, str) or not SLUG.fullmatch(slug) or slug in slugs:
            raise ExportError(f"{source}: invalid/duplicate Zenn slug {slug}")
        slugs.add(slug)
        if meta.get("type") not in {"tech", "idea"}:
            raise ExportError(f"{source}: invalid Zenn article type")
        if not isinstance(meta.get("emoji"), str) or not meta["emoji"]:
            raise ExportError(f"{source}: emoji missing")
        topics = meta.get("topics")
        if not isinstance(topics, list) or not 1 <= len(topics) <= 5 or not all(isinstance(t, str) and re.fullmatch(r"[a-z0-9_-]+", t) for t in topics):
            raise ExportError(f"{source}: invalid topics")
        rendered = render_article(source, {**fields, "body": body}, meta, expected)
        expected[f"articles/{slug}.md"] = rendered.encode("utf-8")
    return expected


def generated_paths(output: Path) -> set[str]:
    return {p.relative_to(output).as_posix() for p in output.rglob("*") if p.is_file()} if output.exists() else set()


def run(root: Path, output: Path, check: bool) -> int:
    expected = build(root)
    existing = generated_paths(output)
    obsolete = existing - set(expected)
    dirty = sorted(obsolete | {path for path, content in expected.items() if not (output / path).is_file() or (output / path).read_bytes() != content})
    if check:
        if dirty:
            print("Zenn export differs from source:\n" + "\n".join(dirty), file=sys.stderr)
            return 1
        print(f"Zenn export: {len(expected)} files up to date")
        return 0
    for path in obsolete:
        (output / path).unlink()
    for path, content in expected.items():
        dest = output / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(content)
    print(f"Zenn export: {len(expected)} files generated")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify output without writing")
    parser.add_argument("--root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    parser.add_argument("--output", type=Path, default=None, help="publication tree destination (default: .zenn-export)")
    args = parser.parse_args()
    try:
        root = args.root.resolve()
        sys.exit(run(root, (args.output or root / ".zenn-export").resolve(), args.check))
    except (ExportError, OSError, ValueError) as exc:
        print(f"Zenn export: {exc}", file=sys.stderr)
        sys.exit(1)
}
