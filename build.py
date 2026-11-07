#!/usr/bin/env python3
"""Tech Style Bytes — tiny static blog builder.

Write a post:   posts/YYYY-MM-DD-slug.md  (front matter + markdown body)
Add photos:     images/  (web-sized, location data stripped)
Build:          python3 build.py            -> docs/  (GitHub Pages serves this folder)
Preview drafts: python3 build.py --drafts

Front matter keys (one per line, `key: value`):
  title, date (YYYY-MM-DD), category, cover, excerpt,
  venue, where, had, vibe, go, rating (0-10), price, gallery (comma list), draft (true/false)
"""
import html, os, re, shutil, sys, datetime
import markdown

SITE = {
    "name": "Tech Style Bytes",
    "tagline": "Tech. Style. Sydney.",
    "url": "https://techstylebytes.com",
    "instagram": "tech.style.bytes",
    "author": "Liza Tinker",
    "description": "Sydney cafes, bars, art, streets, fashion and tech, reviewed by Liza Tinker, Microsoft MVP with a fashion habit.",
}
CATEGORIES = ["Eat & Drink", "Bars", "Art", "Streets", "Fashion", "Tech"]
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "docs")
DRAFTS = "--drafts" in sys.argv
PREVIEW = "--preview" in sys.argv  # explicit index.html links for hosts without directory indexes
# Set True once techstylebytes.com DNS points at GitHub Pages. While False the site is served at
# https://lizatinker.github.io/Techstylebytes/ (all links are relative, so it works under that path).
CUSTOM_DOMAIN_LIVE = False


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower().replace("&", "and")).strip("-")


def esc(s):
    return html.escape(str(s or ""))


def load_posts():
    posts = []
    for fn in sorted(os.listdir(os.path.join(ROOT, "posts"))):
        if not fn.endswith(".md"):
            continue
        raw = open(os.path.join(ROOT, "posts", fn), encoding="utf-8").read()
        m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", raw, re.S)
        meta, body = {}, raw
        if m:
            for line in m.group(1).splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip()
            body = m.group(2)
        if meta.get("draft", "false").lower() == "true" and not DRAFTS:
            continue
        meta["slug"] = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", fn[:-3])
        meta["date"] = datetime.date.fromisoformat(meta.get("date") or fn[:10])
        meta["gallery"] = [g.strip() for g in meta.get("gallery", "").split(",") if g.strip()]
        meta["html"] = markdown.markdown(body, extensions=["extra", "smarty"])
        meta["is_draft"] = meta.get("draft", "false").lower() == "true"
        posts.append(meta)
    return sorted(posts, key=lambda p: p["date"], reverse=True)


def page(title, body, rel, desc=None, image=None, canonical=""):
    t = esc(title + " · " + SITE["name"]) if title else esc(SITE["name"] + " · " + SITE["tagline"])
    d = esc(desc or SITE["description"])
    og_img = f'<meta property="og:image" content="{SITE["url"]}/{esc(image)}">' if image else ""
    nav = "".join(f'<a href="{rel}category/{slugify(c)}/">{esc(c)}</a>' for c in CATEGORIES)
    year = datetime.date.today().year
    return f"""<!DOCTYPE html>
<html lang="en-AU"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t}</title><meta name="description" content="{d}">
<meta property="og:title" content="{t}"><meta property="og:description" content="{d}">{og_img}
<link rel="canonical" href="{SITE['url']}/{canonical}">
<link rel="stylesheet" href="{rel}static/style.css">
</head><body>
<header class="masthead">
  <a class="wordmark" href="{rel}">TECH <span>STYLE</span> BYTES</a>
  <p class="tagline">{esc(SITE['tagline'])}</p>
  <nav>{nav}<a href="{rel}about/">About</a></nav>
</header>
<main>{body}</main>
<footer>
  <p class="wordmark small">TECH <span>STYLE</span> BYTES</p>
  <p>Reviews, photos and opinions by {esc(SITE['author'])}. Always honest, never sponsored unless it says so.</p>
  <p><a href="https://instagram.com/{SITE['instagram']}">Instagram @{SITE['instagram']}</a> · © {year}</p>
</footer>
</body></html>"""


def card(p, rel, big=False):
    rating = f'<span class="score">{esc(p["rating"])}/10</span>' if p.get("rating") else ""
    draft = '<span class="draft">Sample</span>' if p["is_draft"] else ""
    return f"""<a class="card{' big' if big else ''}" href="{rel}posts/{p['slug']}/">
  <div class="img" style="background-image:url('{rel}{esc(p.get('cover',''))}')">{rating}</div>
  <div class="txt"><span class="chip">{esc(p.get('category',''))}</span>{draft}
  <h2>{esc(p['title'])}</h2><p>{esc(p.get('excerpt',''))}</p>
  <time>{p['date'].strftime('%-d %B %Y')}</time></div></a>"""


