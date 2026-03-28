"""
Generador estatico para Bitacora 01234.
Lee markdown con frontmatter YAML desde content/,
renderiza via Jinja2 y genera HTML en docs/.
"""

import os
import re
import json
import shutil
import unicodedata

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader

# --- Rutas ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
CONTENT_DIR = os.path.join(PROJECT_DIR, 'content')
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(PROJECT_DIR, 'static')
DOCS_DIR = os.path.join(PROJECT_DIR, 'docs')

# Hub URL (relativo desde docs/)
HUB_URL = '/'

# Jinja2
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))


# --- SVGs por categoria ---
# Thumbnails (120x80) para listados

SVG_THUMBS = {
    'ia': '''<svg class="article-svg" viewBox="0 0 120 80" xmlns="http://www.w3.org/2000/svg">
    <rect width="120" height="80" fill="#1e293b"/>
    <circle cx="60" cy="32" r="16" fill="none" stroke="#94a3b8" stroke-width="1"/>
    <circle cx="60" cy="32" r="6" fill="#94a3b8" opacity="0.4"/>
    <line x1="36" y1="56" x2="50" y2="44" stroke="#475569" stroke-width="0.8"/>
    <line x1="84" y1="56" x2="70" y2="44" stroke="#475569" stroke-width="0.8"/>
    <line x1="60" y1="48" x2="60" y2="62" stroke="#475569" stroke-width="0.8"/>
    <circle cx="36" cy="58" r="3" fill="#475569"/>
    <circle cx="84" cy="58" r="3" fill="#475569"/>
    <circle cx="60" cy="64" r="3" fill="#475569"/>
    <circle cx="60" cy="32" r="2" fill="#94a3b8"/>
</svg>''',
    'arte': '''<svg class="article-svg" viewBox="0 0 120 80" xmlns="http://www.w3.org/2000/svg">
    <rect width="120" height="80" fill="#1a1a2e"/>
    <rect x="20" y="15" width="30" height="50" fill="none" stroke="#94a3b8" stroke-width="0.8" transform="rotate(-5 35 40)"/>
    <rect x="70" y="15" width="30" height="50" fill="none" stroke="#475569" stroke-width="0.8" transform="rotate(5 85 40)"/>
    <line x1="26" y1="30" x2="44" y2="30" stroke="#94a3b8" stroke-width="0.5" opacity="0.6"/>
    <line x1="26" y1="36" x2="44" y2="36" stroke="#94a3b8" stroke-width="0.5" opacity="0.4"/>
    <circle cx="60" cy="40" r="8" fill="none" stroke="#64748b" stroke-width="0.8" stroke-dasharray="2 2"/>
</svg>''',
    'filosofia': '''<svg class="article-svg" viewBox="0 0 120 80" xmlns="http://www.w3.org/2000/svg">
    <rect width="120" height="80" fill="#1a1a1a"/>
    <text x="15" y="28" fill="#333" font-family="monospace" font-size="8">0</text>
    <text x="35" y="28" fill="#444" font-family="monospace" font-size="8">1</text>
    <text x="55" y="28" fill="#555" font-family="monospace" font-size="8">2</text>
    <text x="75" y="28" fill="#666" font-family="monospace" font-size="8">3</text>
    <text x="95" y="28" fill="#777" font-family="monospace" font-size="8">4</text>
    <line x1="15" y1="38" x2="105" y2="38" stroke="#333" stroke-width="0.5"/>
    <circle cx="18" cy="55" r="10" fill="none" stroke="#fafafa" stroke-width="0.5" opacity="0.3"/>
    <circle cx="40" cy="55" r="10" fill="none" stroke="#e8d44d" stroke-width="0.5" opacity="0.3"/>
    <circle cx="62" cy="55" r="10" fill="none" stroke="#d4519a" stroke-width="0.5" opacity="0.3"/>
    <circle cx="84" cy="55" r="10" fill="none" stroke="#3b82f6" stroke-width="0.5" opacity="0.3"/>
    <circle cx="106" cy="55" r="10" fill="none" stroke="#888" stroke-width="0.5" opacity="0.3"/>
</svg>''',
}

# Heroes (780x160) para paginas de articulo

