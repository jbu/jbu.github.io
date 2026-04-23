# CLAUDE.md

Guidance for Claude Code working in this repo.

## What this is

A personal website and blog on GitHub Pages. Markdown sources in `src/`, rendered HTML committed in the repo root and `blog/`. GitHub Pages serves the built HTML directly — no CI, no deploy step.

Deps: `mistletoe`, `jinja2`, `pymarkdownlnt`. Managed via `uv`, Python pinned via `mise` (3.14).

## Setup

```sh
mise install   # Python + uv + prek; .venv auto-created
uv sync
mise run build # rebuild all pages
mise run serve # preview at localhost:8000
```

`prek` runs `build.py` on every `.md`/`.txt` change and lints Markdown with `pymarkdown`.

## Architecture

- `src/index.md`, `src/cv.md`, `src/blog/*.md` — Markdown sources with YAML-ish frontmatter.
- `src/external_links.txt` — one `date | title | url` per line; merged with blog post frontmatter to build the Scribbles list.
- `build.py` — converts Markdown to HTML via `mistletoe`, wraps in Jinja templates.
- `templates/base.html` — shared `<head>`/`<body>` shell; `index.html`, `cv.html`, `blog_post.html` extend it via `{% block %}`.
- `tufte.css`, `local.css`, `et-book/`, `static/` — styling and assets.
- Built output lives alongside sources: `index.html`, `cv.html`, `blog/*.html`.

## Build behaviour

- The Scribbles list is injected at `<!-- SCRIBBLES -->` in `src/index.md`, merging blog frontmatter + `external_links.txt`, sorted newest-first.
- Posts with `draft: true` in frontmatter are skipped: no HTML output, no Scribbles entry.
- Custom Markdown extensions for Tufte notes: `{side: ...}` → numbered sidenote, `{margin: ...}` → ⊕ margin note.
- Frontmatter is parsed by a tiny hand-rolled reader; it strips surrounding YAML quotes but does not support nested structures.

## Conventions

- Markdown first; use HTML only when attributes require it (classes, `rel=me`, data attributes). Mistletoe passes inline HTML through.
- CSS paths are absolute (`/local.css`, `/tufte.css`) so templates work at any depth.
- No frameworks or client-side JS beyond the Tufte CSS toggles and (optional) MathJax per post.
- Don't add CI/deploy workflows — GitHub Pages serves the committed HTML directly by design.
