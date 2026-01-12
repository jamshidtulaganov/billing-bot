"""
Zoho WorkDrive Integration Module
Handles file uploads, downloads, and folder operations
"""

import requests
import os
from datetime import datetime


class ZohoWorkDrive:
    def __init__(self, client_id, client_secret, refresh_token, api_domain):
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.api_domain = api_domain
        self._access_token = None

    def get_access_token(self):
        """Get a fresh access token using refresh token"""
        url = "https://accounts.zoho.com/oauth/v2/token"
        params = {
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token"
        }

        response = requests.post(url, params=params)
        data = response.json()

        if "access_token" in data:
            self._access_token = data["access_token"]
            return self._access_token
        else:
            raise Exception(f"Failed to get access token: {data}")

    def _get_headers(self):
        """Get authorization headers"""
        if not self._access_token:
            self.get_access_token()
        return {"Authorization": f"Zoho-oauthtoken {self._access_token}"}

    def list_files(self, folder_id):
        """List all files in a folder"""
        url = f"{self.api_domain}/workdrive/api/v1/files/{folder_id}/files"
        headers = self._get_headers()

        response = requests.get(url, headers=headers)

        if response.status_code == 401:  # Token expired
            self.get_access_token()
            headers = self._get_headers()
            response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            return data.get("data", [])
        else:
            raise Exception(f"Failed to list files: {response.json()}")

    def download_file(self, file_id, local_path):
        """Download a file from Zoho WorkDrive"""
        # First get the file metadata to get the download URL
        metadata_url = f"{self.api_domain}/workdrive/api/v1/files/{file_id}"
        headers = self._get_headers()

        metadata_response = requests.get(metadata_url, headers=headers)

        if metadata_response.status_code == 401:  # Token expired
            self.get_access_token()
            headers = self._get_headers()
            metadata_response = requests.get(metadata_url, headers=headers)

        if metadata_response.status_code != 200:
            raise Exception(f"Failed to get file metadata: {metadata_response.status_code}")

        metadata = metadata_response.json()
        download_url = metadata['data']['attributes'].get('download_url')

        if not download_url:
            raise Exception("No download_url found in file metadata")

        # Now download the file using the download URL
        response = requests.get(download_url, headers=headers, stream=True)

        if response.status_code == 401:  # Token expired
            self.get_access_token()
            headers = self._get_headers()
            response = requests.get(download_url, headers=headers, stream=True)

        if response.status_code == 200:
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        else:
            raise Exception(f"Failed to download file: {response.status_code}")

    def upload_file(self, folder_id, file_path):
        """Upload a file to Zoho WorkDrive"""
        url = f"{self.api_domain}/workdrive/api/v1/upload"
        headers = self._get_headers()

        with open(file_path, 'rb') as f:
            files = {'content': (os.path.basename(file_path), f)}
            data = {'parent_id': folder_id, 'override-name-exist': 'true'}

            response = requests.post(url, headers=headers, files=files, data=data)

            if response.status_code == 401:  # Token expired
                self.get_access_token()
                headers = self._get_headers()
                with open(file_path, 'rb') as f2:
                    files = {'content': (os.path.basename(file_path), f2)}
                    response = requests.post(url, headers=headers, files=files, data=data)

            if response.status_code in [200, 201]:
                return response.json()
            else:
                raise Exception(f"Failed to upload file: {response.json()}")

    def delete_file(self, file_id):
        """Delete a file from Zoho WorkDrive"""
        url = f"{self.api_domain}/workdrive/api/v1/files/{file_id}"
        headers = self._get_headers()

        response = requests.delete(url, headers=headers)

        if response.status_code == 401:  # Token expired
            self.get_access_token()
            headers = self._get_headers()
            response = requests.delete(url, headers=headers)

        if response.status_code in [200, 204]:
            return True
        else:
            raise Exception(f"Failed to delete file: {response.json()}")

    def find_file_by_name(self, folder_id, filename):
        """Find a file by name in a folder"""
        files = self.list_files(folder_id)
        for file in files:
            if file['attributes']['name'].lower() == filename.lower():
                return file
        return None

    def get_subfolder_id(self, parent_folder_id, subfolder_name):
        """Get the ID of a subfolder by name"""
        files = self.list_files(parent_folder_id)
        for item in files:
            if item['attributes']['type'] == 'folder' and item['attributes']['name'].lower() == subfolder_name.lower():
                return item['id']
        return None
