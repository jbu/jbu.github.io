#!/usr/bin/env python3
"""Converts src/blog/*.md YAML frontmatter to Zola TOML, writes to content/blog/."""

from pathlib import Path

SRC, DST = Path("src/blog"), Path("content/blog")


def parse_fm(text):
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    _, fm, body = parts
    meta = {}
    for line in fm.strip().splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            v = v.strip()
            if len(v) >= 2 and v[0] == v[-1] and v[0] in ('"', "'"):
                v = v[1:-1]
            meta[k.strip()] = v
    return meta, body.strip()


def to_toml(meta, slug):
    title = meta.get("title", "Untitled").replace('"', '\\"')
    lines = [
        "+++",
        f'title = "{title}"',
        f"date = {meta.get('date', '1970-01-01')}",
        # Explicit template because Zola's automatic section/page.html lookup
        # doesn't resolve templates/blog/page.html in 0.22.1.
        'template = "blog/page.html"',
        # Alias preserves the old .html URL as a redirect to the clean URL.
        f'aliases = ["blog/{slug}.html"]',
    ]
    if meta.get("draft", "").lower() == "true":
        lines.append("draft = true")
    lines += ["", "[extra]", f'authors = "{meta.get("authors", "James Uther")}"']
    if meta.get("mathjax", "").lower() == "true":
        lines.append("mathjax = true")
    lines.append("+++")
    return "\n".join(lines)


DST.mkdir(parents=True, exist_ok=True)
for md in sorted(SRC.glob("*.md")):
    meta, body = parse_fm(md.read_text())
    out = to_toml(meta, md.stem) + "\n\n" + body + "\n"
    (DST / md.name).write_text(out)
    print(f"  {md.name}")

print("Done.")
