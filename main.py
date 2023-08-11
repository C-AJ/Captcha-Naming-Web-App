from google.oauth2 import service_account
from googleapiclient.discovery import build
from drive_access import rename_files, download_files, SCOPES

# Gets credentials from file
creds = service_account.Credentials.from_service_account_file(
    'credentials.json', scopes=SCOPES)

# Initializes google drive instance
service = build('drive', 'v3', credentials=creds)

# Folder ID for testing folder
folder_id = '11_Le0LIIPHquOqa7kJ5Z3TC2AghkuGIT'
rename_files(service, folder_id)