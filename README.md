# Bitacora 01234

Blog estatico del CEREBRO-DIGITAL. Articulos sobre IA, Arte y Filosofia 01234.

## Arquitectura

```
blog-cerebro-digital/
├── content/            # Markdown + frontmatter YAML (fuente de verdad)
├── src/
│   ├── generate_blog.py   # Generador estatico (Python)
│   └── templates/         # Jinja2 (base, index, post, category)
├── static/             # CSS, assets (fuente)
├── docs/               # OUTPUT del build → GitHub Pages
└── index.html          # Redirect local a docs/
```

## Flujo de trabajo

### Crear un articulo

Anadir un `.md` en `content/` con frontmatter:

```yaml
---
title: Titulo del articulo
date: 2025-07-06
category: IA | Arte | Filosofia
conclusion: Texto de cierre del articulo.
---

Contenido en Markdown...
```

### Generar el blog

```bash
python3 src/generate_blog.py
```

Limpia `docs/`, copia `static/`, renderiza templates, genera HTML + search index.

### Desarrollo local

```bash
cd PROYECTOS && python3 -m http.server 8000
# Abrir http://localhost:8000/blog-cerebro-digital/
```

### Despliegue

GitHub Pages sirve desde `/docs` en rama `master`. Tras generar:

```bash
git add -A && git commit -m "rebuild" && git push
```

## Dependencias

```bash
pip install markdown pyyaml jinja2
```

## Diseno

- Tema oscuro (#1a1a1a), tipografia monoespaciada (SF Mono, Fira Code)
- SVGs generados por categoria (IA: red neuronal, Arte: lienzo+grid, Filosofia: jerarquia 01234)
- URLs relativas -- funciona en local y en GitHub Pages sin configuracion
- Sin JavaScript, sin frameworks, sin dependencias frontend

## Categorias SVG

Cada categoria tiene un SVG thumbnail (120x80) para listados y un SVG hero (780x160) para paginas de articulo. Definidos en `generate_blog.py`. Para anadir una nueva categoria, agregar su SVG al diccionario `SVG_THUMBS` y `SVG_HEROES`.
