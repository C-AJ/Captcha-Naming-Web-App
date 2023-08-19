from django.shortcuts import render
from .models import Text
from django.http import HttpResponse
from django.shortcuts import redirect

def home_view(request):
    # Get the URL of the image from Google Drive
    image_id = get_id(service, ORIGIN_ID)
    if not image_id:
        return render(request, 'finished.html')
    url = get_image_url_from_google_drive(service, image_id=image_id)

    # Get the text entered by the user
    if 'rename' in request.POST:
        text = request.POST.get('text')
        current_id = request.POST.get('current_id')
        rename_file(service, current_id, text)
        return redirect('home')
    if 'skip' in request.POST:
        current_id = request.POST.get('current_id')
        move_file_to_folder(service, current_id, TRASH_ID)
        print("skipped")
        return redirect('home')
        

    context = {'url': url, 'image_id': image_id}

    # Render the template with the URL of the image and the text box
    return render(request, 'home.html', context)

import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
import random

SCOPES = ["https://www.googleapis.com/auth/drive"]
creds = service_account.Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
service = build('drive', 'v3', credentials=creds)

# Change to id of 'origin' folder
ORIGIN_ID = '11_Le0LIIPHquOqa7kJ5Z3TC2AghkuGIT'
# Change to id of 'in progress' folder or subfolder
TRASH_ID = "19YNFgPlEPOJ-j8tffE0tF-lEKmIqKx-y"
# Change to id of 'renamed' folder or subfolder
DESTINATION_ID = "1ZOFhIKBaM_3X7NvU1n8kfSjFIIcdPXc6"

def rename_files(service, folder_id):
    # gets a list of all the files in the folder that aren't subfolders
    results = service.files().list(q=f"'{folder_id}' in parents and trashed=false and mimeType != 'application/vnd.google-apps.folder'",
                             fields="nextPageToken, files(id, name)").execute()
    items = results.get("files", [])
    if not items:
        print("No files present")
    else:
        # iterates through every file asks the user to rename it
        for item in items:
            move_file_to_folder(service, file_id=item["id"], folder_id=TRASH_ID)
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
        else:
            print("\nSuccess!")

def rename_file(service, image_id, solution):
    image = service.files().get(fileId=image_id, fields='name, id').execute()
    image_metadata = {"name": solution}
    try:
        service.files().update(fileId=image["id"], body=image_metadata).execute()
        move_file_to_folder(service, file_id=image['id'], folder_id=DESTINATION_ID)
    except HttpError as error:
        print(f"An error occurred: {error}")
    print("successfully renamed")
    return HttpResponse('it worked')


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

def get_id(service, origin_id):
    results = service.files().list(q=f"'{origin_id}' in parents and trashed=false and mimeType != 'application/vnd.google-apps.folder'",
                             fields="nextPageToken, files(id, name)").execute()
    items = results.get("files", [])
    if not items:
        return None
    else:
        random_file = random.choice(items)
        return random_file['id']