def post_page(p):
    rel = "../../"
    facts = [("Where", p.get("where")), ("What I had", p.get("had")), ("Vibe", p.get("vibe")),
             ("Go when", p.get("go")), ("Price", p.get("price"))]
    facts_html = "".join(f"<div><dt>{k}</dt><dd>{esc(v)}</dd></div>" for k, v in facts if v)
    verdict = ""
    if facts_html or p.get("rating"):
        score = f'<div class="bigscore">{esc(p["rating"])}<small>/10</small></div>' if p.get("rating") else ""
        verdict = f'<aside class="verdict"><h3>The verdict</h3>{score}<dl>{facts_html}</dl></aside>'
    gallery = "".join(f'<img src="{rel}{esc(g)}" alt="{esc(p["title"])}" loading="lazy">' for g in p["gallery"])
    gallery = f'<div class="gallery">{gallery}</div>' if gallery else ""
    draft = '<p class="draftnote">Sample layout: this post is a draft and won\'t go live until you approve it.</p>' if p["is_draft"] else ""
    body = f"""<article class="post">
  <div class="hero" style="background-image:url('{rel}{esc(p.get('cover',''))}')"></div>
  <div class="posthead">{draft}<a class="chip" href="{rel}category/{slugify(p.get('category',''))}/">{esc(p.get('category',''))}</a>
  <h1>{esc(p['title'])}</h1><p class="dek">{esc(p.get('excerpt',''))}</p>
  <time>{p['date'].strftime('%-d %B %Y')}</time>{f' · <span class="venue">{esc(p["venue"])}</span>' if p.get('venue') else ''}</div>
  <div class="postbody">{verdict}<div class="prose">{p['html']}</div></div>
  {gallery}
</article>"""
    return page(p["title"], body, rel, p.get("excerpt"), p.get("cover"), f"posts/{p['slug']}/")


def write(path, content):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    if PREVIEW and full.endswith(".html"):
        content = re.sub(r'href="((?:\.\./)*(?:[^"#:]*/)?)"', lambda m: f'href="{m.group(1)}index.html"', content)
    open(full, "w", encoding="utf-8").write(content)


def build():
    posts = load_posts()
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    shutil.copytree(os.path.join(ROOT, "static"), os.path.join(OUT, "static"))
    shutil.copytree(os.path.join(ROOT, "images"), os.path.join(OUT, "images"))
    cname = os.path.join(OUT, "CNAME")
    if CUSTOM_DOMAIN_LIVE:
        open(cname, "w").write("techstylebytes.com\n")
    elif os.path.exists(cname):
        os.remove(cname)
    open(os.path.join(OUT, ".nojekyll"), "w").write("")

    # home
    if posts:
        lead, rest = posts[0], posts[1:]
        grid = "".join(card(p, "") for p in rest) or '<p class="empty">More reviews landing soon.</p>'
        home = f'<section class="lead">{card(lead, "", big=True)}</section><h2 class="section">Latest</h2><section class="grid">{grid}</section>'
    else:
        home = '<p class="empty">First reviews landing soon.</p>'
    write("index.html", page("", home, ""))

    # categories
    for c in CATEGORIES:
        cp = [p for p in posts if p.get("category") == c]
        grid = "".join(card(p, "../../") for p in cp) or f'<p class="empty">No {esc(c)} reviews yet. Soon.</p>'
        write(f"category/{slugify(c)}/index.html",
              page(c, f'<h1 class="section big">{esc(c)}</h1><section class="grid">{grid}</section>', "../../", canonical=f"category/{slugify(c)}/"))

    # posts
    for p in posts:
        write(f"posts/{p['slug']}/index.html", post_page(p))

    # about
    about_md = open(os.path.join(ROOT, "about.md"), encoding="utf-8").read()
    about = f'<article class="about"><img src="../images/liza-pink-blazer.jpg" alt="Liza Tinker"><div class="prose">{markdown.markdown(about_md, extensions=["extra","smarty"])}</div></article>'
    write("about/index.html", page("About", about, "../", canonical="about/"))

    # sitemap
    urls = [""] + ["about/"] + [f"category/{slugify(c)}/" for c in CATEGORIES] + [f"posts/{p['slug']}/" for p in posts if not p["is_draft"]]
    sm = "".join(f"<url><loc>{SITE['url']}/{u}</loc></url>" for u in urls)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>')
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE['url']}/sitemap.xml\n")
    print(f"Built {len(posts)} post(s) -> docs/" + (" (drafts included)" if DRAFTS else ""))


if __name__ == "__main__":
    build()
