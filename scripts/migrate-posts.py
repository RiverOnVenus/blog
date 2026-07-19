#!/usr/bin/env python3
"""Migrate Jekyll _posts to AstroPaper src/content/posts/"""

import os, re, yaml, shutil

JEKYLL_DIR = "_posts"
ASTRO_DIR = "src/content/posts"
IMG_SRC = "assets/img/post"
IMG_DST = "public/images/posts"

def extract_date_slug(filename):
    m = re.match(r'(\d{4}-\d{2}-\d{2})-(.+)\.(?:md|markdown|mdown|mkdn|mkd)$', filename)
    return (m.group(1), m.group(2)) if m else (None, None)

def parse_front_matter(content):
    if not content.startswith('---'):
        return None, content
    parts = content.split('---', 2)
    if len(parts) < 3:
        return None, content
    try:
        return yaml.safe_load(parts[1]), parts[2].strip()
    except yaml.YAMLError:
        return None, content

def make_description(body, n=160):
    text = re.sub(r'<[^>]+>', '', body)
    text = re.sub(r'[#*`\[\]()>!|]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:n]

def convert_body(body):
    # {% include figure.html src="..." gallery="..." caption="..." %}
    def replace_figure(m):
        attrs = m.group(1)
        src = re.search(r'src="([^"]+)"', attrs)
        caption = re.search(r'caption="([^"]+)"', attrs)
        s = src.group(1) if src else ""
        s = s.replace('../assets/img/post/', '/images/posts/')
        cap = caption.group(1) if caption else ""
        if cap:
            return f'<figure>\n  <img src="{s}" alt="{cap}" loading="lazy" decoding="async" />\n  <figcaption>{cap}</figcaption>\n</figure>'
        return f'<img src="{s}" loading="lazy" decoding="async" />'
    body = re.sub(r'\{%\s*include figure\.html\s+([^%]+)\s*%\}', replace_figure, body)
    # * TOC {:toc} → remove (AstroPaper has remark-toc)
    body = re.sub(r'\*\s*TOC\s*\n\{:toc\}\n?', '', body)
    # Other liquid
    body = re.sub(r'\{%[^%]*%\}\n?', '', body)
    body = re.sub(r'\{\{[^}]*\}\}', '', body)
    return body.strip()

def main():
    os.makedirs(ASTRO_DIR, exist_ok=True)
    if os.path.exists(IMG_SRC) and not os.path.exists(IMG_DST):
        shutil.copytree(IMG_SRC, IMG_DST)

    migrated = 0
    for fname in sorted(os.listdir(JEKYLL_DIR)):
        if not fname.endswith(('.md','.markdown','.mdown','.mkdn','.mkd')):
            continue
        date_str, slug = extract_date_slug(fname)
        if not date_str:
            print(f"SKIP {fname}")
            continue
        with open(os.path.join(JEKYLL_DIR, fname)) as f:
            content = f.read()
        fm, body = parse_front_matter(content)
        if fm is None:
            print(f"SKIP {fname} (bad fm)")
            continue
        body = convert_body(body)
        new_fm = {
            'title': fm.get('title', slug.replace('-',' ').title()),
            'description': fm.get('description') or make_description(body),
            'pubDatetime': date_str,
            'tags': fm.get('categories', ['others']),
        }
        if fm.get('draft'):
            new_fm['draft'] = True
        out = os.path.join(ASTRO_DIR, f"{slug}.md")
        with open(out, 'w') as f:
            f.write('---\n')
            yaml.dump(new_fm, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
            f.write('---\n\n')
            f.write(body)
        print(f"OK  {fname} -> {slug}.md")
        migrated += 1
    print(f"\nDone: {migrated} posts migrated")

if __name__ == '__main__':
    main()
