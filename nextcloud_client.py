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