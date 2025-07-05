# Bitácora 01234

Este es el blog estático del CEREBRO-DIGITAL, donde se materializan ideas y conocimientos sobre IA, Arte, Filosofía y más, excluyendo estrictamente cualquier dato sensible.

## Estructura del Proyecto

- `src/`: Contiene el script de generación del blog (`generate_blog.py`) y las plantillas HTML.
- `content/`: Aquí se almacenan los archivos Markdown de los artículos del blog. Cada archivo debe incluir un *front matter* con metadatos.
- `static/`: Archivos CSS, JavaScript e imágenes estáticas del blog.
- `docs/`: Directorio de salida donde se genera el blog estático (HTML, CSS, JS). Este directorio está configurado para el despliegue en GitHub Pages.

## Generación del Blog

Para generar el blog, ejecuta el script `generate_blog.py`:

```bash
python src/generate_blog.py
```

## Despliegue

El contenido generado en la carpeta `docs/` está listo para ser desplegado en GitHub Pages. Configura tu repositorio para servir desde la rama `main` (o `master`) y la carpeta `/docs`.

---

*Forzando una reconstrucción de GitHub Pages.*
