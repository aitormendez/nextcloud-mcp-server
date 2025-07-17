from fastapi import FastAPI
from fastmcp import FastMCP
from typing import List
from nextcloud_client import NextCloudClient

app = FastAPI(title="Nextcloud MCP", version="1.0.0")
mcp = FastMCP.from_fastapi(app=app)

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

from tools.propose_tags import propose_tags as _propose_tags

mcp.tool(_propose_tags)

import signal
import sys

def shutdown_handler(sig, frame):
    print("\n🛑 MCP detenido limpiamente.")
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown_handler)

if __name__ == "__main__":
    mcp.run()