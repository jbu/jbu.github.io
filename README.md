# jbu.github.io

Personal site, hosted on GitHub Pages. Markdown source in `src/`, rendered HTML committed in the repo root and `blog/`. GitHub Pages serves the HTML directly — no CI, no deploy step.

## Layout

```
src/
  index.md              homepage
  cv.md                 CV
  blog/*.md             blog posts
  external_links.txt    non-blog entries in the Scribbles list
templates/
  base.html             shared <head>/<body>
  index.html, cv.html, blog_post.html
build.py                md -> html
static/, tufte.css, local.css, et-book/
index.html, cv.html, blog/*.html   built output (committed)
```

## Author loop

```sh
mise install         # Python 3.14 + uv + prek, .venv auto-created
uv sync              # install build deps
mise run build       # src/*.md -> *.html
mise run serve       # preview at http://localhost:8000
```

Pre-commit (`prek`) runs `build.py` on any `.md`/`.txt` change, so built HTML stays in sync.

## Adding a blog post

1. Create `src/blog/<slug>.md` with frontmatter:

   ```yaml
   ---
   title: Your Title
   date: 2026-04-23
   authors: James Uther
   mathjax: true   # optional, only if post uses math
   draft: true     # optional, skips build + scribbles entry
   ---

   Body as Markdown.
   ```

2. Build. The post appears in the Scribbles list automatically (merged with `external_links.txt` and date-sorted).

## Adding an external link

Add a line to `src/external_links.txt`:

```
2026-04-23 | Title shown in the list | https://example.com/
```

## Tufte sidenotes and margin notes

Inline syntax handled by `build.py`:

- `{side: text}` → numbered sidenote
- `{margin: text}` → ⊕-toggle margin note

Both use the `tufte.css` class structure (`label.margin-toggle` + checkbox + `span.sidenote`/`span.marginnote`).

## Why this setup

- Builds instantly, deploys instantly (GitHub Pages serves static files).
- Very limited supply chain.
- Loads quickly; CO2 footprint is minimal.
- Like `AWK`, this stack won't go out of style next year.

I went through a `hugo` stage, but too many moving parts for what this site needs.
