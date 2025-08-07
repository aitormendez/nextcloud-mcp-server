## MCP Nextcloud Server — Implementación

Este documento describe la implementación actual del servidor MCP personalizado para Nextcloud, incluyendo herramientas y estado de desarrollo.

### 🎯 Objetivo

Permitir la interacción con una biblioteca de libros almacenada en una instancia privada de Nextcloud, utilizando herramientas MCP para listar archivos, leer metadatos, extraer fragmentos de texto y proponer etiquetas temáticas basadas en criterios definidos.

---

## 🔧 Herramientas Implementadas

### `list_files`

**Descripción:**  
Lista los archivos disponibles en una ruta específica del almacenamiento de Nextcloud, utilizando la API WebDAV con autenticación por token.

**Argumentos:**

- `path` (string): Ruta relativa dentro de Nextcloud desde la raíz del almacenamiento autorizado.

**Uso típico:**

Se usa para explorar directorios de autores o categorías dentro de la biblioteca Nextcloud y seleccionar archivos a procesar posteriormente.

**Estado:**  
✅ Implementada y funcional

### `rename_file`

**Descripción:**  
Renombra un archivo dentro de Nextcloud sin perder los metadatos, incluyendo etiquetas aplicadas manualmente.

**Argumentos:**

- `old_path` (string): Ruta actual del archivo en Nextcloud.
- `new_path` (string): Nueva ruta deseada (incluyendo el nombre de archivo).

**Uso típico:**

Permite cambiar nombres normalizando títulos, corrigiendo errores tipográficos o reorganizando la estructura de carpetas sin comprometer la integridad documental.

**Estado:**  
✅ Implementada y funcional

### `propose_tags`

**Descripción:**  
Propone etiquetas temáticas para un archivo dado, basado en su contenido y en los criterios de clasificación definidos en el archivo `Etiquetas de la biblioteca.md`.

**Argumentos:**

- `title` (string): Título del libro.
- `nextcloud_path` (string): Ruta relativa del archivo dentro de la estructura de Nextcloud.
- `tag_criteria_md` (string): Contenido del archivo Markdown que define los criterios y lista actual de etiquetas.

**Flujo de uso:**

1. Leer el archivo de etiquetas con `filesystem__read_file`.
2. Leer un fragmento del archivo EPUB usando `get_epub_chapter_markdown` (si el archivo es EPUB) o `read_pdf` (si es PDF, desde el MCP correspondiente).
3. Pasar los datos a `propose_tags` para que analice el contenido y proponga etiquetas coherentes.

**Estado:**  
✅ Implementada y funcional  
⚠️ Actualmente solo opera correctamente con EPUB, utilizando el MCP `ebook-mcp`.  
⚠️ Las etiquetas propuestas no siempre se ajustan a los criterios, por lo que se ha refinado la lógica de filtrado.

---

### `tag_file`

**Descripción:**  
Asigna una etiqueta existente (o la crea si no existe) a un archivo en Nextcloud.

**Argumentos:**

- `path` (string): Ruta relativa del archivo al que se desea aplicar la etiqueta.
- `tag` (string): Nombre de la etiqueta.

**Uso típico:**  
Tras recibir una propuesta de etiquetas (por ejemplo, desde `propose_tags`), se llama a `tag_file` para aplicar la etiqueta seleccionada al archivo.

**Estado:**  
✅ Implementada y funcional (usa WebDAV `PUT /systemtags-relations/files/{fileid}/{tagid}`).

---

### `list_tags`

**Descripción:**  
Devuelve la lista completa de etiquetas (system tags) configuradas en la instancia de Nextcloud.

**Argumentos:**  
_(ninguno)_

**Uso típico:**  
Para verificar las etiquetas disponibles antes de proponer o asignar nuevas, evitando duplicados por mayúsculas o errores tipográficos.

**Estado:**  
✅ Implementada y funcional (WebDAV `PROPFIND /systemtags`).

---

### `file_tags`

**Descripción:**  
Recupera las etiquetas asignadas a un archivo concreto.

**Argumentos:**

- `path` (string): Ruta relativa del archivo dentro de Nextcloud.

**Uso típico:**  
Comprobar si un archivo ya tiene ciertas etiquetas antes de añadir nuevas para evitar redundancias.

**Estado:**  
✅ Implementada y funcional (WebDAV `PROPFIND /systemtags-relations/files/{fileid}`).

---

---

## 📌 Estado actual

- El MCP está operativo y registrado en Gemini CLI como `nextcloud-mcp-server`.
- El flujo de `propose_tags` ya permite:
  - Leer el archivo EPUB desde Nextcloud.
  - Leer el archivo de etiquetas desde el sistema de archivos local.
  - Proponer etiquetas basadas en los criterios definidos.
- Se ha detectado un problema: algunas etiquetas propuestas (ej. “Exilio”) no cumplen los criterios establecidos:
  - Deben tener potencial de aplicarse a más de un libro.
  - Deben cubrir temas no contemplados por etiquetas ya existentes.
- Nuevas herramientas `tag_file`, `list_tags` y `file_tags` añadidas para gestionar y consultar etiquetas de manera automática.

**Próximo paso:**

- Ajustar o reforzar la lógica de `propose_tags` para cumplir de forma más estricta los criterios definidos en `Etiquetas de la biblioteca.md`.

---