SVG_HEROES = {
    'ia': '''<svg class="post-hero-svg" viewBox="0 0 780 160" xmlns="http://www.w3.org/2000/svg">
    <rect width="780" height="160" fill="#1e293b"/>
    <circle cx="120" cy="50" r="4" fill="#94a3b8" opacity="0.6"/>
    <circle cx="120" cy="80" r="4" fill="#94a3b8" opacity="0.6"/>
    <circle cx="120" cy="110" r="4" fill="#94a3b8" opacity="0.6"/>
    <circle cx="260" cy="40" r="4" fill="#94a3b8" opacity="0.8"/>
    <circle cx="260" cy="70" r="4" fill="#94a3b8" opacity="0.8"/>
    <circle cx="260" cy="100" r="4" fill="#94a3b8" opacity="0.8"/>
    <circle cx="260" cy="130" r="4" fill="#94a3b8" opacity="0.8"/>
    <circle cx="400" cy="60" r="5" fill="#94a3b8"/>
    <circle cx="400" cy="100" r="5" fill="#94a3b8"/>
    <line x1="124" y1="50" x2="256" y2="40" stroke="#475569" stroke-width="0.5"/>
    <line x1="124" y1="50" x2="256" y2="70" stroke="#475569" stroke-width="0.5"/>
    <line x1="124" y1="80" x2="256" y2="70" stroke="#475569" stroke-width="0.5"/>
    <line x1="124" y1="80" x2="256" y2="100" stroke="#475569" stroke-width="0.5"/>
    <line x1="124" y1="110" x2="256" y2="100" stroke="#475569" stroke-width="0.5"/>
    <line x1="124" y1="110" x2="256" y2="130" stroke="#475569" stroke-width="0.5"/>
    <line x1="264" y1="40" x2="396" y2="60" stroke="#475569" stroke-width="0.5"/>
    <line x1="264" y1="70" x2="396" y2="60" stroke="#475569" stroke-width="0.5"/>
    <line x1="264" y1="100" x2="396" y2="100" stroke="#475569" stroke-width="0.5"/>
    <line x1="264" y1="130" x2="396" y2="100" stroke="#475569" stroke-width="0.5"/>
    <ellipse cx="560" cy="80" rx="60" ry="35" fill="none" stroke="#94a3b8" stroke-width="1"/>
    <circle cx="560" cy="80" r="18" fill="none" stroke="#94a3b8" stroke-width="0.8"/>
    <circle cx="560" cy="80" r="6" fill="#94a3b8" opacity="0.4"/>
    <line x1="640" y1="30" x2="700" y2="30" stroke="#334155" stroke-width="0.5"/>
    <line x1="650" y1="50" x2="730" y2="50" stroke="#334155" stroke-width="0.5"/>
    <line x1="640" y1="70" x2="710" y2="70" stroke="#334155" stroke-width="0.5"/>
    <line x1="650" y1="90" x2="740" y2="90" stroke="#334155" stroke-width="0.5"/>
    <line x1="640" y1="110" x2="720" y2="110" stroke="#334155" stroke-width="0.5"/>
    <line x1="650" y1="130" x2="700" y2="130" stroke="#334155" stroke-width="0.5"/>
</svg>''',
    'arte': '''<svg class="post-hero-svg" viewBox="0 0 780 160" xmlns="http://www.w3.org/2000/svg">
    <rect width="780" height="160" fill="#1a1a2e"/>
    <rect x="80" y="20" width="120" height="120" fill="none" stroke="#94a3b8" stroke-width="1"/>
    <rect x="90" y="30" width="100" height="100" fill="none" stroke="#475569" stroke-width="0.5"/>
    <rect x="95" y="35" width="45" height="40" fill="#2a1a1a" opacity="0.8"/>
    <rect x="145" y="35" width="40" height="40" fill="#1a2a2a" opacity="0.8"/>
    <rect x="95" y="80" width="90" height="45" fill="#1a1a2a" opacity="0.6"/>
    <line x1="280" y1="60" x2="380" y2="60" stroke="#94a3b8" stroke-width="3" stroke-linecap="round" opacity="0.3"/>
    <line x1="290" y1="80" x2="370" y2="80" stroke="#94a3b8" stroke-width="2" stroke-linecap="round" opacity="0.2"/>
    <line x1="300" y1="100" x2="360" y2="100" stroke="#94a3b8" stroke-width="1" stroke-linecap="round" opacity="0.15"/>
    <g opacity="0.3">
        <line x1="480" y1="20" x2="480" y2="140" stroke="#475569" stroke-width="0.5"/>
        <line x1="520" y1="20" x2="520" y2="140" stroke="#475569" stroke-width="0.5"/>
        <line x1="560" y1="20" x2="560" y2="140" stroke="#475569" stroke-width="0.5"/>
        <line x1="600" y1="20" x2="600" y2="140" stroke="#475569" stroke-width="0.5"/>
        <line x1="640" y1="20" x2="640" y2="140" stroke="#475569" stroke-width="0.5"/>
        <line x1="680" y1="20" x2="680" y2="140" stroke="#475569" stroke-width="0.5"/>
        <line x1="460" y1="40" x2="700" y2="40" stroke="#475569" stroke-width="0.5"/>
        <line x1="460" y1="80" x2="700" y2="80" stroke="#475569" stroke-width="0.5"/>
        <line x1="460" y1="120" x2="700" y2="120" stroke="#475569" stroke-width="0.5"/>
    </g>
    <path d="M 220 80 Q 350 10 460 80" fill="none" stroke="#64748b" stroke-width="0.8" stroke-dasharray="4 3"/>
</svg>''',
    'filosofia': '''<svg class="post-hero-svg" viewBox="0 0 780 160" xmlns="http://www.w3.org/2000/svg">
    <rect width="780" height="160" fill="#1a1a1a"/>
    <text x="80" y="45" fill="#333" font-family="monospace" font-size="24" font-weight="300">0</text>
    <text x="220" y="45" fill="#444" font-family="monospace" font-size="24" font-weight="300">1</text>
    <text x="360" y="45" fill="#555" font-family="monospace" font-size="24" font-weight="300">2</text>
    <text x="500" y="45" fill="#666" font-family="monospace" font-size="24" font-weight="300">3</text>
    <text x="640" y="45" fill="#777" font-family="monospace" font-size="24" font-weight="300">4</text>
    <line x1="80" y1="60" x2="660" y2="60" stroke="#333" stroke-width="0.5"/>
    <circle cx="90" cy="100" r="22" fill="none" stroke="#fafafa" stroke-width="0.8" opacity="0.25"/>
    <circle cx="230" cy="100" r="22" fill="none" stroke="#e8d44d" stroke-width="0.8" opacity="0.25"/>
    <circle cx="370" cy="100" r="22" fill="none" stroke="#d4519a" stroke-width="0.8" opacity="0.25"/>
    <circle cx="510" cy="100" r="22" fill="none" stroke="#3b82f6" stroke-width="0.8" opacity="0.25"/>
    <circle cx="650" cy="100" r="22" fill="none" stroke="#888" stroke-width="0.8" opacity="0.25"/>
    <circle cx="90" cy="100" r="3" fill="#fafafa" opacity="0.15"/>
    <circle cx="230" cy="100" r="3" fill="#e8d44d" opacity="0.15"/>
    <circle cx="370" cy="100" r="3" fill="#d4519a" opacity="0.15"/>
    <circle cx="510" cy="100" r="3" fill="#3b82f6" opacity="0.15"/>
    <circle cx="650" cy="100" r="3" fill="#888" opacity="0.15"/>
    <text x="90" y="138" fill="#444" font-family="monospace" font-size="7" text-anchor="middle">potencial</text>
    <text x="230" y="138" fill="#444" font-family="monospace" font-size="7" text-anchor="middle">esencia</text>
    <text x="370" y="138" fill="#444" font-family="monospace" font-size="7" text-anchor="middle">analisis</text>
    <text x="510" y="138" fill="#444" font-family="monospace" font-size="7" text-anchor="middle">conexion</text>
    <text x="650" y="138" fill="#444" font-family="monospace" font-size="7" text-anchor="middle">materia</text>
</svg>''',
}

