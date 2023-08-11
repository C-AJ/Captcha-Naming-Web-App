import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build

# function i used to figure out how the api works
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
        with open('test_output/' + item['name'], 'wb') as f:
            f.write(fh.read())


def rename_files(service, folder_id):
    results = service.files().list(q=f"'{folder_id}' in parents and trashed=false and mimeType != 'application/vnd.google-apps.folder'", fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    for item in items:
        print(f"Renaming file: {item['name']}")
        new_name = input("Enter new name for the file: ")
        file_metadata = {'name': new_name}
        try:
            service.files().update(fileId=item['id'], body=file_metadata).execute()
            print(f"File renamed to {new_name}")
        except HttpError as error:
            print(f"An error occurred: {error}")