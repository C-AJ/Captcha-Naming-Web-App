import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def download_files(service, folder_id):
    results = service.files().list(q=f"'{folder_id}' in parents and trashed=false and mimeType != 'application/vnd.google-apps.folder'", fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    for item in items:
        print(f"Downloading file: {item['name']}")
        request = service.files().get_media(fileId=item['id'])
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}.")
        fh.seek(0)
        with open('temp_output/' + item['name'], 'wb') as f:
            f.write(fh.read())

creds = service_account.Credentials.from_service_account_file(
    'credentials.json', scopes=SCOPES)

service = build('drive', 'v3', credentials=creds)

folder_id = '11_Le0LIIPHquOqa7kJ5Z3TC2AghkuGIT'
download_files(service, folder_id)