# SVG por defecto para categorias no mapeadas
SVG_THUMB_DEFAULT = '''<svg class="article-svg" viewBox="0 0 120 80" xmlns="http://www.w3.org/2000/svg">
    <rect width="120" height="80" fill="#222"/>
    <circle cx="60" cy="40" r="15" fill="none" stroke="#475569" stroke-width="0.8"/>
    <circle cx="60" cy="40" r="4" fill="#475569" opacity="0.5"/>
</svg>'''

SVG_HERO_DEFAULT = '''<svg class="post-hero-svg" viewBox="0 0 780 160" xmlns="http://www.w3.org/2000/svg">
    <rect width="780" height="160" fill="#222"/>
    <circle cx="390" cy="80" r="40" fill="none" stroke="#475569" stroke-width="1"/>
    <circle cx="390" cy="80" r="10" fill="#475569" opacity="0.4"/>
</svg>'''


# --- Utilidades ---

def slugify(value):
    """Convierte cadena a slug URL-friendly."""
    value = str(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('utf-8')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    value = re.sub(r'[-\s]+', '-', value)
    return value


def extract_excerpt(html_content, max_chars=160):
    """Extrae texto plano del HTML y trunca para excerpt."""
    text = re.sub(r'<[^>]+>', '', html_content)
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) > max_chars:
        text = text[:max_chars].rsplit(' ', 1)[0] + '...'
    return text


def get_svg(category, size='thumb'):
    """Devuelve SVG segun categoria y tamano."""
    cat_key = slugify(category)
    if size == 'hero':
        return SVG_HEROES.get(cat_key, SVG_HERO_DEFAULT)
    return SVG_THUMBS.get(cat_key, SVG_THUMB_DEFAULT)


# --- Pipeline ---

