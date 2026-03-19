# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A personal website and blog hosted on GitHub Pages. It is intentionally minimal: raw HTML files with no build system, no static site generator, and no framework. The only dependency is `mistletoe` (a Markdown-to-HTML Python library), managed via `uv`.

## Setup

Uses `mise` to manage Python 3.14 and `uv`. The venv is created and sourced automatically by mise.

```sh
mise install   # installs Python + uv, creates .venv
uv sync        # installs mistletoe into .venv
```

## Architecture

- **`index.html`** — homepage
- **`cv.html`** — CV/resume page
- **`blog/`** — individual blog post HTML files, hand-authored
- **`static/`** — images, favicon, and other assets
- **`tufte.css`** — Tufte-style CSS (main stylesheet)
- **`local.css`** — small local overrides
- **`et-book/`** — ET Book font files used by tufte.css

There is no build step. Pages are served directly from the repo root via GitHub Pages. Deployment happens automatically on push via GitHub Pages (no workflow file — uses the default GitHub Pages branch deploy).

## Conventions

- Blog posts live in `blog/` as plain `.html` files.
- Blog posts link back to `../index.html` and reference `../local.css` / `../tufte.css`.
- `mistletoe` is available if you need to convert Markdown to HTML snippets programmatically, but posts are typically written directly in HTML.
- CSS uses the Tufte style (`tufte.css`); avoid adding heavy frameworks.
