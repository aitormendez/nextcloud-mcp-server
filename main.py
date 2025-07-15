from fastmcp import FastMCP
from typing import List
from nextcloud_client import NextCloudClient

mcp = FastMCP(name="Nextcloud MCP Server")
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

if __name__ == "__main__":
    mcp.run()