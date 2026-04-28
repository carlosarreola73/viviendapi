import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from io import BytesIO
from app.core.config import settings

class GoogleDriveService:
    def __init__(self):
        if not settings.GOOGLE_CREDENTIALS_JSON:
            raise ValueError("GOOGLE_CREDENTIALS_JSON is not set in settings")
        
        info = json.loads(settings.GOOGLE_CREDENTIALS_JSON)
        self.credentials = service_account.Credentials.from_service_account_info(
            info, scopes=['https://www.googleapis.com/auth/drive']
        )
        self.service = build('drive', 'v3', credentials=self.credentials)

    def _get_or_create_folder(self, name: str, parent_id: str) -> str:
        query = f"name = '{name}' and mimeType = 'application/vnd.google-apps.folder' and '{parent_id}' in parents and trashed = false"
        response = self.service.files().list(
            q=query, 
            spaces='drive', 
            fields='files(id)',
            supportsAllDrives=True,
            includeItemsFromAllDrives=True
        ).execute()
        
        files = response.get('files', [])
        if files:
            return files[0].get('id')
        
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id]
        }
        file = self.service.files().create(body=file_metadata, fields='id', supportsAllDrives=True).execute()
        return file.get('id')

    def create_placeholder(self, policy_number: str, cert_number: str) -> dict:
        """Crea el archivo vacío para obtener el ID y los links antes de generar el PDF."""
        root_id = settings.SHARED_DRIVE_ID
        policy_folder_id = self._get_or_create_folder(policy_number, root_id)
        cert_folder_id = self._get_or_create_folder(cert_number, policy_folder_id)
        
        file_metadata = {
            'name': f"Certificado_{cert_number}.pdf",
            'parents': [cert_folder_id],
            'mimeType': 'application/pdf'
        }
        
        file = self.service.files().create(
            body=file_metadata, 
            fields='id, webViewLink',
            supportsAllDrives=True
        ).execute()
        
        file_id = file.get('id')
        return {
            "id": file_id,
            "view_link": file.get('webViewLink'),
            "download_link": f"https://drive.google.com/uc?export=download&id={file_id}"
        }

    def update_file_content(self, file_id: str, pdf_buffer: BytesIO):
        """Sube el contenido real del PDF al archivo previamente creado."""
        media = MediaIoBaseUpload(pdf_buffer, mimetype='application/pdf', resumable=True)
        self.service.files().update(
            fileId=file_id,
            media_body=media,
            supportsAllDrives=True
        ).execute()
        
        # Asegurar permisos públicos
        permission = {'type': 'anyone', 'role': 'reader'}
        try:
            self.service.permissions().create(fileId=file_id, body=permission, supportsAllDrives=True).execute()
        except:
            pass

    def upload_pdf(self, policy_number: str, cert_number: str, pdf_buffer: BytesIO) -> dict:
        """Método compatible con el flujo anterior."""
        links = self.create_placeholder(policy_number, cert_number)
        self.update_file_content(links["id"], pdf_buffer)
        return links
