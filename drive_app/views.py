import os
import json
import pandas as pd
from io import BytesIO
from PIL import Image
from pprint import pprint
from datetime import datetime
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from .utils import remove_duplicates     #assign_flags, 
from .filename import parse_filename   
from .grouping import process_images        #, assign_set_flags
from .classification import model_process_images        #, classify_image, handle_classification_results
from .models import ImageClassificationResult, ImageData
from .forms import ImageDataForm
from .load_architecture import load_architecture
from django.views.decorators.csrf import csrf_exempt


# Temporary in-memory storage
TEMP_DATA = []

# Initialize Google Drive API
def get_drive_service():
    from google.oauth2.service_account import Credentials
    SCOPES = ['https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_file('../myapp/credentials.json', scopes=SCOPES)
    return build('drive', 'v3', credentials=creds)

# List folders
def list_folders(request):
    service = get_drive_service()
    folder_id = '1ccHcq8tHZgMt6A5SuLpoQkkoQOOs-VzW'  # Replace with the ID of your main folder
    results = service.files().list(
        q=f"'{folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder'",
        fields="files(id, name)"
    ).execute()
    folders = results.get('files', [])
    return render(request, 'list_folders.html', {'folders': folders})

# Check folder availability based on the selected date
def check_date_folder(request):
    if request.method == 'POST':
        selected_date = request.POST.get('selected_date')
        if not selected_date:
            return render(request, 'list_folders.html', {'error_message': 'Please select a date.'})

        # Format date to match your folder naming convention (e.g., YYYYMMDD)
        folder_name = datetime.strptime(selected_date, '%Y-%m-%d').strftime('%Y%m%d')

        # Fetch folders from Google Drive
        service = get_drive_service()
        folder_id = '1ccHcq8tHZgMt6A5SuLpoQkkoQOOs-VzW'    #'1lY3qkz9skZ8nSFyPGFIEyAbOXCmiLLOj'  # Replace with your main folder ID
        results = service.files().list(
            q=f"'{folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder'",
            fields="files(id, name)"

        ).execute()
        folders = results.get('files', [])

        # Check if the folder exists
        matching_folder = next((folder for folder in folders if folder['name'] == folder_name), None)
        if matching_folder:
            return redirect('list_images', folder_id=matching_folder['id'])
        else:
            return render(request, 'list_folders.html', {'error_message': 'Data for this date is not available.'})

    return render(request, 'list_folders.html')

# List images in the selected folder
def list_images(request, folder_id):
    service = get_drive_service()
    
    image_data = []
    page_token = None           #pagination

    while True:
        results = service.files().list(
            q=f"'{folder_id}' in parents and mimeType contains 'image/'",
            fields="nextPageToken, files(id, name, createdTime, thumbnailLink)",
            pageToken=page_token,
            pageSize=100
        ).execute()
        images = results.get('files', [])

        for file in images:
            parsed_data = parse_filename(file['name'])
            # Example metadata for each image
            image_data.append({
                'thumbnailLink': file['thumbnailLink'],
                'bucketLink': f"https://drive.google.com/uc?id={file['id']}",
                'item_weight':  parsed_data['weight'],                      
                'time_date': parsed_data['timestamp'],                      
                'camera_flag': parsed_data['camera_flag'],             
                'mcu_flag': parsed_data['mcu_flag'],                    
                'name': file.get('name'),
            })

        #check for next page
        page_token = results.get('nextPageToken')
        if not page_token:
            break

    
    image_data = remove_duplicates(image_data)      #remove duplicates
    sets = process_images(image_data)       #create set acc. to random number and set flags for RN(random number), TM(timestamp) and WT(weight)
    print(type(sets)) 

    # Load CLIP model
    model = load_architecture()
    model_process_images(sets, model)     #process the images

    for image_set in sets:
        print("Set:")
        for image in image_set:
            print(f"Filename: {image['name']}, Weight: {image['weight']}, Timestamp: {image['timestamp']}, RN-flag: {image['set_flag']}, TM-flag: {image['time_flag']}, weight-flag: {image['weight_flag']}, prediction: {image['classification_result']}")

    image_data.sort(key=lambda x: x['name'])         # Sort by time_date in ascending order

    #segregate according to RN number sets into columns
    image_rows = []
    for image_data in sets:
        # Handle case where there is exactly 1 image
        if len(image_data) == 1:
            image_rows.append([None, image_data[0]])  # Image in the second column, first column is empty.
        
        # Handle case where there are exactly 2 images
        elif len(image_data) == 2:
            image_rows.append(image_data)  # Both images in one row
        
        # Handle case where there are more than 2 images
        else:
            # Group images into pairs for rows
            for i in range(0, len(image_data), 2):
                image_rows.append(image_data[i:i+2])


    context = {
        "table_rows": image_rows,
        # "form" : form
    }

    return render(request, "list_images.html", context)
    # return render(request, 'list_images.html', {'images': image_data})    


#Update - data for save button
@csrf_exempt
def update_data(request):
    global TEMP_DATA
    if request.method == "POST":
        # Parse the incoming data
        data = json.loads(request.body).get("data", [])
        if not data:
            return JsonResponse({"error": "No data received"}, status=400)

        # Update TEMP_DATA
        TEMP_DATA = data  # Replace or modify as needed
        print("Updated Temporary Data:", TEMP_DATA)  # Debugging
        print(TEMP_DATA)
        return JsonResponse({"message": "Data updated successfully"}, status=200)

    return JsonResponse({"error": "Invalid request"}, status=400)


#export excel file
@csrf_exempt
def export_to_excel(request):
    global TEMP_DATA
    if request.method == "POST":
        if not TEMP_DATA:
            return JsonResponse({"error": "No data to export"}, status=400)

        # Convert TEMP_DATA to DataFrame
        df = pd.DataFrame(TEMP_DATA)
        print("Exporting DataFrame:\n", df)  # Debugging
        # print(df)

        # Create an Excel file in memory
        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = 'attachment; filename="updated_data.xlsx"'

        with pd.ExcelWriter(response, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False)

        return response

    return JsonResponse({"error": "Invalid request"}, status=400)




# #data structure of image_data
# print(type(image_data))
# print(dir(image_data))
# # Loop through the list and inspect each item
# for idx, item in enumerate(image_data):
#     print(f"Item {idx}:")
#     print(f"  Type: {type(item)}")
#     print("  Value:")
#     pprint(item)
#     print("-" * 20)