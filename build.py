#!/usr/bin/env python3
"""
Build script for jbu.github.io.

Converts src/blog/*.md -> blog/*.html and src/index.md -> index.html.
Copies src/cv.html -> cv.html.

External scribbles (non-blog links) live in src/external_links.txt,
one entry per line: date | title | url

Usage: uv run build.py
"""

import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from mistletoe import Document
from mistletoe.html_renderer import HtmlRenderer
from mistletoe.span_token import SpanToken


# ---------------------------------------------------------------------------
# Frontmatter parser
# ---------------------------------------------------------------------------

def parse_frontmatter(text):
    """Parse simple YAML-style frontmatter. Returns (meta_dict, body_str)."""
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    _, fm_block, body = parts
    meta = {}
    for line in fm_block.strip().splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip()
    return meta, body.strip()


# ---------------------------------------------------------------------------
# Custom span tokens for Tufte sidenotes / margin notes
# ---------------------------------------------------------------------------

class SidenoteToken(SpanToken):
    """
    Numbered Tufte sidenote.  Syntax: {side: text here}
    Renders the label/input/span triplet that tufte.css expects.
    """
    pattern = re.compile(r"\{side:\s*(.+?)\}", re.DOTALL)
    parse_inner = True

    def __init__(self, match):
        super().__init__(match)


class MarginNoteToken(SpanToken):
    """
    Tufte margin note (⊕ toggle, no number).  Syntax: {margin: text here}
    """
    pattern = re.compile(r"\{margin:\s*(.+?)\}", re.DOTALL)
    parse_inner = True

    def __init__(self, match):
        super().__init__(match)


# ---------------------------------------------------------------------------
# Renderer
# ---------------------------------------------------------------------------

class TufteRenderer(HtmlRenderer):
    def __init__(self):
        super().__init__(SidenoteToken, MarginNoteToken)
        self._sn_counter = 0
        self._mn_counter = 0

    def reset_counters(self):
        self._sn_counter = 0
        self._mn_counter = 0

    def render_sidenote_token(self, token):
        self._sn_counter += 1
        sid = f"sn-{self._sn_counter}"
        inner = self.render_inner(token)
        return (
            f'<label for="{sid}" class="margin-toggle sidenote-number"></label>'
            f'<input type="checkbox" id="{sid}" class="margin-toggle"/>'
            f'<span class="sidenote">{inner}</span>'
        )

    def render_margin_note_token(self, token):
        self._mn_counter += 1
        mid = f"mn-{self._mn_counter}"
        inner = self.render_inner(token)
        return (
            f'<label for="{mid}" class="margin-toggle margin-number">&#8853;</label>'
            f'<input type="checkbox" id="{mid}" class="margin-toggle"/>'
            f'<span class="marginnote">{inner}</span>'
        )


# ---------------------------------------------------------------------------
# Jinja2 environment
# ---------------------------------------------------------------------------

_jinja_env = Environment(
    loader=FileSystemLoader(Path(__file__).parent / "templates"),
    autoescape=False,
)


# ---------------------------------------------------------------------------
# Build helpers
# ---------------------------------------------------------------------------

def render_md(path, renderer):
    """Read .md file, parse frontmatter, render body HTML. Returns (meta, html)."""
    text = path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(text)
    renderer.reset_counters()
    html = renderer.render(Document(body))
    return meta, html


def collect_blog_posts(src_blog_dir):
    """
    Scan src/blog/*.md for frontmatter.
    Returns list of (date_str, title, slug) sorted newest-first.
    """
    posts = []
    for md_file in Path(src_blog_dir).glob("*.md"):
        text = md_file.read_text(encoding="utf-8")
        meta, _ = parse_frontmatter(text)
        date = meta.get("date", "0000-00-00")
        title = meta.get("title", md_file.stem)
        posts.append((date, title, md_file.stem))
    return sorted(posts, key=lambda x: x[0], reverse=True)


def collect_external_links(external_links_path):
    """
    Read src/external_links.txt.
    Each line: date | title | url
    Returns list of (date_str, title, url).
    """
    path = Path(external_links_path)
    if not path.exists():
        return []
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|", 2)]
        if len(parts) == 3:
            entries.append(tuple(parts))
    return entries


def build_scribbles_html(blog_posts, external_links):
    """
    Merge blog posts + external links, sort by date descending,
    render as <li> lines.
    """
    items = []
    for date, title, slug in blog_posts:
        items.append((date, title, f"blog/{slug}.html", False))
    for date, title, url in external_links:
        items.append((date, title, url, True))
    items.sort(key=lambda x: x[0], reverse=True)

    lines = []
    for date, title, url, _external in items:
        lines.append(f'          <li>{date} &dash; <a href="{url}">{title}</a></li>')
    return "\n".join(lines)


def build_post(src_path, out_path, renderer):
    meta, body_html = render_md(src_path, renderer)
    tmpl = _jinja_env.get_template("blog_post.html")
    html = tmpl.render(
        title=meta.get("title", "Untitled"),
        date=meta.get("date", ""),
        authors=meta.get("authors", "James Uther"),
        mathjax=meta.get("mathjax", "").lower() == "true",
        body_html=body_html,
    )
    out_path.write_text(html, encoding="utf-8")
    print(f"  {src_path.name} -> {out_path.relative_to(out_path.parent.parent)}")


def build_cv(src_cv_path, renderer):
    _meta, body_html = render_md(src_cv_path, renderer)
    tmpl = _jinja_env.get_template("cv.html")
    html = tmpl.render(body_html=body_html)
    out_path = src_cv_path.parent.parent / "cv.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"  cv.md -> cv.html")


def build_index(src_index_path, scribbles_html, renderer):
    _meta, body_html = render_md(src_index_path, renderer)
    tmpl = _jinja_env.get_template("index.html")
    html = tmpl.render(body_html=body_html, scribbles_items_html=scribbles_html)
    out_path = src_index_path.parent.parent / "index.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"  index.md -> index.html")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    root = Path(__file__).parent
    src = root / "src"
    src_blog = src / "blog"
    blog_out = root / "blog"

    blog_out.mkdir(exist_ok=True)

    blog_posts = collect_blog_posts(src_blog)
    external_links = collect_external_links(src / "external_links.txt")
    scribbles_html = build_scribbles_html(blog_posts, external_links)

    with TufteRenderer() as renderer:
        # Build blog posts
        for date, title, slug in blog_posts:
            src_path = src_blog / f"{slug}.md"
            out_path = blog_out / f"{slug}.html"
            build_post(src_path, out_path, renderer)

        # Build index
        build_index(src / "index.md", scribbles_html, renderer)

        # Build cv
        build_cv(src / "cv.md", renderer)

    print(f"Done. {len(blog_posts)} posts built.")


if __name__ == "__main__":
    main()
