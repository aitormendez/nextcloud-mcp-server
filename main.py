from fastmcp import FastMCP
from typing import List
from nextcloud_client import NextCloudClient

mcp = FastMCP(name="Nextcloud MCP Server")
nextcloud = NextCloudClient()

@mcp.tool
def list_files() -> List[str]:
    """Lista los archivos reales en la instancia de Nextcloud."""
    return nextcloud.list_files()

if __name__ == "__main__":
    mcp.run()