def clean_docs():
    """Limpia docs/ antes de generar."""
    if os.path.exists(DOCS_DIR):
        shutil.rmtree(DOCS_DIR)
    os.makedirs(DOCS_DIR)
    print(f"[clean] {DOCS_DIR}")


def copy_static():
    """Copia static/ a docs/static/."""
    if os.path.exists(STATIC_DIR):
        shutil.copytree(STATIC_DIR, os.path.join(DOCS_DIR, 'static'))
        print(f"[copy]  static -> docs/static")


def parse_markdown(filepath):
    """Parsea markdown con frontmatter YAML. Devuelve (metadata, html)."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    front_matter = {}
    markdown_content = content

    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) > 2:
            front_matter = yaml.safe_load(parts[1]) or {}
            markdown_content = parts[2]

    html = markdown.markdown(markdown_content, extensions=['extra'])

    # Conclusion como bloque separado
    conclusion = front_matter.pop('conclusion', None)
    if conclusion:
        html += f'<div class="post-conclusion"><h3>Conclusion</h3><p>{conclusion}</p></div>'

    return front_matter, html


def generate():
    """Genera el blog completo."""
    clean_docs()
    copy_static()

    posts = []

    # Procesar content/*.md
    for filename in sorted(os.listdir(CONTENT_DIR)):
        if not filename.endswith('.md'):
            continue

        filepath = os.path.join(CONTENT_DIR, filename)
        meta, html_content = parse_markdown(filepath)

        # Validar campos requeridos
        required = ['title', 'date', 'category']
        if not all(k in meta for k in required):
            print(f"[skip]  {filename} (faltan campos: {required})")
            continue

        slug = os.path.splitext(filename)[0]
        cat_slug = slugify(meta['category'])

        # URL relativa desde docs/ root
        url = f"{cat_slug}/{slug}.html"

        post = {
            'title': meta['title'],
            'date': str(meta['date']),
            'category': meta['category'],
            'content': html_content,
            'url': url,
            'excerpt': meta.get('excerpt', extract_excerpt(html_content)),
            'svg_thumb': get_svg(meta['category'], 'thumb'),
            'svg_hero': get_svg(meta['category'], 'hero'),
        }
        posts.append(post)

    # Ordenar por fecha desc
    posts.sort(key=lambda p: p['date'], reverse=True)

    # --- Generar paginas de post ---
    post_template = env.get_template('post.html')
    for post in posts:
        cat_slug = slugify(post['category'])
        out_dir = os.path.join(DOCS_DIR, cat_slug)
        os.makedirs(out_dir, exist_ok=True)

        rendered = post_template.render(
            post=post,
            title=post['title'],
            rel_root='../',
            hub_url='/',
        )

        out_path = os.path.join(out_dir, os.path.basename(post['url']))
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(rendered)
        print(f"[post]  {out_path}")

    # --- Generar index ---
    index_template = env.get_template('index.html')
    rendered = index_template.render(
        posts=posts,
        title='Inicio',
        rel_root='./',
        hub_url='/',
    )
    out_path = os.path.join(DOCS_DIR, 'index.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(rendered)
    print(f"[index] {out_path}")

    # --- Generar paginas de categoria ---
    categories = {}
    for post in posts:
        cat = post['category']
        categories.setdefault(cat, []).append(post)

    cat_template = env.get_template('category.html')
    cat_dir = os.path.join(DOCS_DIR, 'categoria')
    os.makedirs(cat_dir, exist_ok=True)

    for cat_name, cat_posts in categories.items():
        cat_slug = slugify(cat_name)

        # URLs relativas para las categorias (estan en categoria/)
        # Los posts se enlazan como ../ia/futuro-ia.html
        posts_with_rel_urls = []
        for p in cat_posts:
            p_copy = dict(p)
            p_copy['url'] = f"../{p['url']}"
            posts_with_rel_urls.append(p_copy)

        rendered = cat_template.render(
            posts=posts_with_rel_urls,
            category_name=cat_name,
            title=f"Categoria: {cat_name}",
            rel_root='../',
            hub_url='/',
        )
        out_path = os.path.join(cat_dir, f"{cat_slug}.html")
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(rendered)
        print(f"[cat]   {out_path}")

    # --- Indice de busqueda ---
    search_index = []
    for post in posts:
        clean = re.sub(r'<[^>]+>', '', post['content'])
        clean = re.sub(r'\s+', ' ', clean).strip()
        search_index.append({
            'title': post['title'],
            'url': post['url'],
            'category': post['category'],
            'content': clean,
        })

    idx_path = os.path.join(DOCS_DIR, 'search_index.json')
    with open(idx_path, 'w', encoding='utf-8') as f:
        json.dump(search_index, f, ensure_ascii=False, indent=2)
    print(f"[search] {idx_path}")

    print(f"\nBlog generado: {len(posts)} articulos")


if __name__ == '__main__':
    generate()
