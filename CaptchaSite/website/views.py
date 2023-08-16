from django.shortcuts import render
from .models import Text

def home_view(request):
    # Get the URL of the image from Google Drive
    image_id = '1YgZYt4NUOF15ZSiLUrpRxQvR5S8eA3_E'
    url = get_image_url_from_google_drive(service, image_id=image_id)

    # Get the text entered by the user
    if request.method == 'POST':
        text = request.POST.get('text')
        Text.objects.create(text=text)

    # Render the template with the URL of the image and the text box
    return render(request, 'home.html', {'url': url})

import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/drive"]
creds = service_account.Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
service = build('drive', 'v3', credentials=creds)
folder_id = '11_Le0LIIPHquOqa7kJ5Z3TC2AghkuGIT'

# Change to id of 'in progress' folder or subfolder
PROGRESS_FOLDER_ID = "19YNFgPlEPOJ-j8tffE0tF-lEKmIqKx-y"
# Change to id of 'renamed' folder or subfolder
DESTINATION_ID = "1ZOFhIKBaM_3X7NvU1n8kfSjFIIcdPXc6"


def rename_files(service, folder_id):
    empty = False
    # gets a list of all the files in the folder that aren't subfolders
    results = service.files().list(q=f"'{folder_id}' in parents and trashed=false and mimeType != 'application/vnd.google-apps.folder'",
                             fields="nextPageToken, files(id, name)").execute()
    items = results.get("files", [])
    if items == []:
        empty = True
    # iterates through every file asks the user to rename it
    for item in items:
        move_file_to_folder(service, file_id=item["id"], folder_id=PROGRESS_FOLDER_ID)
        # TODO: add display_image() here
        print(f"Renaming file: {item['name']}")
        new_name = input("Enter new name for the file: ")
        # gets new name provided by user
        file_metadata = {"name": new_name}
        try:
            # attempts to process name changes onto google drive
            service.files().update(fileId=item["id"], body=file_metadata).execute()
            print(f"File renamed to {new_name}")
            move_file_to_folder(service, file_id=item["id"], folder_id=DESTINATION_ID)
            print("File Successfully Moved.")
            print("")
        except HttpError as error:
            print(f"An error occurred: {error}")
        # TODO: move files to renamed folder
    else:
        if empty:
            print("Captcha Folder Empty. Job Complete!")
        else:
            print("\nSuccess!")


# Function that moves file to destination folder. Does not require origin parameter
def move_file_to_folder(service, file_id, folder_id):
    try:
        # Retrieve the current folder file is in
        file = service.files().get(fileId=file_id, fields="parents").execute()
        previous_parents = ",".join(file.get("parents"))
        # Move the file to the new folder by swapping out old and new 'parent'
        file = service.files().update(fileId=file_id, addParents=folder_id,
                                      removeParents=previous_parents,
                                      fields='id, parents').execute()
        return file.get("parents")

    except HttpError as error:
        print(f"An error occurred: {error}")
        return None


def get_image_url_from_google_drive(service, image_id):

    # Get the URL of the image from Google Drive
    file = service.files().get(fileId=image_id, fields='webContentLink').execute()
    url = file.get('webContentLink')

    # Return the URL of the image
    return url
