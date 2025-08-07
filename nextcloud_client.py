# nextcloud_client.py

import os
import requests
from requests.auth import HTTPBasicAuth
import re
from dotenv import load_dotenv
import xml.etree.ElementTree as ET
from urllib.parse import quote

load_dotenv()

class NextCloudClient:
    def __init__(self):
        base_url = os.getenv("NEXTCLOUD_URL")
        user = os.getenv("NEXTCLOUD_USER")
        password = os.getenv("NEXTCLOUD_PASSWORD")

        if not base_url or not user or not password:
            raise ValueError(
                "NEXTCLOUD_URL, NEXTCLOUD_USER y NEXTCLOUD_PASSWORD deben estar definidos en el entorno"
            )

        self.base_url = base_url.rstrip("/")
        # self.base_url (dav_base) incluye /remote.php/dav/files/<usuario>
        # self.root_url es la raíz del servidor y se usa para llamadas OCS
        # Raíz del servidor (sin la parte WebDAV) para llamadas OCS
        # Ej.: https://cloud.e451.net
        self.root_url = re.split(r"/remote\.php/dav/files/[^/]+", self.base_url, 1)[0]
        self.auth = HTTPBasicAuth(user, password)

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

    # ---------------------------------------------------------------------
    # Gestión de etiquetas (system tags)
    # ---------------------------------------------------------------------

    def _get_file_id(self, path: str) -> str:
        """
        Obtiene el `fileid` interno de Nextcloud para la ruta dada utilizando PROPFIND.
        """
        url = f"{self.base_url}/{self.sanitize_path(path)}"
        headers = {"Depth": "0", "Content-Type": "application/xml"}
        body = """<?xml version="1.0"?>
        <d:propfind xmlns:d="DAV:" xmlns:oc="http://owncloud.org/ns">
            <d:prop>
                <oc:fileid/>
            </d:prop>
        </d:propfind>"""

        response = requests.request(
            "PROPFIND", url, headers=headers, data=body, auth=self.auth
        )

        if response.status_code != 207:
            raise Exception(
                f"Error al obtener fileid: {response.status_code} {response.text}"
            )

        ns = {"d": "DAV:", "oc": "http://owncloud.org/ns"}
        tree = ET.fromstring(response.text)
        fileid_elem = tree.find(".//oc:fileid", ns)
        if fileid_elem is None or not fileid_elem.text:
            raise Exception("No se pudo obtener el fileid del archivo")
        return fileid_elem.text

    def _get_tag_id(self, tag_name: str) -> int | None:
        """
        Devuelve el ID de la etiqueta si existe, en caso contrario None.
        Implementación 100 % WebDAV: PROPFIND sobre /remote.php/dav/systemtags.
        """
        url = f"{self.root_url}/remote.php/dav/systemtags"
        headers = {
            "Depth": "1",
            "Content-Type": "application/xml"
        }
        body = """<?xml version="1.0"?>
        <d:propfind xmlns:d="DAV:" xmlns:oc="http://owncloud.org/ns">
            <d:prop>
                <oc:display-name/>
            </d:prop>
        </d:propfind>"""

        resp = requests.request("PROPFIND", url, headers=headers, data=body, auth=self.auth)

        if resp.status_code != 207:
            raise Exception(f"Error al listar etiquetas: {resp.status_code} {resp.text}")

        ns = {"d": "DAV:", "oc": "http://owncloud.org/ns"}
        tree = ET.fromstring(resp.text)
        for response in tree.findall("d:response", ns):
            href = response.find("d:href", ns)
            display = response.find("d:propstat/d:prop/oc:display-name", ns)
            if display is not None and display.text == tag_name and href is not None:
                # href ejemplo: /remote.php/dav/systemtags/53/
                if href.text:
                    parts = href.text.strip("/").split("/")
                    return int(parts[-1])  # el último fragmento es el ID
        return None

    def _create_tag(self, tag_name: str) -> int:
        """
        Crea una etiqueta mediante WebDAV y devuelve su ID.
        """
        url = f"{self.root_url}/remote.php/dav/systemtags"
        headers = {"Content-Type": "application/json"}
        payload = {
            "name": tag_name,
            "userVisible": True,
            "userAssignable": True,
            "canAssign": True
        }

        resp = requests.post(url, headers=headers, json=payload, auth=self.auth)

        if resp.status_code not in (201, 204):
            raise Exception(f"Error al crear etiqueta: {resp.status_code} {resp.text}")

        # Nextcloud devuelve la ubicación del recurso creado en el header 'Location'
        location = resp.headers.get("Location")
        if not location:
            raise Exception("No se pudo obtener la ubicación de la etiqueta recién creada")

        # Ejemplo de Location: https://host/remote.php/dav/systemtags/99
        tag_id = int(location.rstrip("/").split("/")[-1])
        return tag_id

    def tag_file(self, path: str, tag_name: str):
        """
        Asigna la etiqueta `tag_name` al archivo indicado por `path`.  
        Si la etiqueta no existe se creará automáticamente.
        """
        tag_id = self._get_tag_id(tag_name) or self._create_tag(tag_name)
        file_id = self._get_file_id(path)

        url = f"{self.root_url}/remote.php/dav/systemtags-relations/files/{file_id}/{tag_id}"
        headers = {"Content-Type": "text/xml"}  # requerido aunque el body sea vacío
        resp = requests.put(url, headers=headers, auth=self.auth)

        if resp.status_code not in (201, 204):
            raise Exception(
                f"Error al etiquetar archivo: {resp.status_code} {resp.text}"
            )

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

class PdfReaderClient:
    def __init__(self, mcp_path="./servers-mios/pdf-reader-mcp/main.py"):
        from fastmcp import Client
        self.client = Client(mcp_path)

    def read_text(self, path: str, max_chars: int = 5000) -> str:
        import asyncio

        async def _call():
            async with self.client:
                result = await self.client.call_tool("read_pdf", {
                    "path": path,
                    "max_chars": max_chars
                })
                return result["text"]

        return asyncio.run(_call())