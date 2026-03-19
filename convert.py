#!/usr/bin/env python3
"""
One-shot conversion script: blog/*.html -> src/blog/*.md

Uses BeautifulSoup to extract frontmatter (title, date, authors) and body HTML,
pre-processes Tufte sidenote/marginnote HTML into {side:}/{margin:} markers,
then uses pandoc for the main HTML->Markdown conversion.

Usage: uv run convert.py
"""

import re
import subprocess
import sys
from pathlib import Path

from bs4 import BeautifulSoup, Comment


# ---------------------------------------------------------------------------
# Extract metadata and body from a blog post HTML file
# ---------------------------------------------------------------------------

def extract_post_info(html_text):
    """
    Returns (title, date, authors, body_html, has_mathjax).
    body_html is the content of the body sections (excluding author metadata section).
    """
    soup = BeautifulSoup(html_text, "html.parser")

    # Title
    h1 = soup.find("h1")
    title = h1.get_text(strip=True) if h1 else "Untitled"

    # MathJax
    has_mathjax = bool(soup.find("script", src=re.compile(r"mathjax", re.IGNORECASE)))

    # Author/date: first <section> contains <p><a href="../index.html">Author</a><br>date</p>
    sections = soup.find_all("section")
    authors = "James Uther"
    date = ""
    body_sections = sections

    if sections:
        first_sec = sections[0]
        link = first_sec.find("a", href=re.compile(r"\.\./index\.html"))
        if link:
            authors = link.get_text(strip=True)
            # Date is text after the <br> in the same <p>
            p = link.find_parent("p")
            if p:
                br = p.find("br")
                if br and br.next_sibling:
                    date = str(br.next_sibling).strip()
            # Remove only the author <p> from section 0, keep any remaining content
            if p:
                p.decompose()
            remaining = first_sec.decode_contents().strip()
            body_sections = ([BeautifulSoup(remaining, "html.parser")] if remaining else []) + list(sections[1:])
        # If date still not found, try regex on raw text
        if not date:
            date_match = re.search(r'\b(\d{4}-\d{2}-\d{2})\b', first_sec.get_text())
            if date_match:
                date = date_match.group(1)
                body_sections = sections[1:]

    # Build body HTML from remaining sections
    body_parts = []
    for sec in body_sections:
        # Get the inner content (not the <section> wrapper itself)
        body_parts.append(sec.decode_contents())
    body_html = "\n".join(body_parts).strip()

    # If no sections found, use the article content minus h1 and first p
    if not body_html:
        article = soup.find("article")
        if article:
            # Remove h1 and author paragraph
            for tag in article.find_all(["h1"]):
                tag.decompose()
            body_html = article.decode_contents().strip()

    return title, date, authors, body_html, has_mathjax


# ---------------------------------------------------------------------------
# Pre-process sidenotes/marginnotes before pandoc
# ---------------------------------------------------------------------------

def preprocess_notes(html):
    """
    Replace Tufte sidenote/marginnote HTML triplets with pandoc-safe markers.

    Marginnote (⊕ symbol):
        <label ... class="...margin-toggle...">&#8853;</label>
        <input ... class="...margin-toggle..." />
        <span class="marginnote">CONTENT</span>

    Sidenote (numbered):
        <label ... class="...sidenote-number..."></label>
        <input ... class="...margin-toggle..." />
        <span class="sidenote">CONTENT</span>
    """
    soup = BeautifulSoup(html, "html.parser")
    markers = {}
    counter = [0]

    # Find all margin-toggle labels
    for label in soup.find_all("label", class_="margin-toggle"):
        is_sidenote = "sidenote-number" in label.get("class", [])
        is_marginnote = "margin-number" in label.get("class", [])

        # Find the associated input and span
        input_tag = label.find_next_sibling("input", class_="margin-toggle")
        span_class = "sidenote" if is_sidenote else "marginnote"
        span_tag = label.find_next_sibling("span", class_=span_class)

        if span_tag:
            counter[0] += 1
            note_type = "SIDENOTE" if is_sidenote else "MARGINNOTE"
            key = f"{note_type}_{counter[0]}_END"
            # Preserve inner HTML of the span for link extraction later
            markers[key] = span_tag.decode_contents().strip()

            # Replace label+input+span with a marker
            marker_tag = soup.new_tag("span")
            marker_tag.string = f"@@{key}@@"
            label.replace_with(marker_tag)
            if input_tag:
                input_tag.decompose()
            span_tag.decompose()

    return str(soup), markers


