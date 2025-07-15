from fastmcp import FastMCP
from typing import List

# Crear el servidor
mcp = FastMCP(name="Nextcloud MCP Server")

# Cliente simulado de Nextcloud
class MockNextCloudClient:
    def list_files(self) -> List[str]:
        return ["archivo1.txt", "documento2.pdf", "imagen3.jpg"]

nextcloud_client = MockNextCloudClient()

# Herramienta MCP
@mcp.tool
def list_files() -> List[str]:
    """Lista los archivos disponibles en la carpeta de Nextcloud (simulada)."""
    return nextcloud_client.list_files()

# Ejecutar el servidor
if __name__ == "__main__":
    mcp.run()