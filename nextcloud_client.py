# nextcloud_client.py

import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import xml.etree.ElementTree as ET
from urllib.parse import quote

load_dotenv()

class NextCloudClient:
    def __init__(self):
        self.base_url = os.getenv("NEXTCLOUD_URL").rstrip("/")
        self.auth = HTTPBasicAuth(
            os.getenv("NEXTCLOUD_USER"),
            os.getenv("NEXTCLOUD_PASSWORD")
        )

    def list_files(self, path: str = ""):
        url = f"{self.base_url}/{path}".rstrip("/")
        headers = {
            "Depth": "1",
            "Content-Type": "application/xml"
        }
        body = """<?xml version="1.0"?>
        <d:propfind xmlns:d="DAV:">
            <d:prop>
                <d:displayname/>
            </d:prop>
        </d:propfind>"""

        response = requests.request("PROPFIND", url, headers=headers, data=body, auth=self.auth)

        if response.status_code != 207:
            raise Exception(f"Error al listar archivos: {response.status_code} {response.text}")

        return self._parse_file_list(response.text)

    def _parse_file_list(self, xml_response: str):
        ns = {"d": "DAV:"}
        tree = ET.fromstring(xml_response)
        items = []
        for response in tree.findall("d:response", ns):
            href = response.find("d:href", ns)
            name = response.find("d:propstat/d:prop/d:displayname", ns)
            if href is not None and name is not None:
                # Omitimos la carpeta raíz (misma URL base)
                if name.text and name.text != "/":
                    items.append(name.text)
        return items

    def sanitize_path(self, path: str) -> str:
        prefix = "/remote.php/dav/files/admin/"
        if path.startswith(prefix):
            return path[len(prefix):]
        return path

    def rename_file(self, old_name: str, new_name: str):
        src = f"{self.base_url}/{self.sanitize_path(old_name)}".rstrip("/")
        dst = f"{self.base_url}/{self.sanitize_path(new_name)}".rstrip("/")

        headers = {
            # Evitamos sobrecodificar el esquema "https://"
            "Destination": quote(dst, safe=":/"),
            "Overwrite": "F"
        }

        response = requests.request("MOVE", src, headers=headers, auth=self.auth)

        if response.status_code not in [201, 204]:
            raise Exception(f"Error al renombrar archivo: {response.status_code} {response.text}")

    def read_text_file(self, path: str, max_chars: int = 5000) -> str:
        """Lee un archivo de texto desde Nextcloud usando WebDAV y devuelve su contenido como string."""
        url = f"{self.base_url}/{self.sanitize_path(path)}"
        response = requests.get(url, auth=self.auth)

        if response.status_code != 200:
            raise Exception(f"Error al leer archivo: {response.status_code} {response.text}")

        if path.lower().endswith(".epub"):
            return self.read_epub_text(path, max_chars)
        return response.text[:max_chars]

    def read_epub_text(self, path: str, max_chars: int = 5000) -> str:
        """
        Descarga un archivo EPUB desde Nextcloud y devuelve el contenido de texto plano extraído.
        Solo extrae el contenido de las primeras páginas hasta `max_chars`.
        """
        import tempfile
        import zipfile
        from bs4 import BeautifulSoup

        # Descargar el archivo EPUB desde Nextcloud
        url = f"{self.base_url}/{self.sanitize_path(path)}"
        response = requests.get(url, auth=self.auth)

        if response.status_code != 200:
            raise Exception(f"Error al descargar EPUB: {response.status_code} {response.text}")

        # Guardar el EPUB temporalmente para extraerlo
        with tempfile.NamedTemporaryFile(suffix=".epub", delete=False) as tmp_file:
            tmp_file.write(response.content)
            tmp_path = tmp_file.name

        text_content = ""
        try:
            with zipfile.ZipFile(tmp_path, 'r') as z:
                # Buscar archivos HTML o XHTML para extraer el contenido textual
                for name in z.namelist():
                    if name.endswith(('.html', '.xhtml')):
                        with z.open(name) as f:
                            soup = BeautifulSoup(f.read(), "html.parser")
                            text_content += soup.get_text(separator="\n", strip=True)
                            if len(text_content) >= max_chars:
                                break
        finally:
            os.remove(tmp_path)

        return text_content[:max_chars]