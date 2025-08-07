# Nextcloud MCP Server

Este servidor MCP permite interactuar con una instancia remota de Nextcloud mediante el protocolo MCP (Model Context Protocol), usando herramientas expuestas que pueden ser invocadas desde Gemini CLI u otros entornos compatibles.

## Funcionalidad

Actualmente implementa las siguientes herramientas MCP:

- `list_files(path: str = "") -> List[str]`: Lista los archivos en una ruta determinada de Nextcloud.
- `rename_file(old_name: str, new_name: str) -> str`: Renombra un archivo en Nextcloud conservando etiquetas y metadatos.
- `tag_file(path: str, tag: str) -> str`: Asigna la etiqueta **tag** al archivo **path**. Si la etiqueta no existe se crea automáticamente.
- `list_tags() -> List[str]`: Devuelve la lista de todas las etiquetas (system tags) disponibles en la instancia de Nextcloud.
- `file_tags(path: str) -> List[str]`: Devuelve las etiquetas asignadas al archivo indicado por **path**.

Más herramientas se irán añadiendo progresivamente (eliminación, creación de carpetas, previsualización de archivos, etc.).

## Requisitos

- Python 3.11+
- Entorno virtual (`pyenv-virtualenv` recomendado)
- Paquetes:

```bash
pip install -r requirements.txt
```

> Asegúrate de que `requests`, `fastmcp` y `python-dotenv` estén instalados.

## Configuración

Crea un archivo `.env` en la raíz con las credenciales de acceso a Nextcloud:

```env
NEXTCLOUD_URL=https://your-nextcloud-instance/remote.php/dav/files/your-username/
NEXTCLOUD_USER=your-username
NEXTCLOUD_PASSWORD=your-password-or-app-token
```

## Uso local

Activa el entorno virtual y ejecuta el servidor:

```bash
python main.py
```

## Integración con Gemini CLI

Añade esta configuración al archivo `.gemini/settings.json`:

```json
"nextcloud": {
  "command": "python",
  "args": ["main.py"],
  "cwd": "/Volumes/D/Documentos D/mcp-servers/nextcloud-mcp-server",
  "trust": true
}
```

Luego ejecuta:

```bash
gemini
```

Y podrás invocar herramientas como:

```
Usa list_files para ver los archivos de la carpeta "Materiales espirituales".
Renombra el archivo X por Y usando rename_file.
```

## Licencia

Este proyecto es un fork adaptado para uso personal. No está basado en el código original de Nextcloud, sino en llamadas a su API mediante WebDAV.
