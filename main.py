from fastmcp import FastMCP
from typing import List
from nextcloud_client import NextCloudClient

mcp = FastMCP("Nextcloud MCP")
nextcloud = NextCloudClient()

@mcp.tool
def list_files(path: str = "") -> List[str]:
    """Lista los archivos disponibles en Nextcloud. Puedes indicar un subdirectorio con el parámetro 'path'."""
    return nextcloud.list_files(path)

@mcp.tool
def rename_file(old_name: str, new_name: str) -> str:
    """Renombra un archivo en Nextcloud conservando sus metadatos y etiquetas."""
    nextcloud.rename_file(old_name, new_name)
    return f"Archivo renombrado de '{old_name}' a '{new_name}'"


# Herramienta para etiquetar archivos
@mcp.tool
def tag_file(path: str, tag: str) -> str:
    """Asigna una etiqueta a un archivo en Nextcloud.  
    Si la etiqueta no existe, se creará automáticamente.
    """
    nextcloud.tag_file(path, tag)
    return f"Etiqueta '{tag}' aplicada a '{path}'"

@mcp.tool
def list_tags() -> List[str]:
    """Devuelve todas las etiquetas (system tags) existentes en la instancia de Nextcloud."""
    return nextcloud.list_tags()

@mcp.tool
def file_tags(path: str) -> List[str]:
    """Devuelve las etiquetas asignadas al archivo indicado por 'path'."""
    return nextcloud.tags_for_file(path)

if __name__ == "__main__":
    mcp.run()