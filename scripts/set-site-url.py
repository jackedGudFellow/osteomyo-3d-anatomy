#!/usr/bin/env python3
"""Point every absolute site URL (canonical, Open Graph, Twitter, robots, sitemap)
at one base URL, and refresh the sitemap <lastmod>.

Usage: python3 scripts/set-site-url.py https://example.com/ [--root DIR]
Safe to re-run; it discovers the current base from <link rel="canonical">.
"""
import argparse, datetime, pathlib, re, sys

ap = argparse.ArgumentParser()
ap.add_argument("url")
ap.add_argument("--root", default=str(pathlib.Path(__file__).resolve().parent.parent))
a = ap.parse_args()

if not re.fullmatch(r"https?://[A-Za-z0-9.-]+(:\d+)?(/[A-Za-z0-9._~/-]*)?", a.url):
    sys.exit("URL must look like https://host/ or https://host/subpath/")
new = a.url.rstrip("/") + "/"
root = pathlib.Path(a.root)
index = root / "index.html"
m = re.search(r'<link rel="canonical" href="([^"]+)"', index.read_text(encoding="utf-8"))
if not m:
    sys.exit("canonical link not found in index.html")
old = m.group(1)

for name in ("index.html", "robots.txt", "sitemap.xml"):
    p = root / name
    t = p.read_text(encoding="utf-8").replace(old, new)
    if name == "sitemap.xml":
        t = re.sub(r"<lastmod>[^<]*</lastmod>", f"<lastmod>{datetime.date.today().isoformat()}</lastmod>", t)
    p.write_text(t, encoding="utf-8")
print(f"{old} -> {new}")
