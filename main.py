from google.oauth2 import service_account
from googleapiclient.discovery import build
from drive_access import rename_files

SCOPES = ['https://www.googleapis.com/auth/drive']

creds = service_account.Credentials.from_service_account_file(
    'credentials.json', scopes=SCOPES)

service = build('drive', 'v3', credentials=creds)

folder_id = '11_Le0LIIPHquOqa7kJ5Z3TC2AghkuGIT'
rename_files(service, folder_id)