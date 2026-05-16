# jbu.github.io

Personal site, hosted on GitHub Pages. Markdown source in `content/`, built HTML committed in `docs/`. GitHub Pages serves `docs/` directly from the main branch — no CI, no deploy step.

Built with [Zola](https://www.getzola.org).

## Layout

```
content/
  _index.md             homepage body
  cv.md                 CV
  blog/*.md             blog posts
  links/*.md            non-blog entries in the Scribbles list
templates/
  base.html             shared <head>/<body>
  index.html            homepage (Scribbles injected here)
  cv.html
  blog/page.html        blog post template
  shortcodes/           sidenote and marginnote shortcodes
static/
  static/               images and other assets (served at /static/)
  tufte.css, local.css
  et-book/              fonts
config.toml             Zola config
docs/                   built output (committed, served by GitHub Pages)
```

## Author loop

```sh
mise install         # Zola
mise run build       # content/ -> docs/
mise run serve       # preview at http://127.0.0.1:1111 with live reload
```

## Adding a blog post

1. Create `content/blog/<slug>.md` with frontmatter:

   ```toml
   +++
   title = "Your Title"
   date = 2026-04-23
   template = "blog/page.html"
   aliases = ["blog/<slug>.html"]  # redirect from old-style URL

   [extra]
   authors = "James Uther"
   mathjax = true   # optional, only if post uses maths
   +++

   Body as Markdown.
   ```

2. `mise run build`. The post appears in the Scribbles list automatically (merged with `content/links/` and date-sorted).

## Adding an external link

Create `content/links/<slug>.md`:

```toml
+++
title = "Title shown in the list"
date = 2026-04-23

[extra]
url = "https://example.com/"
+++
```

## Tufte sidenotes and margin notes

Use body shortcodes in posts:

```
{% sidenote(num="1") %}Note text here.{% end %}
{% marginnote(num="1") %}Note text here.{% end %}
```

Both use the `tufte.css` class structure (`label.margin-toggle` + checkbox + `span.sidenote`/`span.marginnote`). The `num` must be unique within a page.

## Deploying

```sh
mise run build
jj commit -m "build"
jj git push
```

GitHub Pages is configured to serve from the `docs/` folder on the main branch.

## RSS

The blog feed is at `/blog/rss.xml`.

## Why this setup

- Builds instantly, deploys instantly (GitHub Pages serves static files).
- Very limited supply chain — Zola is a single self-contained binary.
- Loads quickly; CO2 footprint is minimal.
