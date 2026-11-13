#!/usr/bin/env python3
"""Tech Style Bytes — tiny static blog builder.

Write a post:   posts/YYYY-MM-DD-slug.md  (front matter + markdown body)
Add photos:     images/  (web-sized, location data stripped)
Build:          python3 build.py            -> docs/  (GitHub Pages serves this folder)
Preview drafts: python3 build.py --drafts

Front matter keys (one per line, `key: value`):
  title, date (YYYY-MM-DD), category, cover, excerpt,
  venue, where, had, vibe, go, rating (0-10), price, gallery (comma list), draft (true/false)
  Places (shown in the "Find it" box at the bottom + Google structured data):
    address, hours, website, venue_instagram (handle, no @), place_type (Cafe, Bakery, Restaurant, BarOrPub)
  reel: the Instagram reel URL for this post (embedded on the page)
  keywords: comma list for SEO (optional)
  gallery items can carry alt text: images/x.jpg | Alt text here
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
CATEGORIES = ["Eat & Drink", "Bars", "Art", "Streets", "Fashion", "Tech", "Work Smart"]
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "docs")
DRAFTS = "--drafts" in sys.argv
PREVIEW = "--preview" in sys.argv  # explicit index.html links for hosts without directory indexes
# Set True once techstylebytes.com DNS points at GitHub Pages. While False the site is served at
# https://lizatinker.github.io/Techstylebytes/ (all links are relative, so it works under that path).
CUSTOM_DOMAIN_LIVE = True


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
        meta["gallery"] = [tuple((x.strip() for x in (g + "|").split("|")[:2])) for g in meta.get("gallery", "").split(",") if g.strip()]
        meta["html"] = markdown.markdown(body, extensions=["extra", "smarty"])
        meta["is_draft"] = meta.get("draft", "false").lower() == "true"
        posts.append(meta)
    return sorted(posts, key=lambda p: p["date"], reverse=True)


def page(title, body, rel, desc=None, image=None, canonical="", og_type="website", extra_head=""):
    t = esc(title + " · " + SITE["name"]) if title else esc(SITE["name"] + " · " + SITE["tagline"])
    d = esc(desc or SITE["description"])
    og_img = f'<meta property="og:image" content="{SITE["url"]}/{esc(image)}">' if image else ""
    nav = "".join(f'<a href="{rel}category/{slugify(c)}/">{esc(c)}</a>' for c in CATEGORIES)
    year = datetime.date.today().year
    return f"""<!DOCTYPE html>
<html lang="en-AU"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t}</title><meta name="description" content="{d}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="author" content="{esc(SITE['author'])}">
<meta property="og:site_name" content="{esc(SITE['name'])}"><meta property="og:locale" content="en_AU">
<meta property="og:type" content="{og_type}"><meta property="og:url" content="{SITE['url']}/{canonical}">
<meta property="og:title" content="{t}"><meta property="og:description" content="{d}">{og_img}
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{t}"><meta name="twitter:description" content="{d}">
<link rel="canonical" href="{SITE['url']}/{canonical}">{extra_head}
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
    gallery = "".join(f'<img src="{rel}{esc(g)}" alt="{esc(a or p["title"])}" loading="lazy">' for g, a in p["gallery"])
    gallery = f'<div class="gallery">{gallery}</div>' if gallery else ""
    draft = '<p class="draftnote">Sample layout: this post is a draft and won\'t go live until you approve it.</p>' if p["is_draft"] else ""
    body = f"""<article class="post">
  <div class="hero" style="background-image:url('{rel}{esc(p.get('cover',''))}')"></div>
  <div class="posthead">{draft}<a class="chip" href="{rel}category/{slugify(p.get('category',''))}/">{esc(p.get('category',''))}</a>
  <h1>{esc(p['title'])}</h1><p class="dek">{esc(p.get('excerpt',''))}</p>
  <time>{p['date'].strftime('%-d %B %Y')}</time>{f' · <span class="venue">{esc(p["venue"])}</span>' if p.get('venue') else ''}</div>
  <div class="postbody">{verdict}<div class="prose">{p['html']}</div></div>
  {gallery}
  {reel_block(p)}
  {find_it(p)}
</article>"""
    head = f'<meta property="article:published_time" content="{p["date"].isoformat()}">'
    if p.get("keywords"):
        head += f'<meta name="keywords" content="{esc(p["keywords"])}">'
    head += json_ld(p)
    return page(p["title"], body, rel, p.get("excerpt"), p.get("cover"), f"posts/{p['slug']}/", "article", head)


def maps_url(p):
    import urllib.parse
    return "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote(f"{p.get('venue','')} {p['address']}")


