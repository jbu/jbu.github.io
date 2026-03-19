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
# Pre-process HTML before pandoc
# ---------------------------------------------------------------------------

def preprocess_html(html):
    """Normalize HTML attributes that would produce broken markdown."""
    soup = BeautifulSoup(html, "html.parser")
    # Collapse whitespace in img title/alt attributes — multiline titles
    # cause pymarkdown to crash on the resulting markdown image syntax.
    for img in soup.find_all("img"):
        for attr in ("title", "alt"):
            if img.get(attr):
                img[attr] = re.sub(r'\s+', ' ', img[attr].strip())
    # Same for link title attributes
    for a in soup.find_all("a"):
        if a.get("title"):
            a["title"] = re.sub(r'\s+', ' ', a["title"].strip())
    return str(soup)


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
            # -link_attributes/-fenced_code_attributes/-inline_code_attributes:
            #   strip {attr} syntax that mistletoe/pymarkdown don't understand
            "--to=markdown-raw_html-native_divs-native_spans-fenced_divs+fenced_code_blocks-link_attributes-fenced_code_attributes-inline_code_attributes",
            "--wrap=auto",
            "--columns=120",
            "--markdown-headings=atx",
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
# Post-process markdown for lint compliance
# ---------------------------------------------------------------------------

def clean_markdown(md):
    """Strip trailing whitespace, fix list spacing, collapse multiple blank lines,
    convert indented code blocks to fenced, and ensure blank lines around fences."""
    lines = md.split('\n')

    # Pass 1: strip trailing whitespace and fix list marker spacing
    cleaned = []
    for line in lines:
        line = line.rstrip()
        # Fix extra spaces after list markers: "*   text" -> "* text" (MD030)
        line = re.sub(r'^(\s*[-*+])\s{2,}', r'\1 ', line)
        line = re.sub(r'^(\s*\d+\.)\s{2,}', r'\1 ', line)
        cleaned.append(line)

    # Pass 2: collapse consecutive blank lines to one (MD012)
    collapsed = []
    prev_blank = False
    for line in cleaned:
        is_blank = (line == '')
        if is_blank and prev_blank:
            continue
        collapsed.append(line)
        prev_blank = is_blank

    # Pass 3: convert 4-space indented code blocks to fenced (MD046)
    # Only convert outside existing fenced blocks to avoid corrupting their content.
    fenced = []
    i = 0
    in_fence = False
    lines = collapsed
    while i < len(lines):
        line = lines[i]
        # Track fence state: opening fence starts with ``` (+ optional lang), closing is exactly ```
        if line.startswith('```') and not in_fence:
            in_fence = True
            fenced.append(line)
            i += 1
            continue
        if line == '```' and in_fence:
            in_fence = False
            fenced.append(line)
            i += 1
            continue
        if in_fence:
            fenced.append(line)
            i += 1
            continue
        # Outside a fence: convert 4-space indented code blocks
        prev_blank = not fenced or fenced[-1] == ''
        if prev_blank and line.startswith('    ') and not line.startswith('\t'):
            block = []
            j = i
            while j < len(lines):
                if lines[j].startswith('    '):
                    block.append(lines[j])
                    j += 1
                elif lines[j] == '' and j + 1 < len(lines) and lines[j + 1].startswith('    '):
                    block.append('')
                    j += 1
                else:
                    break
            while block and block[-1] == '':
                block.pop()
            fenced.append('```')
            for bl in block:
                fenced.append(bl[4:] if bl.startswith('    ') else bl)
            fenced.append('```')
            i = j
        else:
            fenced.append(line)
            i += 1

    # Pass 4: merge split code blocks — closing ``` + indented-continuation + opening ```
    # (pandoc splits wide pandas/tabular output across multiple fenced blocks)
    merged = []
    i = 0
    in_fence = False
    lines = fenced
    while i < len(lines):
        line = lines[i]
        if line.startswith('```') and not in_fence:
            in_fence = True
        elif line == '```' and in_fence:
            in_fence = False
            # Look ahead: closing ``` followed by 4-space-indented lines then another ```
            # means this is a split code block — merge by skipping both fence markers
            if i + 1 < len(lines) and lines[i + 1].startswith('    '):
                j = i + 1
                cont = []
                while j < len(lines) and lines[j].startswith('    '):
                    cont.append(lines[j][4:])
                    j += 1
                if j < len(lines) and lines[j] == '```':
                    # Don't close this block — add continuation and skip opening ```
                    merged.extend(cont)
                    in_fence = True  # We're still inside the merged block
                    i = j + 1
                    continue
        merged.append(line)
        i += 1

    # Pass 5: ensure blank lines after closing fence markers (MD031)
    result = []
    in_fence = False
    for i, line in enumerate(merged):
        if line.startswith('```'):
            if not in_fence:
                in_fence = True
            else:
                in_fence = False
                result.append(line)
                # Add blank line after closing fence if next line is non-blank
                if i + 1 < len(merged) and merged[i + 1] != '':
                    result.append('')
                continue
        result.append(line)

    return '\n'.join(result)


# ---------------------------------------------------------------------------
# Main conversion
# ---------------------------------------------------------------------------

def convert_post(html_path, out_path):
    html_text = html_path.read_text(encoding="utf-8")

    title, date, authors, body_html, has_mathjax = extract_post_info(html_text)

    # Normalize HTML attributes before pandoc
    body_html = preprocess_html(body_html)

    # Pre-process Tufte note HTML into markers
    body_html, markers = preprocess_notes(body_html)

    # Convert body HTML -> Markdown via pandoc
    md = html_to_markdown(body_html)

    # Restore note markers as {side:}/{margin:} syntax
    md = postprocess_notes(md, markers)

    # Clean up whitespace and formatting for lint compliance
    md = clean_markdown(md)

    # Build YAML frontmatter — quote values that contain YAML-special characters
    def yaml_str(s):
        if any(c in s for c in ':#&*?|<>{}[]!\'"%@`'):
            return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'
        return s

    fm_lines = ["---", f"title: {yaml_str(title)}"]
    if date:
        fm_lines.append(f"date: {date}")
    fm_lines.append(f"authors: {yaml_str(authors)}")
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
