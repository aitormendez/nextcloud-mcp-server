import os
from webdav3.client import Client
from typing import List, Dict
import tempfile

class NextCloudClient:
    def __init__(self, share_url: str):
        """Initialize NextCloud client with the share URL."""
        self.share_url = share_url
        self.webdav_options = {
            'webdav_hostname': "https://cloud.monadical.com/public.php/webdav",
            'webdav_token': 'EE7yBz8tF85kMsw'  # Token from the share URL
        }
        self.client = Client(self.webdav_options)
        
    def list_files(self) -> List[str]:
        """List all files in the shared folder."""
        try:
            files = self.client.list()
            return [f for f in files if not f.endswith('/')]  # Filter out directories
        except Exception as e:
            print(f"Error listing files: {e}")
            return []

    def read_file(self, file_path: str) -> str:
        """Read the content of a file from NextCloud."""
        try:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                self.client.download_file(file_path, temp_file.name)
                with open(temp_file.name, 'r') as f:
                    content = f.read()
                os.unlink(temp_file.name)
                return content
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return ""

    def build_context(self) -> Dict[str, str]:
        """Build context from all files in the shared folder."""
        context = {}
        files = self.list_files()
        for file_path in files:
            content = self.read_file(file_path)
            context[file_path] = content
        return context