def find_it(p):
    if not (p.get("address") or p.get("website") or p.get("venue_instagram")):
        return ""
    rows = []
    if p.get("address"):
        rows.append(f'<div><dt>Address</dt><dd><a href="{esc(maps_url(p))}" rel="noopener">{esc(p["address"])}</a></dd></div>')
    if p.get("hours"):
        rows.append(f'<div><dt>Hours</dt><dd>{esc(p["hours"])}</dd></div>')
    if p.get("website"):
        label = re.sub(r"^https?://(www\.)?", "", p["website"]).rstrip("/")
        rows.append(f'<div><dt>Website</dt><dd><a href="{esc(p["website"])}" rel="noopener">{esc(label)}</a></dd></div>')
    if p.get("venue_instagram"):
        h = p["venue_instagram"].lstrip("@")
        rows.append(f'<div><dt>Instagram</dt><dd><a href="https://instagram.com/{esc(h)}" rel="noopener">@{esc(h)}</a></dd></div>')
    return f'<aside class="findit"><h3>Find it</h3><p class="findname">{esc(p.get("venue") or p["title"])}</p><dl>{"".join(rows)}</dl></aside>'


def reel_block(p):
    if not p.get("reel"):
        return ""
    u = esc(p["reel"])
    return f'''<section class="reel"><h3>Watch the reel</h3>
  <blockquote class="instagram-media" data-instgrm-permalink="{u}" data-instgrm-version="14"><a href="{u}">Watch this review on Instagram @{esc(SITE['instagram'])}</a></blockquote>
  <script async src="https://www.instagram.com/embed.js"></script></section>'''


def json_ld(p):
    import json
    url = f"{SITE['url']}/posts/{p['slug']}/"
    img = f"{SITE['url']}/{p['cover']}" if p.get("cover") else None
    author = {"@type": "Person", "name": SITE["author"], "url": f"{SITE['url']}/about/",
              "sameAs": [f"https://instagram.com/{SITE['instagram']}"]}
    data = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": p["title"],
            "description": p.get("excerpt", ""), "datePublished": p["date"].isoformat(),
            "author": author, "publisher": {"@type": "Organization", "name": SITE["name"], "url": SITE["url"]},
            "mainEntityOfPage": url, "url": url, "articleSection": p.get("category", ""), "inLanguage": "en-AU"}
    if img:
        data["image"] = img
    if p.get("keywords"):
        data["keywords"] = p["keywords"]
    graph = [data]
    if p.get("address"):
        place = {"@type": p.get("place_type") or "LocalBusiness", "name": p.get("venue") or p["title"]}
        parts = [x.strip() for x in p["address"].split(",")]
        addr = {"@type": "PostalAddress", "streetAddress": parts[0], "addressCountry": "AU"}
        m = re.search(r"([A-Za-z ]+?)\s+(NSW|VIC|QLD|SA|WA|TAS|ACT|NT)\s+(\d{4})", p["address"])
        if m:
            addr.update(addressLocality=m.group(1).strip(), addressRegion=m.group(2), postalCode=m.group(3))
        place["address"] = addr
        same = [x for x in [p.get("website"), f"https://instagram.com/{p['venue_instagram'].lstrip('@')}" if p.get("venue_instagram") else None] if x]
        if same:
            place["sameAs"] = same
        if p.get("website"):
            place["url"] = p["website"]
        review = {"@type": "Review", "itemReviewed": place, "author": author, "datePublished": p["date"].isoformat(),
                  "name": p["title"], "url": url}
        if p.get("rating"):
            review["reviewRating"] = {"@type": "Rating", "ratingValue": p["rating"], "bestRating": "10", "worstRating": "0"}
        graph.append(review)
    blob = json.dumps(graph if len(graph) > 1 else data, ensure_ascii=False).replace("</", "<\\/")
    return f'<script type="application/ld+json">{blob}</script>'


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
        grid = "".join(card(p, "../../") for p in cp) or f'<p class="empty">No {esc(c)} posts yet. Soon.</p>'
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
    latest = posts[0]["date"].isoformat() if posts else datetime.date.today().isoformat()
    mods = {f"posts/{p['slug']}/": p["date"].isoformat() for p in posts}
    sm = "".join(f"<url><loc>{SITE['url']}/{u}</loc><lastmod>{mods.get(u, latest)}</lastmod></url>" for u in urls)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>')
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE['url']}/sitemap.xml\n")
    print(f"Built {len(posts)} post(s) -> docs/" + (" (drafts included)" if DRAFTS else ""))


if __name__ == "__main__":
    build()