def postprocess_notes(md, markers):
    """Replace @@KEY@@ markers with {margin: ...} or {side: ...} syntax."""
    for key, content in markers.items():
        # Convert <a href="...">text</a> links to markdown
        content_md = re.sub(
            r'<a\s+href="([^"]+)"[^>]*>([^<]+)</a>',
            r'[\2](\1)',
            content
        )
        # Strip remaining HTML tags
        content_md = re.sub(r'<[^>]+>', '', content_md).strip()
        # Collapse whitespace
        content_md = re.sub(r'\s+', ' ', content_md)

        if key.startswith("MARGINNOTE_"):
            replacement = "{margin: " + content_md + "}"
        else:
            replacement = "{side: " + content_md + "}"
        md = md.replace(f"@@{key}@@", replacement)

    # Strip orphaned ⊕ characters left over from malformed label HTML
    # (e.g. <label .../>&#8853;</label> where BS4 treats &#8853; as a text sibling)
    md = re.sub(r'\s*⊕\s*', ' ', md)
    return md


# ---------------------------------------------------------------------------
# Run pandoc
# ---------------------------------------------------------------------------

def html_to_markdown(html):
    """Convert HTML body to Markdown using pandoc."""
    result = subprocess.run(
        [
            "pandoc",
            "--from=html",
            # Disable extensions that produce non-standard markdown:
            # -raw_html: don't pass through raw HTML (use markdown equivalents)
            # -native_divs: don't use ::: div syntax
            # -native_spans: don't produce native span syntax
            # -fenced_divs: disable fenced div (:::) blocks
            # +fenced_code_blocks: always use ``` for code, not indentation
            "--to=markdown-raw_html-native_divs-native_spans-fenced_divs+fenced_code_blocks-link_attributes-fenced_code_attributes-inline_code_attributes",
            "--wrap=none",
        ],
        input=html,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        print(f"  pandoc error: {result.stderr}", file=sys.stderr)
    return result.stdout


# ---------------------------------------------------------------------------
# Main conversion
# ---------------------------------------------------------------------------

def convert_post(html_path, out_path):
    html_text = html_path.read_text(encoding="utf-8")

    title, date, authors, body_html, has_mathjax = extract_post_info(html_text)

    # Pre-process Tufte note HTML into markers
    body_html, markers = preprocess_notes(body_html)

    # Convert body HTML -> Markdown via pandoc
    md = html_to_markdown(body_html)

    # Restore note markers as {side:}/{margin:} syntax
    md = postprocess_notes(md, markers)

    # Build YAML frontmatter
    fm_lines = ["---", f"title: {title}"]
    if date:
        fm_lines.append(f"date: {date}")
    fm_lines.append(f"authors: {authors}")
    if has_mathjax:
        fm_lines.append("mathjax: true")
    fm_lines.append("---")
    fm = "\n".join(fm_lines)

    out_path.write_text(fm + "\n\n" + md.strip() + "\n", encoding="utf-8")
    print(f"  {html_path.name} -> {out_path.name}  [{date}] {title!r}")


def main():
    root = Path(__file__).parent
    blog_dir = root / "blog"
    out_dir = root / "src" / "blog"
    out_dir.mkdir(parents=True, exist_ok=True)

    html_files = sorted(blog_dir.glob("*.html"))
    print(f"Converting {len(html_files)} posts...")
    for html_path in html_files:
        out_path = out_dir / f"{html_path.stem}.md"
        try:
            convert_post(html_path, out_path)
        except Exception as e:
            print(f"  ERROR {html_path.name}: {e}", file=sys.stderr)
            import traceback; traceback.print_exc()

    print(f"\nDone. Output in {out_dir}")


if __name__ == "__main__":
    main()
