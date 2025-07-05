import os
import markdown
import yaml
from jinja2 import Environment, FileSystemLoader
import shutil
import unicodedata
import re
from PIL import Image # Importar Pillow

# Rutas de directorios
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONTENT_DIR = os.path.join(os.path.dirname(BASE_DIR), 'content')
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(os.path.dirname(BASE_DIR), 'static')
DOCS_DIR = os.path.join(os.path.dirname(BASE_DIR), 'docs')
RESOURCES_DIR = '/Users/a01234/CEREBRO-DIGITAL/RECURSOS/' # Ruta absoluta a /RECURSOS/
THUMBNAILS_DIR = os.path.join(STATIC_DIR, 'thumbnails') # Nueva carpeta para miniaturas

# URL base para GitHub Pages (nombre del repositorio)
BASE_URL = '/blog-cerebro-digital'

# Configuración de Jinja2
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

def slugify(value):
    """
    Convierte una cadena a un slug amigable para URL.
    Elimina acentos, convierte a minúsculas y reemplaza espacios/caracteres especiales por guiones.
    """
    value = str(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('utf-8')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    value = re.sub(r'[-\s]+', '-', value)
    return value

def clean_docs_dir():
    """Limpia el directorio docs/ antes de generar nuevos archivos."""
    if os.path.exists(DOCS_DIR):
        shutil.rmtree(DOCS_DIR)
    os.makedirs(DOCS_DIR)
    print(f"Directorio '{DOCS_DIR}' limpiado.")

def copy_static_files():
    """Copia los archivos estáticos (CSS, JS, imágenes) a la carpeta docs/."""
    if os.path.exists(STATIC_DIR):
        shutil.copytree(STATIC_DIR, os.path.join(DOCS_DIR, 'static'))
        print(f"Archivos estáticos copiados de '{STATIC_DIR}' a '{DOCS_DIR}/static'.")
    else:
        print(f"Advertencia: El directorio estático '{STATIC_DIR}' no existe.")

def process_thumbnail(image_path, output_dir, size=(900, 600), quality=95):
    """
    Procesa una imagen para usarla como miniatura: redimensiona y optimiza.
    Retorna la ruta relativa de la miniatura generada.
    """
    if not os.path.exists(image_path):
        print(f"Advertencia: La imagen de miniatura no existe: {image_path}")
        return None

    os.makedirs(output_dir, exist_ok=True)
    filename = slugify(os.path.splitext(os.path.basename(image_path))[0]) + os.path.splitext(os.path.basename(image_path))[1]
    output_path = os.path.join(output_dir, filename)

    try:
        with Image.open(image_path) as img:
            img = img.copy() # Crear una copia para evitar problemas con archivos abiertos
            img.thumbnail(size, Image.Resampling.LANCZOS)
            img.save(output_path, optimize=True, quality=quality)
        print(f"Miniatura generada: {output_path}")
        return os.path.join('/static/thumbnails', filename)
    except Exception as e:
        print(f"Error al procesar la miniatura {image_path}: {e}")
        return None

def parse_markdown_file(filepath):
    """Parsea un archivo Markdown, extrayendo el front matter y el contenido."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Separar front matter y contenido
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) > 2:
            front_matter = yaml.safe_load(parts[1])
            markdown_content = parts[2]
        else:
            front_matter = {}
            markdown_content = content
    else:
        front_matter = {}
        markdown_content = content

    html_content = markdown.markdown(markdown_content)

    # Añadir conclusión al contenido HTML si existe
    if 'conclusion' in front_matter and front_matter['conclusion']:
        html_content += f'<div class="post-conclusion"><h3>Conclusión</h3><p>{front_matter['conclusion']}</p></div>'

    # Eliminar la conclusión del front_matter para que no se procese dos veces en la plantilla
    if 'conclusion' in front_matter:
        del front_matter['conclusion']

    return front_matter, html_content

def generate_blog():
    clean_docs_dir()
    copy_static_files()

    # Asegurarse de que el directorio de miniaturas exista
    os.makedirs(THUMBNAILS_DIR, exist_ok=True)

    posts = []

    # Procesar archivos Markdown
    for root, _, files in os.walk(CONTENT_DIR):
        for filename in files:
            if filename.endswith('.md'):
                filepath = os.path.join(root, filename)
                front_matter, html_content = parse_markdown_file(filepath)

                # Validar metadatos esenciales
                if not all(k in front_matter for k in ['title', 'date', 'category']):
                    print(f"Advertencia: Archivo '{filename}' no tiene todos los metadatos esenciales (title, date, category). Saltando.")
                    continue

                # Procesar miniatura si se especifica
                thumbnail_url = None
                if 'thumbnail' in front_matter and front_matter['thumbnail']:
                    # Construir la ruta absoluta de la imagen de origen
                    source_image_path = os.path.join(RESOURCES_DIR, front_matter['thumbnail'].lstrip('/'))
                    thumbnail_url = process_thumbnail(source_image_path, THUMBNAILS_DIR)

                # Crear URL amigable
                slug = os.path.splitext(filename)[0]
                category_slug = slugify(front_matter['category'])
                post_url = os.path.join('/', category_slug, f'{slug}.html')

                post_data = {
                    'title': front_matter['title'],
                    'date': front_matter['date'],
                    'category': front_matter['category'],
                    'content': html_content,
                    'url': post_url,
                    'thumbnail': thumbnail_url # Añadir la URL de la miniatura
                }
                posts.append(post_data)

                # Generar página individual del post
                post_template = env.get_template('post.html')
                rendered_post = post_template.render(post=post_data)

                output_dir = os.path.join(DOCS_DIR, category_slug)
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, f'{slug}.html')
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(rendered_post)
                print(f"Generado: {output_path}")

    # Ordenar posts por fecha (más reciente primero)
    posts.sort(key=lambda x: x['date'], reverse=True)

    # Generar página de índice
    index_template = env.get_template('index.html')
    rendered_index = index_template.render(posts=posts, year=2025, title="Inicio", base_url=BASE_URL)
    with open(os.path.join(DOCS_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(rendered_index)
    print(f"Generado: {os.path.join(DOCS_DIR, 'index.html')}")

    print("Generación del blog completada.")

    # Generar páginas de categoría
    category_posts = {}
    for post in posts:
        category = post['category']
        if category not in category_posts:
            category_posts[category] = []
        category_posts[category].append(post)

    category_template = env.get_template('category.html')
    for category, cat_posts in category_posts.items():
        category_slug = slugify(category)
        rendered_category = category_template.render(posts=cat_posts, category_name=category, title=f"Categoría: {category}", base_url=BASE_URL)
        output_path = os.path.join(DOCS_DIR, 'categoria', f'{category_slug}.html')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(rendered_category)
        print(f"Generado: {output_path}")

if __name__ == '__main__':
    generate_blog()